import os
from abc import ABC, abstractmethod

from controls.Database import Database


class Storage(ABC):

    def __init__(self, type_: str):
        self._type = type_

    @abstractmethod
    def get_user(self, **kwargs) -> dict or None:
        pass

    @abstractmethod
    def get_elements(self, **kwargs) -> list[dict]:
        pass

    @abstractmethod
    def get_element(self, **kwargs) -> dict or None:
        pass

    @abstractmethod
    def set_element(self, element: dict) -> None:
        pass

    @abstractmethod
    def delete_element_by_id(self, user_id: int, element_id: int) -> None:
        pass


class DBStorage(Storage):

    def __init__(self, type_: str):
        super().__init__(type_)

        self._db = Database(
            host=os.getenv('DATABASE_HOST'),
            user=os.getenv('DATABASE_USER'),
            password=os.getenv('DATABASE_PASSWORD'),
            database=os.getenv('DATABASE_NAME')
        )

    @staticmethod
    def _parse_dict(_dict: dict) -> list[str]:
        def convert(key: tuple or str):
            if key.startswith('_'):
                return f"`{key.lstrip('_')}` != %s"
            return f'`{key}` = %s'
        return [convert(key) for key in _dict.keys()]

    @staticmethod
    def _to_array_dict(cursor) -> list[dict]:
        return [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

    @staticmethod
    def _to_dict(cursor) -> dict or None:
        return next(iter(DBStorage._to_array_dict(cursor)), None)

    def get_user(self, **kwargs) -> dict or None:
        if len(kwargs) == 0:
            return None
        sql = "SELECT * " \
              "FROM users " \
              "WHERE " + ' and '.join(self._parse_dict(kwargs))
        result = self._db.execute(sql, *kwargs.values())
        return self._to_dict(result)

    def get_elements(self, **kwargs) -> list[dict]:
        sql = "SELECT t.*, u.telegram_id " \
              f"FROM {self._type} t " \
              "JOIN users u ON u.user_id = t.user_id " + \
              ("WHERE " + ' and '.join(self._parse_dict(kwargs)) if len(kwargs) else '')
        result = self._db.execute(sql, *kwargs.values())
        return self._to_array_dict(result)

    def get_element(self, **kwargs) -> dict or None:
        sql = "SELECT t.*, u.telegram_id " \
              f"FROM {self._type} t " \
              "JOIN users u ON u.user_id = t.user_id " + \
              ("WHERE " + ' and '.join(self._parse_dict(kwargs)) if len(kwargs) else '')
        result = self._db.execute(sql, *kwargs.values())
        return self._to_dict(result)

    def set_element(self, element: dict) -> None:
        sql = f"INSERT INTO {self._type} (" + (','.join(element.keys())) + ") " \
              "VALUES (" + ('%s,' * len(element.values())).rstrip(',') + ") "
        self._db.execute(sql, *element.values())
        self._db.commit()
        if self._db.row_count == 0:
            raise ValueError('No row added')

    def delete_element_by_id(self, user_id: int, element_id: int) -> None:
        sql = f"DELETE FROM {self._type} " \
              "WHERE user_id = %s and element_id = %s"
        self._db.execute(sql, user_id, element_id)
        self._db.commit()
        if self._db.row_count == 0:
            raise ValueError('No row deleted')
