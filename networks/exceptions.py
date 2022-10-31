
class RequestException(Exception):
    def __init__(self, message='Request Exception'):
        super().__init__(message)


class NotFoundException(RequestException):
    def __init__(self, message='Not Found'):
        super().__init__(message)


class CloudFlareException(RequestException):
    def __init__(self, message='Unable to bypass CloudFlare'):
        super().__init__(message)
