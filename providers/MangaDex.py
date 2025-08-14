from httpx import Request

from utils.utils import jsonify, find_element
from networks.Requests import get
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
        return get(f'{self.API_URL}/chapter?includes[]=manga&translatedLanguage[]={self.LANG}&order[publishAt]=desc')

    def updates_parser(self, response) -> list[ComicElement]:
        document = jsonify(response)

        data = document.get('data', [])

        elements = []
        managed_manga = set()
        for chapter in data:
            manga = find_element(
                lambda x: x.get('type', '') == 'manga',
                chapter.get('relationships', [])
            )
            chapter = chapter.get('attributes', {})

            if manga.get('id', '') in managed_manga:
                continue
            managed_manga.add(manga.get('id', ''))

            manga_titles = manga.get('attributes', {}).get('title', {})

            elements.append(ComicElement(
                title=manga_titles.get('en', '') or (list(manga_titles.items()) or [('', '')])[0][1],
                url=f'{self.BASE_URL}/title/{manga.get("id", "")}',
                number=chapter.get('chapter', '') or '0',
            ))
        return elements


class MangaDexIT(MangaDex):

    NAME = 'MangaDexIT'
    LANG = 'it'
