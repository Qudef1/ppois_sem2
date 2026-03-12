"""Критерии поиска для фильтрации записей."""

from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class SearchCriteria:
    """Критерии поиска записей."""
    
    group: Optional[str] = None
    surname: Optional[str] = None
    absence_type: Optional[Literal['illness', 'other', 'unexcused']] = None
    min_absences: Optional[int] = None
    max_absences: Optional[int] = None
    
    def __post_init__(self):
        """Очистка значений после инициализации."""
        if self.group:
            self.group = self.group.strip()
        if self.surname:
            self.surname = self.surname.strip()
    
    def is_valid(self) -> bool:
        """Проверка: заполнено ли хотя бы одно условие."""
        return any([
            self.group,
            self.surname,
            self.absence_type is not None,
            self.min_absences is not None
        ])
    
    def to_dict(self) -> dict:
        """Преобразовать в словарь, исключая None."""
        return {k: v for k, v in self.__dict__.items() if v is not None}
