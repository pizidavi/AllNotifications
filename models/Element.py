from dataclasses import dataclass


@dataclass
class Element:
    title: str

    def to_dict(self) -> dict:
        return vars(self)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
               self.title.lower() == other.title.lower()

    def __hash__(self):
        return hash(('title', self.title))

    def __str__(self):
        return f'{self.title}'


@dataclass
class ComicElement(Element):
    url: str
    number: str
    # lang: str

    def __eq__(self, other):
        return super().__eq__(other)  # and self.lang == other.lang

    def __hash__(self):
        return super().__hash__()

    def __str__(self):
        return super().__str__() + f' - {self.number}'
