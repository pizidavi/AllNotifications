from storages import DBStorage


class ComicsDBStorage(DBStorage):

    def search_elements_by_title(self, title: str) -> list[dict]:
        sql = "SELECT * " \
              f"FROM {self._type} " \
              "WHERE title LIKE %s"
        result = self._db.execute(sql, f'%{title}%')
        return self._to_array_dict(result)

    def set_element_number(self, element_id: int, number: str) -> None:
        sql = "UPDATE " + self._type + " " \
              "SET number = %s " \
              "WHERE element_id = %s and disabled = 0"
        self._db.execute(sql, number, element_id)
        self._db.commit()
