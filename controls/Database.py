import mysql.connector

DB_CONNECTION = None


class Database:

    def __init__(self, host, user, password, database):
        global DB_CONNECTION

        self.__db = None
        if DB_CONNECTION is None or not DB_CONNECTION.is_connected():
            self.__db = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                charset='utf8',
                autocommit=True
            )
            DB_CONNECTION = self.__db
        else:
            self.__db = DB_CONNECTION
        self.__cursor = self.__db.cursor(named_tuple=True)

    @property
    def row_count(self):
        return self.__cursor.rowcount

    def connect(self):
        global DB_CONNECTION
        self.__db.connect()
        DB_CONNECTION = self.__db

    def execute(self, sql, *args):
        if not self.__db.is_connected():
            self.connect()
        self.__cursor.execute(sql, args)
        return self.__cursor

    def commit(self):
        if not self.__db.is_connected():
            self.connect()
        self.__db.commit()

    def close(self):
        self.__cursor.close()
        self.__db.close()
