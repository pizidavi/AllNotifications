import os
import time
import json
import socket
import requests.packages.urllib3.util.connection as urllib3_cn
from abc import ABC, abstractmethod

import requests
import httpx

from utils import utils
from utils.logger import get_logger
from networks.exceptions import *


def allowed_gai_family():
    """ Use only IPv4 for requests """
    return socket.AF_INET


urllib3_cn.allowed_gai_family = allowed_gai_family
logger = get_logger(__name__)


class HttpClient(ABC):

    @abstractmethod
    def send(self, request: requests.Request) -> str:
        """
        Send a request
        :param request: Request builder
        :return: Request content
        """
        pass


class RequestsClient(HttpClient):

    def __init__(self):
        self.__session = requests.Session()

    def send(self, request) -> str:
        prepped = self.__session.prepare_request(request)
        r = self.__session.send(prepped)
        if not (200 <= r.status_code <= 299):
            raise HTTPStatusError(r.status_code, request.url)
        return r.text

    def __del__(self):
        self.__session.close()


class HttpxClient(HttpClient):

    def __init__(self):
        self.__client = httpx.Client(follow_redirects=True)

    def send(self, request) -> str:
        prepped = httpx.Request(request.method, request.url, headers=request.headers)
        r = self.__client.send(prepped)
        r.raise_for_status()
        return r.text

    def __del__(self):
        self.__client.close()
