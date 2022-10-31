from utils.utils import soupify
from networks.exceptions import NotFoundException
from models.Element import ComicElement
from providers import ComicProvider


class MangaNato(ComicProvider):

    BASE_URL = 'https://manganato.com'
    NAME = 'MangaNato'
    LANG = 'en'
    ICON = '📘'

    def updates_parser(self, response: str) -> list[ComicElement]:
        document = soupify(response)
        entries = document.find(class_='panel-content-homepage')
        if entries is None:
            raise NotFoundException()
        entries = entries.find_all(class_='content-homepage-item')

        elements = []
        for entry in entries:
            anchor = entry.find(class_='item-title').find('a')
            title = anchor.text.strip().replace("’", "'")
            href = anchor.get('href')
            number = entry.find(class_='item-chapter')
            if number is None:
                continue
            number = number.find('a').text.removeprefix('Chapter ').split(':')[0]

            elements.append(
                ComicElement(title, href, number)
            )
        return elements
