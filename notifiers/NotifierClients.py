import os
import time
import urllib.parse
import httpx
from abc import ABC, abstractmethod

from utils.logger import get_logger

logger = get_logger(__name__)


class Notifier(ABC):

    @abstractmethod
    def send(self, *args, **kwargs) -> bool:
        """
        Send a notification
        :param kwargs: Params
        """
        pass


class Telegram(Notifier):

    WEBSITE: str = 'https://api.telegram.org/bot{token}/{method}?{params}'
    DEFAULT_PARAMS: dict = {'parse_mode': 'Markdown'}

    def __init__(self, token: str = None):
        self.__token = token if token is not None else os.getenv('TELEGRAM_TOKEN')

    def send(self, chat_id: str, message: str) -> bool:
        if type(chat_id) == str and chat_id == 'owner':
            chat_id = os.getenv('ADMIN_CHAT_ID')

        max_retries = 3
        retries = 0
        while retries < max_retries:
            try:
                url = self.__prepare_url('sendMessage', {'chat_id': chat_id, 'text': message})
                response = httpx.get(url)
                return response.json().get('ok', False)
            except Exception as e:
                retries += 1
                logger.debug('NotifierException: %s | Retrying', str(e))
                time.sleep(2)
        return False

    def __prepare_url(self, method: str, params: dict = None) -> str:
        if params is None:
            params = {}
        params = {**self.DEFAULT_PARAMS, **params}
        parsed_params = urllib.parse.urlencode(params)
        return self.WEBSITE.format(token=self.__token, method=method, params=parsed_params)
