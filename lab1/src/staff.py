from typing import List, Dict, Any, Optional
from enum import Enum


class StaffType(str, Enum):
    """Перечисление типов сотрудников для сериализации."""
    STAFF = "staff"
    ACTOR = "actor"
    DIRECTOR = "director"
    COSTUME_DESIGNER = "costume_designer"


class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.__age = age

    def get_age(self) -> int:
        return self.__age

    def to_dict(self) -> Dict[str, Any]:
        return {"__type__": StaffType.STAFF.value, "name": self.name, "age": self.get_age()}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Person":
        return cls(data["name"], data["age"])

class Staff(Person):
    def __init__(self, name: str, age: int, salary: float):
        super().__init__(name, age)
        self.__salary = salary

    def get_salary(self) -> float:
        return self.__salary

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"__type__": StaffType.STAFF.value, "salary": self.get_salary()})
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Staff":
        return cls(data["name"], data["age"], data["salary"])

class Actor(Staff):
    def __init__(self, name: str, age: int, salary: float, role: str = None):
        super().__init__(name, age, salary)
        self.role = role
        self.assigned_costumes: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "__type__": StaffType.ACTOR.value,
            "role": self.role,
            "assigned_costumes": {
                k: (v.to_dict() if hasattr(v, 'to_dict') else v)
                for k, v in self.assigned_costumes.items()
            }
        })
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Actor":
        obj = cls(data["name"], data["age"], data["salary"], data.get("role"))
        if "assigned_costumes" in data and isinstance(data["assigned_costumes"], dict):
            from theater import Costume
            obj.assigned_costumes = {
                k: Costume.from_dict(v) if isinstance(v, dict) else v
                for k, v in data["assigned_costumes"].items()
            }
        return obj

    def attend_repetition(self, repetition: Any) -> bool:
        """Актёр отмечается на репетиции. Добавляет себя в список присутствующих."""
        if hasattr(repetition, 'attendance_list'):
            if self not in repetition.attendance_list:
                repetition.check_list(self)
                return True
        return False

    def check_seat_in_hall(self, hall: Any, sector: int, row: int, seat: int) -> bool:
        """Проверяет доступность конкретного места в зале.
        Возвращает True если место свободно, False если занято."""
        if hasattr(hall, 'is_seat_available'):
            try:
                return hall.is_seat_available(sector, row, seat)
            except Exception:
                return False
        return False

    def assign_costume(self, costume: Any):
        """Назначает костюм актёру. Принимает объект Costume."""
        if hasattr(costume, 'name'):
            self.assigned_costumes[costume.name] = costume
        else:
            # Обратная совместимость: если передана строка
            self.assigned_costumes[str(costume)] = costume

    def remove_costume(self, costume_name: str) -> bool:
        """Убирает костюм у актёра по названию."""
        if costume_name in self.assigned_costumes:
            del self.assigned_costumes[costume_name]
            return True
        return False

    def get_costumes(self) -> Dict[str, Any]:
        """Возвращает словарь назначенных костюмов."""
        return self.assigned_costumes

    # Реплики по умолчанию для разных ролей
    DEFAULT_REPLIKES = {
        "Hamlet": "Быть или не быть — вот в чём вопрос!",
        "King": "Я король! Я требую подчинения!",
        "Queen": "О, мой бедный сын...",
        "Knight": "За короля и страну!",
        "Jester": "Смех продлевает жизнь, милорд!",
        "Servant": "Слушаюсь, ваше сиятельство!",
        "Doctor": "Пациент скорее мёртв, чем жив...",
        "Guard": "Кто идёт?",
        "Lover": "Моя любовь к тебе вечна!",
        "Villain": "Месть будет сладкой!",
    }

    def play(self, setting: Any = None) -> str:
        """
        Актёр произносит реплику на сцене.
        Возвращает строку с репликой актёра.
        """
        # Если актёр играет роль в постановке, используем реплику по роли
        if self.role:
            replika = self.DEFAULT_REPLIKES.get(self.role)
            if replika:
                return f"[{self.name} в роли '{self.role}']: {replika}"
        
        # Если есть постановка, пробуем получить реплику из контекста
        if setting and hasattr(setting, 'name'):
            return f"[{self.name} в постановке '{setting.name}']: (импровизирует...)"
        
        # Реплика по умолчанию
        return f"[{self.name}]: (выходит на поклон)"

    def perform_on_stage(self, stage: Any, setting: Any = None) -> str:
        """
        Актёр выступает на сцене в рамках постановки.
        Возвращает строку с информацией о выступлении.
        """
        if not hasattr(stage, 'name') or not stage.is_available:
            return f"[{self.name}]: Сцена '{stage.name if hasattr(stage, 'name') else 'N/A'}' недоступна для выступления."
        
        replika = self.play(setting)
        return f"=== ВЫСТУПЛЕНИЕ НА СЦЕНЕ '{stage.name}' ===\n{replika}\n=== КОНЕЦ ВЫСТУПЛЕНИЯ ==="

    def add_replique(self, role: str, replika: str):
        """Добавляет пользовательскую реплику для роли."""
        self.DEFAULT_REPLIKES[role] = replika

class Director(Staff):
    def __init__(self, name: str, age: int, salary: float):
        super().__init__(name, age, salary)
        self.directed_settings: List[Any] = []

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"__type__": StaffType.DIRECTOR.value, "directed_settings": [s.to_dict() if hasattr(s, 'to_dict') else s for s in self.directed_settings]})
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Director":
        obj = cls(data["name"], data["age"], data["salary"])
        from theater import Setting
        obj.directed_settings = [Setting.from_dict(s) if isinstance(s, dict) else s for s in data.get("directed_settings", [])]
        return obj

    def direct_setting(self, setting: Any):
        self.directed_settings.append(setting)


class CostumeDesigner(Staff):
    def __init__(self, name: str, age: int, salary: float):
        super().__init__(name, age, salary)
        self.created_costumes: List[Any] = []

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"__type__": StaffType.COSTUME_DESIGNER.value, "created_costumes": [c.to_dict() if hasattr(c, 'to_dict') else c for c in self.created_costumes]})
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CostumeDesigner":
        obj = cls(data["name"], data["age"], data["salary"])
        from theater import Costume
        obj.created_costumes = [Costume.from_dict(c) if isinstance(c, dict) else c for c in data.get("created_costumes", [])]
        return obj

    def create_costume(self, costume: Any):
        self.created_costumes.append(costume)
