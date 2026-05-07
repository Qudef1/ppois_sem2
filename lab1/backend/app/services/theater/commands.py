from __future__ import annotations

from datetime import datetime

from app.services.theater.base import OperationResult
from app.services.theater.domain_imports import Actor, AuditoryHall, Director, Repetition, Setting, TheaterException


class TheaterCommandsMixin:
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
        repetition = Repetition(durability, f"Репетиция: {setting.name}", datetime.fromisoformat(date), setting)
        self._theater.add_repetition(repetition)
        return OperationResult(True, "Репетиция добавлена.")

    def mark_actors_at_repetition(self, repetition_name: str, actor_names: list[str]) -> OperationResult:
        repetition = next((rep for rep in self.repetitions if rep.name == repetition_name), None)
        if not repetition:
            return OperationResult(False, "Репетиция не найдена.")

        actors_map = {actor.name: actor for actor in self.actors}
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
