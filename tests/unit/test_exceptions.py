"""Unit tests for the awsipranges custom exceptions."""

from dataclasses import dataclass

import pytest

from awsipranges.config import AWS_IP_ADDRESS_RANGES_URL
from awsipranges.exceptions import AWSIPRangesException, HTTPError, raise_for_status


# Helper classes
@dataclass
class Response:
    url: str = AWS_IP_ADDRESS_RANGES_URL
    status: int = 200
    reason: str = "OK"


@dataclass
class LegacyResponse:
    _url: str = AWS_IP_ADDRESS_RANGES_URL
    _status: int = 200

    def geturl(self) -> str:
        return self._url

    def getstatus(self) -> int:
        return self._status


@dataclass
class LegacyResponseWithCode:
    _url: str = AWS_IP_ADDRESS_RANGES_URL
    code: int = 200

    def geturl(self) -> str:
        return self._url


@dataclass
class BadResponseNoStatus:
    url: str = AWS_IP_ADDRESS_RANGES_URL


@dataclass
class BadResponseNoURL:
    status: int = 200


# Happy path tests
def test_raising_aws_ip_ranges_exception():
    with pytest.raises(AWSIPRangesException):
        raise AWSIPRangesException("Custom error message.")


def test_raising_http_error():
    with pytest.raises(HTTPError):
        raise HTTPError(
            "Request failed because of something you did",
            status=400,
            reason="Bad Request",
        )


def test_convert_aws_ip_ranges_exception_to_str():
    exception = AWSIPRangesException("Custom error message.")
    exception_str = str(exception)
    print(exception_str)


def test_convert_aws_ip_ranges_exception_to_repr():
    exception = AWSIPRangesException("Custom error message.")
    exception_repr = repr(exception)
    print(exception_repr)


def test_convert_http_error_to_str():
    exception = HTTPError(
        "Request failed because of something you did",
        status=400,
        reason="Bad Request",
    )
    exception_str = str(exception)
    print(exception_str)


def test_convert_http_error_to_repr():
    exception = HTTPError(
        "Request failed because of something you did",
        status=400,
        reason="Bad Request",
    )
    exception_repr = repr(exception)
    print(exception_repr)


def test_raise_for_status_ok():
    response = Response()
    raise_for_status(response)


def test_legacy_raise_for_status_ok():
    response = LegacyResponse()
    raise_for_status(response)


def test_legacy_response_with_code_ok():
    response = LegacyResponseWithCode()
    raise_for_status(response)


# Unhappy path tests
def test_raise_for_status_client_error():
    with pytest.raises(HTTPError):
        response = Response(status=400, reason="Bad Request")
        raise_for_status(response)


def test_raise_for_status_server_error():
    with pytest.raises(HTTPError):
        response = Response(status=500, reason="Internal Server Error")
        raise_for_status(response)


def test_legacy_raise_for_status_client_error():
    with pytest.raises(HTTPError):
        response = LegacyResponse(_status=400)
        raise_for_status(response)


def test_legacy_response_with_code_client_error():
    with pytest.raises(HTTPError):
        response = LegacyResponseWithCode(code=400)
        raise_for_status(response)


def test_bad_response_no_status():
    with pytest.raises(ValueError):
        response = BadResponseNoStatus()
        raise_for_status(response)


def test_bad_response_no_url():
    with pytest.raises(ValueError):
        response = BadResponseNoURL()
        raise_for_status(response)
