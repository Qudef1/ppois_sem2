from __future__ import annotations

from dataclasses import dataclass

from app.services.theater.domain_imports import Actor, AuditoryHall, Director, Repetition, Setting


@dataclass(frozen=True)
class OperationResult:
    ok: bool
    message: str


class TheaterBaseMixin:
    @property
    def actors(self) -> list[Actor]:
        return [staff for staff in self._theater.staff_manager.staff if isinstance(staff, Actor)]

    @property
    def directors(self) -> list[Director]:
        return [staff for staff in self._theater.staff_manager.staff if isinstance(staff, Director)]

    @property
    def settings(self) -> list[Setting]:
        return self._theater.performance_manager.settings

    @property
    def repetitions(self) -> list[Repetition]:
        return self._theater.performance_manager.repetitions

    @property
    def halls(self) -> list[AuditoryHall]:
        return self._theater.resource_manager.hall_manager.halls
