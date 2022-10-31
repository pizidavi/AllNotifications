from httpx import Request
from functools import wraps

from utils.headers import get_random_header

__all__ = ['get', 'post']

DEFAULT_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    **get_random_header()
}
DEFAULT_COOKIES = {}


def setup(func):
    """
    Decorator which takes a function and converts it into a request method
    """
    @wraps(func)
    def wrapper(url: str,
                headers: dict = None,
                cookies: dict = None,
                **kwargs) -> Request:
        if headers is None:
            headers = {}
        if cookies is None:
            cookies = {}

        method = func.__name__.upper()
        headers = {**DEFAULT_HEADERS, **headers}
        cookies = {**DEFAULT_COOKIES, **cookies}

        return Request(method, url, headers=headers, cookies=cookies, **kwargs)
    return wrapper


@setup
def get(url: str, headers: dict = None, cookies: dict = None, **kwargs) -> Request:
    """
    Build a GET request
    :param url: URL
    :param headers: headers
    :param cookies: cookies
    :param kwargs: other params
    :return: Request builder
    """
    pass


@setup
def post(url: str, headers: dict = None, cookies: dict = None, **kwargs) -> Request:
    """
    Build a POST request
    :param url: URL
    :param headers: headers
    :param cookies: cookies
    :param kwargs: other params
    :return: Request builder
    """
    pass
