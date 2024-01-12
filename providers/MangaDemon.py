from utils.utils import soupify
from networks.Requests import get
from networks.exceptions import NotFoundException
from models.Element import ComicElement
from providers import ComicProvider


class MangaDemon(ComicProvider):

    BASE_URL = 'https://demoncomics.org'
    NAME = 'MangaDemon'
    LANG = 'en'
    ICON = '👿'

    def updates_request(self):
        return get(f'{self.BASE_URL}/updates')

    def updates_parser(self, response: str) -> list[ComicElement]:
        document = soupify(response)

        entries = document.find(id='content')
        if entries is None:
            raise NotFoundException('Content not found')
        entries = entries.find('ul')
        if entries is None:
            raise NotFoundException('List not found')
        entries = entries.find_all('li')

        elements = []
        for entry in entries:
            anchor = entry.find(class_='novel-title').find('a')
            title = anchor.text.strip().replace("’", "'")
            href = self.BASE_URL + anchor.get('href')

            chapter = entry.find(class_='chapternumber').find('a').text
            number = chapter.replace('Chapter', '').strip()

            elements.append(
                ComicElement(title, href, number)
            )
        return elements
