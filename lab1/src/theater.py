import json
from typing import List, Dict, Any

from actions import Setting, Repetition
from halls import AuditoryHall
from resources import Stage, Costume, CostumeRoom
from managers import StaffManager, HallManager, PerformanceManager, TicketManager, ResourceManager


class Theater:
    __type__ = "theater"

    def __init__(self, name: str):
        self.name = name
        self.staff_manager = StaffManager()
        self.hall_manager = HallManager()
        self.performance_manager = PerformanceManager()
        self.ticket_manager = TicketManager()
        self.resource_manager = ResourceManager()

    def add_staff(self, staff_member):
        self.staff_manager.add_staff(staff_member)

    def add_hall(self, hall: AuditoryHall):
        self.resource_manager.hall_manager.add_hall(hall)

    def add_setting(self, setting: Setting):
        self.performance_manager.add_setting(setting)

    def add_repetition(self, repetition: Repetition):
        self.performance_manager.add_repetition(repetition)

    def bind_setting_to_hall(self, setting_name: str, hall_id: str, base_price: float = 100.0) -> List[Any]:
        """Привязать постановку к залу и создать билеты."""
        setting = next((s for s in self.performance_manager.settings if s.name == setting_name), None)
        if not setting:
            from exception import TheaterException
            raise TheaterException(f"Постановка '{setting_name}' не найдена")
        hall = self.resource_manager.hall_manager.get_hall_by_id(hall_id)
        tickets = setting.bind_to_hall(hall, base_price)
        for ticket in tickets:
            self.ticket_manager.add_ticket(ticket)
        return tickets

    def sell_ticket(self, ticket_id: str) -> bool:
        ticket = next((t for t in self.ticket_manager.tickets if t.ticket_id == ticket_id), None)
        if ticket:
            hall = self.resource_manager.hall_manager.get_hall_by_id(ticket.hall_id)
            ticket.link_hall(hall)
        return self.ticket_manager.sell_ticket(ticket_id, self.resource_manager.hall_manager)

    def create_costume(self, name: str, size: str, color: str) -> Costume:
        """Создать костюм."""
        costume = Costume(name, size, color)
        self.resource_manager.add_costume(costume)
        return costume

    def assign_costume_to_actor(self, costume: Costume, actor):
        """Назначить костюм актёру."""
        actor.assign_costume(costume)

    def to_dict(self) -> Dict[str, Any]:
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
        theater = cls(data["name"])
        
        # Восстанавливаем менеджеров
        theater.staff_manager = StaffManager.from_dict(data["staff_manager"])
        theater.performance_manager = PerformanceManager.from_dict(data["performance_manager"])
        theater.resource_manager = ResourceManager.from_dict(data["resource_manager"])

        # Восстанавливаем связи постановок с залами и билетами
        for setting in theater.performance_manager.settings:
            if hasattr(setting, '_pending_hall_id') and setting._pending_hall_id:
                try:
                    hall = theater.resource_manager.hall_manager.get_hall_by_id(setting._pending_hall_id)
                    setting.link_hall_and_tickets(hall, theater.ticket_manager)
                except Exception:
                    pass

        return theater

    def save_to_file(self, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)

    def load_from_file(self, filepath: str):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            loaded_theater = Theater.from_dict(data)
            self.name = loaded_theater.name
            self.staff_manager = loaded_theater.staff_manager
            self.resource_manager = loaded_theater.resource_manager
            self.performance_manager = loaded_theater.performance_manager
            self.ticket_manager = loaded_theater.ticket_manager

