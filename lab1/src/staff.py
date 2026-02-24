from typing import List, Dict, Any


class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.__age = age

    def get_age(self) -> int:
        return self.__age

    def to_dict(self) -> Dict[str, Any]:
        return {"__type__": "person", "name": self.name, "age": self.get_age()}

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
        base.update({"__type__": "staff", "salary": self.get_salary()})
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
            "__type__": "actor",
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
        """Отметиться на репетиции."""
        if hasattr(repetition, 'attendance_list'):
            if self not in repetition.attendance_list:
                repetition.check_list(self)
                return True
        return False

    def assign_costume(self, costume: Any):
        """Назначить костюм актёру."""
        if hasattr(costume, 'name'):
            self.assigned_costumes[costume.name] = costume
        else:
            self.assigned_costumes[str(costume)] = costume

    def get_costumes(self) -> Dict[str, Any]:
        return self.assigned_costumes


class Director(Staff):
    def __init__(self, name: str, age: int, salary: float):
        super().__init__(name, age, salary)
        self.directed_settings: List[Any] = []

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "__type__": "director",
            "directed_settings": [s.to_dict() if hasattr(s, 'to_dict') else s for s in self.directed_settings]
        })
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Director":
        obj = cls(data["name"], data["age"], data["salary"])
        from theater import Setting
        obj.directed_settings = [Setting.from_dict(s) if isinstance(s, dict) else s for s in data.get("directed_settings", [])]
        return obj

    def direct_setting(self, setting: Any):
        self.directed_settings.append(setting)
