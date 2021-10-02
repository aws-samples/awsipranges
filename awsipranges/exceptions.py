"""Custom exceptions."""

from typing import Optional, Tuple


class AWSIPRangesException(Exception):
    """Base class for all awsipranges exceptions."""


class HTTPError(AWSIPRangesException):
    """An HTTP/HTTPS error."""

    args: Tuple[object, ...]
    status: Optional[int]
    reason: Optional[str]

    def __init__(self, *args, status: Optional[int], reason: Optional[str]):
        super(HTTPError, self).__init__(*args)
        self.args = args
        self.status = status
        self.reason = reason

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"{', '.join([repr(arg) for arg in self.args])}, "
            f"status={self.status!r}, "
            f"reason={self.reason!r}"
            f")"
        )

    def __str__(self):
        msg = []
        if self.status:
            msg.append(str(self.status))

        if self.reason:
            msg.append(self.reason)

        if self.args:
            if msg:
                msg.append("-")
            msg += [str(arg) for arg in self.args]

        return " ".join(msg)


def raise_for_status(response):
    """Raise an HTTPError on 4xx and 5xx status codes."""
    # Get the status code
    if hasattr(response, "status"):
        status = int(response.status)
    elif hasattr(response, "code"):
        status = int(response.code)
    elif hasattr(response, "getstatus"):
        status = int(response.getstatus())
    else:
        raise ValueError(
            f"Response object {response!r} does not contain a status code."
        )

    # Get the URL
    if hasattr(response, "url"):
        url = response.url
    elif hasattr(response, "geturl"):
        url = response.geturl()
    else:
        raise ValueError(f"Response object {response!r} does not contain a url.")

    # Get the reason, if available
    reason = response.reason if hasattr(response, "reason") else None

    if 400 <= status < 500:
        raise HTTPError(f"Client error for URL: {url}", status=status, reason=reason)

    if 500 <= status < 600:
        raise HTTPError(f"Server error for URL: {url}", status=status, reason=reason)
