from notifiers.NotifierClients import Notifier

DEBUG = 0
INFO = 10
WARN = 20
WARNING = WARN
ERROR = 30
CRITICAL = 40
OK = 99


class ProviderLogging:
    NOTIFIER: Notifier

    def __init__(self, provider: str, notifier: Notifier):
        self.NOTIFIER = notifier

        self.__provider = provider
        self.__log: dict[int, dict[str, int or True]] = {}

    def log(self, level: int, id_: str, message: str, force_send: bool = False) -> None:
        """
        Log "message" with the integer severity "level".
        If the same Log is triggered more than 3 times, send a notification to "owner"
        :param level: Log severity level
        :param id_: ID
        :param message: Message sent in the notification
        :param force_send: Send message even if count < 3 times
        """
        if level not in self.__log:
            self.__log[level] = {}
        if id_ not in self.__log[level]:
            self.__log[level][id_] = 1
            if not force_send:
                return
        if isinstance(self.__log[level][id_], bool):  # message already sent
            return

        self.__log[level][id_] += 1
        if force_send or self.__log[level][id_] >= 3:
            self.NOTIFIER.send(chat_id='owner', message=message)
            self.__log[level][id_] = True

    def remove(self, id_: str, message: str = None):
        """
        Reset Log count.
        If the Log was triggered more than 3 times, send a notification of "Log returned" to "owner"
        :param id_: ID
        :param message: Message sent in the notification
        """
        found = -1
        for level in self.__log.keys():
            if id_ not in self.__log[level]:
                continue
            found = max(found, self.__log[level][id_]) if not isinstance(self.__log[level][id_], bool) else True
            del self.__log[level][id_]

        if (isinstance(found, bool) or found >= 3) and message:
            self.NOTIFIER.send(chat_id='owner', message=message)

    def debug(self, id_: str, message: str, force_send: bool = False) -> None:
        """ Alias of .log(DEBUG, id_, message) """
        self.log(DEBUG, id_, f'*DEBUG*\nSource: {self.__provider}\nReason: {message}', force_send)

    def info(self, id_: str, message: str, force_send: bool = False) -> None:
        """ Alias of .log(INFO, id_, message) """
        self.log(INFO, id_, f'*INFO*\nSource: {self.__provider}\nReason: {message}', force_send)

    def warning(self, id_: str, message: str, force_send: bool = False) -> None:
        """ Alias of .log(WARNING, id_, message) """
        self.log(WARNING, id_, f'⚠️*WARNING*\nSource: {self.__provider}\nReason: {message}', force_send)

    def error(self, id_: str, message: str, force_send: bool = False) -> None:
        """ Alias of .log(ERROR, id_, message) """
        self.log(ERROR, id_, f'⛔ *ERROR*\nSource: {self.__provider}\nReason: {message}', force_send)

    def critical(self, id_: str, message: str, force_send: bool = True) -> None:
        """ Alias of .log(CRITICAL, id_, message, True) """
        self.log(CRITICAL, id_, f'⛔ *CRITICAL*\nSource: {self.__provider}\nReason: {message}', force_send)

    def ok(self, id_: str, message: str = None):
        """ Alias of .remove(id_, message) """
        self.remove(id_, f'✅ *OK*\nSource: {self.__provider}\nReason: {message if message else ""}')
