from datetime import datetime
from typing import List, Dict, Any, Optional


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

    def __init__(self, durability: float, name: str, date: datetime, director: Any):
        super().__init__(durability, name, date)
        self.director = director
        self.cast: List[Any] = []
        self.hall: Optional["AuditoryHall"] = None
        self.tickets: List["Ticket"] = []
        self.base_price: float = 100.0

    def add_cast(self, actor: Any):
        self.cast.append(actor)

    def bind_to_hall(self, hall: "AuditoryHall", base_price: float = 100.0) -> List["Ticket"]:
        """Привязывает постановку к залу и создаёт билеты."""
        from seats import Ticket

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
            "__type__": "setting",
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
        cast = []
        director = None

        if data.get("cast"):
            from staff import Actor
            cast = [Actor.from_dict(a) for a in data["cast"]]

        if data.get("director"):
            from staff import Director
            director = Director.from_dict(data["director"])

        setting = cls(data["durability"], data["name"], date, director)
        setting.cast = cast
        setting.base_price = data.get("base_price", 100.0)
        setting._pending_hall_id = data.get("hall_id")
        setting._pending_tickets_data = data.get("tickets", [])
        return setting

    def link_hall_and_tickets(self, hall: "AuditoryHall", ticket_manager: Any):
        """Восстанавливает связи после загрузки из JSON."""
        from seats import Ticket

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
        self.attendance_list: List[Any] = []

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "__type__": "repetition",
            "setting": self.setting.to_dict() if hasattr(self.setting, 'to_dict') else self.setting,
            "attendance_list": [s.to_dict() for s in self.attendance_list]
        })
        return base

    def check_list(self, staff: Any):
        self.attendance_list.append(staff)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        date = datetime.fromisoformat(data.get("date", "")) if data.get("date") else datetime.now()

        setting = None
        if data.get("setting"):
            setting = Setting.from_dict(data["setting"])

        attendance_list = []
        if data.get("attendance_list"):
            from staff import Staff
            attendance_list = [Staff.from_dict(s) for s in data["attendance_list"]]

        rep = cls(data["durability"], data["name"], date, setting)
        rep.attendance_list = attendance_list
        return rep
