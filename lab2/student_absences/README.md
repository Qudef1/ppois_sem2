# Учёт пропусков студентов

**MVC-приложение** на PyQt6 для учёта, поиска и анализа пропусков студентов.
Поддержка SQLite, XML (SAX-чтение / DOM-запись), пагинации и двух режимов
отображения данных — таблица и дерево.

---

## 📁 Структура проекта

```
lab2/student_absences/
├── main.py                          # Точка входа
├── README.md                        # Документация
├── requirements.txt                 # Зависимости
│
├── controllers/                     # CONTROLLER
│   ├── __init__.py
│   └── main_controller.py           # MainController — связывает Model и View
│
├── models/                          # MODEL
│   ├── __init__.py
│   ├── config.py                    # Константы, SQL-запросы, пути
│   ├── record.py                    # StudentRecord — модель данных
│   ├── criteria.py                  # SearchCriteria — критерии поиска/удаления
│   ├── database.py                  # Database — работа с SQLite3
│   └── xml_handler.py               # XMLWriter (DOM), XMLReader (SAX)
│
├── views/                           # VIEW
│   ├── __init__.py
│   ├── main_window.py               # MainWindow — главное окно с таблицей
│   ├── dialogs/
│   │   ├── __init__.py              # Реэкспорт всех диалогов
│   │   ├── input_dialog.py          # Ввод / редактирование записи
│   │   ├── search_dialog.py         # Поиск (3 вкладки) + пагинация
│   │   ├── delete_dialog.py         # Удаление по критериям (3 вкладки)
│   │   ├── groups_dialog.py         # Просмотр групп и студентов
│   │   └── tree_view_dialog.py      # Отображение в виде дерева
│   └── widgets/
│       ├── __init__.py              # Реэкспорт PaginationWidget
│       └── pagination_window.py     # Виджет пагинации
│
└── resources/
    └── data/
        ├── students.db              # SQLite база данных
        └── students.xml             # XML файл
```

---

## 🏗 Архитектура MVC

```
┌─────────────────────────────────────────────────┐
│ VIEW (Представление) — views/                    │
│  MainWindow  InputDialog  SearchDialog           │
│  DeleteDialog  GroupsDialog  TreeViewDialog       │
│  PaginationWidget                                 │
└──────────────────────┬──────────────────────────┘
                       │ Сигналы PyQt6
                       ▼
┌─────────────────────────────────────────────────┐
│ CONTROLLER — controllers/main_controller.py      │
│  on_menu_action()  load_data()  add_record()     │
│  search_records()  delete_records()  show_tree() │
│  save_xml()  load_xml()                          │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│ MODEL — models/                                  │
│  StudentRecord  Database  SearchCriteria         │
│  XMLWriter / XMLReader  config                   │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Запуск

```bash
cd lab2/student_absences
python main.py
```

---

## 📋 Функциональность

### Главное окно

| Элемент | Описание |
|---|---|
| Таблица (6 колонок) | ФИО, Группа, По болезни, По др. причинам, Без уважит., Итого |
| Пагинация | Навигация ← →, выбор размера страницы (5–100) |
| Меню «Файл» | Загрузить XML, Сохранить XML, Выход |
| Меню «Операции» | Добавить, Поиск, Удалить, Группы, Дерево записей |
| Панель инструментов | Быстрые кнопки: Добавить, Поиск, Удалить, Группы, Дерево |

### Операции

#### Добавить запись
- Диалог с полями: ФИО, Группа, 3 счётчика пропусков
- Валидация: ФИО ≥ 2 слова, Группа ≥ 4 символа, пропуски 0–999
- Автоформатирование: ФИО → title case, Группа → strip
- Проверка дубликатов по `(full_name, group_number)`

#### Поиск записей
3 вкладки:
1. **Группа или фамилия** — точное совпадение группы / начало фамилии
2. **Пропуски и вид** — минимум пропусков по выбранному типу
3. **Фамилия + диапазон** — фамилия + интервал по конкретному виду

Результаты отображаются с **собственной пагинацией** внутри диалога.

#### Удаление записей
Аналогично поиску (3 вкладки), логика — **AND** между условиями.

#### Дерево записей (немодальное окно)
Отображение данных в котором каждая запись является листовым элементом.

#### XML
- **Экспорт** — DOM (`xml.dom.minidom`): `<students>` → `<student id="N">` → `<field type="...">`
- **Импорт** — SAX (`xml.sax`): парсинг → `clear_all()` → `create()` для каждой записи

---

## 🗃 Модель данных

### StudentRecord

| Поле | Тип | Описание |
|---|---|---|
| `id` | `int` | Первичный ключ (0 для новых) |
| `full_name` | `str` | ФИО (автоformat: `.strip().title()`) |
| `group` | `str` | Номер группы (автоformat: `.strip()`) |
| `absences_illness` | `int` | Пропуски по болезни |
| `absences_other` | `int` | Пропуски по другим причинам |
| `absences_unexcused` | `int` | Пропуски без уважительной причины |

**Свойства:**
- `total_absences` — сумма всех пропусков
- `surname` — первое слово из ФИО

**Валидация:** `validate() → (bool, str | None)`

### Уникальность

Уникальный индекс SQLite на `(full_name, group_number)`.
При попытке добавить дубликат `Database.create()` бросает `ValueError`,
контроллер выводит `QMessageBox.warning`.

---

## 🔄 Основные потоки данных

### Добавление записи
```
Меню «Добавить» → InputDialog → validate()
  → Database.create() → load_data() → обновление таблицы
```

### Поиск
```
Меню «Поиск» → SearchDialog → get_criteria()
  → Database.search() → set_search_results() → пагинация в диалоге
```

### Пагинация (главное окно)
```
Кнопка «След.» → page_changed(page)
  → Controller.on_page_changed() → db.get_all_paged()
  → MainWindow.set_table_data()
```

### Экспорт XML
```
Меню «Сохранить XML» → QFileDialog → db.get_all()
  → XMLWriter.write() → QMessageBox
```

---

## ⚙️ Конфигурация

Файл `models/config.py`:

| Константа | Значение |
|---|---|
| `PAGE_SIZE_DEFAULT` | `10` |
| `DATABASE_PATH` | `resources/data/students.db` |
| `XML_DEFAULT_PATH` | `resources/data/students.xml` |

---


## ⚠️ Известные проблемы

| Проблема | Файл | Описание |
|---|---|---|
| Ошибка в `groups_dialog.py` | `_display_students()` | Запись в колонку с индексом 5 при `setColumnCount(5)` (индексы 0–4) |
| `requirements.txt` | — | Указан `PyQt5`, код использует `PyQt6`; `pydantic` не используется |
| Отсутствуют тесты | — | Нет покрытия тестами |
