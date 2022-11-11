from datetime import datetime
from abc import ABC, abstractmethod
from httpx import Request

from utils.logger import get_logger
from utils import utils
from networks.HttpClients import HttpClient, HttpxClient
from networks.Requests import get
from storages.BaseStorage import Storage
from storages.ComicsDBStorage import ComicsDBStorage
from notifiers.NotifierClients import Notifier, Telegram
from models.ProviderLogging import ProviderLogging
from models.Element import Element, ComicElement

logger = get_logger(__name__)


class BaseProvider(ABC):
    BASE_URL: str
    NAME: str
    TYPE: str

    STORAGE: Storage
    HTTP_CLIENT: HttpClient = HttpxClient()

    NOTIFIER: Notifier
    NOTIFIER_MESSAGE: str

    def __init__(self, register_commands: callable = None, disabled: bool = False):
        self.NOTIFIER = Telegram()

        self.logging: ProviderLogging = ProviderLogging(self.NAME, self.NOTIFIER)
        self.disabled = disabled
        self._register_commands = register_commands or (lambda t, c: None)

    def updates_request(self) -> Request:
        """
        HTTP Request to execute
        :return: Request function
        """
        return get(f'{self.BASE_URL}/')

    @abstractmethod
    def updates_parser(self, response: str) -> list[Element]:
        """
        Parse response to list[Element]
        :param response: Request's response
        :return: List of Element
        """
        pass

    @abstractmethod
    def manage_elements(self, elements: list[Element], history: list[Element] = None) -> list[Element]:
        """
        Manage parsed elements to do something
        :param elements: List of Element
        :param history: List of Element of other providers of the same Type
        :return: List of the managed elements
        """
        pass

    def _fix_url(self, url: str) -> str:
        """
        Fix url that does not start with "http" or "BASE_URL"
        :param url: url
        :return: Fixed url
        """
        if url.startswith('http'):
            return url
        if url.startswith('//'):
            return f'https:{url}'
        if url.startswith('/'):
            return f'{self.BASE_URL}{url}'
        return f'{self.BASE_URL}/{url}'


class ComicProvider(BaseProvider):
    TYPE: str = 'comics'
    LANG: str
    ICON: str = '❓'

    NOTIFIER_MESSAGE: str = '*Nuovo capitolo!* {icon}\n[{title} - {number}]({url})'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.STORAGE: ComicsDBStorage = ComicsDBStorage(self.TYPE)

        commands = [
            ('list', self._get_elements),
            ('add', self._add_element),
            ('del', self._remove_element)
        ]
        self._register_commands(self.TYPE, commands)

    def _get_elements(self, user_id: int, arguments: list[str]) -> str:
        """ List comics """
        elements = self.STORAGE.get_elements(user_id=user_id)
        elements.sort(key=lambda x: x.get('title'))

        message = '<b>Lista</b>\n\n'
        for element in elements:
            flag = utils.iso639_to_flag(element.get('lang'))
            style = ('<s>', '</s>') if element.get('disabled') == 1 else ('', '')
            suffix = ''
            if element.get('last_update') is None or \
                    (datetime.now() - element.get('last_update')).days > 60:
                suffix = '❗'
            message += f"{flag} {style[0]}{element.get('title')}{style[1]} {suffix}\n"
        message += f'\nTotale: {len(elements)}'
        return message

    def _add_element(self, user_id: int, arguments: list[str]) -> str or bool or None:
        """ Add comic [/add_comics <titolo> \n <lingua> \n <provider>] """
        if len(arguments) == 0:
            return f'Less arguments than expected: 1 required but 0 given'
        element = {
            'user_id': 1,
            'title': arguments[0].replace('’', '\'').strip(),
            'lang': arguments[1].lower().strip() if len(arguments) >= 2 else 'en',
            'provider': arguments[2].upper().strip() if len(arguments) >= 3 else None
        }
        logger.debug('Try adding element: %s', element)
        try:
            self.STORAGE.set_element(element)
            logger.info('Added element: %s', element)
            return f"<pre>{element['title']} ({element['lang']})</pre> has been successfully added"
        except Exception as e:
            logger.error(e)
            return f'<b>Error:</b> <pre>{e}</pre>'

    def _remove_element(self, user_id: int, arguments: list[str]) -> str or bool or None:
        """ Remove comic [/del_comics <id>] """
        if len(arguments) == 0:
            return f'Less arguments than expected: 1 required but 0 given'

        element_id = utils.try_parse(int, arguments[0])
        if element_id is None:
            return f'{arguments[0]} is not a number'

        logger.debug('Try removing element: %s', element_id)
        try:
            self.STORAGE.delete_element_by_id(user_id, element_id)
            logger.info('Removed element: %s', element_id)
            return 'Successfully removed'
        except Exception as e:
            logger.error(e)
            return f'<b>Error:</b> <pre>{e}</pre>'

    @abstractmethod
    def updates_parser(self, response: str) -> list[ComicElement]:
        pass

    def manage_elements(self, elements: list[ComicElement], history: list[ComicElement] = None) -> list[ComicElement]:
        if history is None:
            history = []
        managed_elements = []

        for element in elements:
            # Find if is a tracked element and number is different
            items = self.STORAGE.get_elements(title=element.title, lang=self.LANG, disabled=0)
            if len(items) == 0:
                continue
            managed_elements.append(element)

            if items[0].get('number', None) is not None and items[0].get('number', None) == element.number:
                continue
            if utils.find(lambda x: x == element, history):
                logger.debug('Already managed: %s. Skipped', str(element))
                continue

            _number = utils.try_parse_regex(float, element.number or '')
            _number_old = utils.try_parse_regex(float, items[0].get('number', None) or '')
            if type(_number) == type(_number_old) == float:
                if _number <= _number_old:
                    logger.debug('Previous number (%s) is higher than: "%s". Skipped', _number_old, str(element))
                    continue

            logger.info('New: "%s" (found %s time)', str(element), len(items))

            # Update new element's number
            for e in items:
                self.STORAGE.set_element_number(e.get('element_id'), element.number)

                _lang = utils.iso639_to_flag(self.LANG)
                chat_id = e.get('telegram_id', None)
                message = self.NOTIFIER_MESSAGE.format(icon=self.ICON,
                                                       title=element.title + (f' {_lang}' if _lang != '' else ''),
                                                       number=element.number,
                                                       url=element.url)
                if chat_id is not None:
                    result = self.NOTIFIER.send(chat_id, message)
                    if not result:
                        logger.error('Failed to send notification to %s for %s', chat_id, str(element))

        return managed_elements
