from typing import List, Dict, Any

class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.__age = age

    def get_age(self) -> int:
        return self.__age

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "age": self.get_age()}

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
        base.update({"salary": self.get_salary()})
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Staff":
        return cls(data["name"], data["age"], data["salary"])

class Actor(Staff):
    def __init__(self, name: str, age: int, salary: float, role: str = None):
        super().__init__(name, age, salary)
        self.role = role
        self.assigned_costume: str = None

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"role": self.role, "assigned_costume": self.assigned_costume})
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Actor":
        obj = cls(data["name"], data["age"], data["salary"], data.get("role"))
        obj.assigned_costume = data.get("assigned_costume")
        return obj

    def attend_repetition(self, repetition_id: str):
        # в реальной системе здесь будет вызов внешней функции
        pass

    def assign_costume(self, costume_id: str):
        self.assigned_costume = costume_id

class Director(Staff):
    def __init__(self, name: str, age: int, salary: float):
        super().__init__(name, age, salary)
        self.directed_settings: List[str] = []  # будем хранить ID спектаклей

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"directed_settings": self.directed_settings})
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Director":
        obj = cls(data["name"], data["age"], data["salary"])
        obj.directed_settings = data.get("directed_settings", [])
        return obj

    def direct_setting(self, setting_id: str):
        self.directed_settings.append(setting_id)

class CostumeDesigner(Staff):
    def __init__(self, name: str, age: int, salary: float):
        super().__init__(name, age, salary)
        self.created_costumes: List[str] = []  # ID костюмов

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"created_costumes": self.created_costumes})
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CostumeDesigner":
        obj = cls(data["name"], data["age"], data["salary"])
        obj.created_costumes = data.get("created_costumes", [])
        return obj

    def create_costume(self, costume_name: str):
        self.created_costumes.append(costume_name)
