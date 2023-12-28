import re
import json
from typing import Any, AnyStr
from bs4 import BeautifulSoup


def soupify(content: bytes or str):
    """
    Parse HTML with BeautifulSoup
    :param content: HTML
    :return: soup
    """
    return BeautifulSoup(content, 'html.parser')

def jsonify(content: bytes or str) -> dict:
    """
    Parse JSON
    :param content: JSON
    :return: dict
    """
    return json.loads(content)


def find(callback: callable, array: list) -> bool:
    """
    Find element in array that verify a callback
    :param callback: function
    :param array: list to search
    :return: True if the element is present, False instead
    """
    return True if next((x for x in array if callback(x)), None) is not None else False

def find_element(callback: callable, array: list):
    """
    Find element in array that verify a callback
    :param callback: function
    :param array: list to search
    :return: Element is present, None instead
    """
    return next((x for x in array if callback(x)), None)


def confront(key: str, a: Any, b: Any) -> bool:
    if key.startswith('_'):
        if type(a) == str and type(b) == str:
            return b.lower() not in a.lower()
        return a != b
    else:
        if type(a) == str and type(b) == str:
            return b.lower() in a.lower()
        return a == b


def is_sub_dict(parent_dict: dict, sub_dict: dict) -> bool:
    """
    Check if a dict is a sub-dict of other dict
    :param parent_dict: parent dict
    :param sub_dict: dict to check
    :return: True if is a sub-dict, False instead
    """
    return all(confront(key, parent_dict.get(key.lstrip('_'), None), val) for key, val in sub_dict.items())


def try_parse(type_: type, value: Any, default: Any = None) -> Any:
    """
    Try parse Value in Type
    :param type_: type of parsing
    :param value: value to parse
    :param default: value if parse fails
    :return: parsed value
    """
    try:
        return type_(value)
    except (TypeError, ValueError):
        pass
    return default


def try_parse_regex(type_: type, value: AnyStr, default: Any = None, regex: str = None) -> Any:
    """
    Try parse found Value with Regex in Type
    :param type_: type of parsing
    :param value: value to parse
    :param default: value if parse fails
    :param regex: regex to find value | already filled for Int, Float
    :return:
    """
    if regex is None:
        if type_ is int:
            regex = r'^\d+'
        elif type_ is float:
            regex = r'^([0-9]*[.])?[0-9]+'
        else:
            return default
    found = re.search(regex, value)
    if found is not None:
        return try_parse(type_, found.group(), default)
    return default


def iso639_to_name(iso: str) -> str:
    """
    Parse ISO639-1 code in real name
    :param iso: ISO639-1 code
    :return: Language name
    """
    names = {'en': 'English', 'it': ''}
    return names.get(iso, names['en'])


def iso639_to_flag(iso: str) -> str:
    """
    Parse ISO639-1 code in real name
    :param iso: ISO639-1 code
    :return: Language name
    """
    names = {'en': '🇬🇧', 'it': '🇮🇹'}
    return names.get(iso, '')


def create_object(name: str, dict_: dict) -> object:
    return type(name, (object,), dict_)()
