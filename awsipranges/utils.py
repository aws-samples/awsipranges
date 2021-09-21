"""Utility functions."""

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from ipaddress import (
    IPv4Network,
    IPv6Network,
)
from typing import Any, FrozenSet, Generator, Iterable, Set, Tuple, Type, Union


def check_type(
    variable_name: str,
    obj: Any,
    acceptable_types: Union[Type, Tuple[Type, ...]],
    optional: bool = False,
):
    """Object is an instance of one of the acceptable types or None.
    Args:
        variable_name: The name of the variable being inspected.
        obj: The object to inspect.
        acceptable_types: A type or tuple of acceptable types.
        optional(bool): Whether or not the object may be None.
    Raises:
        TypeError: If the object is not an instance of one of the acceptable
            types, or if the object is None and optional=False.
    """
    assert isinstance(variable_name, str)
    if not isinstance(acceptable_types, tuple):
        acceptable_types = (acceptable_types,)
    assert isinstance(optional, bool)

    if isinstance(obj, acceptable_types):
        # Object is an instance of an acceptable type.
        return
    elif optional and obj is None:
        # Object is None, and that is okay!
        return
    else:
        # Object is something else.
        raise TypeError(
            f"{variable_name} should be a "
            f"{', '.join([t.__name__ for t in acceptable_types])}"
            f"{', or None' if optional else ''}. Received {obj!r} which is a "
            f"{type(obj).__name__}."
        )


def normalize_to_set(
    value: Union[None, str, int, Iterable[Union[str, int]]]
) -> Set[Union[str, int]]:
    """Normalize an optional or iterable variable to a set of unique values."""
    if value is None:
        return set()

    if isinstance(value, (str, int)):
        return {value}

    if isinstance(value, Iterable):
        return set(value)

    raise TypeError("The value must be a string, integer, iterable type, or None.")


def validate_values(
    variable_name: str,
    values: Set[Union[str, int]],
    valid_values: FrozenSet[Union[str, int]],
):
    """Validate the values in a set against a set of valid values."""
    if not values.issubset(valid_values):
        raise ValueError(
            f"One or more of the provided {variable_name} {values!r} do not "
            f"exist in this set of AWS IP address ranges. "
            f"Valid {variable_name}: {valid_values}"
        )


def supernets(
    subnet: Union[IPv4Network, IPv6Network]
) -> Generator[Union[IPv4Network, IPv6Network], None, None]:
    """Incrementally yield the supernets of the provided subnet."""
    for prefix_length in range(subnet.prefixlen, 0, -1):
        yield subnet.supernet(new_prefix=prefix_length)
