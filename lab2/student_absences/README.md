# Учет пропусков студентов — Полная документация

Desktop-приложение для учёта пропусков занятий студентами с архитектурой **MVC (Model-View-Controller)**.

---

## 📋 Оглавление

1. [О проекте](#о-проекте)
2. [Стек технологий](#стек-технологий)
3. [Структура проекта](#структура-проекта)
4. [Архитектура MVC](#архитектура-mvc)
5. [Pipeline работы данных](#pipeline-работы-данных)
6. [Установка и запуск](#установка-и-запуск)
7. [Функционал](#функционал)
8. [Модель данных](#модель-данных)
9. [API компонентов](#api-компонентов)

---

## 📖 О проекте

Приложение предназначено для лабораторной работы по курсу "Проектирование ПО интеллектуальных систем".

**Назначение:**
- Учёт студентов и их пропусков занятий
- Добавление, редактирование, удаление записей
- Поиск по различным критериям
- Экспорт/импорт данных в XML
- Пагинация записей
- Отображение в виде таблицы или дерева

---

## 🛠 Стек технологий

| Компонент | Технология | Версия |
|-----------|------------|--------|
| **Язык программирования** | Python | 3.10+ |
| **GUI фреймворк** | PyQt5 | 5.15+ |
| **База данных** | SQLite3 | встроенная |
| **XML парсинг** | xml.sax / xml.dom.minidom | встроенные |
| **Модели данных** | dataclasses | встроенные |
| **ОС** | Linux | любая |

### Зависимости

```
PyQt5>=5.15.0
```

---

## 📁 Структура проекта

```
lab2/student_absences/
├── main.py                     # Точка входа
├── requirements.txt            # Зависимости
├── README.md                   # Документация
│
├── controllers/
│   ├── __init__.py
│   └── main_controller.py      # Контроллер (MVC)
│
├── models/
│   ├── __init__.py
│   ├── config.py               # Конфигурация и константы
│   ├── record.py               # Модель записи (dataclass)
│   ├── criteria.py             # Критерии поиска (dataclass)
│   ├── database.py             # Работа с SQLite
│   ├── xml_handler.py          # XML (SAX для чтения, DOM для записи)
│   └── generate_data.py        # Генератор тестовых данных
│
├── views/
│   ├── __init__.py
│   ├── main_window.py          # Главное окно
│   └── dialogs/
│       ├── __init__.py
│       ├── input_dialog.py     # Диалог добавления/редактирования
│       ├── search_dialog.py    # Диалог поиска
│       └── delete_dialog.py    # Диалог удаления
│
├── widgets/
│   ├── __init__.py
│   └── pagination_window.py    # Виджет пагинации
│
└── resources/
    └── data/                   # Данные (создаётся автоматически)
        ├── students.db         # SQLite база данных
        └── students.xml        # XML файл
```

---

## 🏗 Архитектура MVC

```
┌─────────────────────────────────────────────────────────────────┐
│                         VIEW (Представление)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ MainWindow   │  │ InputDialog  │  │ SearchDialog         │  │
│  │ + Table      │  │ + Форма      │  │ + Условия + Таблица  │  │
│  │ + Tree       │  │ + Валидация  │  │ + Пагинация          │  │
│  │ + Pagination │  │              │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────┐                                              │
│  │ DeleteDialog │                                              │
│  │ + Условия    │                                              │
│  └──────────────┘                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
              Сигналы PyQt5 (pyqtSignal, slots)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CONTROLLER (Контроллер)                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ MainController                                              │ │
│  │ • on_menu_action() — обработка действий меню               │ │
│  │ • load_data() — загрузка данных в View                     │ │
│  │ • add_record() — добавление записи                         │ │
│  │ • search_records() — поиск                                 │ │
│  │ • delete_records() — удаление                               │ │
│  │ • save_xml() / load_xml() — работа с XML                   │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       MODEL (Модель)                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ StudentRecord│  │ Database     │  │ XML Handler          │  │
│  │ • validate() │  │ • CRUD       │  │ • SAX (чтение)       │  │
│  │ • to_dict()  │  │ • search()   │  │ • DOM (запись)       │  │
│  │ • from_dict()│  │ • pagination │  │ • minidom / xml.sax  │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────┐                                              │
│  │ SearchCriteria│                                             │
│  │ • is_valid() │                                              │
│  └──────────────┘                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
      ┌──────────────┐              ┌──────────────┐
      │ SQLite (БД)  │              │ XML (файл)   │
      └──────────────┘              └──────────────┘
```

---

## 🔄 Pipeline работы данных

### 1. Запуск приложения

```
main.py → MainController() → Database.init_db() → MainWindow.show()
```

### 2. Загрузка данных (пагинация)

```
User открывает приложение
    ↓
MainController.load_data()
    ↓
Database.get_all_paged(page=1, page_size=10)
    ↓
SQL: SELECT * FROM students ORDER BY id LIMIT 10 OFFSET 0
    ↓
[StudentRecord, StudentRecord, ...]
    ↓
MainWindow.set_table_data(records)
    ↓
QTableWidget обновляется
```

### 3. Добавление записи

```
User → Menu "Операции" → "Добавить запись"
    ↓
InputDialog.show()
    ↓
User вводит данные → нажимает "Сохранить"
    ↓
InputDialog.on_save()
    ↓
StudentRecord.validate() → (True, None)
    ↓
MainController.add_record()
    ↓
Database.create(record)
    ↓
SQL: INSERT INTO students (full_name, group_number, ...) VALUES (?, ?, ...)
    ↓
MainController.load_data() → обновление таблицы
```

### 4. Поиск записей

```
User → Menu "Операции" → "Поиск записей"
    ↓
SearchDialog.show()
    ↓
User вводит условия (группа, фамилия, диапазон)
    ↓
User нажимает "Найти"
    ↓
SearchDialog.get_criteria() → SearchCriteria
    ↓
MainController.perform_search(dialog)
    ↓
Database.search_paged(criteria, page=1, page_size=10)
    ↓
SQL: SELECT * FROM students WHERE group_number = ? OR full_name LIKE ? ...
    ↓
[StudentRecord, ...], total_count
    ↓
SearchDialog.set_search_results(records, total)
    ↓
QTableWidget в диалоге обновляется
```

### 5. Удаление записей

```
User → Menu "Операции" → "Удалить записи"
    ↓
DeleteDialog.show()
    ↓
User вводит условия → нажимает "Удалить"
    ↓
DeleteDialog.get_criteria() → SearchCriteria
    ↓
MainController.delete_records()
    ↓
Database.delete_by_criteria(criteria)
    ↓
SQL: DELETE FROM students WHERE group_number = ? OR full_name LIKE ?
    ↓
count = cursor.rowcount
    ↓
DeleteDialog.show_result(count)
    ↓
MainController.load_data() → обновление таблицы
```

### 6. Сохранение в XML (DOM)

```
User → Menu "Файл" → "Сохранить в XML"
    ↓
MainController.save_xml()
    ↓
Database.get_all() → [StudentRecord, ...]
    ↓
XMLWriter.write(records, filepath)
    ↓
xml.dom.minidom.Document()
    ↓
<students>
  <student id="1">
    <full_name type="string">Иванов Иван Иванович</full_name>
    <group type="string">ПИ-201</group>
    <absences_illness type="int">5</absences_illness>
    ...
  </student>
</students>
```

### 7. Загрузка из XML (SAX)

```
User → Menu "Файл" → "Загрузить из XML"
    ↓
MainController.load_xml()
    ↓
XMLReader.read(filepath)
    ↓
xml.sax.make_parser() → setContentHandler(XMLReader)
    ↓
parser.parse(filepath)
    ↓
startElement('student', attrs) → current_record = {'id': 1}
    ↓
startElement('full_name') → current_field = 'full_name'
    ↓
characters("Иванов Иван Иванович") → current_data += ...
    ↓
endElement('full_name') → current_record['full_name'] = "Иванов..."
    ↓
endElement('student') → StudentRecord.from_dict(current_record)
    ↓
Database.clear_all() → DELETE FROM students
    ↓
Database.create(record) для каждой записи
```

---

## 🚀 Установка и запуск

### Требования

- Python 3.10+
- PyQt5

### Установка

```bash
# Перейдите в директорию проекта
cd lab2/student_absences

# Установите зависимости
pip install -r requirements.txt

# Или вручную
pip install PyQt5
```

### Запуск

```bash
# Запуск приложения
python main.py

# Генерация тестовых данных (50 записей)
python models/generate_data.py
```

---

## 📊 Функционал

### Главное окно

| Элемент | Описание |
|---------|----------|
| **Таблица** | Отображение записей (ФИО, Группа, Пропуски) |
| **Дерево** | Иерархическое представление записей |
| **Пагинация** | First, Prev, Next, Last, размер страницы |
| **Меню** | Файл, Операции, Вид |
| **Toolbar** | Быстрый доступ к операциям |

### Операции

| Операция | Описание |
|----------|----------|
| **Добавить** | Диалог с формой ввода и валидацией |
| **Поиск** | 3 вкладки: группа/фамилия, вид пропуска, диапазон |
| **Удалить** | Удаление по условию (группа, фамилия) |
| **Сохранить XML** | Экспорт всех записей в XML (DOM) |
| **Загрузить XML** | Импорт записей из XML (SAX) |

---

## 📈 Модель данных

### StudentRecord

```python
@dataclass
class StudentRecord:
    id: int = 0
    full_name: str = ""          # Мин. 2 слова
    group: str = ""              # Мин. 4 символа
    absences_illness: int = 0    # 0-999
    absences_other: int = 0      # 0-999
    absences_unexcused: int = 0  # 0-999
    
    @property
    def total_absences(self) -> int: ...
    
    def validate(self) -> tuple[bool, Optional[str]]: ...
```

### SearchCriteria

```python
@dataclass
class SearchCriteria:
    group: Optional[str] = None
    surname: Optional[str] = None
    absence_type: Optional[Literal['illness', 'other', 'unexcused']] = None
    min_absences: Optional[int] = None
    max_absences: Optional[int] = None
    
    def is_valid(self) -> bool: ...
```

---

## 🔌 API компонентов

### Database

| Метод | Описание |
|-------|----------|
| `create(record)` | Добавить запись |
| `get_all_paged(page, page_size)` | Получить страницу записей |
| `search_paged(criteria, page, page_size)` | Поиск с пагинацией |
| `delete_by_criteria(criteria)` | Удаление по условию |
| `clear_all()` | Очистить все записи |
| `get_all()` | Получить все записи |

### XMLWriter

| Метод | Описание |
|-------|----------|
| `write(records, filepath)` | Записать записи в XML (DOM) |

### XMLReader

| Метод | Описание |
|-------|----------|
| `read(filepath)` | Прочитать записи из XML (SAX) |

---

## 📝 Примечания

- Все строки интерфейса на **русском языке**
- Валидация данных на уровне модели
- Обработка ошибок через try-except
- Пагинация на уровне БД (LIMIT/OFFSET)
- SAX эффективен для больших XML файлов
- DOM удобен для записи структурированного XML

---

**Версия:** 1.0  
**Курс:** Проектирование ПО интеллектуальных систем  
**Лабораторная работа №2**
