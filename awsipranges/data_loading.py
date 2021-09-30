"""Load AWS IP address ranges."""

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import hashlib
import json
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from awsipranges.config import (
    AWS_IP_ADDRESS_RANGES_URL,
    CREATE_DATE_FORMAT,
    CREATE_DATE_TIMEZONE,
)
from awsipranges.exceptions import raise_for_status
from awsipranges.models.awsipprefix import aws_ip_prefix
from awsipranges.models.awsipprefixes import AWSIPPrefixes
from awsipranges.utils import check_type


def get_json_data(
    cafile: Union[str, Path, None] = None, capath: Union[str, Path, None] = None
) -> Tuple[Dict[str, Any], Optional[str]]:
    """Retrieve and parse the AWS IP address ranges JSON file."""
    check_type("cafile", cafile, (str, Path), optional=True)
    cafile = Path(cafile) if isinstance(cafile, str) else cafile
    if cafile and not cafile.is_file():
        raise ValueError(
            "Invalid path; cafile must be a path to a bundled CA certificate file."
        )

    check_type("capath", capath, (str, Path), optional=True)
    capath = Path(capath) if isinstance(capath, str) else capath
    if capath and not capath.is_dir():
        raise ValueError("Invalid path; capath must be a path to a directory.")

    with urllib.request.urlopen(
        AWS_IP_ADDRESS_RANGES_URL, cafile=cafile, capath=capath
    ) as response:
        raise_for_status(response)

        response_bytes = response.read()
        response_data = json.loads(response_bytes)

        if "md5" in hashlib.algorithms_available:
            md5_hash = hashlib.md5()
            md5_hash.update(response_bytes)
            md5_hex_digest = md5_hash.hexdigest()
        else:
            md5_hex_digest = None

    return response_data, md5_hex_digest


def get_ranges(cafile: Path = None, capath: Path = None) -> AWSIPPrefixes:
    """Get the AWS IP address ranges from the published JSON document.

    It is your responsibility to verify the TLS certificate presented by the
    server. By default, the Python
    [urllib](https://docs.python.org/3/library/urllib.html) module (used by
    this function) verifies the TLS certificate presented by the server against
    the system-provided certificate datastore.

    You can download the Amazon root CA certificates from the
    [Amazon Trust Services](https://www.amazontrust.com/repository/)
    repository.

    The optional `cafile` and `capath` parameters may be used to specify a set
    of trusted CA certificates for the HTTPS request. `cafile` should point to a
    single file containing a bundle of CA certificates, whereas `capath`
    should point to a directory of certificate files with OpenSSL hash filenames.
    To verify the TLS certificate against Amazon root certificates, download the
    CA certificates (in PEM format) from Amazon Trust Services and provide the
    path to the certificate(s) using the `cafile` or `capath` parameters.

    See the OpenSSL [SSL_CTX_load_verify_locations](https://www.openssl.org/docs/man1.1.0/man3/SSL_CTX_set_default_verify_dir.html)
    documentation for details on the expected CAfile and CApath file formats.

    **Parameters:**

    - **cafile** (_optional_ Path) - path to a file of stacked (concatenated) CA
      certificates in PEM format

    - **capath** (_optional_ Path) - path to a directory containing one or more
      certificates in PEM format using the OpenSSL subject-name-hash filenames

    **Returns:**

    The AWS IP address ranges in a `AWSIPPrefixes` collection.
    """
    json_data, json_md5 = get_json_data(cafile=cafile, capath=capath)

    assert "syncToken" in json_data
    assert "createDate" in json_data
    assert "prefixes" in json_data
    assert "ipv6_prefixes" in json_data

    return AWSIPPrefixes(
        sync_token=json_data["syncToken"],
        create_date=datetime.strptime(
            json_data["createDate"], CREATE_DATE_FORMAT
        ).replace(tzinfo=CREATE_DATE_TIMEZONE),
        ipv4_prefixes=(aws_ip_prefix(record) for record in json_data["prefixes"]),
        ipv6_prefixes=(aws_ip_prefix(record) for record in json_data["ipv6_prefixes"]),
        md5=json_md5,
    )
