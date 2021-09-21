"""Test the tests utility functions."""

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)

import pytest

import tests.utils


ITERATIONS_OF_RANDOM_TESTS = 100


pytestmark = pytest.mark.test_utils


# Happy path tests
def test_random_string():
    for _ in range(ITERATIONS_OF_RANDOM_TESTS):
        random_string = tests.utils.random_string(1, 50)
        assert isinstance(random_string, str)
        assert 1 <= len(random_string) <= 50


def test_random_ipv4_address():
    for _ in range(ITERATIONS_OF_RANDOM_TESTS):
        random_address = tests.utils.random_ipv4_address()
        assert isinstance(random_address, IPv4Address)


def test_random_ipv4_interface():
    for _ in range(ITERATIONS_OF_RANDOM_TESTS):
        random_interface = tests.utils.random_ipv4_interface()
        assert isinstance(random_interface, IPv4Interface)
        assert isinstance(random_interface.ip, IPv4Address)
        assert isinstance(random_interface.network, IPv4Network)


def test_random_ipv4_network():
    for _ in range(ITERATIONS_OF_RANDOM_TESTS):
        random_network = tests.utils.random_ipv4_network()
        assert isinstance(random_network, IPv4Network)


def test_random_ipv4_host_in_network():
    for _ in range(ITERATIONS_OF_RANDOM_TESTS):
        random_network = tests.utils.random_ipv4_network(
            max_prefix_length=tests.utils.IPV4_MAX_PREFIX_LENGTH - 2,
        )
        random_host = tests.utils.random_ipv4_host_in_network(random_network)
        assert isinstance(random_host, IPv4Address)
        assert random_host in random_network


def test_random_ipv4_subnet_in_network():
    for _ in range(ITERATIONS_OF_RANDOM_TESTS):
        random_network = tests.utils.random_ipv4_network(
            max_prefix_length=tests.utils.IPV4_MAX_PREFIX_LENGTH - 2,
        )
        random_subnet = tests.utils.random_ipv4_subnet_in_network(random_network)
        assert isinstance(random_subnet, IPv4Network)
        assert random_subnet.subnet_of(random_network)


def test_random_ipv6_address():
    for _ in range(ITERATIONS_OF_RANDOM_TESTS):
        random_address = tests.utils.random_ipv6_address()
        assert isinstance(random_address, IPv6Address)


def test_random_ipv6_interface():
    for _ in range(ITERATIONS_OF_RANDOM_TESTS):
        random_interface = tests.utils.random_ipv6_interface()
        assert isinstance(random_interface, IPv6Interface)
        assert isinstance(random_interface.ip, IPv6Address)
        assert isinstance(random_interface.network, IPv6Network)


def test_random_ipv6_network():
    for _ in range(ITERATIONS_OF_RANDOM_TESTS):
        random_network = tests.utils.random_ipv6_network()
        assert isinstance(random_network, IPv6Network)


def test_random_ipv6_host_in_network():
    for _ in range(ITERATIONS_OF_RANDOM_TESTS):
        random_network = tests.utils.random_ipv6_network(
            max_prefix_length=tests.utils.IPV6_MAX_PREFIX_LENGTH - 2,
        )
        random_host = tests.utils.random_ipv6_host_in_network(random_network)
        assert isinstance(random_host, IPv6Address)
        assert random_host in random_network


def test_random_ipv6_subnet_in_network():
    for _ in range(ITERATIONS_OF_RANDOM_TESTS):
        random_network = tests.utils.random_ipv6_network(
            max_prefix_length=tests.utils.IPV6_MAX_PREFIX_LENGTH - 2,
        )
        random_subnet = tests.utils.random_ipv6_subnet_in_network(random_network)
        assert isinstance(random_subnet, IPv6Network)
        assert random_subnet.subnet_of(random_network)
