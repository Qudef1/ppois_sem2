class TheaterException(Exception):
    """Базовое исключение для системы управления театром."""
    def __init__(self, message: str = "Произошла ошибка в системе театра"):
        super().__init__(message)


class InvalidSeatException(TheaterException):
    """Исключение для ошибок, связанных с местами в зале."""
    def __init__(self, message: str = "Неверное или занятое место"):
        super().__init__(message)


class TicketNotFoundException(TheaterException):
    """Исключение для случая, когда билет не найден."""
    def __init__(self, message: str = "Билет не найден"):
        super().__init__(message)
