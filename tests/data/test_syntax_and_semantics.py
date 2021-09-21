"""Test the syntax of the AWS IP address ranges JSON data.

https://docs.aws.amazon.com/general/latest/gr/aws-ip-ranges.html

Testing the documented data structures and assumptions validates the data
dependencies and lets us know when something changes.
"""

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import urllib.request
from collections import defaultdict
from datetime import datetime
from ipaddress import ip_network, IPv4Network, IPv6Network
from typing import Any, Dict, List

import pytest

from awsipranges.config import (
    AWS_IP_ADDRESS_RANGES_URL,
    CREATE_DATE_FORMAT,
    CREATE_DATE_TIMEZONE,
)


pytestmark = pytest.mark.data


# Fixtures
@pytest.fixture(scope="module")
def json_data() -> Dict[str, Any]:
    """Retrieve and parse JSON data from a URL."""
    with urllib.request.urlopen(AWS_IP_ADDRESS_RANGES_URL) as response:
        response_data = json.load(response)
    return response_data


@pytest.fixture(scope="module")
def create_date(json_data) -> datetime:
    """The JSON file publication date and time as a Python datetime object.

    createDate is the JSON document's publication date and time, in UTC
    YY-MM-DD-hh-mm-ss format.
    """
    assert "createDate" in json_data
    create_date_string = json_data["createDate"]
    assert isinstance(create_date_string, str)

    create_date_datetime = datetime.strptime(create_date_string, CREATE_DATE_FORMAT)
    create_date_datetime = create_date_datetime.replace(tzinfo=CREATE_DATE_TIMEZONE)

    return create_date_datetime


@pytest.fixture(scope="module")
def deduplicated_prefixes(json_data) -> Dict[IPv4Network, List[Dict[str, str]]]:
    """Dictionary of `prefixes` indexed by IPv4Network."""
    deduplicated_prefixes = defaultdict(list)

    for prefix in json_data["prefixes"]:
        prefix_string = prefix["ip_prefix"]
        prefix_network = ip_network(prefix_string)
        deduplicated_prefixes[prefix_network].append(prefix)

    return deduplicated_prefixes


@pytest.fixture(scope="module")
def deduplicated_ipv6_prefixes(json_data) -> Dict[IPv6Network, List[Dict[str, str]]]:
    """Dictionary of `ipv6_prefixes` indexed by IPv6Network."""
    deduplicated_ipv6_prefixes = defaultdict(list)

    for ipv6_prefix in json_data["ipv6_prefixes"]:
        prefix_string = ipv6_prefix["ipv6_prefix"]
        prefix_network = ip_network(prefix_string)
        deduplicated_ipv6_prefixes[prefix_network].append(ipv6_prefix)

    return deduplicated_ipv6_prefixes


# Tests
def test_log_sync_token(json_data):
    """Capture the syncToken for the JSON data file."""
    print("syncToken:", json_data["syncToken"])


def test_log_json_data_summary(
    json_data, deduplicated_prefixes, deduplicated_ipv6_prefixes
):
    """Capture a summary of the data to the test log."""
    json_data_summary = {
        "sync_token": json_data["syncToken"],
        "create_date": json_data["createDate"],
        "prefixes": {
            "count": len(json_data["prefixes"]),
            "unique": len(deduplicated_prefixes),
            "duplicate": len(json_data["prefixes"]) - len(deduplicated_prefixes),
        },
        "ipv6_prefixes": {
            "count": len(json_data["ipv6_prefixes"]),
            "unique": len(deduplicated_ipv6_prefixes),
            "duplicate": len(json_data["ipv6_prefixes"])
            - len(deduplicated_ipv6_prefixes),
        },
    }
    print("json_data_summary = ", json.dumps(json_data_summary, indent=2))


def test_parsing_create_date(create_date):
    """Ensure the createDate attribute is parsable into a Python datetime."""
    assert isinstance(create_date, datetime)


def test_sync_token_is_publication_time_in_unix_epoch_time_format(
    json_data, create_date
):
    """Ensure the syncToken is the publication time, in Unix epoch time format."""
    assert "syncToken" in json_data
    sync_token = int(json_data["syncToken"])
    assert isinstance(sync_token, int)

    publication_time = datetime.fromtimestamp(sync_token, tz=CREATE_DATE_TIMEZONE)

    assert publication_time == create_date


def test_prefixes_syntax(json_data):
    """Validate the structure of the IPv4 `prefixes` objects."""
    assert "prefixes" in json_data
    prefixes = json_data["prefixes"]
    assert isinstance(prefixes, list)

    for prefix in prefixes:
        assert "ip_prefix" in prefix
        assert isinstance(prefix["ip_prefix"], str)
        assert isinstance(ip_network(prefix["ip_prefix"]), IPv4Network)

        assert "region" in prefix
        assert isinstance(prefix["region"], str)

        assert "network_border_group" in prefix
        assert isinstance(prefix["network_border_group"], str)

        assert "service" in prefix
        assert isinstance(prefix["service"], str)


def test_ipv6_prefixes_syntax(json_data):
    """Validate the structure of the IPv6 `ipv6_prefixes` objects."""
    assert "ipv6_prefixes" in json_data
    ipv6_prefixes = json_data["ipv6_prefixes"]
    assert isinstance(ipv6_prefixes, list)

    for ipv6_prefix in ipv6_prefixes:
        assert "ipv6_prefix" in ipv6_prefix
        assert isinstance(ipv6_prefix["ipv6_prefix"], str)
        assert isinstance(ip_network(ipv6_prefix["ipv6_prefix"]), IPv6Network)

        assert "region" in ipv6_prefix
        assert isinstance(ipv6_prefix["region"], str)

        assert "network_border_group" in ipv6_prefix
        assert isinstance(ipv6_prefix["network_border_group"], str)

        assert "service" in ipv6_prefix
        assert isinstance(ipv6_prefix["service"], str)


def test_duplicate_prefix_records_are_from_same_region(deduplicated_prefixes):
    """Verify duplicate records for a prefix are from the same Region.

    A single prefix should not be advertised from multiple Regions.
    """
    test = True
    for prefix, records in deduplicated_prefixes.items():
        region = records[0]["region"]
        if not all([record["region"] == region for record in records]):
            test = False
            print(
                f"Prefix {prefix!s} is advertised from multiple Regions: "
                f"{[record['region'] for record in records]}"
            )
    assert test


def test_duplicate_prefix_records_are_from_same_network_border_group(
    deduplicated_prefixes,
):
    """Verify duplicate records are from the same network border group.

    A single prefix should not be advertised from multiple network border
    groups.
    """
    test = True
    for prefix, records in deduplicated_prefixes.items():
        network_border_group = records[0]["network_border_group"]
        if not all(
            [
                record["network_border_group"] == network_border_group
                for record in records
            ]
        ):
            test = False
            print(
                f"Prefix {prefix!s} is advertised from multiple network border groups: "
                f"{[record['network_border_group'] for record in records]}"
            )
    assert test


def test_duplicate_prefix_records_are_for_different_services(
    deduplicated_prefixes,
):
    """Verify duplicate records for a prefix are for different services.

    A single prefix may service multiple AWS services, which should be the cause
    for having duplicate records. Each duplicate records should be for a
    different service.
    """
    test = True
    for prefix, records in deduplicated_prefixes.items():
        if len(records) == 1:
            # A single record for this prefix
            continue

        # Unique set of services from the records
        services = {record["service"] for record in records}
        if len(services) != len(records):
            test = False
            print(
                f"Prefix {prefix!s} has duplicate services: "
                f"{[record['service'] for record in records]}"
            )
    assert test


def test_prefixes_contain_subnets(deduplicated_prefixes):
    """Verify IPv4 prefixes contain subnets (more specific prefixes)."""
    for test_prefix in deduplicated_prefixes:
        for prefix in deduplicated_prefixes:
            if test_prefix != prefix and test_prefix.subnet_of(prefix):
                assert True
                return
    assert False


def test_duplicate_ipv6_prefix_records_are_from_same_region(deduplicated_ipv6_prefixes):
    """Verify duplicate records for a prefix are from the same Region.

    A single prefix should not be advertised from multiple Regions.
    """
    test = True
    for prefix, records in deduplicated_ipv6_prefixes.items():
        region = records[0]["region"]
        if not all([record["region"] == region for record in records]):
            test = False
            print(
                f"Prefix {prefix!s} is advertised from multiple Regions: "
                f"{[record['region'] for record in records]}"
            )
    assert test


def test_duplicate_ipv6_prefix_records_are_from_same_network_border_group(
    deduplicated_ipv6_prefixes,
):
    """Verify duplicate records are from the same network border group.

    A single prefix should not be advertised from multiple network border
    groups.
    """
    test = True
    for prefix, records in deduplicated_ipv6_prefixes.items():
        network_border_group = records[0]["network_border_group"]
        if not all(
            [
                record["network_border_group"] == network_border_group
                for record in records
            ]
        ):
            test = False
            print(
                f"Prefix {prefix!s} is advertised from multiple network border "
                f"groups: "
                f"{[record['network_border_group'] for record in records]}"
            )
    assert test


def test_duplicate_ipv6_prefix_records_are_for_different_services(
    deduplicated_ipv6_prefixes,
):
    """Verify duplicate records for a prefix are for different services.

    A single prefix may service multiple AWS services, which should be the cause
    for having duplicate records. Each duplicate records should be for a
    different service.
    """
    test = True
    for prefix, records in deduplicated_ipv6_prefixes.items():
        if len(records) == 1:
            # A single record for this prefix
            continue

        # Unique set of services from the records
        services = {record["service"] for record in records}
        if len(services) != len(records):
            test = False
            print(
                f"Prefix {prefix!s} has duplicate services: "
                f"{[record['service'] for record in records]}"
            )
    assert test


def test_ipv6_prefixes_contain_subnets(deduplicated_ipv6_prefixes):
    """Verify IPv6 prefixes contain subnets (more specific prefixes)."""
    for test_ipv6_prefix in deduplicated_ipv6_prefixes:
        for ipv6_prefix in deduplicated_ipv6_prefixes:
            if test_ipv6_prefix != ipv6_prefix and test_ipv6_prefix.subnet_of(
                ipv6_prefix
            ):
                assert True
                return
    assert False
