# Developer Interfaces

All public interfaces and classes are exposed under the main `awsipranges`
package.

## get_ranges()

::: awsipranges.get_ranges
    :docstring:

## AWSIPPrefixes

::: awsipranges.AWSIPPrefixes
    :docstring:
    :members:

## AWSIPPrefix

Base class for the `AWSIPv4Prefix` and `AWSIPv6Prefix` classes. `AWSIPPrefix` objects are _immutable_ and _hashable_ and therefore may be added to Python sets and be used as keys in dictionaries.

::: awsipranges.AWSIPPrefix
    :docstring:
    :members:

### AWSIPv4Prefix

Supports all the properties and methods of the [`AWSIPPrefix`](./api.md#awsipprefix) base class and the Python native [`IPv4Network`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Network) class.

::: awsipranges.AWSIPv4Prefix
    :docstring:
    :members: ip_prefix 

### AWSIPv6Prefix

Supports all the properties and methods of the [`AWSIPPrefix`](./api.md#awsipprefix) base class and the Python native [`IPv6Network`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv6Network) class.

::: awsipranges.AWSIPv6Prefix
    :docstring:
    :members: ipv6_prefix
