import re

from utils.utils import soupify
from networks.Requests import get
from networks.exceptions import NotFoundException
from models.Element import ComicElement
from providers import ComicProvider


class MangaWorld(ComicProvider):

    BASE_URL = 'https://www.mangaworld.cx'
    NAME = 'MangaWorld'
    LANG = 'it'
    ICON = '📕'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__cookies = {}

    def updates_request(self):
        return get(f'{self.BASE_URL}/', cookies=self.__cookies)

    def manage_response(self, response: str) -> str:
        regex = r'document.cookie="MWCookie=(\w+)\s?;'
        match = re.findall(regex, response)
        if len(match):
            self.__cookies['MWCookie'] = match[0]
            request = get(f'{self.BASE_URL}/?d=1', cookies=self.__cookies)
            response = self.HTTP_CLIENT.send(request)
        return response

    def updates_parser(self, response: str) -> list[ComicElement]:
        document = soupify(response)
        entries = document.find(class_='comics-grid')
        if entries is None:
            raise NotFoundException()
        entries = entries.find_all(class_='entry')

        elements = []
        for entry in entries:
            anchor = entry.find('a', class_='manga-title')
            title = anchor.text.strip()
            href = anchor.get('href')
            number = entry.find(class_='xanh').get('title', '').removeprefix('Capitolo ')
            elements.append(
                ComicElement(title, href, number)
            )
        return elements
