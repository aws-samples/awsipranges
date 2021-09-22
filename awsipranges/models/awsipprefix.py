"""Model an AWS IP Prefix as a native Python object."""

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import itertools
from abc import ABC, abstractmethod
from functools import total_ordering
from ipaddress import (
    ip_network,
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from typing import Any, Dict, Iterable, Tuple, Union

from awsipranges.utils import check_type


@total_ordering
class AWSIPPrefix(ABC):
    """AWS IP Prefix."""

    __slots__ = ["_prefix", "_region", "_network_border_group", "_services"]

    _prefix: Union[IPv4Network, IPv6Network]
    _region: str
    _network_border_group: str
    _services: Tuple[str, ...]

    def __init__(
        self,
        prefix: Union[str, IPv4Network, IPv6Network],
        region: str,
        network_border_group: str,
        services: Union[str, Iterable[str]],
    ) -> None:
        super().__init__()

        check_type("prefix", prefix, (str, IPv4Network, IPv6Network))
        check_type("region", region, str)
        check_type("network_border_group", network_border_group, str)
        check_type("services", services, (str, tuple))

        self._prefix = ip_network(prefix) if isinstance(prefix, str) else prefix
        self._region = region
        self._network_border_group = network_border_group
        self._services = (
            (services,) if isinstance(services, str) else tuple(sorted(services))
        )

    @property
    @abstractmethod
    def prefix(self) -> Union[IPv4Network, IPv6Network]:
        """The public IP network prefix."""
        return self._prefix

    @property
    def region(self) -> str:
        """The AWS Region or `GLOBAL` for edge locations.

        The `CLOUDFRONT` and `ROUTE53` ranges are GLOBAL.
        """
        return self._region

    @property
    def network_border_group(self) -> str:
        """The name of the network border group.

        A network border group is a unique set of Availability Zones or Local
        Zones from where AWS advertises IP addresses.
        """
        return self._network_border_group

    @property
    def services(self) -> Tuple[str, ...]:
        """Services that use IP addresses in this IP prefix.

        The addresses listed for `API_GATEWAY` are egress only.

        The service `"AMAZON"` is not a service but rather an identifier used
        to get all IP address ranges - meaning that every prefix is contained in
        the subset of prefixes tagged with the `"AMAZON"` service. Some IP
        address ranges are only tagged with the `"AMAZON"` service.
        """
        return self._services

    def __repr__(self) -> str:
        """An executable string representation of this object."""
        return (
            f"{self.__class__.__name__}("
            f"{str(self._prefix)!r}, "
            f"region={self._region!r}, "
            f"network_border_group={self._network_border_group!r}, "
            f"services={self._services!r}"
            f")"
        )

    def __str__(self) -> str:
        """The IP prefix in CIDR notation."""
        return self._prefix.with_prefixlen

    @property
    def __tuple(self) -> tuple:
        """A tuple representation of the AWS IP prefix."""
        return self._prefix, self._region, self._network_border_group, self._services

    def __eq__(self, other) -> bool:
        """Compare for equality.

        This method allows comparisons between AWSIPPrefix objects, None,
        IPv4Network and IPv6Network objects, and strings that can be converted
        to IPv4Network and IPv6Network objects.

        **Raises:**

        A `ValueError` exception if the `other` object is a string and
        cannot be converted to an IPv4Network or IPv6Network object.

        A `TypeError` if the `other` object is of an unsupported type.
        """
        if other is None:
            return False

        if isinstance(other, str):
            other = ip_network(other)

        if isinstance(other, (IPv4Network, IPv6Network)):
            return self.prefix == other

        if isinstance(other, AWSIPPrefix):
            return self.__tuple == other.__tuple

        raise TypeError(
            f"Cannot compare an AWSIPPrefix object with an object of type"
            f" {other!r}."
        )

    def __hash__(self) -> int:
        return hash(self.__tuple)

    def __lt__(self, other) -> bool:
        """Comparison operator to facilitate sorting.

        **Sort order:**

        - IPv4 prefixes before IPv6 prefixes
        - IP network addresses in ascending order
        - IP prefix length in ascending order
        - Region in ascending order
        - Network border group in ascending order
        - Services in ascending order
        """
        # Allow comparison between AWSIPPrefixes and Python native IPv4 and IPv6
        # network objects.
        if isinstance(other, (IPv4Network, IPv6Network)):
            if self.prefix != other:
                return self.prefix < other
            else:
                return False

        # Compare two AWSIPPrefix objects
        if self.prefix.version != other.prefix.version:
            return self.prefix.version < other.prefix.version

        if self.prefix.network_address != other.prefix.network_address:
            return self.prefix.network_address < other.prefix.network_address

        if self.prefix.prefixlen != other.prefix.prefixlen:
            return self.prefix.prefixlen < other.prefix.prefixlen

        if self.region != other.region:
            return self.region < other.region

        if self.network_border_group != other.network_border_group:
            return self.network_border_group < other.network_border_group

        if self.services != other.services:
            return self.services < other.services

        return False

    def __contains__(
        self,
        item: Union[
            str,
            IPv4Address,
            IPv4Network,
            IPv4Interface,
            IPv6Address,
            IPv6Network,
            IPv6Interface,
        ],
    ) -> bool:
        check_type(
            "item",
            item,
            (
                str,
                IPv4Address,
                IPv4Network,
                IPv4Interface,
                IPv6Address,
                IPv6Network,
                IPv6Interface,
            ),
        )

        item_network = ip_network(item, strict=False)

        if item_network.version != self.version:
            return False

        return item_network.subnet_of(self._prefix)

    @property
    def version(self) -> int:
        """The IP version (4, 6)."""
        return self._prefix.version

    @property
    @abstractmethod
    def network_address(self) -> Union[IPv4Address, IPv6Address]:
        """The network address for the network."""
        return self._prefix.network_address

    @property
    def prefixlen(self) -> int:
        """Length of the network prefix, in bits."""
        return self._prefix.prefixlen

    @property
    def with_prefixlen(self) -> str:
        """A string representation of the IP prefix, in network/prefix notation."""
        return self._prefix.with_prefixlen

    @property
    @abstractmethod
    def netmask(self) -> Union[IPv4Address, IPv6Address]:
        """The net mask, as an IP Address object."""
        return self._prefix.netmask

    @property
    def with_netmask(self) -> str:
        """A string representation of the network, with the mask in net mask notation."""
        return self._prefix.with_netmask

    @property
    @abstractmethod
    def hostmask(self) -> Union[IPv4Address, IPv6Address]:
        """The host mask (aka. wildcard mask), as an IP Address object."""
        return self._prefix.hostmask

    @property
    def with_hostmask(self) -> str:
        """A string representation of the network, with the mask in host mask notation."""
        return self._prefix.with_hostmask

    @property
    def num_addresses(self) -> int:
        """The total number of addresses in the network."""
        return self._prefix.num_addresses

    def __getattr__(self, name: str) -> Any:
        """Proxy all other attributes to self._prefix."""
        return getattr(self._prefix, name)


class AWSIPv4Prefix(AWSIPPrefix):
    """AWS IPv4 Prefix."""

    __slots__ = ["_prefix", "_region", "_network_border_group", "_services"]

    _prefix: IPv4Network

    def __init__(
        self,
        prefix: Union[str, IPv4Network],
        region: str,
        network_border_group: str,
        services: Union[str, Iterable[str]],
    ) -> None:
        super().__init__(
            prefix=prefix,
            region=region,
            network_border_group=network_border_group,
            services=services,
        )
        check_type("prefix", self._prefix, IPv4Network)

    @property
    def prefix(self) -> IPv4Network:
        """The public IPv4 network prefix."""
        return self._prefix

    @property
    def ip_prefix(self) -> IPv4Network:
        """The public IPv4 network prefix.

        This is a convenience attribute to maintain API compatibility with the
        JSON attribute names.
        """
        return self._prefix

    @property
    def network_address(self) -> IPv4Address:
        """The network address for the network."""
        return self._prefix.network_address

    @property
    def netmask(self) -> IPv4Address:
        """The net mask, as an IPv4Address object."""
        return self._prefix.netmask

    @property
    def hostmask(self) -> IPv4Address:
        """The host mask (aka. wildcard mask), as an IPv4Address object."""
        return self._prefix.hostmask


class AWSIPv6Prefix(AWSIPPrefix):
    """AWS IPv6 Prefix."""

    __slots__ = ["_prefix", "_region", "_network_border_group", "_services"]

    _prefix: IPv6Network

    def __init__(
        self,
        prefix: Union[str, IPv6Network],
        region: str,
        network_border_group: str,
        services: Union[str, Iterable[str]],
    ) -> None:
        super().__init__(
            prefix=prefix,
            region=region,
            network_border_group=network_border_group,
            services=services,
        )
        check_type("prefix", self._prefix, IPv6Network)

    @property
    def prefix(self) -> IPv6Network:
        """The public IPv6 network prefix."""
        return self._prefix

    @property
    def ipv6_prefix(self) -> IPv6Network:
        """The public IPv6 network prefix.

        This is a convenience attribute to maintain API compatibility with the
        JSON attribute names.
        """
        return self._prefix

    @property
    def network_address(self) -> IPv6Address:
        """The network address for the network."""
        return self._prefix.network_address

    @property
    def netmask(self) -> IPv6Address:
        """The net mask, as an IPv6Address object."""
        return self._prefix.netmask

    @property
    def hostmask(self) -> IPv6Address:
        """The host mask (aka. wildcard mask), as an IPv6Address object."""
        return self._prefix.hostmask


def aws_ip_prefix(json_data: Dict[str, str]) -> Union[AWSIPv4Prefix, AWSIPv6Prefix]:
    """Factory function to create AWS IP Prefix objects from JSON data."""
    check_type("data", json_data, dict)
    assert "ip_prefix" in json_data or "ipv6_prefix" in json_data
    assert "region" in json_data
    assert "network_border_group" in json_data
    assert "service" in json_data

    if "ip_prefix" in json_data:
        return AWSIPv4Prefix(
            prefix=json_data["ip_prefix"],
            region=json_data["region"],
            network_border_group=json_data["network_border_group"],
            services=json_data["service"],
        )

    if "ipv6_prefix" in json_data:
        return AWSIPv6Prefix(
            prefix=json_data["ipv6_prefix"],
            region=json_data["region"],
            network_border_group=json_data["network_border_group"],
            services=json_data["service"],
        )


def combine_prefixes(
    prefixes: Iterable[Union[AWSIPv4Prefix, AWSIPv6Prefix]]
) -> Union[AWSIPv4Prefix, AWSIPv6Prefix]:
    """Combine multiple AWS IP prefix records into a single AWS IP prefix.

    The prefix records should have identical prefixes, regions, and network
    border groups. Only the services should be combined.
    """
    prefixes = list(prefixes)
    assert len(prefixes) > 1

    first = prefixes[0]

    check_type("prefixes", first, (AWSIPv4Prefix, AWSIPv6Prefix))
    for prefix in prefixes[1:]:
        check_type("prefixes", prefix, type(first))

    # Ensure prefixes are the same (only services are different) before combining
    if not all(
        [
            (prefix.prefix, prefix.region, prefix.network_border_group)
            == (first.prefix, first.region, first.network_border_group)
            for prefix in prefixes[1:]
        ]
    ):
        raise ValueError(
            "Cannot combine prefixes with different prefix, region, or "
            "network_border_group values."
        )

    # Combine the services
    services = set(
        itertools.chain.from_iterable((prefix.services for prefix in prefixes))
    )
    services = tuple(sorted(services))

    return type(first)(
        prefix=first.prefix,
        region=first.region,
        network_border_group=first.network_border_group,
        services=services,
    )
