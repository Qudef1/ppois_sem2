class TheaterException(Exception):
    pass

class InvalidSeatException(TheaterException):
    pass

class TicketNotFoundException(TheaterException):
    pass

class InvalidDateException(TheaterException):
    pass