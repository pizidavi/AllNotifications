from httpx import Request

from utils.utils import soupify
from networks.Requests import get
from networks.exceptions import NotFoundException
from models.Element import ComicElement
from providers import ComicProvider


class ReadM(ComicProvider):

    BASE_URL = 'https://readm.org'
    NAME = 'ReadM'
    LANG = 'en'
    ICON = '📓'

    def updates_request(self) -> Request:
        return get(f'{self.BASE_URL}/latest-releases')

    def updates_parser(self, response: str) -> list[ComicElement]:
        document = soupify(response)
        entries = document.find('ul', class_='latest-updates')
        if entries is None:
            raise NotFoundException()
        entries = entries.find_all('li', class_='segment-poster-sm')

        elements = []
        for entry in entries:
            anchor = entry.find('h2').find('a')
            title = anchor.text.strip().replace("’", "'")
            href = self._fix_url(anchor.get('href'))
            chapter = entry.find('ul', class_='chapters').find('li')
            if chapter is None:
                continue
            number = chapter.find('a').text.strip()

            elements.append(
                ComicElement(title, href, number)
            )
        return elements
