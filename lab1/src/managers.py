from typing import List, Dict, Any, Optional

from staff import Staff, Actor, Director, CostumeDesigner
from exceptions import (
    TheaterException, TicketNotFoundException
)


class StaffManager:
    def __init__(self):
        self.staff: List[Staff] = []

    def add_staff(self, staff_member: Staff):
        self.staff.append(staff_member)

    def get_staff(self) -> List[Staff]:
        return self.staff

    def to_dict(self) -> Dict[str, Any]:
        return {"staff": [s.to_dict() for s in self.staff]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StaffManager":
        manager = cls()
        for staff_data in data.get("staff", []):
            # определить тип
            if "role" in staff_data:
                staff_obj = Actor.from_dict(staff_data)
            elif "directed_settings" in staff_data:
                staff_obj = Director.from_dict(staff_data)
            elif "created_costumes" in staff_data:
                staff_obj = CostumeDesigner.from_dict(staff_data)
            else:
                staff_obj = Staff.from_dict(staff_data)
            manager.add_staff(staff_obj)
        return manager


class HallManager:
    def __init__(self):
        self.halls: List[Any] = []

    def add_hall(self, hall: Any):
        self.halls.append(hall)

    def get_hall_by_id(self, hall_id: str) -> Any:
        for hall in self.halls:
            if hall.hall_id == hall_id:
                return hall
        raise TheaterException(
            f"Зал с ID '{hall_id}' не найден в системе"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"halls": [h.to_dict() for h in self.halls]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HallManager":
        # импорт здесь, чтобы избежать циклических импортов
        from theater import AuditoryHall

        manager = cls()
        for hall_data in data.get("halls", []):
            hall = AuditoryHall.from_dict(hall_data)
            manager.add_hall(hall)
        return manager


class PerformanceManager:
    def __init__(self):
        self.settings: List[Any] = []
        self.repetitions: List[Any] = []

    def add_setting(self, setting: Any):
        self.settings.append(setting)

    def add_repetition(self, repetition: Any):
        self.repetitions.append(repetition)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "settings": [s.to_dict() for s in self.settings],
            "repetitions": [r.to_dict() for r in self.repetitions]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerformanceManager":
        from theater import Setting, Repetition

        manager = cls()
        for setting_data in data.get("settings", []):
            manager.add_setting(Setting.from_dict(setting_data))
        for rep_data in data.get("repetitions", []):
            manager.add_repetition(Repetition.from_dict(rep_data))
        return manager


class TicketManager:
    def __init__(self):
        self.tickets: List[Any] = []

    def add_ticket(self, ticket: Any):
        self.tickets.append(ticket)

    def get_all_tickets(self) -> List[Any]:
        return self.tickets

    def sell_ticket(self, ticket_id: str, hall_manager: HallManager) -> bool:
        ticket = next((t for t in self.tickets if t.ticket_id == ticket_id), None)
        if not ticket:
            raise TicketNotFoundException(
                f"Билет с ID '{ticket_id}' не найден в системе"
            )
        return ticket.sell_ticket(hall_manager)

    def to_dict(self) -> Dict[str, Any]:
        return {"tickets": [t.to_dict() for t in self.tickets]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TicketManager":
        from theater import Ticket

        manager = cls()
        for ticket_data in data.get("tickets", []):
            manager.add_ticket(Ticket.from_dict(ticket_data))
        return manager


class ResourceManager:
    def __init__(self):
        self.stages: List[Any] = []
        self.costume_rooms: List[Any] = []
        self.costumes: List[Any] = []
        self.hall_manager = HallManager()

    def add_stage(self, stage: Any):
        self.stages.append(stage)

    def add_costume_room(self, room: Any):
        self.costume_rooms.append(room)

    def add_costume(self, costume: Any):
        self.costumes.append(costume)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stages": [s.to_dict() for s in self.stages],
            "costume_rooms": [cr.to_dict() for cr in self.costume_rooms],
            "costumes": [c.to_dict() for c in self.costumes],
            "halls": self.hall_manager.to_dict()["halls"]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceManager":
        from theater import Stage, CostumeRoom, Costume

        manager = cls()
        for stage_data in data.get("stages", []):
            manager.add_stage(Stage.from_dict(stage_data))
        for room_data in data.get("costume_rooms", []):
            manager.add_costume_room(CostumeRoom.from_dict(room_data))
        for costume_data in data.get("costumes", []):
            manager.add_costume(Costume.from_dict(costume_data))
        halls_data = {"halls": data.get("halls", [])}
        manager.hall_manager = HallManager.from_dict(halls_data)
        return manager
