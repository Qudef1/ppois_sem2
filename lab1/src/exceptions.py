"""
Пользовательские исключения для театральной системы.
"""


class TheaterException(Exception):
    """Базовое исключение для всех ошибок театральной системы"""
    pass


class InvalidSeatException(TheaterException):
    """Исключение при попытке доступа к несуществующему месту или при занятости места"""
    pass


class TicketNotFoundException(TheaterException):
    """Исключение при поиске несуществующего билета"""
    pass


class InvalidDateException(TheaterException):
    """Исключение при неверной дате или времени"""
    pass
