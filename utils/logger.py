import sys
import logging
import logging.handlers as handlers

StreamHandler = logging.StreamHandler(sys.stdout)
StreamHandler.setLevel(logging.INFO)
StreamHandler.setFormatter(logging.Formatter('%(levelname)s:%(asctime)s: %(message)s'))

FileHandler = handlers.RotatingFileHandler('syslog.log', maxBytes=200000, backupCount=1)
FileHandler.setLevel(logging.WARNING)
FileHandler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(asctime)s:%(message)s'))


def get_logger(name: str) -> logging.Logger:
    """
    Auto-set important options in logger
    :param name: logger's name
    :return: Logger instance
    """
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    logger.addHandler(StreamHandler)
    logger.addHandler(FileHandler)
    return logger


def set_level(level: int or str) -> None:
    """
    Set logger's level
    :param level: logger's level
    """
    StreamHandler.setLevel(level)
