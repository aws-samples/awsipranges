"""Tests utility functions and classes."""

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import random
import string
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)


IPV4_START = "1.0.0.0"
IPV4_END = "223.255.255.0"
IPV4_MIN_PREFIX_LENGTH = 8
IPV4_MAX_PREFIX_LENGTH = 32

IPV6_START = "2000::"
IPV6_END = "2c00:ffff:ffff:ffff:ffff:ffff:ffff:ffff"
IPV6_MIN_PREFIX_LENGTH = 8
IPV6_MAX_PREFIX_LENGTH = 128

RANDOM_STRING_CHARACTERS = string.ascii_letters + "0123456789" + "-"


def random_string(min_length: int = 12, max_length: int = 12) -> str:
    assert min_length <= max_length
    if min_length == max_length:
        length = max_length
    else:
        length = random.randint(min_length, max_length)

    random_characters = [random.choice(RANDOM_STRING_CHARACTERS) for _ in range(length)]

    return "".join(random_characters)


def random_ipv4_address(
    start: str = IPV4_START,
    end: str = IPV4_END,
) -> IPv4Address:
    start_int = int(IPv4Address(start))
    end_int = int(IPv4Address(end))
    ip_int = random.randint(start_int, end_int)
    return IPv4Address(ip_int)


def random_ipv4_interface(
    start: str = IPV4_START,
    end: str = IPV4_END,
    min_prefix_length: int = IPV4_MIN_PREFIX_LENGTH,
    max_prefix_length: int = IPV4_MAX_PREFIX_LENGTH,
) -> IPv4Interface:
    ip = random_ipv4_address(start, end)
    prefix_len = random.randint(min_prefix_length, max_prefix_length)
    return IPv4Interface((ip, prefix_len))


def random_ipv4_network(
    start: str = IPV4_START,
    end: str = IPV4_END,
    min_prefix_length: int = IPV4_MIN_PREFIX_LENGTH,
    max_prefix_length: int = IPV4_MAX_PREFIX_LENGTH,
) -> IPv4Network:
    interface = random_ipv4_interface(
        start=start,
        end=end,
        min_prefix_length=min_prefix_length,
        max_prefix_length=max_prefix_length,
    )
    return interface.network


def random_ipv4_host_in_network(network: IPv4Network) -> IPv4Address:
    if network.prefixlen == IPV4_MAX_PREFIX_LENGTH:
        # Host (/32) network
        return network.network_address
    elif network.prefixlen == IPV4_MAX_PREFIX_LENGTH - 1:
        # Point-to-point (/31) network
        start_int = int(network.network_address)
        end_int = int(network.network_address) + 1
    else:
        start_int = int(network.network_address) + 1
        end_int = int(network.network_address) + network.num_addresses - 2

    ip_int = random.randint(start_int, end_int)
    return IPv4Address(ip_int)


def random_ipv4_subnet_in_network(network: IPv4Network) -> IPv4Network:
    if network.prefixlen == IPV4_MAX_PREFIX_LENGTH:
        # Host (/32) network
        return network
    elif network.prefixlen == IPV4_MAX_PREFIX_LENGTH - 1:
        # Point-to-point (/31) network
        subnet_int = random.choice([0, 1])
        prefix_len = IPV4_MAX_PREFIX_LENGTH
    else:
        # Regular network
        min_prefix_len = network.prefixlen + 1
        max_prefix_len = IPV4_MAX_PREFIX_LENGTH - 1
        prefix_len = random.randint(min_prefix_len, max_prefix_len)
        num_subnet_bits = prefix_len - network.prefixlen
        subnet_int = random.randint(0, (2 ** num_subnet_bits) - 1)

    ip_int = int(network.network_address) + (
        subnet_int << (IPV4_MAX_PREFIX_LENGTH - prefix_len)
    )
    return IPv4Network((ip_int, prefix_len))


def random_ipv6_address(
    start: str = IPV6_START,
    end: str = IPV6_END,
) -> IPv6Address:
    start_int = int(IPv6Address(start))
    end_int = int(IPv6Address(end))
    ip_int = random.randint(start_int, end_int)
    return IPv6Address(ip_int)


def random_ipv6_interface(
    start: str = IPV6_START,
    end: str = IPV6_END,
    min_prefix_length: int = IPV6_MIN_PREFIX_LENGTH,
    max_prefix_length: int = IPV6_MAX_PREFIX_LENGTH,
) -> IPv6Interface:
    ip = random_ipv6_address(start, end)
    prefix_len = random.randint(min_prefix_length, max_prefix_length)
    return IPv6Interface((ip, prefix_len))


def random_ipv6_network(
    start: str = IPV6_START,
    end: str = IPV6_END,
    min_prefix_length: int = IPV6_MIN_PREFIX_LENGTH,
    max_prefix_length: int = IPV6_MAX_PREFIX_LENGTH,
) -> IPv6Network:
    interface = random_ipv6_interface(
        start=start,
        end=end,
        min_prefix_length=min_prefix_length,
        max_prefix_length=max_prefix_length,
    )
    return interface.network


def random_ipv6_host_in_network(network: IPv6Network) -> IPv6Address:
    if network.prefixlen == IPV6_MAX_PREFIX_LENGTH:
        # Host (/128) network
        return network.network_address
    elif network.prefixlen == IPV6_MAX_PREFIX_LENGTH - 1:
        # Point-to-point (/127) network
        start_int = int(network.network_address)
        end_int = int(network.network_address) + 1
    else:
        start_int = int(network.network_address) + 1
        end_int = int(network.network_address) + network.num_addresses - 2

    ip_int = random.randint(start_int, end_int)
    return IPv6Address(ip_int)


def random_ipv6_subnet_in_network(network: IPv6Network) -> IPv6Network:
    if network.prefixlen == IPV6_MAX_PREFIX_LENGTH:
        # Host (/128) network
        return network
    elif network.prefixlen == IPV6_MAX_PREFIX_LENGTH - 1:
        # Point-to-point (/127) network
        subnet_int = random.choice([0, 1])
        prefix_len = IPV6_MAX_PREFIX_LENGTH
    else:
        # Regular network
        min_prefix_len = network.prefixlen + 1
        max_prefix_len = IPV6_MAX_PREFIX_LENGTH - 1
        prefix_len = random.randint(min_prefix_len, max_prefix_len)
        num_subnet_bits = prefix_len - network.prefixlen
        subnet_int = random.randint(0, (2 ** num_subnet_bits) - 1)

    ip_int = int(network.network_address) + (
        subnet_int << (IPV6_MAX_PREFIX_LENGTH - prefix_len)
    )
    return IPv6Network((ip_int, prefix_len))
