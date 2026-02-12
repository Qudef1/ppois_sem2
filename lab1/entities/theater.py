import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from managers import StaffManager

class TheaterCapacityError(Exception):
    pass

class Action:
    def __init__(self, durability: float, date: str):
        self.durability = durability
        self.date = date

    def to_dict(self) -> Dict[str, Any]:
        return {"durability": self.durability, "date": self.date}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Action":
        return cls(data["durability"], data["date"])

class Setting(Action):
    def __init__(self, durability: float, name: str, date: str, cast_ids: List[str] = None):
        super().__init__(durability, date)
        self.name = name
        self.cast_ids = cast_ids or []

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"name": self.name, "cast_ids": self.cast_ids})
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Setting":
        return cls(data["durability"], data["name"], data["date"], data.get("cast_ids", []))

class Repetition(Action):
    def __init__(self, durability: float, setting_id: str, importance: str, date: str = "", attendance_ids: List[str] = None):
        super().__init__(durability, date)
        self.importance = importance
        self.setting_id = setting_id  # ID спектакля
        self.attendance_ids = attendance_ids or []

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "importance": self.importance,
            "setting_id": self.setting_id,
            "attendance_ids": self.attendance_ids
        })
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Repetition":
        return cls(
            data["durability"],
            data["setting_id"],
            data["importance"],
            data.get("date", ""),
            data.get("attendance_ids", [])
        )

class Seat:
    def __init__(self, seat_number: int):
        self.seat_number = seat_number
        self.is_occupied = False

    def to_dict(self) -> Dict[str, Any]:
        return {"seat_number": self.seat_number, "is_occupied": self.is_occupied}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Seat":
        obj = cls(data["seat_number"])
        obj.is_occupied = data.get("is_occupied", False)
        return obj

class Ticket:
    def __init__(self, ticket_id: str, price: float, setting_id: str, sector: int, row: int, seat: int, hall_id: str):
        self.ticket_id = ticket_id
        self.price = price
        self.setting_id = setting_id
        self.sector = sector
        self.row = row
        self.seat = seat
        self.hall_id = hall_id
        self.is_sold = False

    def sell_ticket(self, hall_manager: "HallManager") -> bool:
        if not self.is_sold:
            hall = hall_manager.get_hall_by_id(self.hall_id)
            if hall and hall.is_seat_available(self.sector, self.row, self.seat):
                hall.occupy_seat(self.sector, self.row, self.seat)
                self.is_sold = True
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ticket_id": self.ticket_id,
            "price": self.price,
            "setting_id": self.setting_id,
            "sector": self.sector,
            "row": self.row,
            "seat": self.seat,
            "hall_id": self.hall_id,
            "is_sold": self.is_sold
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Ticket":
        obj = cls(
            data["ticket_id"],
            data["price"],
            data["setting_id"],
            data["sector"],
            data["row"],
            data["seat"],
            data["hall_id"]
        )
        obj.is_sold = data.get("is_sold", False)
        return obj

class Costume:
    def __init__(self, name: str, size: str, color: str):
        self.name = name
        self.size = size
        self.color = color

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "size": self.size, "color": self.color}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Costume":
        return cls(data["name"], data["size"], data["color"])

class CostumeRoom:
    def __init__(self, name: str, costume_ids: List[str] = None):
        self.name = name
        self.costume_ids = costume_ids or []

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "costume_ids": self.costume_ids}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CostumeRoom":
        return cls(data["name"], data.get("costume_ids", []))

class Stage:
    def __init__(self, name: str, capacity: int, equipment: List[str] = None, is_available: bool = True):
        self.name = name
        self.capacity = capacity
        self.equipment = equipment or []
        self.is_available = is_available

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "capacity": self.capacity,
            "equipment": self.equipment,
            "is_available": self.is_available
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Stage":
        return cls(
            data["name"],
            data["capacity"],
            data.get("equipment", []),
            data.get("is_available", True)
        )

class AuditoryHall:
    def __init__(self, name: str, sectors: int, rows_per_sector: int, seats_per_row: int, hall_id: str):
        self.name = name
        self.sectors = sectors
        self.rows_per_sector = rows_per_sector
        self.seats_per_row = seats_per_row
        self.hall_id = hall_id
        self.seats = [
            [
                [Seat(s) for s in range(seats_per_row)]
                for r in range(rows_per_sector)
            ]
            for sec in range(sectors)
        ]
        self.audience_count = 0
        self.capacity = sectors * rows_per_sector * seats_per_row

    def is_seat_available(self, sector: int, row: int, seat: int) -> bool:
        if 0 <= sector < self.sectors and 0 <= row < self.rows_per_sector and 0 <= seat < self.seats_per_row:
            return not self.seats[sector][row][seat].is_occupied
        return False

    def occupy_seat(self, sector: int, row: int, seat: int) -> bool:
        if self.is_seat_available(sector, row, seat):
            self.seats[sector][row][seat].is_occupied = True
            self.audience_count += 1
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        seats_serialized = [
            [
                [s.to_dict() for s in row]
                for row in sector
            ]
            for sector in self.seats
        ]
        return {
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
        hall = cls(
            data["name"],
            data["sectors"],
            data["rows_per_sector"],
            data["seats_per_row"],
            data["hall_id"]
        )
        # восстановить seats
        hall.seats = [
            [
                [Seat.from_dict(s) for s in row]
                for row in sector
            ]
            for sector in data["seats"]
        ]
        hall.audience_count = data.get("audience_count", 0)
        return hall

class HallManager:
    def __init__(self):
        self.halls: List[AuditoryHall] = []

    def add_hall(self, hall: AuditoryHall):
        self.halls.append(hall)

    def get_hall_by_id(self, hall_id: str) -> Optional[AuditoryHall]:
        for hall in self.halls:
            if hall.hall_id == hall_id:
                return hall
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {"halls": [h.to_dict() for h in self.halls]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HallManager":
        manager = cls()
        for hall_data in data.get("halls", []):
            hall = AuditoryHall.from_dict(hall_data)
            manager.add_hall(hall)
        return manager

class PerformanceManager:
    def __init__(self):
        self.settings: List[Setting] = []
        self.repetitions: List[Repetition] = []

    def add_setting(self, setting: Setting):
        self.settings.append(setting)

    def add_repetition(self, repetition: Repetition):
        self.repetitions.append(repetition)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "settings": [s.to_dict() for s in self.settings],
            "repetitions": [r.to_dict() for r in self.repetitions]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerformanceManager":
        manager = cls()
        for setting_data in data.get("settings", []):
            manager.add_setting(Setting.from_dict(setting_data))
        for rep_data in data.get("repetitions", []):
            manager.add_repetition(Repetition.from_dict(rep_data))
        return manager

class TicketManager:
    def __init__(self):
        self.tickets: List[Ticket] = []

    def add_ticket(self, ticket: Ticket):
        self.tickets.append(ticket)

    def get_all_tickets(self) -> List[Ticket]:
        return self.tickets

    def sell_ticket(self, ticket_id: str, hall_manager: HallManager) -> bool:
        ticket = next((t for t in self.tickets if t.ticket_id == ticket_id), None)
        if ticket:
            return ticket.sell_ticket(hall_manager)
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {"tickets": [t.to_dict() for t in self.tickets]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TicketManager":
        manager = cls()
        for ticket_data in data.get("tickets", []):
            manager.add_ticket(Ticket.from_dict(ticket_data))
        return manager

class ResourceManager:
    def __init__(self):
        self.stages: List[Stage] = []
        self.costume_rooms: List[CostumeRoom] = []
        self.hall_manager = HallManager()

    def add_stage(self, stage: Stage):
        self.stages.append(stage)

    def add_costume_room(self, room: CostumeRoom):
        self.costume_rooms.append(room)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stages": [s.to_dict() for s in self.stages],
            "costume_rooms": [cr.to_dict() for cr in self.costume_rooms],
            "halls": self.hall_manager.to_dict()["halls"]  # вложенный объект
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceManager":
        manager = cls()
        for stage_data in data.get("stages", []):
            manager.add_stage(Stage.from_dict(stage_data))
        for room_data in data.get("costume_rooms", []):
            manager.add_costume_room(CostumeRoom.from_dict(room_data))
        # восстановить залы
        halls_data = {"halls": data.get("halls", [])}
        manager.hall_manager = HallManager.from_dict(halls_data)
        return manager

class Theater:
    def __init__(self, name: str):
        self.name = name
        self.staff_manager = StaffManager()
        self.performance_manager = PerformanceManager()
        self.ticket_manager = TicketManager()
        self.resource_manager = ResourceManager()

    def save_to_file(self, filename: str = "theater_state.json"):
        data = {
            "name": self.name,
            "staff_manager": self.staff_manager.to_dict(),
            "performance_manager": self.performance_manager.to_dict(),
            "ticket_manager": self.ticket_manager.to_dict(),
            "resource_manager": self.resource_manager.to_dict()
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, filename: str = "theater_state.json") -> "Theater":
        if not Path(filename).exists():
            raise FileNotFoundError(f"Файл состояния не найден: {filename}")
        
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        theater = cls(data["name"])
        theater.staff_manager = StaffManager.from_dict(data["staff_manager"])
        theater.performance_manager = PerformanceManager.from_dict(data["performance_manager"])
        theater.ticket_manager = TicketManager.from_dict(data["ticket_manager"])
        theater.resource_manager = ResourceManager.from_dict(data["resource_manager"])
        return theater