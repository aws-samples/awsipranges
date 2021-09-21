"""Unit tests for the awsipprefix module."""

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import ipaddress
import random

from awsipranges.models.awsipprefix import aws_ip_prefix, AWSIPv4Prefix, AWSIPv6Prefix
from tests.utils import (
    random_ipv4_host_in_network,
    random_ipv4_network,
    random_ipv6_host_in_network,
    random_ipv6_network,
    random_string,
)


ITERATIONS_OF_RANDOM_TESTS = 100


# Helper functions
def random_aws_ipv4_prefix() -> AWSIPv4Prefix:
    return AWSIPv4Prefix(
        prefix=random_ipv4_network(),
        region=random_string(),
        network_border_group=random_string(),
        services=(tuple(random_string() for _ in range(random.randint(1, 5)))),
    )


def random_aws_ipv6_prefix() -> AWSIPv6Prefix:
    return AWSIPv6Prefix(
        prefix=random_ipv6_network(),
        region=random_string(),
        network_border_group=random_string(),
        services=(tuple(random_string() for _ in range(random.randint(1, 5)))),
    )


# Happy path tests
def test_creating_basic_aws_ipv4_prefix():
    prefix = AWSIPv4Prefix(
        prefix="3.5.140.0/22",
        region="ap-northeast-2",
        network_border_group="ap-northeast-2",
        services=("AMAZON", "EC2", "S3"),
    )
    assert isinstance(prefix, AWSIPv4Prefix)
    print(repr(prefix))


def test_creating_basic_aws_ipv4_prefix_with_factory_function():
    json_data = {
        "ip_prefix": "3.5.140.0/22",
        "region": "ap-northeast-2",
        "network_border_group": "ap-northeast-2",
        "service": "EC2",
    }
    prefix = aws_ip_prefix(json_data)
    assert isinstance(prefix, AWSIPv4Prefix)
    print(repr(prefix))


def test_creating_random_aws_ipv4_prefixes():
    for _ in range(ITERATIONS_OF_RANDOM_TESTS):
        prefix = random_aws_ipv4_prefix()
        assert isinstance(prefix, AWSIPv4Prefix)


def test_aws_ip4_prefix_attribute_access():
    prefix = random_aws_ipv4_prefix()
    assert isinstance(prefix, AWSIPv4Prefix)
    assert isinstance(prefix.prefix, ipaddress.IPv4Network)
    assert prefix.prefix == prefix.ip_prefix
    assert isinstance(prefix.region, str)
    assert isinstance(prefix.network_border_group, str)
    assert isinstance(prefix.services, tuple)
    assert isinstance(prefix.version, int)
    assert prefix.version == 4
    assert isinstance(prefix.prefixlen, int)
    assert isinstance(prefix.network_address, ipaddress.IPv4Address)
    assert isinstance(prefix.netmask, ipaddress.IPv4Address)
    assert isinstance(prefix.hostmask, ipaddress.IPv4Address)
    assert isinstance(prefix.with_prefixlen, str)
    assert isinstance(prefix.with_netmask, str)
    assert isinstance(prefix.with_hostmask, str)


def test_aws_ipv4_prefix_repr():
    print(repr(random_aws_ipv4_prefix()))


def test_aws_ipv4_prefix_str():
    print(random_aws_ipv4_prefix())


def test_aws_ipv4_prefix_eq():
    prefix = random_aws_ipv4_prefix()
    other_prefix = AWSIPv4Prefix(
        prefix=prefix.prefix,
        region=prefix.region,
        network_border_group=prefix.network_border_group,
        services=prefix.services,
    )
    assert prefix == other_prefix


def test_aws_ipv4_prefix_subnet_sort_order():
    supernet = AWSIPv4Prefix(
        "10.0.0.0/8",
        region=random_string(),
        network_border_group=random_string(),
        services=random_string(),
    )
    subnet1 = AWSIPv4Prefix(
        "10.0.0.0/16",
        region=random_string(),
        network_border_group=random_string(),
        services=random_string(),
    )
    subnet2 = AWSIPv4Prefix(
        "10.1.0.0/16",
        region=random_string(),
        network_border_group=random_string(),
        services=random_string(),
    )

    networks = [subnet2, subnet1, supernet]
    networks.sort()

    assert networks == [supernet, subnet1, subnet2]


def test_aws_ipv4_prefix_contains():
    prefix = random_aws_ipv4_prefix()
    address = random_ipv4_host_in_network(prefix.prefix)
    network = ipaddress.IPv4Network((address, 32))
    interface = ipaddress.IPv4Interface((address, network.prefixlen))
    string = str(address)

    assert string in prefix
    assert address in prefix
    assert network in prefix
    assert interface in prefix


def test_creating_basic_aws_ipv6_prefix():
    prefix = AWSIPv6Prefix(
        prefix="2a05:d070:e000::/40",
        region="me-south-1",
        network_border_group="me-south-1",
        services=("AMAZON", "EC2", "S3"),
    )
    assert isinstance(prefix, AWSIPv6Prefix)
    print(repr(prefix))


def test_creating_basic_aws_ipv6_prefix_with_factory_function():
    json_data = {
        "ipv6_prefix": "2a05:d070:e000::/40",
        "region": "me-south-1",
        "service": "EC2",
        "network_border_group": "me-south-1",
    }
    prefix = aws_ip_prefix(json_data)
    assert isinstance(prefix, AWSIPv6Prefix)
    print(repr(prefix))


def test_creating_random_aws_ipv6_prefixes():
    for _ in range(ITERATIONS_OF_RANDOM_TESTS):
        prefix = random_aws_ipv6_prefix()
        assert isinstance(prefix, AWSIPv6Prefix)


def test_aws_ip6_prefix_attribute_access():
    prefix = random_aws_ipv6_prefix()
    assert isinstance(prefix, AWSIPv6Prefix)
    assert isinstance(prefix.prefix, ipaddress.IPv6Network)
    assert prefix.prefix == prefix.ipv6_prefix
    assert isinstance(prefix.region, str)
    assert isinstance(prefix.network_border_group, str)
    assert isinstance(prefix.services, tuple)
    assert isinstance(prefix.version, int)
    assert prefix.version == 6
    assert isinstance(prefix.prefixlen, int)
    assert isinstance(prefix.network_address, ipaddress.IPv6Address)
    assert isinstance(prefix.netmask, ipaddress.IPv6Address)
    assert isinstance(prefix.hostmask, ipaddress.IPv6Address)
    assert isinstance(prefix.with_prefixlen, str)
    assert isinstance(prefix.with_netmask, str)
    assert isinstance(prefix.with_hostmask, str)


def test_aws_ipv6_prefix_repr():
    print(repr(random_aws_ipv6_prefix()))


def test_aws_ipv6_prefix_str():
    print(random_aws_ipv6_prefix())


def test_aws_ipv6_prefix_eq():
    prefix = random_aws_ipv6_prefix()
    other_prefix = AWSIPv6Prefix(
        prefix=prefix.prefix,
        region=prefix.region,
        network_border_group=prefix.network_border_group,
        services=prefix.services,
    )
    assert prefix == other_prefix


def test_aws_ipv6_prefix_subnet_sort_order():
    supernet = AWSIPv6Prefix(
        "2001:face::/32",
        region=random_string(),
        network_border_group=random_string(),
        services=random_string(),
    )
    subnet1 = AWSIPv6Prefix(
        "2001:face::/48",
        region=random_string(),
        network_border_group=random_string(),
        services=random_string(),
    )
    subnet2 = AWSIPv6Prefix(
        "2001:face:1::/48",
        region=random_string(),
        network_border_group=random_string(),
        services=random_string(),
    )

    networks = [subnet2, subnet1, supernet]
    networks.sort()

    assert networks == [supernet, subnet1, subnet2]


def test_aws_ipv6_prefix_contains():
    prefix = random_aws_ipv6_prefix()
    address = random_ipv6_host_in_network(prefix.prefix)
    network = ipaddress.IPv6Network((address, 128))
    interface = ipaddress.IPv6Interface((address, network.prefixlen))
    string = str(address)

    assert string in prefix
    assert address in prefix
    assert network in prefix
    assert interface in prefix
