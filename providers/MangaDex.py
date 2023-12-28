from httpx import Request

from utils.utils import jsonify, find_element
from networks.Requests import get
from networks.HttpClients import HttpClient, SeleniumClient
from networks.exceptions import NotFoundException
from models.Element import ComicElement
from providers import ComicProvider


class MangaDex(ComicProvider):

    BASE_URL = 'https://mangadex.org'
    API_URL = 'https://api.mangadex.org'
    NAME = 'MangaDex'
    LANG = 'en'
    ICON = '📙'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def updates_request(self) -> Request:
        return get(f'{self.API_URL}/chapter?includes[]=manga&translatedLanguage[]={self.LANG}&order[updatedAt]=desc')

    def updates_parser(self, response) -> list[ComicElement]:
        document = jsonify(response)

        data = document.get('data', [])

        elements = []
        for chapter in data:
            manga = find_element(
                lambda x: x.get('type', '') == 'manga',
                chapter.get('relationships', [])
            )
            chapter = chapter.get('attributes', {})

            elements.append(ComicElement(
                title=manga.get('attributes', {}).get('title', {}).get('en', ''),
                url=f'{self.BASE_URL}/title/{manga.get("id", "")}',
                number=chapter.get('chapter', ''),
            ))
        return elements


class MangaDexIT(MangaDex):

    NAME = 'MangaDexIT'
    LANG = 'it'
