from __future__ import annotations

from app.services.theater.base import TheaterBaseMixin
from app.services.theater.commands import TheaterCommandsMixin
from app.services.theater.domain_imports import Theater
from app.services.theater.queries import TheaterQueriesMixin


class TheaterService(TheaterBaseMixin, TheaterCommandsMixin, TheaterQueriesMixin):
    """Facade service that combines theater commands and query views."""

    def __init__(self, theater: Theater | None = None) -> None:
        self._theater = theater or Theater("Default Theater")

    @property
    def theater(self) -> Theater:
        return self._theater
