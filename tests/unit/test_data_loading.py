"""Unit tests for the data_loading module."""

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Iterable
from urllib.parse import urljoin
from urllib.request import urlopen

import pytest
from OpenSSL import crypto

from awsipranges.data_loading import get_json_data


AMAZON_TRUST_SERVICES_REPOSITORY_URL = "https://www.amazontrust.com/repository/"

AMAZON_ROOT_CA_FILENAMES = [
    "AmazonRootCA1.pem",
    "AmazonRootCA2.pem",
    "AmazonRootCA3.pem",
    "AmazonRootCA4.pem",
]


pytestmark = pytest.mark.extra_data_loading


# Helper functions
def calculate_subject_name_hash(pem: str) -> str:
    """Calculate the OpenSSL subject_name_hash for a certificate in PEM format."""
    assert isinstance(pem, str)
    certificate = crypto.load_certificate(crypto.FILETYPE_PEM, pem.encode())
    return format(certificate.subject_name_hash(), "02x")


def save_to_stacked_certificate_file(
    certificates: Iterable[str], file_path: Path
) -> Path:
    """Save certificates (in PEM format) to a directory of hashed certificates."""
    assert isinstance(certificates, Iterable)
    assert isinstance(file_path, Path)

    stacked_certificates = "\n".join(
        (certificate.strip() for certificate in certificates)
    )

    with open(file_path, "w") as file:
        file.write(stacked_certificates)

    return file_path


def save_to_directory_of_hashed_certificates(pem: str, directory: Path) -> Path:
    """Save a certificate (in PEM format) to a directory of hashed certificates."""
    assert isinstance(pem, str)
    assert isinstance(directory, Path)
    assert directory.is_dir()

    subject_name_hash = calculate_subject_name_hash(pem)
    certificate_number = 0

    while True:
        file_path = directory / f"{subject_name_hash}.{certificate_number}"
        if file_path.exists():
            certificate_number += 1
            continue
        else:
            with open(file_path, "w") as file:
                file.write(pem)
            break

    return file_path


# Fixtures
@pytest.fixture(scope="module")
def certificates_directory() -> Path:
    with TemporaryDirectory(suffix="certificates") as certificates_directory:
        yield Path(certificates_directory)


@pytest.fixture(scope="module")
def amazon_root_certificates() -> Dict[str, str]:
    """Download the Amazon root certificates from Amazon Trust Services."""
    amazon_root_certificates = {}
    for ca_filename in AMAZON_ROOT_CA_FILENAMES:
        with urlopen(
            urljoin(AMAZON_TRUST_SERVICES_REPOSITORY_URL, ca_filename)
        ) as response:
            assert response.status == 200
            certificate_contents = response.read().decode()
            amazon_root_certificates[ca_filename] = certificate_contents

    return amazon_root_certificates


@pytest.fixture(scope="module")
def cafile(
    amazon_root_certificates: Dict[str, str], certificates_directory: Path
) -> Path:
    cafile = certificates_directory / "stacked_certificates.pem"
    save_to_stacked_certificate_file(amazon_root_certificates.values(), cafile)

    return cafile


@pytest.fixture(scope="module")
def capath(
    amazon_root_certificates: Dict[str, str], certificates_directory: Path
) -> Path:
    capath = certificates_directory
    assert capath.is_dir()
    for certificate in amazon_root_certificates.values():
        save_to_directory_of_hashed_certificates(certificate, capath)

    return capath


# Happy path tests
def test_get_json_data():
    json_data = get_json_data()
    assert isinstance(json_data, dict)


def test_get_json_data_with_cafile(cafile: Path):
    json_data = get_json_data(cafile=cafile)
    assert isinstance(json_data, dict)


def test_get_json_data_with_capath(capath: Path):
    json_data = get_json_data(capath=capath)
    assert isinstance(json_data, dict)
