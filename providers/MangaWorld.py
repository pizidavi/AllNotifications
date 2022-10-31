from utils.utils import soupify
from networks.exceptions import NotFoundException
from models.Element import ComicElement
from providers import ComicProvider


class MangaWorld(ComicProvider):

    BASE_URL = 'https://www.mangaworld.so'
    NAME = 'MangaWorld'
    LANG = 'it'
    ICON = '📕'

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
