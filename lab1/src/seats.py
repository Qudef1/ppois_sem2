from typing import Dict, Any, Optional


class Seat:
    __type__ = "seat"

    def __init__(self, seat_number: int):
        self.seat_number = seat_number
        self.is_occupied = False

    def to_dict(self) -> Dict[str, Any]:
        return {"__type__": self.__type__, "seat_number": self.seat_number, "is_occupied": self.is_occupied}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Seat":
        seat = cls(data["seat_number"])
        seat.is_occupied = data.get("is_occupied", False)
        return seat


class Ticket:
    __type__ = "ticket"
    _counter = 0

    @classmethod
    def _next_id(cls) -> str:
        cls._counter += 1
        return str(cls._counter)

    def __init__(self, price: float, setting: Any, sector: int, row: int, seat: int,
                 hall_id: str, hall_obj: Optional["AuditoryHall"] = None):
        self.price = price
        self.setting = setting
        self.sector = sector
        self.row = row
        self.seat = seat
        self.hall_id = hall_id
        self._hall = hall_obj
        self.is_sold = False
        self.ticket_id = Ticket._next_id()

    def set_ticket_id(self, tid: str):
        """Устанавливает ID билета вручную (при загрузке из JSON)."""
        self.ticket_id = tid
        try:
            num = int(tid)
            if num >= Ticket._counter:
                Ticket._counter = num
        except ValueError:
            pass

    def link_hall(self, hall: "AuditoryHall"):
        if self.hall_id != hall.hall_id:
            raise ValueError(f"ID зала не совпадает: {self.hall_id} != {hall.hall_id}")
        self._hall = hall

    def sell_ticket(self) -> bool:
        from exception import InvalidSeatException, TheaterException

        if self.is_sold:
            raise TheaterException(f"Билет {self.ticket_id} уже продан")

        # Помечаем билет как проданный и занимаем место
        self.is_sold = True
        self._hall.occupy_seat(self.sector, self.row, self.seat)
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "__type__": self.__type__,
            "ticket_id": self.ticket_id,
            "price": self.price,
            "setting_name": self.setting.name if self.setting else None,
            "sector": self.sector,
            "row": self.row,
            "seat": self.seat,
            "hall_id": self.hall_id,
            "is_sold": self.is_sold
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Ticket":
        obj = cls(data["price"], None, data["sector"], data["row"], data["seat"], data["hall_id"])
        obj.set_ticket_id(data["ticket_id"])
        obj.is_sold = data.get("is_sold", False)
        obj._pending_setting_name = data.get("setting_name")
        return obj

    def link_setting(self, setting: Any):
        self.setting = setting
