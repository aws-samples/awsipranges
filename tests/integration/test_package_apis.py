"""End-to-end package API tests."""

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import random
from datetime import datetime, timezone

import pytest

import awsipranges
from awsipranges import AWSIPPrefixes, AWSIPv4Prefix, AWSIPv6Prefix
from tests.utils import (
    random_ipv4_address,
    random_ipv4_host_in_network,
    random_ipv4_subnet_in_network,
    random_ipv6_address,
    random_ipv6_host_in_network,
    random_ipv6_subnet_in_network,
)


# Fixtures
@pytest.fixture(scope="session")
def aws_ip_ranges() -> AWSIPPrefixes:
    """Get the AWS IP address ranges."""
    return awsipranges.get_ranges()


# Happy path tests
def test_get_ranges(aws_ip_ranges: AWSIPPrefixes):
    assert isinstance(aws_ip_ranges, AWSIPPrefixes)


def test_create_date_is_utc_datetime(aws_ip_ranges: AWSIPPrefixes):
    assert isinstance(aws_ip_ranges.create_date, datetime)
    assert aws_ip_ranges.create_date.tzinfo == timezone.utc


def test_sync_token_is_opaque_string(aws_ip_ranges: AWSIPPrefixes):
    assert isinstance(aws_ip_ranges.sync_token, str)
    assert len(aws_ip_ranges.sync_token) > 0


def test_ipv4_prefixes_are_aws_ip4_prefixes(aws_ip_ranges: AWSIPPrefixes):
    for prefix in aws_ip_ranges.ipv4_prefixes:
        assert isinstance(prefix, AWSIPv4Prefix)


def test_ipv6_prefixes_are_aws_ipv6_prefixes(aws_ip_ranges: AWSIPPrefixes):
    for prefix in aws_ip_ranges.ipv6_prefixes:
        assert isinstance(prefix, AWSIPv6Prefix)


def test_can_iterate_over_all_aws_ip_prefixes(aws_ip_ranges: AWSIPPrefixes):
    for prefix in aws_ip_ranges:
        assert isinstance(prefix, (AWSIPv4Prefix, AWSIPv6Prefix))
    assert len(list(aws_ip_ranges)) == len(aws_ip_ranges.ipv4_prefixes) + len(
        aws_ip_ranges.ipv6_prefixes
    )


def test_can_check_if_ipv4_address_is_contained_in_aws_ip_prefixes(
    aws_ip_ranges: AWSIPPrefixes,
):
    prefix = random.choice(aws_ip_ranges.ipv4_prefixes)
    address = random_ipv4_host_in_network(prefix.prefix)
    assert address in aws_ip_ranges
    assert str(address) in aws_ip_ranges


def test_can_check_if_ipv6_address_is_contained_in_aws_ip_prefixes(
    aws_ip_ranges: AWSIPPrefixes,
):
    prefix = random.choice(aws_ip_ranges.ipv6_prefixes)
    address = random_ipv6_host_in_network(prefix.prefix)
    assert address in aws_ip_ranges
    assert str(address) in aws_ip_ranges


def test_can_index_aws_ip_prefix_by_ipv4_address(aws_ip_ranges: AWSIPPrefixes):
    prefix = random.choice(aws_ip_ranges.ipv4_prefixes)
    address = random_ipv4_host_in_network(prefix.prefix)

    # Possible prefixes
    possible_prefixes = set(aws_ip_ranges.get_prefix_and_supernets(address))
    assert prefix in possible_prefixes

    assert aws_ip_ranges[address] in possible_prefixes
    assert aws_ip_ranges[str(address)] in possible_prefixes


def test_can_index_aws_ip_prefix_by_ipv6_address(aws_ip_ranges: AWSIPPrefixes):
    prefix = random.choice(aws_ip_ranges.ipv6_prefixes)
    address = random_ipv6_host_in_network(prefix.prefix)

    # Possible prefixes
    possible_prefixes = set(aws_ip_ranges.get_prefix_and_supernets(address))
    assert prefix in possible_prefixes

    assert aws_ip_ranges[address] in possible_prefixes
    assert aws_ip_ranges[str(address)] in possible_prefixes


@pytest.mark.slow
def test_can_index_all_aws_ip_prefix_by_ipv4_address(aws_ip_ranges: AWSIPPrefixes):
    for prefix in aws_ip_ranges.ipv4_prefixes:
        address = random_ipv4_host_in_network(prefix.prefix)

        # Possible prefixes
        possible_prefixes = set(aws_ip_ranges.get_prefix_and_supernets(address))
        assert prefix in possible_prefixes

        assert aws_ip_ranges[address] in possible_prefixes
        assert aws_ip_ranges[str(address)] in possible_prefixes


@pytest.mark.slow
def test_can_index_all_aws_ip_prefix_by_ipv6_address(aws_ip_ranges: AWSIPPrefixes):
    for prefix in aws_ip_ranges.ipv6_prefixes:
        address = random_ipv6_host_in_network(prefix.prefix)

        # Possible prefixes
        possible_prefixes = set(aws_ip_ranges.get_prefix_and_supernets(address))
        assert prefix in possible_prefixes

        assert aws_ip_ranges[address] in possible_prefixes
        assert aws_ip_ranges[str(address)] in possible_prefixes


def test_can_index_aws_ip_prefix_by_ipv4_network(aws_ip_ranges: AWSIPPrefixes):
    prefix = random.choice(aws_ip_ranges.ipv4_prefixes)
    network = prefix.prefix

    # Possible prefixes
    possible_prefixes = set(aws_ip_ranges.get_prefix_and_supernets(network))
    assert prefix in possible_prefixes

    assert aws_ip_ranges[network] in possible_prefixes
    assert aws_ip_ranges[str(network)] in possible_prefixes


def test_can_index_aws_ip_prefix_by_ipv6_network(aws_ip_ranges: AWSIPPrefixes):
    prefix = random.choice(aws_ip_ranges.ipv6_prefixes)
    network = prefix.prefix

    # Possible prefixes
    possible_prefixes = set(aws_ip_ranges.get_prefix_and_supernets(network))
    assert prefix in possible_prefixes

    assert aws_ip_ranges[network] in possible_prefixes
    assert aws_ip_ranges[str(network)] in possible_prefixes


def test_can_index_aws_ip_prefix_by_ipv4_subnet(aws_ip_ranges: AWSIPPrefixes):
    prefix = random.choice(aws_ip_ranges.ipv4_prefixes)
    subnet = random_ipv4_subnet_in_network(prefix.prefix)

    # Possible prefixes
    possible_prefixes = set(aws_ip_ranges.get_prefix_and_supernets(subnet))
    assert prefix in possible_prefixes

    assert aws_ip_ranges[subnet] in possible_prefixes
    assert aws_ip_ranges[str(subnet)] in possible_prefixes


def test_can_index_aws_ip_prefix_by_ipv6_subnet(aws_ip_ranges: AWSIPPrefixes):
    prefix = random.choice(aws_ip_ranges.ipv6_prefixes)
    subnet = random_ipv6_subnet_in_network(prefix.prefix)

    # Possible prefixes
    possible_prefixes = set(aws_ip_ranges.get_prefix_and_supernets(subnet))
    assert prefix in possible_prefixes

    assert aws_ip_ranges[subnet] in possible_prefixes
    assert aws_ip_ranges[str(subnet)] in possible_prefixes


def test_can_get_aws_ip_prefix_by_ipv4_address(aws_ip_ranges: AWSIPPrefixes):
    prefix = random.choice(aws_ip_ranges.ipv4_prefixes)
    address = random_ipv4_host_in_network(prefix.prefix)

    # Possible prefixes
    possible_prefixes = set(aws_ip_ranges.get_prefix_and_supernets(address))
    assert prefix in possible_prefixes

    assert aws_ip_ranges.get(address) in possible_prefixes
    assert aws_ip_ranges.get(str(address)) in possible_prefixes


def test_can_get_aws_ip_prefix_by_ipv6_address(aws_ip_ranges: AWSIPPrefixes):
    prefix = random.choice(aws_ip_ranges.ipv6_prefixes)
    address = random_ipv6_host_in_network(prefix.prefix)

    # Possible prefixes
    possible_prefixes = set(aws_ip_ranges.get_prefix_and_supernets(address))
    assert prefix in possible_prefixes

    assert aws_ip_ranges.get(address) in possible_prefixes
    assert aws_ip_ranges.get(str(address)) in possible_prefixes


def test_get_unknown_ipv4_address_returns_default_value(aws_ip_ranges: AWSIPPrefixes):
    address = random_ipv4_address()
    assert aws_ip_ranges.get(address, default="default") == "default"
    assert aws_ip_ranges.get(str(address), default="default") == "default"


def test_get_unknown_ipv6_address_returns_default_value(aws_ip_ranges: AWSIPPrefixes):
    address = random_ipv6_address()
    assert aws_ip_ranges.get(address, default="default") == "default"
    assert aws_ip_ranges.get(str(address), default="default") == "default"


def test_can_filter_by_region(aws_ip_ranges: AWSIPPrefixes):
    region = random.choice(list(aws_ip_ranges.regions))
    filtered_ranges = aws_ip_ranges.filter(regions=region)
    for prefix in filtered_ranges:
        assert prefix.region == region


def test_can_filter_by_multiple_regions(aws_ip_ranges: AWSIPPrefixes):
    regions = [
        random.choice(list(aws_ip_ranges.regions)),
        random.choice(list(aws_ip_ranges.regions)),
    ]
    filtered_ranges = aws_ip_ranges.filter(regions=regions)
    for prefix in filtered_ranges:
        assert prefix.region in regions


def test_can_filter_by_network_border_group(aws_ip_ranges: AWSIPPrefixes):
    network_border_group = random.choice(list(aws_ip_ranges.network_border_groups))
    filtered_ranges = aws_ip_ranges.filter(network_border_groups=network_border_group)
    for prefix in filtered_ranges:
        assert prefix.network_border_group == network_border_group


def test_can_filter_by_multiple_network_border_groups(aws_ip_ranges: AWSIPPrefixes):
    network_border_groups = [
        random.choice(list(aws_ip_ranges.network_border_groups)),
        random.choice(list(aws_ip_ranges.network_border_groups)),
    ]
    filtered_ranges = aws_ip_ranges.filter(network_border_groups=network_border_groups)
    for prefix in filtered_ranges:
        assert prefix.network_border_group in network_border_groups


def test_can_filter_by_service(aws_ip_ranges: AWSIPPrefixes):
    service = random.choice(list(aws_ip_ranges.services))
    filtered_ranges = aws_ip_ranges.filter(services=service)
    for prefix in filtered_ranges:
        assert service in prefix.services


def test_can_filter_by_multiple_services(aws_ip_ranges: AWSIPPrefixes):
    services = [
        random.choice(list(aws_ip_ranges.services)),
        random.choice(list(aws_ip_ranges.services)),
    ]
    filtered_ranges = aws_ip_ranges.filter(services=services)
    for prefix in filtered_ranges:
        assert set(services).intersection(set(prefix.services))
