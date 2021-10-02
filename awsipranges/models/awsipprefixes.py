"""Model a set of AWS IP address prefixes as a python collection."""

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import itertools
import pprint
from bisect import bisect_left
from collections import defaultdict
from datetime import datetime
from ipaddress import (
    ip_network,
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from typing import FrozenSet, Iterable, Optional, Tuple, Union

from awsipranges.models.awsipprefix import (
    AWSIPv4Prefix,
    AWSIPv6Prefix,
    combine_prefixes,
)
from awsipranges.utils import check_type, normalize_to_set, supernets, validate_values


# Main class
class AWSIPPrefixes(object):
    """A collection of AWS IP address prefixes."""

    _sync_token: Optional[str]
    _create_date: Optional[datetime]
    _ipv4_prefixes: Tuple[AWSIPv4Prefix, ...]
    _ipv6_prefixes: Tuple[AWSIPv6Prefix, ...]
    _md5: Optional[str]

    _regions: Optional[FrozenSet[str]] = None
    _network_border_groups: Optional[FrozenSet[str]] = None
    _services: Optional[FrozenSet[str]] = None

    def __init__(
        self,
        sync_token: Optional[str] = None,
        create_date: Optional[datetime] = None,
        ipv4_prefixes: Iterable[AWSIPv4Prefix] = None,
        ipv6_prefixes: Iterable[AWSIPv6Prefix] = None,
        md5: Optional[str] = None,
    ) -> None:
        super().__init__()

        check_type("sync_token", sync_token, str, optional=True)
        check_type("create_date", create_date, datetime, optional=True)
        check_type("ipv4_prefixes", ipv4_prefixes, Iterable)
        check_type("ipv6_prefixes", ipv6_prefixes, Iterable)
        check_type("md5", md5, str, optional=True)

        self._sync_token = sync_token
        self._create_date = create_date
        self._ipv4_prefixes = self._process_prefixes(ipv4_prefixes)
        self._ipv6_prefixes = self._process_prefixes(ipv6_prefixes)
        self._md5 = md5

    @staticmethod
    def _process_prefixes(
        prefixes: Iterable[Union[AWSIPv4Prefix, AWSIPv6Prefix]],
    ) -> Tuple[Union[AWSIPv4Prefix, AWSIPv6Prefix], ...]:
        """Create a deduplicated sorted tuple of AWS IP prefixes."""
        collect_duplicates = defaultdict(list)
        for prefix in prefixes:
            collect_duplicates[prefix.prefix].append(prefix)

        deduplicated_prefixes = list()
        for prefixes in collect_duplicates.values():
            if len(prefixes) == 1:
                prefix = prefixes[0]
            else:
                prefix = combine_prefixes(prefixes)
            deduplicated_prefixes.append(prefix)

        deduplicated_prefixes.sort()

        return tuple(deduplicated_prefixes)

    def _get_prefix(
        self, prefix: Union[str, IPv4Network, IPv6Network]
    ) -> Union[None, AWSIPv4Prefix, AWSIPv6Prefix]:
        """Retrieve a specific prefix from the AWS IP address ranges."""
        check_type("prefix", prefix, (str, IPv4Network, IPv6Network))
        if isinstance(prefix, str):
            prefix = ip_network(prefix)

        if isinstance(prefix, IPv4Network):
            prefixes_collection = self.ipv4_prefixes
        elif isinstance(prefix, IPv6Network):
            prefixes_collection = self.ipv6_prefixes
        else:
            raise TypeError("`prefix` must be an IPv4Network or IPv6Network object.")

        # Retrieve the prefix from the collection
        index = bisect_left(prefixes_collection, prefix)
        if (
            index != len(prefixes_collection)
            and prefixes_collection[index].prefix == prefix
        ):
            return prefixes_collection[index]
        else:
            # Not found
            return None

    @property
    def sync_token(self) -> str:
        """The publication time, in Unix epoch time format."""
        return self._sync_token

    @property
    def syncToken(self) -> str:  # noqa
        """The publication time, in Unix epoch time format.

        This is a convenience attribute to maintain API compatibility with the
        JSON attribute names.
        """
        return self._sync_token

    @property
    def create_date(self) -> datetime:
        """The publication date and time, in UTC."""
        return self._create_date

    @property
    def createDate(self) -> datetime:  # noqa
        """The publication date and time, in UTC.

        This is a convenience attribute to maintain API compatibility with the
        JSON attribute names.
        """
        return self._create_date

    @property
    def ipv4_prefixes(self) -> Tuple[AWSIPv4Prefix, ...]:
        """The IPv4 prefixes in the collection."""
        return self._ipv4_prefixes

    @property
    def prefixes(self) -> Tuple[AWSIPv4Prefix, ...]:
        """The IPv4 prefixes in the collection.

        This is a convenience attribute to maintain API compatibility with the
        JSON attribute names.
        """
        return self._ipv4_prefixes

    @property
    def ipv6_prefixes(self) -> Tuple[AWSIPv6Prefix, ...]:
        """The IPv6 prefixes in the collection."""
        return self._ipv6_prefixes

    @property
    def md5(self) -> Optional[str]:
        """The MD5 cryptographic hash value of the ip-ranges.json file.

        You can use this value to verify the integrity of the downloaded file.
        """
        return self._md5

    def __repr__(self) -> str:
        return pprint.pformat(
            {
                "sync_token": self.sync_token,
                "create_date": self.create_date,
                "ipv4_prefixes": self.ipv4_prefixes,
                "ipv6_prefixes": self.ipv6_prefixes,
                "md5": self.md5,
            }
        )

    def __contains__(
        self,
        item: Union[
            str,
            IPv4Address,
            IPv6Address,
            IPv4Interface,
            IPv6Interface,
            IPv4Network,
            IPv6Network,
            AWSIPv4Prefix,
            AWSIPv6Prefix,
        ],
    ) -> bool:
        """Is the IP address, interface, or network in the AWS IP Address ranges?"""
        try:
            self[item]
        except KeyError:
            return False
        else:
            return True

    def __getitem__(
        self,
        item: Union[
            str,
            IPv4Address,
            IPv6Address,
            IPv4Network,
            IPv6Network,
            IPv4Interface,
            IPv6Interface,
            AWSIPv4Prefix,
            AWSIPv6Prefix,
        ],
    ):
        """Get the AWS IP address prefix that contains the IPv4 or IPv6 item.

        Returns the longest-match prefix that contains the provided item.

        **Parameters:**

        - **item** (str, IPv4Address, IPv6Address, IPv4Network, IPv6Network,
          IPv4Interface, IPv6Interface, AWSIPv4Prefix, AWSIPv6Prefix) - the item
          to retrieve from the collection

        **Returns:**

        The `AWSIPv4Prefix` or `AWSIPv6Prefix` that contains the provided `item`.

        **Raises:**

        A `KeyError` exception if the provided `item` is not contained in the
        collection.
        """
        if isinstance(item, (AWSIPv4Prefix, AWSIPv6Prefix)):
            network = item.prefix
        else:
            network = ip_network(item, strict=False)

        for supernet in supernets(network):
            supernet_prefix = self._get_prefix(supernet)
            if supernet_prefix:
                return supernet_prefix

        raise KeyError(
            f"{item!r} is not contained in this AWSIPAddressRanges collection."
        )

    def get(
        self,
        key: Union[
            str,
            IPv4Address,
            IPv6Address,
            IPv4Network,
            IPv6Network,
            IPv4Interface,
            IPv6Interface,
            AWSIPv4Prefix,
            AWSIPv6Prefix,
        ],
        default=None,
    ) -> Union[AWSIPv4Prefix, AWSIPv6Prefix]:
        """Get the AWS IP address prefix that contains the IPv4 or IPv6 key.

        Returns the longest-match prefix that contains the provided key or the
        value of the `default=` parameter if the key is not found in the
        collection.

        **Parameters:**

        - **key** (str, IPv4Address, IPv6Address, IPv4Network, IPv6Network,
          IPv4Interface, IPv6Interface, AWSIPv4Prefix, AWSIPv6Prefix) - the IP
          address or network to retrieve from the collection
        - **default** - the value to return if the key is not found in the
          collection

        **Returns:**

        The `AWSIPv4Prefix` or `AWSIPv6Prefix` that contains the provided key.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def get_prefix_and_supernets(
        self,
        key: Union[
            str,
            IPv4Address,
            IPv6Address,
            IPv4Network,
            IPv6Network,
            IPv4Interface,
            IPv6Interface,
            AWSIPv4Prefix,
            AWSIPv6Prefix,
        ],
        default=None,
    ) -> Optional[Tuple[Union[AWSIPv4Prefix, AWSIPv6Prefix], ...]]:
        """Get the prefix and supernets that contain the IPv4 or IPv6 key.

        Returns a tuple that contains the longest-match prefix and supernets
        that contains the provided key or the value of the `default=` parameter
        if the key is not found in the collection.

        The tuple is sorted by prefix length in ascending order (shorter prefixes
        come before longer prefixes).

        **Parameters:**

        - **key** (str, IPv4Address, IPv6Address, IPv4Network, IPv6Network,
          IPv4Interface, IPv6Interface, AWSIPv4Prefix, AWSIPv6Prefix) - the IP
          address or network to retrieve from the collection
        - **default** - the value to return if the key is not found in the
          collection

        **Returns:**

        A tuple of the `AWSIPv4Prefix`es or `AWSIPv6Prefix`es that contains the
        provided key.
        """
        if isinstance(key, (AWSIPv4Prefix, AWSIPv6Prefix)):
            network = key.prefix
        else:
            network = ip_network(key, strict=False)

        prefixes = list()
        for supernet in supernets(network):
            prefix = self._get_prefix(supernet)
            if prefix:
                prefixes.append(prefix)

        if prefixes:
            prefixes.sort()
            return tuple(prefixes)
        else:
            return default

    def __iter__(self):
        return itertools.chain(self.ipv4_prefixes, self.ipv6_prefixes)

    def __len__(self):
        return len(self.ipv4_prefixes) + len(self.ipv6_prefixes)

    @property
    def regions(self) -> FrozenSet[str]:
        """The set of regions in the collection."""
        if self._regions is None:
            self._regions = frozenset((prefix.region for prefix in self))

        return self._regions

    @property
    def network_border_groups(self) -> FrozenSet[str]:
        """The set of network border groups in the collection."""
        if self._network_border_groups is None:
            self._network_border_groups = frozenset(
                (prefix.network_border_group for prefix in self)
            )

        return self._network_border_groups

    @property
    def services(self) -> FrozenSet[str]:
        """The set of services in the collection.

        The service `"AMAZON"` is not a service but rather an identifier used
        to get all IP address ranges - meaning that every prefix is contained in
        the subset of prefixes tagged with the `"AMAZON"` service. Some IP
        address ranges are only tagged with the `"AMAZON"` service.
        """
        if self._services is None:
            self._services = frozenset(
                (service for prefix in self for service in prefix.services)
            )

        return self._services

    def filter(
        self,
        regions: Union[None, str, Iterable[str]] = None,
        network_border_groups: Union[None, str, Iterable[str]] = None,
        services: Union[None, str, Iterable[str]] = None,
        versions: Union[None, int, Iterable[int]] = None,
    ):
        """Filter the AWS IP address ranges.

        The service `"AMAZON"` is not a service but rather an identifier used
        to get all IP address ranges - meaning that every prefix is contained in
        the subset of prefixes tagged with the `"AMAZON"` service. Some IP
        address ranges are only tagged with the `"AMAZON"` service.

        **Parameters:**

        - **regions** (_optional_ str or iterable sequence of strings) - the
          AWS Regions to include in the subset
        - **network_border_groups** (_optional_ str or iterable sequence of
          strings) - the AWS network border groups to include in the subset
        - **services** (_optional_ str or iterable sequence of strings) - the
          AWS services to include in the subset
        - **versions** (_optional_ int) - the IP address version (4, 6) to
          include in the subset

        **Returns:**

        A new `AWSIPPrefixes` object that contains the subset of IP prefixes that
        match your filter criteria.
        """
        # Normalize, validate, and process the input variables

        # regions
        regions = normalize_to_set(regions) or self.regions
        validate_values("region", regions, valid_values=self.regions)

        # network_border_groups
        network_border_groups = (
            normalize_to_set(network_border_groups) or self.network_border_groups
        )
        validate_values(
            "network_border_group",
            network_border_groups,
            valid_values=self.network_border_groups,
        )

        # services
        services = normalize_to_set(services) or self.services
        validate_values("services", services, valid_values=self.services)

        # prefix_type -> prefix_version
        versions = normalize_to_set(versions) or {4, 6}
        validate_values("versions", versions, valid_values=frozenset((4, 6)))

        # Generate the filtered prefix list
        return self.__class__(
            sync_token=self.sync_token,
            create_date=self.create_date,
            ipv4_prefixes=tuple()
            if 4 not in versions
            else (
                prefix
                for prefix in self.ipv4_prefixes
                if prefix.region in regions
                if prefix.network_border_group in network_border_groups
                if set(prefix.services).intersection(services)
            ),
            ipv6_prefixes=tuple()
            if 6 not in versions
            else (
                prefix
                for prefix in self.ipv6_prefixes
                if prefix.region in regions
                if prefix.network_border_group in network_border_groups
                if set(prefix.services).intersection(services)
            ),
        )
