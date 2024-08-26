from datetime import datetime

from utils.utils import soupify
from networks.Requests import get
from networks.exceptions import NotFoundException
from models.Element import ComicElement
from providers import ComicProvider


class MangaDemon(ComicProvider):

    BASE_URL = 'https://demonicscans.org'
    NAME = 'MangaDemon'
    LANG = 'en'
    ICON = '👿'

    def updates_parser(self, response: str) -> list[ComicElement]:
        document = soupify(response)

        entries = document.find(id='updates-container')
        if entries is None:
            raise NotFoundException('Content not found')
        entries = entries.find_all(class_='updates-element')
        if len(entries) == 0:
            raise NotFoundException('List not found')

        current_number_date = datetime.now().strftime('%Y-%m-%d')
        elements = []
        for entry in entries:
            container = entry.find(class_='updates-element-info')

            anchor = entry.find('h2').find('a')
            title = anchor.attrs['title'].strip().replace("’", "'")
            href = self.BASE_URL + anchor.get('href')

            chapters = entry.find_all(class_='chap-date')
            if len(chapters) == 0:
                continue

            chapter = None
            for c in chapters:
                if c.find_all('a')[1].text.strip() == current_number_date:
                    chapter = c
                    break
            if chapter is None:
                continue
            number = chapter.find('a').text.replace('Chapter', '').strip()

            elements.append(
                ComicElement(title, href, number)
            )
        return elements
