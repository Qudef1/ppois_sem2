import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
import staff
from exception import InvalidSeatException, TheaterException
from managers import TicketManager


class ActionType(str, Enum):
    """Перечисление типов действий для сериализации."""
    ACTION = "action"
    SETTING = "setting"
    REPETITION = "repetition"


class Action:
    __type__ = "action"
    
    def __init__(self, durability: float, name: str, date: datetime):
        self.durability = durability
        self.name = name
        self.date = date

    def to_dict(self) -> Dict[str, Any]:
        date_str = self.date.isoformat() if isinstance(self.date, datetime) else str(self.date)
        return {"__type__": self.__type__, "durability": self.durability, "name": self.name, "date": date_str}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        try:
            date = datetime.fromisoformat(data["date"]) if isinstance(data["date"], str) else data["date"]
        except (ValueError, KeyError):
            date = datetime.now()

        return cls(data["durability"], data["name"], date)

class Setting(Action):
    __type__ = "setting"
    
    def __init__(self, durability: float, name: str, date: datetime, director: staff.Director):
        super().__init__(durability, name, date)
        self.director = director
        self.cast: List[staff.Actor] = []
        self.hall: Optional["AuditoryHall"] = None
        self.tickets: List["Ticket"] = []
        self.base_price: float = 100.0

    def add_cast(self, actor: staff.Actor):
        self.cast.append(actor)

    def bind_to_hall(self, hall: "AuditoryHall", base_price: float = 100.0) -> List["Ticket"]:
        """Привязывает постановку к залу и автоматически создаёт билеты для всех мест."""
        self.hall = hall
        self.base_price = base_price
        self.tickets = []

        for sector_idx in range(hall.sectors):
            for row_idx in range(hall.rows_per_sector):
                for seat_idx in range(hall.seats_per_row):
                    price_multiplier = 1.0 - (sector_idx * 0.2)
                    price = max(self.base_price * price_multiplier, self.base_price * 0.5)

                    ticket = Ticket(
                        price=price,
                        setting=self,
                        sector=sector_idx,
                        row=row_idx,
                        seat=seat_idx,
                        hall_id=hall.hall_id,
                        hall_obj=hall
                    )
                    self.tickets.append(ticket)

        return self.tickets

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "__type__": ActionType.SETTING.value,
            "cast": [a.to_dict() for a in self.cast],
            "director": self.director.to_dict(),
            "hall_id": self.hall.hall_id if self.hall else None,
            "base_price": self.base_price,
            "tickets": [t.to_dict() for t in self.tickets]
        })
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        date = datetime.fromisoformat(data.get("date", "")) if data.get("date") else datetime.now()
        cast = [staff.Actor.from_dict(a) for a in data.get("cast", [])]
        director = staff.Director.from_dict(data["director"]) if data.get("director") else None
        setting = cls(
            data["durability"],
            data["name"],
            date,
            director
        )
        setting.cast = cast
        setting.base_price = data.get("base_price", 100.0)
        setting._pending_hall_id = data.get("hall_id")
        setting._pending_tickets_data = data.get("tickets", [])
        return setting

    def link_hall_and_tickets(self, hall: "AuditoryHall", ticket_manager: "TicketManager"):
        """Привязывает зал и восстанавливает билеты после загрузки из JSON."""
        self.hall = hall
        for ticket_data in self._pending_tickets_data:
            ticket = Ticket.from_dict(ticket_data)
            ticket.link_hall(hall)
            ticket.link_setting(self)
            ticket_manager.add_ticket(ticket)
            self.tickets.append(ticket)
        self._pending_tickets_data = []
        self._pending_hall_id = None
    
class Repetition(Action):
    __type__ = "repetition"
    
    def __init__(self, durability: float, name: str, date: datetime, setting: Setting):
        super().__init__(durability, name, date)
        self.setting = setting
        self.attendance_list: List[staff.Staff] = []

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "__type__": ActionType.REPETITION.value,
            "setting": self.setting.to_dict() if hasattr(self.setting, 'to_dict') else self.setting,
            "attendance_list": [s.to_dict() for s in self.attendance_list]
        })
        return base

    def check_list(self, actor: staff.Staff):
        self.attendance_list.append(actor)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        date = datetime.fromisoformat(data.get("date", "")) if data.get("date") else datetime.now()
        setting = Setting.from_dict(data["setting"])
        attendance_list = [staff.Staff.from_dict(s) for s in data.get("attendance_list", [])]

        rep = cls(
            data["durability"],
            data["name"],
            date,
            setting
        )
        rep.attendance_list = attendance_list
        return rep
    
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
        """Генерирует следующий уникальный ID билета."""
        cls._counter += 1
        return f"TKT-{cls._counter:06d}"

    @classmethod
    def _update_counter(cls, ticket_id: str):
        """Обновляет счётчик, чтобы он был не меньше числового значения из переданного ID."""
        import re
        numbers = re.findall(r'\d+', ticket_id)
        if numbers:
            max_num = max(int(n) for n in numbers)
            if max_num >= cls._counter:
                cls._counter = max_num

    @classmethod
    def reset_counter(cls):
        """Сбрасывает счётчик (полезно для тестов)."""
        cls._counter = 0

    def __init__(self, price: float, setting: "Setting", sector: int, row: int, seat: int,
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
        """Устанавливает ID билета вручную."""
        self.ticket_id = tid
        Ticket._update_counter(tid)

    def link_hall(self, hall: "AuditoryHall"):
        """Метод для связи билета с объектом зала после загрузки из JSON"""
        if self.hall_id != hall.hall_id:
            raise ValueError(f"ID зала не совпадает: {self.hall_id} != {hall.hall_id}")
        self._hall = hall

    @property
    def hall(self):
        if self._hall is None:
            raise RuntimeError(f"Зал для билета {self.ticket_id} не привязан. Вызовите link_hall().")
        return self._hall

    def sell_ticket(self) -> bool:
        if self.is_sold:
            raise TheaterException(f"Билет {self.ticket_id} уже продан")

        current_hall = self.hall

        if not current_hall.is_seat_available(self.sector, self.row, self.seat):
            raise InvalidSeatException(
                f"Место сектор {self.sector}, ряд {self.row}, место {self.seat} уже занято"
            )

        current_hall.occupy_seat(self.sector, self.row, self.seat)
        self.is_sold = True
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
        obj = cls(
            data["price"],
            None,
            data["sector"],
            data["row"],
            data["seat"],
            data["hall_id"]
        )
        obj.set_ticket_id(data["ticket_id"])
        obj.is_sold = data.get("is_sold", False)
        obj._pending_setting_name = data.get("setting_name")
        return obj

    def link_setting(self, setting: "Setting"):
        """Привязывает постановку к билету после загрузки из JSON."""
        self.setting = setting
        
class AuditoryHall:
    __type__ = "auditory_hall"
    
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
        """Проверяет, доступно ли место с заданными координатами"""
        if 0 <= sector < self.sectors and 0 <= row < self.rows_per_sector and 0 <= seat < self.seats_per_row:
            return not self.seats[sector][row][seat].is_occupied
        raise InvalidSeatException(f"Неверные координаты места: сектор {sector}, ряд {row}, место {seat}")

    def occupy_seat(self, sector: int, row: int, seat: int) -> bool:
        """Занимает место с заданными координатами"""
        if not self.is_seat_available(sector, row, seat):
            raise InvalidSeatException(f"Место уже занято: сектор {sector}, ряд {row}, место {seat}")
        self.seats[sector][row][seat].is_occupied = True
        self.audience_count += 1
        return True

    def to_dict(self) -> Dict[str, Any]:
        seats_serialized = [
            [[s.to_dict() for s in row] for row in sector]
            for sector in self.seats
        ]
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
        hall = cls(
            data["name"],
            data["sectors"],
            data["rows_per_sector"],
            data["seats_per_row"],
            data["hall_id"]
        )
        hall.seats = [
            [[Seat.from_dict(s) for s in row] for row in sector]
            for sector in data["seats"]
        ]
        hall.audience_count = data.get("audience_count", 0)
        return hall

class Stage:
    __type__ = "stage"
    
    def __init__(self, name: str, capacity: int, equipment: List[str]):
        self.name = name
        self.capacity = capacity
        self.equipment = equipment
        self.is_available = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "__type__": self.__type__,
            "name": self.name,
            "capacity": self.capacity,
            "equipment": self.equipment,
            "is_available": self.is_available
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Stage":
        stage = cls(data["name"], data["capacity"], data["equipment"])
        stage.is_available = data.get("is_available", True)
        return stage


class Costume:
    __type__ = "costume"
    
    def __init__(self, name: str, size: str, color: str):
        self.name = name
        self.size = size
        self.color = color

    def to_dict(self) -> Dict[str, Any]:
        return {
            "__type__": self.__type__,
            "name": self.name,
            "size": self.size,
            "color": self.color
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Costume":
        return cls(data["name"], data["size"], data["color"])


class CostumeRoom:
    __type__ = "costume_room"
    
    def __init__(self, name: str):
        self.name = name
        self.costume_ids: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "__type__": self.__type__,
            "name": self.name,
            "costume_ids": self.costume_ids
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CostumeRoom":
        room = cls(data["name"])
        room.costume_ids = data.get("costume_ids", [])
        return room
    
    
class Theater:
    __type__ = "theater"
    
    def __init__(self, name: str):
        self.name = name
        from managers import StaffManager, HallManager, PerformanceManager, TicketManager, ResourceManager

        self.staff_manager = StaffManager()
        self.hall_manager = HallManager()
        self.performance_manager = PerformanceManager()
        self.ticket_manager = TicketManager()
        self.resource_manager = ResourceManager()

    def add_staff(self, staff_member):
        """Добавить сотрудника в театр"""
        self.staff_manager.add_staff(staff_member)

    def add_hall(self, hall):
        """Добавить зал в театр"""
        self.resource_manager.hall_manager.add_hall(hall)

    def add_setting(self, setting):
        """Добавить постановку в театр"""
        self.performance_manager.add_setting(setting)

    def bind_setting_to_hall(self, setting_name: str, hall_id: str, base_price: float = 100.0) -> List["Ticket"]:
        """Привязать постановку к залу и автоматически создать билеты."""
        setting = next((s for s in self.performance_manager.settings if s.name == setting_name), None)
        if not setting:
            raise TheaterException(f"Постановка '{setting_name}' не найдена")

        hall = self.resource_manager.hall_manager.get_hall_by_id(hall_id)
        tickets = setting.bind_to_hall(hall, base_price)

        for ticket in tickets:
            self.ticket_manager.add_ticket(ticket)

        return tickets

    def add_ticket(self, ticket):
        """Добавить билет в театр"""
        self.ticket_manager.add_ticket(ticket)

    def sell_ticket(self, ticket_id: str) -> bool:
        """Продать билет"""
        ticket = next((t for t in self.ticket_manager.tickets if t.ticket_id == ticket_id), None)
        if ticket:
            hall = self.resource_manager.hall_manager.get_hall_by_id(ticket.hall_id)
            ticket.link_hall(hall)
        return self.ticket_manager.sell_ticket(ticket_id, self.resource_manager.hall_manager)

    def to_dict(self) -> Dict[str, Any]:
        """Конвертировать театр в словарь для сохранения"""
        return {
            "__type__": self.__type__,
            "name": self.name,
            "staff_manager": self.staff_manager.to_dict(),
            "performance_manager": self.performance_manager.to_dict(),
            "ticket_manager": self.ticket_manager.to_dict(),
            "resource_manager": self.resource_manager.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Theater":
        """Создать театр из словаря при загрузке"""
        theater = cls(data["name"])

        # Восстановление всех компонентов
        theater.staff_manager = theater.staff_manager.__class__.from_dict(data["staff_manager"])
        theater.performance_manager = theater.performance_manager.__class__.from_dict(data["performance_manager"])
        # НЕ восстанавливаем TicketManager.from_dict - билеты будут восстановлены из Setting
        theater.resource_manager = theater.resource_manager.__class__.from_dict(data["resource_manager"])

        # Восстанавливаем связь постановок с залами и билетами
        for setting in theater.performance_manager.settings:
            if hasattr(setting, '_pending_hall_id') and setting._pending_hall_id:
                try:
                    hall = theater.resource_manager.hall_manager.get_hall_by_id(setting._pending_hall_id)
                    setting.link_hall_and_tickets(hall, theater.ticket_manager)
                except TheaterException:
                    pass  # Зал не найден, связь будет восстановлена позже

        # Восстанавливаем связь между билетами и постановками (по setting_name)
        settings_by_name = {s.name: s for s in theater.performance_manager.settings}
        for ticket in theater.ticket_manager.tickets:
            if hasattr(ticket, '_pending_setting_name') and ticket._pending_setting_name:
                setting = settings_by_name.get(ticket._pending_setting_name)
                if setting:
                    ticket.link_setting(setting)
                ticket._pending_setting_name = None

        return theater
            
    def save_to_file(self, filepath: str):
        """Сохранить состояние театра в файл JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)
                
    def load_from_file(self, filepath: str):
        """Загрузить состояние театра из файла JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            loaded_theater = Theater.from_dict(data)
                
            
            self.name = loaded_theater.name
            self.staff_manager = loaded_theater.staff_manager
            self.resource_manager = loaded_theater.resource_manager
            self.performance_manager = loaded_theater.performance_manager
            self.ticket_manager = loaded_theater.ticket_manager
            
            
    def reset(self):
        """Сбросить состояние театра к начальному"""
        self.staff_manager = self.staff_manager.__class__()
        self.performance_manager = self.performance_manager.__class__()
        self.ticket_manager = self.ticket_manager.__class__()
        self.resource_manager = self.resource_manager.__class__()
        self.resource_manager.hall_manager = self.resource_manager.hall_manager.__class__()
        