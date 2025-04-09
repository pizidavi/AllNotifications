from utils.utils import soupify
from networks.exceptions import NotFoundException
from models.Element import ComicElement
from providers import ComicProvider


class MangaNato(ComicProvider):

    BASE_URL = 'https://www.natomanga.com'
    NAME = 'MangaNato'
    LANG = 'en'
    ICON = '📘'

    def updates_parser(self, response: str) -> list[ComicElement]:
        document = soupify(response)
        entries = document.find(id='contentstory')
        if entries is None:
            raise NotFoundException()
        entries = entries.find_all(class_='itemupdate')
        if len(entries) == 0:
            raise NotFoundException()

        elements = []
        for entry in entries:
            anchor = entry.find('h3').find('a')

            title = anchor.text.strip().replace("’", "'")
            href = anchor.get('href')

            chapters = entry.find_all('span')
            if len(chapters) == 0:
                continue

            chapter = None
            for c in chapters:
                if c.text.strip().endswith(' ago'):
                    chapter = c
                    break

            if chapter is None:
                chapter = chapters[0]

            number = chapter.find('a').text.removeprefix('Chapter ').split(':')[0]

            elements.append(
                ComicElement(title, href, number)
            )
        return elements
