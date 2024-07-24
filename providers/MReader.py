from httpx import Request

from utils.utils import soupify
from networks.Requests import get
from networks.exceptions import NotFoundException
from models.Element import ComicElement
from providers import ComicProvider


class MReader(ComicProvider):

    BASE_URL = 'https://www.mgeko.cc'
    NAME = 'MGeko'
    LANG = 'en'
    ICON = '📗'

    def updates_request(self) -> Request:
        return get(f'{self.BASE_URL}/jumbo/manga/')

    def updates_parser(self, response) -> list[ComicElement]:
        document = soupify(response)

        entries = document.find(class_='chapters')
        if entries is None:
            raise NotFoundException()
        entries = entries.find_all(class_='novel-item')

        elements = []
        for entry in entries:
            anchor = entry.find('a', class_='list-body')
            title = anchor.get('title').strip().replace('’', '\'')
            href = self.BASE_URL + anchor.get('href')
            number = anchor.find(class_='chapter-title').text.strip()\
                .removeprefix('Chapter ').removesuffix('-eng-li').replace('-', '.')
            elements.append(
                ComicElement(title, href, number)
            )
        return elements
