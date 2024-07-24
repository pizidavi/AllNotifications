from utils.utils import jsonify
from networks.Requests import get
from networks.exceptions import NotFoundException
from models.Element import ComicElement
from providers import ComicProvider


class Comick(ComicProvider):

    BASE_URL = 'https://comick.io'
    API_URL = 'https://api.comick.io'
    NAME = 'Comick'
    LANG = 'en'
    ICON = '👿'

    def updates_request(self):
        return get(f'{self.API_URL}/chapter?lang=en&page=1&order=new')

    def updates_parser(self, response: str) -> list[ComicElement]:
        entries = jsonify(response)
        if len(entries) == 0:
            raise NotFoundException('No entries found')

        elements = []
        for entry in entries:
            title = entry.get('md_comics').get('title')
            href = self.BASE_URL + '/comic/' + entry.get('md_comics').get('slug')

            chapter = entry.get('chap')
            # volume = entry.get('vol')

            elements.append(
                ComicElement(title, href, chapter)
            )
        return elements
