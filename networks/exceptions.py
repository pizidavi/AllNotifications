
class RequestException(Exception):
    def __init__(self, message='Request Exception'):
        super().__init__(message)


class HTTPStatusError(RequestException):
    ERROR_TYPES = {
        1: "Informational response",
        3: "Redirect response",
        4: "Client error",
        5: "Server error",
    }

    def __init__(self, status_code: int, url: str = None):
        status_class = status_code // 100
        error_type = HTTPStatusError.ERROR_TYPES.get(status_class, "Invalid status code")

        if url is not None:
            message = "{error_type} '{status_code}'"
        else:
            message = "{error_type} '{status_code}' for url '{url}'"
        message = message.format(error_type=error_type, status_code=status_code, url=url)
        super().__init__(message)


class NotFoundException(RequestException):
    def __init__(self, message='Not Found'):
        super().__init__(message)


class CloudFlareException(RequestException):
    def __init__(self, message='Unable to bypass CloudFlare'):
        super().__init__(message)
