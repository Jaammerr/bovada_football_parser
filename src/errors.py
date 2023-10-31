from tls_client import response as tls_response


class TLSSessionError(Exception):
    """Exception that is raised when a TLS session error occurs."""

    pass


def raise_for_status(response: tls_response) -> None:
    """Raises stored :class:`TLSSessionError`, if one occurred."""

    # Custom error handling for TLSClient because we doesn't have raise_for_status method
    http_error_msg = ""
    if 400 <= response.status_code < 500:
        http_error_msg = f"{response.status_code} Client Error for url {response.url}"

    elif 500 <= response.status_code < 600:
        http_error_msg = f"{response.status_code} Server Error for url: {response.url}"

    if http_error_msg:
        raise TLSSessionError(http_error_msg)
