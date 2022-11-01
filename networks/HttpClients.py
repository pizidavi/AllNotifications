import os
import time
from abc import ABC, abstractmethod

from httpx import Client, Request
import undetected_chromedriver as uc

from utils import utils
from networks.exceptions import *


class HttpClient(ABC):

    @abstractmethod
    def send(self, request: Request) -> str:
        """
        Send a request
        :param request: Request builder
        :return: Request content
        """
        pass


class HttpxClient(HttpClient):

    def __init__(self):
        self.__session = Client()

    def send(self, request: Request) -> str:
        r = self.__session.send(request)
        r.raise_for_status()
        return r.text

    def __del__(self):
        self.__session.close()


class SeleniumClient(HttpClient):

    def __init__(self):
        self.__chrome_version = os.getenv('CHROME_VERSION', None) or None
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
        self.__session = uc.Chrome(options=options, version_main=self.__chrome_version, headless=True)

    def send(self, request: Request) -> str:
        url = str(request.url)
        self.__session.get(url)

        page_source = self.__session.page_source

        max_retry = utils.try_parse(int, os.getenv('CLOUDFLARE_MAX_RETRIES'), 3)
        retry = 0
        while page_source.find('<title>Just a moment...</title>') >= 0:
            time.sleep(5)
            retry += 1
            page_source = self.__session.page_source

            if retry > max_retry:
                self._start_session()
                raise CloudFlareException()

        return page_source

    def __del__(self):
        if self.__session is not None:
            try:
                self.__session.quit()
            except Exception:
                pass
