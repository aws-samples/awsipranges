# Quickstart

`awsipranges` helps you answer simple questions fast and makes it easy for you to leverage the AWS IP range data in your Python automation scripts and infrastructure configurations.

To get started, make sure you have:

- `awsipranges` [installed](./index.md#installation)
- `awsipranges` [upgraded to the latest version](./index.md#installation)

Then dive-in with this Quickstart to begin working with the AWS IP address ranges as native Python objects!

## Verify server TLS certificates

*How do I know that I am working with the authentic and latest AWS IP address ranges?*

By default, if you do not provide trusted certificates, the Python [urllib](https://docs.python.org/3/library/urllib.html) module (used by the `awsipranges.get_ranges()` function) verifies the TLS certificate presented by the server against the system-provided certificate datastore.

It is your responsibility to verify the TLS certificate presented by the server. `awsipranges` downloads the latest AWS IP address ranges from the [published JSON file](https://docs.aws.amazon.com/general/latest/gr/aws-ip-ranges.html) and makes it easy for you to verify the authenticity of the TLS certificate presented by the server.

Amazon publishes their root Certificate Authority (CA) certificates in the [Amazon Trust Services Repository](https://www.amazontrust.com/repository/).

To verify the TLS certificate presented by the Amazon IP ranges server (ip-ranges.amazonaws.com):

1. Download the Amazon Root CA certificates (in PEM format) from the [Amazon Trust Services Repository](https://www.amazontrust.com/repository/).

2. Prepare the certificates for use by either:

    - Stacking (concatenating) the files into a single certificate bundle (single file)

    - Storing them in a directory using OpenSSL hash filenames

      You can do this with the [`c_rehash` script](https://www.openssl.org/docs/man1.1.0/man1/rehash.html) included in many OpenSSL distributions:

      ```shell
      ❯ c_rehash amazon_root_certificates/
      ```

    > ***Tip***: See [`tests/unit/test_data_loading.py`](https://github.com/aws-samples/awsipranges/blob/main/tests/unit/test_data_loading.py) in the `awsipranges` repository for sample Python functions that download the Amazon Root CA certificates and prepare the certificates as both a stacked certificate bundle file and as a directory with OpenSSL hash filenames.

3. Pass the path to the prepared certificates to the `awsipranges.get_ranges()` function using the `cafile` or `capath` parameters:

    - `cafile=` path to the stacked certificate bundle file

    - `capath=` path to the directory containing the certificates with OpenSSL hashed filenames

    ```python
    >>> import awsipranges
    
    # Using a stacked certificate bundle
    >>> aws_ip_ranges = awsipranges.get_ranges(cafile="amazon_root_certificates.pem")
    
    # Using directory containing the certificates with OpenSSL hashed filenames
    >>> aws_ip_ranges = awsipranges.get_ranges(capath="amazon_root_certificates/")
    ```

## Download AWS IP address ranges

One line of code (okay, two if you count the import statement) is all it takes to download and parse the AWS IP address ranges into a pythonic data structure:

```python
>>> import awsipranges
>>> aws_ip_ranges = awsipranges.get_ranges()
```

The [`awsipranges.get_ranges()`](./api.md#get_ranges) function returns an [`AWSIPPrefixes`](./api.md#awsipprefixes) object, which is a structured collection of AWS IP prefixes.

You can access the `create_date` and `sync_token` attributes of the `AWSIPPrefixes` collection to check the version of the downloaded JSON file and verify the integrity of the file with the `md5` attribute:

```python
>>> aws_ip_ranges.create_date
datetime.datetime(2021, 10, 1, 16, 33, 13, tzinfo=datetime.timezone.utc)

>>> aws_ip_ranges.sync_token
'1633105993'

>>> aws_ip_ranges.md5
'59e4cd7f4757a9f380c626d772a5eef2'
```

You can access the IPv4 and IPv6 address prefixes with the `ipv4_prefixes` and `ipv6_prefixes` attributes:

```python
>>> aws_ip_ranges.ipv4_prefixes
(AWSIPv4Prefix('3.0.0.0/15', region='ap-southeast-1', network_border_group='ap-southeast-1', services=('AMAZON', 'EC2')),
 AWSIPv4Prefix('3.0.5.32/29', region='ap-southeast-1', network_border_group='ap-southeast-1', services=('EC2_INSTANCE_CONNECT',)),
 AWSIPv4Prefix('3.0.5.224/27', region='ap-southeast-1', network_border_group='ap-southeast-1', services=('ROUTE53_RESOLVER',)),
 AWSIPv4Prefix('3.2.0.0/24', region='us-east-1', network_border_group='us-east-1-iah-1', services=('AMAZON', 'EC2')),
 AWSIPv4Prefix('3.2.2.0/24', region='us-east-1', network_border_group='us-east-1-mia-1', services=('AMAZON', 'EC2')),
 ...)

>>> aws_ip_ranges.ipv6_prefixes
(AWSIPv6Prefix('2400:6500:0:9::1/128', region='ap-southeast-3', network_border_group='ap-southeast-3', services=('AMAZON',)),
 AWSIPv6Prefix('2400:6500:0:9::2/128', region='ap-southeast-3', network_border_group='ap-southeast-3', services=('AMAZON',)),
 AWSIPv6Prefix('2400:6500:0:9::3/128', region='ap-southeast-3', network_border_group='ap-southeast-3', services=('AMAZON',)),
 AWSIPv6Prefix('2400:6500:0:9::4/128', region='ap-southeast-3', network_border_group='ap-southeast-3', services=('AMAZON',)),
 AWSIPv6Prefix('2400:6500:0:7000::/56', region='ap-southeast-1', network_border_group='ap-southeast-1', services=('AMAZON',)),
 ...)
```

...and if that's all this library did, it would be pretty boring.

## Check an IP address or network

*How can I check to see if an IP address or network is contained in the AWS IP address ranges?*

[`AWSIPPrefixes`](./api.md#awsipprefixes) works like a standard python collection. You can check to see if an IP address, interface, or network is contained in the collection by using the Python `in` operator:

```python
>>> '52.94.5.15' in aws_ip_ranges
True

>>> '43.195.173.0/24' in aws_ip_ranges
True

>>> IPv4Network('13.50.0.0/16') in aws_ip_ranges
True

>>> '1.1.1.1' in aws_ip_ranges
False
```

## Find an AWS IP prefix

*How can I find the AWS IP prefix that contains an IP address or network?*

You can get the longest-match prefix that contains an IP address or network by indexing into the `AWSIPPrefixes` collection or using the `get()` method just like you do with a Python dictionary:

```python
>>> aws_ip_ranges['52.94.5.15']
AWSIPv4Prefix('52.94.5.0/24', region='eu-west-1', network_border_group='eu-west-1', services=('AMAZON', 'DYNAMODB'))

>>> aws_ip_ranges.get('52.94.5.15')
AWSIPv4Prefix('52.94.5.0/24', region='eu-west-1', network_border_group='eu-west-1', services=('AMAZON', 'DYNAMODB'))

>>> aws_ip_ranges.get('1.1.1.1', default='Nope')
'Nope'
```

The AWS IP address ranges contain supernet and subnet prefixes, so an IP address or network may be contained in more than one AWS IP prefix. Use the `get_prefix_and_supernets()` method to retrieve all IP prefixes that contain an IP address or network:

```python
>>> aws_ip_ranges.get_prefix_and_supernets('3.218.180.73')
(AWSIPv4Prefix('3.208.0.0/12', region='us-east-1', network_border_group='us-east-1', services=('AMAZON', 'EC2')),
 AWSIPv4Prefix('3.218.180.0/22', region='us-east-1', network_border_group='us-east-1', services=('DYNAMODB',)),
 AWSIPv4Prefix('3.218.180.0/25', region='us-east-1', network_border_group='us-east-1', services=('DYNAMODB',)))
```

## Filter AWS IP prefixes

*How can I filter the AWS IP prefixes by Region, network border group, or service?*

The `filter()` method allows you to select a subset of AWS IP prefixes from the collection. You can filter on `regions`, `network_border_groups`, IP `versions` (4, 6), and `services`. The `filter()` method returns a new `AWSIPPrefixes` object that contains the subset of IP prefixes that match your filter criteria.

You may pass a single value (`regions='eu-central-2'`) or a sequence of values (`regions=['eu-central-1', 'eu-central-2']`) to the filter parameters. The `filter()` method returns the prefixes that match all the provided parameters; selecting prefixes where the prefix's attributes intersect the provided set of values.

For example, `filter(regions=['eu-central-1', 'eu-central-2'], services='EC2', versions=4)` will select all IP version `4` prefixes that have `EC2` in the prefix's list of services and are in the `eu-central-1` or `eu-central-2` Regions.

```python
>>> aws_ip_ranges.filter(regions='eu-central-2', services='EC2', versions=4)
{'create_date': datetime.datetime(2021, 9, 16, 17, 43, 14, tzinfo=datetime.timezone.utc),
 'ipv4_prefixes': (AWSIPv4Prefix('3.5.52.0/22', region='eu-central-2', network_border_group='eu-central-2', services=('AMAZON', 'EC2', 'S3')),
                   AWSIPv4Prefix('16.62.0.0/15', region='eu-central-2', network_border_group='eu-central-2', services=('AMAZON', 'EC2')),
                   AWSIPv4Prefix('52.94.250.0/28', region='eu-central-2', network_border_group='eu-central-2', services=('AMAZON', 'EC2')),
                   AWSIPv4Prefix('99.151.80.0/21', region='eu-central-2', network_border_group='eu-central-2', services=('AMAZON', 'EC2'))),
 'ipv6_prefixes': (),
 'sync_token': '1631814194'}
```

> ***Tip***: You can view the set of all regions, network border groups, and services contained in an `AWSIPPrefixes` collection with the `regions`, `network_border_groups`, and `services` attributes.

```python
>>> aws_ip_ranges.services
frozenset({'AMAZON',
           'AMAZON_APPFLOW',
           'AMAZON_CONNECT',
           'API_GATEWAY',
           'CHIME_MEETINGS',
           'CHIME_VOICECONNECTOR',
           'CLOUD9',
           'CLOUDFRONT',
           'CODEBUILD',
           'DYNAMODB',
           'EBS',
           'EC2',
           'EC2_INSTANCE_CONNECT',
           'GLOBALACCELERATOR',
           'KINESIS_VIDEO_STREAMS',
           'ROUTE53',
           'ROUTE53_HEALTHCHECKS',
           'ROUTE53_HEALTHCHECKS_PUBLISHING',
           'ROUTE53_RESOLVER',
           'S3',
           'WORKSPACES_GATEWAYS'})
```

## Work with AWS IP prefix objects

*My router/firewall wants IP networks in a net-mask or host-mask format. Do the AWS IP prefix objects provide a way for me to get the prefix in the format I need?*

[`AWSIPv4Prefix`](./api.md#awsipv4prefix) and [`AWSIPv6Prefix`](./api.md#awsipv6prefix) objects are proxies around [`IPv4Network`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Network) and [`IPv6Network`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv6Network) objects from the Python standard library (see the [`ipaddress`](https://docs.python.org/3/library/ipaddress.html) module). They support all the attributes and methods available on the `IPv4Network` and `IPv6Network` objects. They also inherit additional attributes (like `region`, `network_border_group`, and `services`) and additional functionality from the [`AWSIPPrefix`](./api.md#awsipprefix) base class.

Combining the functionality provided by the standard library objects with the rich collection capabilities provided by the `awsipranges` library allows you to complete complex tasks easily:

Like adding routes to the `DYNAMODB` prefixes in the `eu-west-1` Region to a router:

```python
>>> for prefix in aws_ip_ranges.filter(regions='eu-west-1', services='DYNAMODB'):
...     print(f"ip route {prefix.network_address} {prefix.netmask} 1.1.1.1")
...
ip route 52.94.5.0 255.255.255.0 1.1.1.1
ip route 52.94.24.0 255.255.254.0 1.1.1.1
ip route 52.94.26.0 255.255.254.0 1.1.1.1
ip route 52.119.240.0 255.255.248.0 1.1.1.1
```

Or, configuring an access control list to allow traffic to the `S3` prefixes in `eu-north-1`:

```python
>>> for prefix in aws_ip_ranges.filter(regions='eu-north-1', services='S3', versions=4):
...     print(f"permit tcp any {prefix.network_address} {prefix.hostmask} eq 443")
...
permit tcp any 3.5.216.0 0.0.3.255 eq 443
permit tcp any 13.51.71.176 0.0.0.15 eq 443
permit tcp any 13.51.71.192 0.0.0.15 eq 443
permit tcp any 52.95.169.0 0.0.0.255 eq 443
permit tcp any 52.95.170.0 0.0.1.255 eq 443
```

These are only a couple possibilities. Python and `awsipranges` allow you to use the AWS IP ranges in your automation scripts to accomplish powerful tasks simply.

## What about IPv6?

All the functionality and examples shown in this Quickstart also work with IPv6 prefixes! 😎
