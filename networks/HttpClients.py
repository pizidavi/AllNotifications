import os
import time
import json
import socket
import requests.packages.urllib3.util.connection as urllib3_cn
from abc import ABC, abstractmethod

import requests
import httpx
import undetected_chromedriver as uc
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

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


class SeleniumClient(HttpClient):

    def __init__(self):
        self.__chrome_version = os.getenv('CHROME_VERSION', None) or None
        self.__max_retries = utils.try_parse(int, os.getenv('CLOUDFLARE_MAX_RETRIES'), 3)
        self.__session = None
        self._start_session()

    def _start_session(self):
        if self.__session is not None:
            try:
                self.__session.delete_all_cookies()
                self.__session.quit()
            except Exception:
                pass

        options = uc.ChromeOptions()
        options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
        desired_capabilities = DesiredCapabilities.CHROME.copy()
        desired_capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
        self.__session = uc.Chrome(options=options, desired_capabilities=desired_capabilities,
                                   version_main=self.__chrome_version, headless=True)

    def send(self, request) -> str:
        url = str(request.url)
        self._navigate_to(url)

        page_source = self.__session.page_source
        return page_source

    def _navigate_to(self, url):
        self.__session.get(url)

        response: dict or None = None
        for entry in self.__session.get_log('performance'):
            entry = json.loads(entry['message'])['message']
            if entry['method'] == 'Network.responseReceived':
                if entry['params']['response']['url'] == self.__session.current_url:
                    response = entry['params']['response']
        if response is None:
            raise RequestException()
        elif response.get('status', 200) == 503:
            page_source = self.__session.page_source
            retries = 0
            while page_source.find('<title>Just a moment...</title>') >= 0:
                logger.debug('CloudFlare detected' if retries == 0 else 'Failed bypass CloudFlare, retrying...')
                time.sleep(5)

                page_source = self.__session.page_source
                retries += 1

                if retries > self.__max_retries:
                    self._start_session()
                    raise CloudFlareException()
            logger.debug('CloudFlare bypassed')

        elif not (200 <= response.get('status', -1) <= 299):
            raise HTTPStatusError(response['status'], url)

    def __del__(self):
        if self.__session is not None:
            try:
                self.__session.quit()
            except Exception:
                pass
