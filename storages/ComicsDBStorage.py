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

    def get_ignored_elements(self) -> list[dict]:
        self.delete_ignored_elements()

        sql = "SELECT * " \
              f"FROM {self._type}_ignored"
        result = self._db.execute(sql)
        return self._to_array_dict(result)

    def set_ignored_element(self, element_id: int, provider: str) -> None:
        sql = f"INSERT INTO {self._type}_ignored (element_id, provider) " \
              "VALUES (%s, %s) "
        self._db.execute(sql, element_id, provider)
        self._db.commit()
        if self._db.row_count == 0:
            raise ValueError('No row added')

    def delete_ignored_elements(self) -> None:
        sql = f"DELETE FROM {self._type}_ignored " \
              "WHERE createdAt < DATE_SUB(NOW(), INTERVAL 24 HOUR)"
        self._db.execute(sql)
        self._db.commit()
