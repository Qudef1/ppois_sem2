# Руководство по сериализации в Theater Management System

## Обзор

Система управления театром поддерживает полную сериализацию/десериализацию всех объектов в JSON формат. Это позволяет сохранять состояние театра между сеансами работы.

## Архитектура

### Модуль `serialization.py`

Централизованный менеджер сериализации предоставляет:

- **`Serializer`** — класс для управления сериализацией
- **`@serializable`** — декоратор для автоматической регистрации классов
- **`register_builtin_types()`** — функция для регистрации всех встроенных типов

### Принцип работы

1. Каждый класс имеет атрибут `__type__` для идентификации
2. Метод `to_dict()` преобразует объект в словарь с полем `__type__`
3. Метод `from_dict()` восстанавливает объект из словаря
4. `Serializer` управляет реестром типов и процессом (де)сериализации

## Использование

### Базовая сериализация

```python
from src.serialization import Serializer, register_builtin_types
from src.theater import Theater, AuditoryHall, Setting
from src.staff import Director, Actor

# Регистрируем типы (один раз при старте)
register_builtin_types()

# Создаём театр
theater = Theater("Grand Theater")
hall = AuditoryHall("Main Hall", 3, 10, 15, "hall_001")
theater.add_hall(hall)

# Сериализация в файл
Serializer.save_to_file(theater, "theater_state.json")

# Десериализация из файла
loaded_theater = Serializer.load_from_file("theater_state.json")
```

### Прямая (де)сериализация объектов

```python
from src.theater import Costume

# Создание объекта
costume = Costume("Royal Robe", "L", "Purple")

# Сериализация
data = Serializer.serialize(costume)
# {'__type__': 'costume', 'name': 'Royal Robe', 'size': 'L', 'color': 'Purple'}

# Десериализация
restored = Serializer.deserialize(data)
```

### Ручная регистрация типов

```python
class MyCustomClass:
    __type__ = "my_custom"
    
    def to_dict(self):
        return {"__type__": self.__type__, "data": "..."}
    
    @classmethod
    def from_dict(cls, data):
        obj = cls()
        # восстановление полей
        return obj

# Регистрация
Serializer.register_type(MyCustomClass)
```

### Использование декоратора

```python
from src.serialization import serializable

@serializable("my_class")
class MyClass:
    __type__ = "my_class"
    # ...
```

## Формат JSON

### Пример сохранённого театра

```json
{
    "__type__": "theater",
    "name": "Grand Theater",
    "staff_manager": {
        "__type__": "staff_manager",
        "staff": [
            {
                "__type__": "actor",
                "name": "Иванов Иван",
                "age": 35,
                "salary": 75000.0,
                "role": "Гамлет",
                "assigned_costumes": {}
            },
            {
                "__type__": "director",
                "name": "Петров Петр",
                "age": 50,
                "salary": 120000.0,
                "directed_settings": []
            }
        ]
    },
    "performance_manager": {...},
    "ticket_manager": {...},
    "resource_manager": {...}
}
```

## Типы данных

### Сотрудники (staff.py)

| Тип | `__type__` | Описание |
|-----|------------|----------|
| `Person` | `staff` | Базовый класс |
| `Staff` | `staff` | Сотрудник |
| `Actor` | `actor` | Актёр |
| `Director` | `director` | Режиссёр |
| `CostumeDesigner` | `costume_designer` | Костюмер |

### Постановки (theater.py)

| Тип | `__type__` | Описание |
|-----|------------|----------|
| `Action` | `action` | Базовое действие |
| `Setting` | `setting` | Постановка |
| `Repetition` | `repetition` | Репетиция |

### Инфраструктура (theater.py)

| Тип | `__type__` | Описание |
|-----|------------|----------|
| `Theater` | `theater` | Театр |
| `AuditoryHall` | `auditory_hall` | Зал |
| `Seat` | `seat` | Место |
| `Ticket` | `ticket` | Билет |
| `Stage` | `stage` | Сцена |
| `Costume` | `costume` | Костюм |
| `CostumeRoom` | `costume_room` | Костюмерная |

### Менеджеры (managers.py)

| Тип | `__type__` | Описание |
|-----|------------|----------|
| `StaffManager` | `staff_manager` | Управление сотрудниками |
| `HallManager` | `hall_manager` | Управление залами |
| `PerformanceManager` | `performance_manager` | Управление постановками |
| `TicketManager` | `ticket_manager` | Управление билетами |
| `ResourceManager` | `resource_manager` | Управление ресурсами |

## Обработка ошибок

### Отсутствие типа в данных

```python
data = {"name": "Test"}  # Нет __type__
Serializer.deserialize(data)
# ValueError: Отсутствует поле __type__ в данных
```

### Незарегистрированный тип

```python
data = {"__type__": "unknown_type", ...}
Serializer.deserialize(data)
# ValueError: Неизвестный тип: unknown_type
```

### Отсутствие метода from_dict

```python
class BadClass:
    __type__ = "bad"

Serializer.register_type(BadClass)
data = {"__type__": "bad", ...}
Serializer.deserialize(data)
# ValueError: Класс BadClass не имеет метода from_dict()
```

## Тестирование

Запуск тестов сериализации:

```bash
cd lab1_remake
venv/bin/python -m pytest tests/test_theater.py::TestSerialization -v
```

### Покрытые тесты

- `test_serializer_register_type` — регистрация типа
- `test_serializer_serialize` — сериализация объекта
- `test_serializer_deserialize` — десериализация объекта
- `test_serializer_round_trip` — полный цикл (сериализация → десериализация)
- `test_serializer_save_load_file` — сохранение/загрузка из файла
- `test_serializer_theater_complex` — сложный объект Theater
- `test_type_enums` — перечисления типов
- `test_all_types_have_type_attribute` — наличие `__type__` у всех классов

## Миграция со старой версии

Если у вас есть старые JSON-файлы без `__type__`:

1. Старые файлы **не будут совместимы** с новой системой
2. Рекомендуется обновить файлы через экспорт в новой версии
3. Для обратной совместимости можно модифицировать `from_dict()` методы

## Best Practices

1. **Всегда вызывайте `register_builtin_types()`** перед (де)сериализацией
2. **Не изменяйте `__type__`** после начала использования — это сломает совместимость
3. **Добавляйте новые поля с `default`** в `from_dict()` для обратной совместимости
4. **Используйте `Serializer.clear_registry()`** в тестах для изоляции

## Пример полного рабочего цикла

```python
from datetime import datetime
from src.serialization import Serializer, register_builtin_types
from src.theater import Theater, AuditoryHall, Setting
from src.staff import Director, Actor

# Инициализация
register_builtin_types()

# Создание театра с данными
theater = Theater("Театр Драмы")

# Добавление сотрудников
director = Director("Сергей Михалков", 55, 150000.0)
actor = Actor("Александр Иванов", 30, 80000.0, "Ромео")
theater.add_staff(director)
theater.add_staff(actor)

# Добавление зала
hall = AuditoryHall("Большой зал", 3, 15, 20, "main_hall")
theater.add_hall(hall)

# Добавление постановки
setting = Setting(2.5, "Ромео и Джульетта", datetime(2025, 6, 15), director)
setting.add_cast(actor)
theater.add_setting(setting)

# Привязка к залу (создание билетов)
theater.bind_setting_to_hall("Ромео и Джульетта", "main_hall", base_price=500.0)

# Продажа билетов
tickets = theater.ticket_manager.get_all_tickets()
tickets[0].sell_ticket()
tickets[1].sell_ticket()

# Сохранение
Serializer.save_to_file(theater, "theater_2025.json")
print("Театр сохранён!")

# ... позже ...

# Загрузка
loaded = Serializer.load_from_file("theater_2025.json")
print(f"Загружен театр: {loaded.name}")
print(f"Сотрудников: {len(loaded.staff_manager.get_staff())}")
print(f"Билетов продано: {sum(1 for t in loaded.ticket_manager.tickets if t.is_sold)}")
```

## Лицензия

Часть проекта Theater Management System.
