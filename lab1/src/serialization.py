"""
Модуль сериализации для системы управления театром.

Предоставляет централизованную регистрацию типов и методы
для сохранения/загрузки объектов в JSON.
"""
import json
from datetime import datetime
from typing import Dict, Any, Type, Callable, Optional
from pathlib import Path


class Serializer:
    """
    Централизованный менеджер сериализации.
    
    Регистрирует типы данных и обеспечивает правильную
    десериализацию на основе __type__.
    """
    
    _type_registry: Dict[str, Type] = {}
    _type_field: str = "__type__"
    
    @classmethod
    def register_type(cls, class_obj: Type, type_name: Optional[str] = None) -> None:
        """
        Регистрирует класс для сериализации.
        
        Args:
            class_obj: Класс для регистрации
            type_name: Имя типа (по умолчанию берётся из __type__ атрибута класса)
        """
        if type_name is None:
            if hasattr(class_obj, '__type__'):
                type_name = class_obj.__type__
            else:
                type_name = class_obj.__name__.lower()
        cls._type_registry[type_name] = class_obj
    
    @classmethod
    def get_type(cls, type_name: str) -> Optional[Type]:
        """Получает класс по имени типа."""
        return cls._type_registry.get(type_name)
    
    @classmethod
    def serialize(cls, obj: Any) -> Dict[str, Any]:
        """
        Сериализует объект в словарь.

        Объект должен иметь метод to_dict().
        """
        if not hasattr(obj, 'to_dict'):
            raise ValueError(f"Объект типа {type(obj).__name__} не имеет метода to_dict()")
        return obj.to_dict()

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> Any:
        """
        Десериализует объект из словаря.

        Словарь должен содержать поле __type__.
        """
        if cls._type_field not in data:
            raise ValueError(f"Отсутствует поле {cls._type_field} в данных")

        type_name = data[cls._type_field]
        class_obj = cls.get_type(type_name)

        if class_obj is None:
            raise ValueError(f"Неизвестный тип сериализации: {type_name}")

        if not hasattr(class_obj, 'from_dict'):
            raise ValueError(f"Класс {class_obj.__name__} не имеет метода from_dict()")

        return class_obj.from_dict(data)
    
    @classmethod
    def save_to_file(cls, obj: Any, filepath: str, indent: int = 4) -> None:
        """Сохраняет объект в JSON файл."""
        data = cls.serialize(obj)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> Any:
        """Загружает объект из JSON файла."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.deserialize(data)
    
    @classmethod
    def clear_registry(cls) -> None:
        """Очищает реестр типов (полезно для тестов)."""
        cls._type_registry.clear()


# ==================== Декораторы для автоматической регистрации ====================

def serializable(type_name: Optional[str] = None):
    """
    Декоратор для автоматической регистрации класса в Serializer.
    
    Пример:
        @serializable("setting")
        class Setting:
            __type__ = "setting"
            ...
    """
    def decorator(cls: Type) -> Type:
        Serializer.register_type(cls, type_name)
        return cls
    return decorator


# ==================== Регистрация встроенных типов ====================

def register_builtin_types():
    """Регистрирует встроенные типы для сериализации."""
    from theater import (
        Theater, Setting, Repetition, Seat, Ticket, 
        AuditoryHall, Stage, Costume, CostumeRoom, Action
    )
    from staff import Person, Staff, Actor, Director, CostumeDesigner
    from managers import (
        StaffManager, HallManager, PerformanceManager, 
        TicketManager, ResourceManager
    )
    
    # Регистрируем все типы
    Serializer.register_type(Theater)
    Serializer.register_type(Setting)
    Serializer.register_type(Repetition)
    Serializer.register_type(Seat)
    Serializer.register_type(Ticket)
    Serializer.register_type(AuditoryHall)
    Serializer.register_type(Stage)
    Serializer.register_type(Costume)
    Serializer.register_type(CostumeRoom)
    Serializer.register_type(Action)
    
    Serializer.register_type(Person)
    Serializer.register_type(Staff)
    Serializer.register_type(Actor)
    Serializer.register_type(Director)
    Serializer.register_type(CostumeDesigner)
    
    Serializer.register_type(StaffManager)
    Serializer.register_type(HallManager)
    Serializer.register_type(PerformanceManager)
    Serializer.register_type(TicketManager)
    Serializer.register_type(ResourceManager)
