# Лабораторная работа: Система управления театром

## Предметная область
Организация и проведение театральных представлений.

## Основные сущности
| Класс | Описание |
|-------|----------|
| `Theater` | Главный класс, координирующий все компоненты |
| `Actor`, `Director` | Сотрудники театра |
| `Setting` | Театральная постановка (спектакль) |
| `Repetition` | Репетиция постановки |
| `AuditoryHall` | Зрительный зал с местами |
| `Ticket` | Билет на постановку |
| `Stage`, `Costume`, `CostumeRoom` | Ресурсы театра |

## Операции
- Организация репетиций
- Создание и назначение костюмов
- Продажа билетов (по секторам/рядам/местам)
- Проведение спектаклей
- Сохранение/загрузка состояния (JSON)

## Структура проекта
```
lab1/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI роуты
│   │   ├── theater_service.py # Application service (общая модель + use-cases)
│   │   ├── templates/       # HTML шаблоны
│   │   └── static/          # CSS/JS
│   └── README.md            # Документация web-интерфейса
├── src/
│   ├── theater.py       # Класс Theater
│   ├── actions.py       # Setting, Repetition
│   ├── seats.py         # Seat, Ticket
│   ├── halls.py         # AuditoryHall
│   ├── resources.py     # Stage, Costume, CostumeRoom
│   ├── staff.py         # Person, Staff, Actor, Director
│   ├── managers.py      # Менеджеры коллекций
│   ├── exception.py     # Исключения
│   └── main_menu.py     # CLI-интерфейс
├── tests/
│   └──test_theater.py
└── docs/
    ├── class_diagram.puml
    └── state_diagram.puml
```

## Запуск
```bash
cd lab1/src
python3 main_menu.py
```

## Тесты
```bash
cd lab1
python3 -m unittest discover tests -v
```

## Web-интерфейс (л/р №4)
```bash
cd lab1/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Подробнее: `lab1/backend/README.md`

## Сериализация
- Все классы имеют методы `to_dict()` и `from_dict()`
- Состояние сохраняется в JSON через `Theater.save_to_file()`
- При загрузке автоматически восстанавливаются связи между объектами

## Авторы
Студент группы [группа]
