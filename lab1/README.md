# Theater Management System

Система управления театром - объектно-ориентированное приложение для управления театральными постановками, персоналом, костюмами и билетами.

## Структура проекта

```
lab1/
├── src/                    # Исходный код приложения
│   ├── __init__.py
│   ├── main.py            # CLI интерфейс с 15 командами
│   ├── exceptions.py      # 4 класса исключений
│   ├── staff.py           # Классы для персонала (Актёры, Режиссёры, Дизайнеры)
│   ├── theater.py         # Основные сущности театра
│   └── managers.py        # 5 менеджеров для управления ресурсами
├── tests/                 # Модульные и интеграционные тесты
│   ├── __init__.py
│   └── test_theater.py    # 18 реалистичных тестов
├── data/                  # Данные приложения
│   └── theater_state.json # Сохранённое состояние театра (JSON)
├── docs/                  # Документация
│   └── class_diagram.puml # Диаграмма классов
├── README.md              # Этот файл
├── requirements.txt       # Зависимости проекта
└── .gitignore             # Git ignore правила
```

## Требования

- Python 3.8+
- pytest (для тестирования)
- coverage (для анализа покрытия кода)

## Установка

1. Клонируйте репозиторий:
```bash
cd ppois_sem2/lab1
```

2. Создайте виртуальное окружение (если ещё не создано):
```bash
python3 -m venv ../venv
source ../venv/bin/activate  # Linux/Mac
# или
../venv\Scripts\activate  # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Использование

### Запуск CLI

```bash
cd src
python main.py
```

#### Основные команды:

```bash
# Управление персоналом
python main.py add_actor           # Добавить актёра
python main.py add_director        # Добавить режиссёра
python main.py add_costumedesigner # Добавить дизайнера костюмов
python main.py list_staff          # Список персонала

# Управление залами
python main.py create_hall         # Создать зрительный зал

# Управление костюмами
python main.py create_costume      # Создать костюм
python main.py assign_costume      # Назначить костюм актёру

# Управление спектаклями
python main.py add_setting         # Добавить спектакль
python main.py assign_actor_setting       # Добавить актёра в спектакль
python main.py assign_director_setting    # Назначить режиссёра спектаклю

# Управление билетами
python main.py create_ticket       # Создать билет
python main.py sell_ticket         # Продать билет
python main.py list_tickets        # Список билетов

# Управление репетициями
python main.py create_setup        # Организовать репетицию

# Управление состоянием
python main.py --load              # Загрузить состояние из файла
python main.py --save              # Сохранить состояние в файл
python main.py --reset             # Создать новый театр
```

### Запуск тестов

```bash
# Все тесты
pytest tests/test_theater.py -v

# С отчётом о покрытии
pytest tests/test_theater.py --cov=src --cov-report=term-missing

# Конкретный тест
pytest tests/test_theater.py::TestTheaterRealScenarios::test_01_setup_romeo_and_juliette_complete
```

## Архитектура

### Иерархия классов

#### Person / Staff

```
Person
├── name: str
└── age: int

Staff(Person)
├── salary: float
├── Actor(Staff)
│   ├── role: str
│   └── assigned_costume: Optional[Costume]
├── Director(Staff)
│   └── directed_settings: list[int]
└── CostumeDesigner(Staff)
    └── created_costumes: list[int]
```

#### Theater Entities

```
Action (base class для dated events)
├── durability: int
└── datetime: datetime

Setting(Action)
├── name: str
├── cast_ids: list[int]
└── director_id: int

Repetition(Action)
├── setting_id: int
├── importance: int
└── attendance_ids: list[int]

Seat
├── seat_number: int
└── is_occupied: bool

Ticket
├── id: int
├── price: float
├── coordinates: tuple[int, int]
├── hall_id: int
└── is_sold: bool

Costume
├── name: str
├── size: str
└── color: str

CostumeRoom
├── name: str
└── costume_ids: list[int]

Stage
├── name: str
├── capacity: int
├── equipment: list[str]
└── is_available: bool

AuditoryHall (3D matrix of seats)
├── hall_id: int
├── sectors: int
├── rows: int
├── seats_per_row: int
└── seats: list[list[list[Seat]]]

Theater (main orchestrator)
├── name: str
├── staff_manager: StaffManager
├── performance_manager: PerformanceManager
├── ticket_manager: TicketManager
└── resource_manager: ResourceManager
```

### Managers

- **StaffManager**: управление персоналом (актёры, режиссёры, дизайнеры)
- **HallManager**: управление залами
- **PerformanceManager**: управление спектаклями и репетициями
- **TicketManager**: управление билетами и продажами
- **ResourceManager**: управление сценой, костюмами и залами

### Exception System (4 основных класса)

```python
TheaterException          # Базовое исключение
├── InvalidSeatException  # Ошибка при работе с местами
├── TicketNotFoundException # Билет не найден
└── InvalidDateException   # Неверная дата
```

## Формат сохранения состояния

Состояние театра сохраняется в JSON формате (`data/theater_state.json`):

```json
{
  "name": "Городской театр",
  "staff_manager": {
    "staff": [
      {"type": "Actor", "id": 1, "name": "Иван Петров", "age": 30, "salary": 50000, "role": "Принц", "assigned_costume": null}
    ]
  },
  "performance_manager": {...},
  "ticket_manager": {...},
  "resource_manager": {...}
}
```

## Разработка

### Добавление новой функции

1. Реализуйте функцию в соответствующем модуле (`src/`)
2. Добавьте тесты в `tests/test_theater.py`
3. Убедитесь, что все тесты проходят: `pytest tests/test_theater.py -v`
4. Проверьте покрытие: `pytest tests/test_theater.py --cov=src --cov-report=term-missing`

### Стиль кода

- Используйте type hints (аннотации типов)
- Документируйте публичные методы с docstrings
- Следуйте PEP 8
- Максимальная длина строки: 100 символов

## История версий

### v1.0.0 (Current)
- **4 класса исключений** (уменьшено с 16+)
- **18 интеграционных тестов** - все проходят успешно
- **55% общее покрытие кода**:
  - 100% exceptions.py
  - 93% managers.py
  - 92% staff.py
  - 80% theater.py
  - 0% main.py (CLI тестируется вручную)
- **Полная система управления театром** с 15 командами CLI
- **Профессиональная структура проекта** (src/, tests/, data/, docs/)
- **Умное управление путями** для кроссдиректориального запуска
- Готово к использованию в production

## Авторы

Theater Development Team

## Лицензия

MIT
