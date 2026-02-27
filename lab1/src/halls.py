from typing import Dict, Any, List
from seats import Seat
from exception import InvalidSeatException


class AuditoryHall:
    __type__ = "auditory_hall"

    def __init__(self, name: str, sectors: int, rows_per_sector: int, seats_per_row: int, hall_id: str):
        self.name = name
        self.sectors = sectors
        self.rows_per_sector = rows_per_sector
        self.seats_per_row = seats_per_row
        self.hall_id = hall_id
        self.seats = [
            [[Seat(s) for s in range(seats_per_row)] for r in range(rows_per_sector)]
            for sec in range(sectors)
        ]
        self.audience_count = 0
        self.capacity = sectors * rows_per_sector * seats_per_row

    def is_seat_available(self, sector: int, row: int, seat: int) -> bool:
        if 0 <= sector < self.sectors and 0 <= row < self.rows_per_sector and 0 <= seat < self.seats_per_row:
            return not self.seats[sector][row][seat].is_occupied
        raise InvalidSeatException(f"Неверные координаты места: сектор {sector}, ряд {row}, место {seat}")

    def occupy_seat(self, sector: int, row: int, seat: int) -> bool:
        if not self.is_seat_available(sector, row, seat):
            raise InvalidSeatException(f"Место уже занято: сектор {sector}, ряд {row}, место {seat}")
        self.seats[sector][row][seat].is_occupied = True
        self.audience_count += 1
        return True

    def to_dict(self) -> Dict[str, Any]:
        seats_serialized = [[[s.to_dict() for s in row] for row in sector] for sector in self.seats]
        return {
            "__type__": self.__type__,
            "name": self.name,
            "sectors": self.sectors,
            "rows_per_sector": self.rows_per_sector,
            "seats_per_row": self.seats_per_row,
            "hall_id": self.hall_id,
            "seats": seats_serialized,
            "audience_count": self.audience_count,
            "capacity": self.capacity
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditoryHall":
        hall = cls(data["name"], data["sectors"], data["rows_per_sector"], data["seats_per_row"], data["hall_id"])
        # Восстанавливаем структуру мест
        hall.seats = [[[Seat.from_dict(s) for s in row] for row in sector] for sector in data["seats"]]
        for sector in hall.seats:
            for row in sector:
                for seat in row:
                    seat.is_occupied = False
        hall.audience_count = 0
        return hall
