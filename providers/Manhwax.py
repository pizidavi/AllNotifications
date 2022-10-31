from utils.utils import soupify
from networks.exceptions import NotFoundException
from models.Element import ComicElement
from providers import ComicProvider


class Manhwax(ComicProvider):

    BASE_URL = 'https://manhwax.net'
    NAME = 'Manhwax'
    LANG = 'en'
    ICON = '🔞'

    def updates_parser(self, response: str) -> list[ComicElement]:
        document = soupify(response)
        entries = document.find('ul', class_='slick_item')
        if entries is None:
            raise NotFoundException()
        entries = entries.find_all('li')

        elements = []
        for entry in entries:
            container = entry.find(class_='main_text')
            anchor = container.find(class_='title').find('a')
            title = anchor.text.strip()
            href = self._fix_url(anchor.get('href'))
            number = container.find(class_='chapter').find('a').text.removeprefix('Chapter ')
            elements.append(
                ComicElement(title, href, number)
            )
        return elements
