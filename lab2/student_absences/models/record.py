from dataclasses import dataclass
from typing import Optional


@dataclass
class StudentRecord:
    """Модель записи о студенте."""
    
    id: int = 0
    full_name: str = ""
    group: str = ""
    absences_illness: int = 0
    absences_other: int = 0
    absences_unexcused: int = 0
    
    def __post_init__(self):
        """Валидация после инициализации."""
        self.full_name = self.full_name.strip().title() if self.full_name else ""
        self.group = self.group.strip() if self.group else ""
        
    @property
    def total_absences(self) -> int:
        """Общее количество пропусков."""
        return self.absences_illness + self.absences_other + self.absences_unexcused
    
    @property
    def surname(self) -> str:
        """Фамилия студента (первое слово в ФИО)."""
        return self.full_name.split()[0] if self.full_name else ""
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Проверка валидности записи.
        
        Returns:
            Кортеж (валидно, сообщение об ошибке).
        """
        if not self.full_name or len(self.full_name.split()) < 2:
            return False, "ФИО должно содержать как минимум 2 слова"
        
        if not self.group or len(self.group) < 4:
            return False, "Группа должна содержать минимум 4 символа"
        
        if not (0 <= self.absences_illness <= 999):
            return False, "Пропуски по болезни должны быть от 0 до 999"
        
        if not (0 <= self.absences_other <= 999):
            return False, "Пропуски по другим причинам должны быть от 0 до 999"
        
        if not (0 <= self.absences_unexcused <= 999):
            return False, "Пропуски без уважительной причины должны быть от 0 до 999"
        
        return True, None
    
    def to_dict(self) -> dict:
        """Преобразовать в словарь."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "group": self.group,
            "absences_illness": self.absences_illness,
            "absences_other": self.absences_other,
            "absences_unexcused": self.absences_unexcused,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "StudentRecord":
        """Создать из словаря."""
        return cls(
            id=data.get("id", 0),
            full_name=data.get("full_name", ""),
            group=data.get("group", ""),
            absences_illness=data.get("absences_illness", 0),
            absences_other=data.get("absences_other", 0),
            absences_unexcused=data.get("absences_unexcused", 0),
        )
