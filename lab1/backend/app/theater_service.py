from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


LAB1_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = LAB1_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from actions import Repetition, Setting
from exception import TheaterException
from halls import AuditoryHall
from staff import Actor, Director
from theater import Theater


@dataclass(frozen=True)
class OperationResult:
    ok: bool
    message: str


class TheaterService:
    """Application service around domain model for web usage."""

    def __init__(self, theater: Theater | None = None) -> None:
        self._theater = theater or Theater("Default Theater")

    @property
    def theater(self) -> Theater:
        return self._theater

    def rename_theater(self, new_name: str) -> OperationResult:
        if not new_name.strip():
            return OperationResult(False, "Название не может быть пустым.")
        self._theater.name = new_name.strip()
        return OperationResult(True, "Название театра обновлено.")

    def add_hall(self, name: str, sectors: int, rows: int, seats: int, hall_id: str) -> OperationResult:
        hall = AuditoryHall(name.strip(), sectors, rows, seats, hall_id.strip())
        self._theater.add_hall(hall)
        return OperationResult(True, f"Зал '{name}' добавлен.")

    def add_actor(self, name: str, age: int, salary: float, role: str | None) -> OperationResult:
        actor = Actor(name.strip(), age, salary, role.strip() if role else None)
        self._theater.add_staff(actor)
        return OperationResult(True, f"Актер '{name}' добавлен.")

    def add_director(self, name: str, age: int, salary: float) -> OperationResult:
        director = Director(name.strip(), age, salary)
        self._theater.add_staff(director)
        return OperationResult(True, f"Режиссер '{name}' добавлен.")

    def add_setting(self, name: str, durability: float, date: str, director_name: str) -> OperationResult:
        director = next((d for d in self.directors if d.name == director_name), None)
        if not director:
            return OperationResult(False, "Режиссер не найден.")
        setting = Setting(durability, name.strip(), datetime.fromisoformat(date), director)
        self._theater.add_setting(setting)
        return OperationResult(True, f"Постановка '{name}' добавлена.")

    def create_costume(self, name: str, size: str, color: str) -> OperationResult:
        self._theater.create_costume(name.strip(), size.strip().upper(), color.strip())
        return OperationResult(True, f"Костюм '{name}' создан.")

    def bind_setting_to_hall(self, setting_name: str, hall_id: str, base_price: float) -> OperationResult:
        tickets = self._theater.bind_setting_to_hall(setting_name, hall_id, base_price)
        return OperationResult(True, f"Создано {len(tickets)} билетов.")

    def add_actor_to_setting(self, actor_name: str, setting_name: str) -> OperationResult:
        actor = next((a for a in self.actors if a.name == actor_name), None)
        setting = next((s for s in self.settings if s.name == setting_name), None)
        if not actor or not setting:
            return OperationResult(False, "Актер или постановка не найдены.")
        setting.add_cast(actor)
        return OperationResult(True, f"Актер '{actor.name}' добавлен в '{setting.name}'.")

    def assign_costume_to_actor(self, costume_name: str, actor_name: str) -> OperationResult:
        actor = next((a for a in self.actors if a.name == actor_name), None)
        costume = next((c for c in self._theater.resource_manager.costumes if c.name == costume_name), None)
        if not actor or not costume:
            return OperationResult(False, "Актер или костюм не найдены.")
        self._theater.assign_costume_to_actor(costume, actor)
        return OperationResult(True, f"Костюм '{costume_name}' назначен актеру '{actor_name}'.")

    def add_repetition(self, setting_name: str, date: str, durability: float) -> OperationResult:
        setting = next((s for s in self.settings if s.name == setting_name), None)
        if not setting:
            return OperationResult(False, "Постановка не найдена.")
        rep = Repetition(durability, f"Репетиция: {setting.name}", datetime.fromisoformat(date), setting)
        self._theater.add_repetition(rep)
        return OperationResult(True, "Репетиция добавлена.")

    def mark_actors_at_repetition(self, repetition_name: str, actor_names: list[str]) -> OperationResult:
        repetition = next((r for r in self.repetitions if r.name == repetition_name), None)
        if not repetition:
            return OperationResult(False, "Репетиция не найдена.")
        actors_map = {a.name: a for a in self.actors}
        added = 0
        for name in actor_names:
            actor = actors_map.get(name)
            if actor and actor not in repetition.attendance_list:
                repetition.check_list(actor)
                added += 1
        return OperationResult(True, f"Отмечено актеров: {added}.")

    def sell_ticket(self, ticket_id: str) -> OperationResult:
        try:
            self._theater.sell_ticket(ticket_id)
            return OperationResult(True, f"Билет #{ticket_id} продан.")
        except TheaterException as exc:
            return OperationResult(False, str(exc))

    def save_state(self, path: str) -> OperationResult:
        try:
            self._theater.save_to_file(path)
            return OperationResult(True, f"Сохранено в: {path}")
        except Exception as exc:  # noqa: BLE001
            return OperationResult(False, f"Ошибка сохранения: {exc}")

    def load_state(self, path: str) -> OperationResult:
        try:
            self._theater.load_from_file(path)
            return OperationResult(True, f"Загружено из: {path}")
        except Exception as exc:  # noqa: BLE001
            return OperationResult(False, f"Ошибка загрузки: {exc}")

    @property
    def actors(self) -> list[Actor]:
        return [s for s in self._theater.staff_manager.staff if isinstance(s, Actor)]

    @property
    def directors(self) -> list[Director]:
        return [s for s in self._theater.staff_manager.staff if isinstance(s, Director)]

    @property
    def settings(self) -> list[Setting]:
        return self._theater.performance_manager.settings

    @property
    def repetitions(self) -> list[Repetition]:
        return self._theater.performance_manager.repetitions

    @property
    def halls(self) -> list[AuditoryHall]:
        return self._theater.resource_manager.hall_manager.halls

    def dashboard(self) -> dict[str, Any]:
        tickets = self._theater.ticket_manager.tickets
        sold = [t for t in tickets if t.is_sold]
        return {
            "theater": self._theater,
            "name": self._theater.name,
            "actors": self.actors,
            "directors": self.directors,
            "settings": self.settings,
            "repetitions": self.repetitions,
            "halls": self.halls,
            "costumes": self._theater.resource_manager.costumes,
            "tickets": tickets,
            "sold_tickets": sold,
            "available_tickets": [t for t in tickets if not t.is_sold],
        }

    def info_summary(self) -> dict[str, Any]:
        halls = self.halls
        tickets = self._theater.ticket_manager.tickets
        sold = [t for t in tickets if t.is_sold]
        return {
            "theater_name": self._theater.name,
            "staff_count": len(self._theater.staff_manager.staff),
            "halls_count": len(halls),
            "total_capacity": sum(h.capacity for h in halls),
            "settings_count": len(self.settings),
            "repetitions_count": len(self.repetitions),
            "tickets_count": len(tickets),
            "sold_tickets_count": len(sold),
            "available_tickets_count": len(tickets) - len(sold),
            "stages_count": len(self._theater.resource_manager.stages),
            "costume_rooms_count": len(self._theater.resource_manager.costume_rooms),
            "costumes_count": len(self._theater.resource_manager.costumes),
        }

    def info_staff(self) -> dict[str, Any]:
        return {
            "total": len(self._theater.staff_manager.staff),
            "actors": [
                {
                    "name": actor.name,
                    "age": actor.get_age(),
                    "salary": actor.get_salary(),
                    "role": actor.role,
                    "costumes_count": len(actor.get_costumes()),
                }
                for actor in self.actors
            ],
            "directors": [
                {
                    "name": director.name,
                    "age": director.get_age(),
                    "salary": director.get_salary(),
                    "directed_settings_count": len(director.directed_settings),
                }
                for director in self.directors
            ],
        }

    def info_halls(self) -> dict[str, Any]:
        halls_data: list[dict[str, Any]] = []
        for hall in self.halls:
            occupied = sum(1 for sector in hall.seats for row in sector for seat in row if seat.is_occupied)
            halls_data.append(
                {
                    "name": hall.name,
                    "hall_id": hall.hall_id,
                    "sectors": hall.sectors,
                    "rows_per_sector": hall.rows_per_sector,
                    "seats_per_row": hall.seats_per_row,
                    "capacity": hall.capacity,
                    "occupied": occupied,
                    "available": hall.capacity - occupied,
                }
            )
        return {"halls": halls_data}

    def info_settings(self) -> dict[str, Any]:
        settings_data = [
            {
                "name": setting.name,
                "duration_hours": setting.durability,
                "date": setting.date.isoformat() if hasattr(setting.date, "isoformat") else str(setting.date),
                "director": setting.director.name if setting.director else None,
                "cast_count": len(setting.cast),
                "hall": setting.hall.name if setting.hall else None,
            }
            for setting in self.settings
        ]
        repetitions_data = [
            {
                "name": repetition.name,
                "duration_hours": repetition.durability,
                "date": repetition.date.isoformat() if hasattr(repetition.date, "isoformat") else str(repetition.date),
                "setting": repetition.setting.name if repetition.setting else None,
                "attendance_count": len(repetition.attendance_list),
            }
            for repetition in self.repetitions
        ]
        return {"settings": settings_data, "repetitions": repetitions_data}

    def info_tickets(self) -> dict[str, Any]:
        tickets = self._theater.ticket_manager.tickets
        sold = [ticket for ticket in tickets if ticket.is_sold]
        return {
            "total": len(tickets),
            "sold": len(sold),
            "available": len(tickets) - len(sold),
            "revenue": sum(ticket.price for ticket in sold),
            "tickets": [
                {
                    "ticket_id": ticket.ticket_id,
                    "setting": ticket.setting.name if ticket.setting else None,
                    "hall_id": ticket.hall_id,
                    "sector": ticket.sector,
                    "row": ticket.row,
                    "seat": ticket.seat,
                    "price": ticket.price,
                    "is_sold": ticket.is_sold,
                }
                for ticket in tickets
            ],
        }

    def info_resources(self) -> dict[str, Any]:
        resource_manager = self._theater.resource_manager
        return {
            "stages": [
                {
                    "name": stage.name,
                    "capacity": stage.capacity,
                    "equipment": stage.equipment,
                    "is_available": stage.is_available,
                }
                for stage in resource_manager.stages
            ],
            "costume_rooms": [
                {"name": room.name, "costume_ids": room.costume_ids}
                for room in resource_manager.costume_rooms
            ],
            "costumes": [
                {"name": costume.name, "size": costume.size, "color": costume.color}
                for costume in resource_manager.costumes
            ],
        }

    def info_all(self) -> dict[str, Any]:
        return {
            "summary": self.info_summary(),
            "staff": self.info_staff(),
            "halls": self.info_halls(),
            "performances": self.info_settings(),
            "tickets": self.info_tickets(),
            "resources": self.info_resources(),
        }
