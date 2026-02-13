import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from managers import StaffManager, HallManager, PerformanceManager, TicketManager, ResourceManager
from staff import Actor, Director, Staff
from exceptions import (
    TheaterException, InvalidSeatException, TicketNotFoundException
)

class Action:
    def __init__(self, durability: float, date: datetime):
        self.durability = durability
        self.date = date

    def to_dict(self) -> Dict[str, Any]:
        return {"durability": self.durability, "date": self.date.isoformat()}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Action":
        date = datetime.fromisoformat(data["date"]) if isinstance(data["date"], str) else data["date"]
        return cls(data["durability"], date)

class Setting(Action):
    def __init__(self, durability: float, name: str, date: datetime, cast: List[Actor] = None, director: Director = None):
        super().__init__(durability, date)
        self.name = name
        self.cast = cast or []
        self.director = director

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "name": self.name,
            "cast": [a.to_dict() for a in self.cast],
            "director": self.director.to_dict() if self.director else None
        })
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Setting":
        date = datetime.fromisoformat(data.get("date", "")) if data.get("date") else datetime.now()
        cast = [Actor.from_dict(a) for a in data.get("cast", [])]
        director = Director.from_dict(data["director"]) if data.get("director") else None
        return cls(
            data["durability"],
            data["name"],
            date,
            cast,
            director
        )

class Repetition(Action):
    def __init__(self, durability: float, setting: "Setting", importance: str, date: datetime, attendance: List[Staff] = None):
        super().__init__(durability, date)
        self.importance = importance
        self.setting = setting  # Объект Setting
        self.attendance = attendance or []

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "importance": self.importance,
            "setting": self.setting.to_dict(),  # Сохраняем весь объект
            "attendance": [s.to_dict() for s in self.attendance]
        })
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Repetition":
        date = datetime.fromisoformat(data.get("date", "")) if data.get("date") else datetime.now()
        setting = Setting.from_dict(data["setting"])  # Восстанавливаем объект
        attendance = [Staff.from_dict(s) for s in data.get("attendance", [])]
        return cls(
            data["durability"],
            setting,
            data["importance"],
            date,
            attendance
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
    num = 0

    def __init__(self, price: float, setting: "Setting", sector: int, row: int, seat: int, hall: "AuditoryHall"):
        self.ticket_id = self.generate_id(setting)
        self.price = price
        self.setting = setting  # Объект Setting
        self.sector = sector
        self.row = row
        self.seat = seat
        self.hall_id = hall.hall_id  # Объект AuditoryHall
        self.is_sold = False

    def generate_id(self, setting: "Setting"):
        Ticket.num += 1
        return f'{setting.name}_{Ticket.num}'

    def sell_ticket(self, hall_manager: "HallManager") -> bool:
        if self.is_sold:
            raise TheaterException(
                f"Билет {self.ticket_id} уже продан"
            )
        
        # Используем напрямую self.hall
        if not self.hall.is_seat_available(self.sector, self.row, self.seat):
            raise InvalidSeatException(
                f"Место сектор {self.sector}, ряд {self.row}, место {self.seat} уже занято"
            )
        
        self.hall.occupy_seat(self.sector, self.row, self.seat)
        self.is_sold = True
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ticket_id": self.ticket_id,
            "price": self.price,
            "setting": self.setting.to_dict(),
            "sector": self.sector,
            "row": self.row,
            "seat": self.seat,
            "hall_id": self.hall_id,
            "is_sold": self.is_sold
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Ticket":
        setting = Setting.from_dict(data["setting"])
        obj = cls(
            data["price"],
            setting,
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
    def __init__(self, name: str, costumes: List["Costume"] = None):
        self.name = name
        self.costumes = costumes or []

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "costumes": [c.to_dict() for c in self.costumes]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CostumeRoom":
        costumes = [Costume.from_dict(c) for c in data.get("costumes", [])]
        return cls(data["name"], costumes)

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
        raise InvalidSeatException(
            f"Неверные координаты места: сектор {sector}, ряд {row}, место {seat}"
        )

    def occupy_seat(self, sector: int, row: int, seat: int) -> bool:
        if not self.is_seat_available(sector, row, seat):
            raise InvalidSeatException(
                f"Место уже занято: сектор {sector}, ряд {row}, место {seat}"
            )
        self.seats[sector][row][seat].is_occupied = True
        self.audience_count += 1
        return True

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


class Theater:
    def __init__(self, name: str):
        self.name = name
        self.staff_manager = StaffManager()
        self.performance_manager = PerformanceManager()
        self.ticket_manager = TicketManager()
        self.resource_manager = ResourceManager()

    @staticmethod
    def _get_data_dir() -> Path:
        """Получить директорию для данных"""
        # Ищем директорию data относительно текущего скрипта
        current = Path.cwd()
        # Проверяем если мы в src/, tests/ или в корне lab1/
        if (current / "data").exists():
            return current / "data"
        elif (current.parent / "data").exists():
            return current.parent / "data"
        else:
            # Создаём data если её нет
            data_dir = current / "data"
            data_dir.mkdir(exist_ok=True)
            return data_dir

    def save_to_file(self, filename: str = "theater_state.json"):
        try:
            # Если это просто имя файла, сохраняем в data/
            filepath = Path(filename)
            if filepath.is_absolute() or "/" in filename or "\\" in filename:
                # Это полный путь
                target_file = Path(filename)
            else:
                # Это просто имя файла, сохраняем в data/
                target_file = self._get_data_dir() / filename
                target_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "name": self.name,
                "staff_manager": self.staff_manager.to_dict(),
                "performance_manager": self.performance_manager.to_dict(),
                "ticket_manager": self.ticket_manager.to_dict(),
                "resource_manager": self.resource_manager.to_dict()
            }
            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            raise TheaterException(
                f"Ошибка при сохранении файла {filename}: {e}"
            )

    @classmethod
    def load_from_file(cls, filename: str = "theater_state.json") -> "Theater":
        # Если это просто имя файла, ищем в data/
        filepath = Path(filename)
        if filepath.is_absolute() or "/" in filename or "\\" in filename:
            # Это полный путь
            target_file = Path(filename)
        else:
            # Это просто имя файла, ищем в data/
            current = Path.cwd()
            if (current / "data" / filename).exists():
                target_file = current / "data" / filename
            elif (current.parent / "data" / filename).exists():
                target_file = current.parent / "data" / filename
            else:
                target_file = Path(filename)
        
        if not target_file.exists():
            raise TheaterException(
                f"Файл состояния не найден: {filename}"
            )
        
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (IOError, OSError, json.JSONDecodeError) as e:
            raise TheaterException(
                f"Ошибка при загрузке файла {filename}: {e}"
            )
        
        try:
            theater = cls(data["name"])
            theater.staff_manager = StaffManager.from_dict(data["staff_manager"])
            theater.performance_manager = PerformanceManager.from_dict(data["performance_manager"])
            theater.ticket_manager = TicketManager.from_dict(data["ticket_manager"])
            theater.resource_manager = ResourceManager.from_dict(data["resource_manager"])
            return theater
        except KeyError as e:
            raise TheaterException(
                f"Некорректный формат состояния в файле {filename}. Отсутствует ключ: {e}"
            )