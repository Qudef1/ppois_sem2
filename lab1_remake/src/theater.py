import json 
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import staff 
from exception import InvalidSeatException, TheaterException

class Action:
    def __init__(self,durability:float,name:str,date:datetime):
        self.durability = durability
        self.name = name
        self.date = date

    def to_dict(self) -> Dict[str,Any]:
        return {"durability":self.durability,"name":self.name,"date":self.date}
    
    @classmethod
    def from_dict(cls,data: Dict[str,Any]):
        try:
            date = datetime.fromisoformat(data["date"]) if isinstance(data["date"],str) else data["date"] 
        except:
            RuntimeError()

        return cls(data["durability"],data["name"],data["date"])

class Setting(Action):
    def __init__(self,durability:float,name:str,date:datetime,director:staff.Director):
        super().__init__(durability,name,date)
        self.director = director
        self.cast: List[staff.Actor] = []

    def add_cast(self,actor:staff.Actor):
        self.cast.append(actor)

    def to_dict(self):
        base = super().to_dict()
        base.update({
            "cast": [a.to_dict() for a in self.cast],
            "director": self.director.to_dict()
        })
    
    @classmethod
    def from_dict(cls, data:Dict[str,Any]):
        date = datetime.fromisoformat(data.get("date", "")) if data.get("date") else datetime.now()
        cast = [staff.Actor.from_dict(a) for a in data.get("cast", [])]
        director = staff.Director.from_dict(data["director"]) if data.get("director") else None
        return cls(
            data["durability"],
            data["name"],
            date,
            director,
            cast
        )
    
class Repetition(Action):
    def __init__(self, durability, name, date,setting:Setting):
        super().__init__(durability, name, date)
        self.setting = setting
        self.attendance_list: List[staff.Staff] = []

    def to_dict(self):
        base = super().to_dict()
        base.update({
            "setting":self.setting
        })

    def check_list(self,actor:staff.Staff):
        self.attendance_list.append(actor)

    @classmethod
    def from_dict(cls,data:Dict[str,Any]):
        date = datetime.fromisoformat(data.get("date", "")) if data.get("date") else datetime.now()
        setting = Setting.from_dict(data["setting"])  # Восстанавливаем объект
        attendance_list = [staff.Staff.from_dict(s) for s in data.get("attendance_list",[])]

        return cls(
            data["durability"],
            setting,
            data["name"],
            date,
            attendance_list
        )
    
class Seat:
    def __init__(self,seat_number:int):
        self.seat_number = seat_number
        self.is_occupied = False

    def to_dict(self):
        return {"seat_number":self.seat_number,"is_occupied":self.is_occupied}
    
    @classmethod
    def from_dict(cls,data:Dict[str,Any]):
        return cls(data["seat_number"],data["is_occupied"])
    
class Ticket:
    num = 0  # Внимание: при загрузке из JSON этот счетчик нужно будет обновить вручную

    def __init__(self, price: float, setting: "Setting", sector: int, row: int, seat: int, 
                 hall_id: str, hall_obj: Optional["AuditoryHall"] = None):
        # ID генерируем только если создаем новый билет, а не загружаем
        # В from_dict мы передаем готовый ticket_id, поэтому логику генерации лучше вынести
        self.price = price
        self.setting = setting
        self.sector = sector
        self.row = row
        self.seat = seat
        
        # Храним ID всегда
        self.hall_id = hall_id
        # Храним ссылку на объект для работы логики (может быть None после загрузки)
        self._hall = hall_obj 
        self.is_sold = False
        self.ticket_id = "" # Будет установлен явно

    def set_ticket_id(self, tid: str):
        self.ticket_id = tid

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
        # Теперь мы не передаем hall_manager сюда, а используем привязанный объект
        if self.is_sold:
            raise TheaterException(f"Билет {self.ticket_id} уже продан")
        
        # Используем привязанный объект зала
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
            "ticket_id": self.ticket_id,
            "price": self.price,
            "setting": self.setting.to_dict(),
            "sector": self.sector,
            "row": self.row,
            "seat": self.seat,
            "hall_id": self.hall_id,  # Сохраняем ТОЛЬКО ID
            "is_sold": self.is_sold
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Ticket":
        setting = Setting.from_dict(data["setting"])
        # Создаем объект, передавая hall_id строкой. Объект зала пока None.
        obj = cls(
            data["price"],
            setting,
            data["sector"],
            data["row"],
            data["seat"],
            data["hall_id"] 
        )
        obj.set_ticket_id(data["ticket_id"])
        obj.is_sold = data.get("is_sold", False)
        return obj
        
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
        def __init__(self, name: str, capacity: int, equipment: List[str]):
            self.name = name
            self.capacity = capacity
            self.equipment = equipment
            self.is_available = True
    
        def to_dict(self) -> Dict[str, Any]:
            return {
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
        def __init__(self, name: str, size: str, color: str):
            self.name = name
            self.size = size
            self.color = color
    
        def to_dict(self) -> Dict[str, Any]:
            return {
                "name": self.name,
                "size": self.size,
                "color": self.color
            }
    
        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> "Costume":
            return cls(data["name"], data["size"], data["color"])
    
    
class CostumeRoom:
        def __init__(self, name: str):
            self.name = name
            self.costume_ids: List[str] = []
    
        def to_dict(self) -> Dict[str, Any]:
            return {
                "name": self.name,
                "costume_ids": self.costume_ids
            }
    
        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> "CostumeRoom":
            room = cls(data["name"])
            room.costume_ids = data.get("costume_ids", [])
            return room
    
    
class Theater:
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
            
        def add_ticket(self, ticket):
            """Добавить билет в театр"""
            self.ticket_manager.add_ticket(ticket)
            
        def sell_ticket(self, ticket_id: str) -> bool:
            """Продать билет"""
            # Связываем билет с его залом перед продажей
            ticket = next((t for t in self.ticket_manager.tickets if t.ticket_id == ticket_id), None)
            if ticket:
                # Находим соответствующий зал и связываем с билетом
                hall = self.resource_manager.hall_manager.get_hall_by_id(ticket.hall_id)
                ticket.link_hall(hall)
            return self.ticket_manager.sell_ticket(ticket_id, self.resource_manager.hall_manager)
            
        def to_dict(self) -> Dict[str, Any]:
            """Конвертировать театр в словарь для сохранения"""
            return {
                "name": self.name,
                "staff_manager": self.staff_manager.to_dict(),
                "hall_manager": self.resource_manager.hall_manager.to_dict(),  # HallManager находится внутри ResourceManager
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
            theater.resource_manager.hall_manager = theater.resource_manager.hall_manager.__class__.from_dict(data["hall_manager"])
            theater.performance_manager = theater.performance_manager.__class__.from_dict(data["performance_manager"])
            theater.ticket_manager = theater.ticket_manager.__class__.from_dict(data["ticket_manager"])
            theater.resource_manager = theater.resource_manager.__class__.from_dict(data["resource_manager"])
            
            # После восстановления данных, нужно пересвязать билеты с залами
            for ticket in theater.ticket_manager.tickets:
                try:
                    hall = theater.resource_manager.hall_manager.get_hall_by_id(ticket.hall_id)
                    ticket.link_hall(hall)
                except TheaterException:
                    # Зал может не существовать, в таком случае отложим связывание
                    pass
            
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
                
                # Копируем загруженные данные в текущий объект
                self.name = loaded_theater.name
                self.staff_manager = loaded_theater.staff_manager
                self.resource_manager = loaded_theater.resource_manager
                self.performance_manager = loaded_theater.performance_manager
                self.ticket_manager = loaded_theater.ticket_manager
                # hall_manager уже часть resource_manager
            
        def reset(self):
            """Сбросить состояние театра к начальному"""
            self.staff_manager = self.staff_manager.__class__()
            self.performance_manager = self.performance_manager.__class__()
            self.ticket_manager = self.ticket_manager.__class__()
            self.resource_manager = self.resource_manager.__class__()
            self.resource_manager.hall_manager = self.resource_manager.hall_manager.__class__()
        