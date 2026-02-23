from typing import Dict, Any, List


class Stage:
    __type__ = "stage"

    def __init__(self, name: str, capacity: int, equipment: List[str]):
        self.name = name
        self.capacity = capacity
        self.equipment = equipment
        self.is_available = True

    def to_dict(self) -> Dict[str, Any]:
        return {"__type__": self.__type__, "name": self.name, "capacity": self.capacity,
                "equipment": self.equipment, "is_available": self.is_available}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Stage":
        stage = cls(data["name"], data["capacity"], data["equipment"])
        stage.is_available = data.get("is_available", True)
        return stage


class Costume:
    __type__ = "costume"

    def __init__(self, name: str, size: str, color: str):
        self.name = name
        self.size = size
        self.color = color

    def to_dict(self) -> Dict[str, Any]:
        return {"__type__": self.__type__, "name": self.name, "size": self.size, "color": self.color}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Costume":
        return cls(data["name"], data["size"], data["color"])


class CostumeRoom:
    __type__ = "costume_room"

    def __init__(self, name: str):
        self.name = name
        self.costume_ids: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {"__type__": self.__type__, "name": self.name, "costume_ids": self.costume_ids}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CostumeRoom":
        room = cls(data["name"])
        room.costume_ids = data.get("costume_ids", [])
        return room
