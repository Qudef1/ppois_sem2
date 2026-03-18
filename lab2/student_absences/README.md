# Учет пропусков студентов — Полная документация

**MVC-приложение** для учёта пропусков занятий студентами.

---

## ✅ Соответствие требованиям лабораторной работы

| № | Требование | Реализация | Файл |
|---|------------|------------|------|
| 1 | **MVC архитектура** | Model (`models/`), View (`views/`), Controller (`controllers/`) | Все |
| 2 | **Ввод записей через диалог** | `InputDialog` с формой и валидацией | `views/dialogs/input_dialog.py` |
| 3 | **Поиск в отдельном диалоге** | `SearchDialog` с 3 вкладками условий | `views/dialogs/search_dialog.py` |
| 4 | **Результат поиска в том же диалоге** | `QTableWidget` + `PaginationWidget` внутри диалога | `views/dialogs/search_dialog.py` |
| 5 | **Удаление в отдельном диалоге** | `DeleteDialog` (не в диалоге поиска) | `views/dialogs/delete_dialog.py` |
| 6 | **Сообщение о результате удаления** | `show_result(count)` — показывает сколько удалено | `views/dialogs/delete_dialog.py` |
| 7 | **Отображение массива в главном окне** | `QTableWidget` в `MainWindow` | `views/main_window.py` |
| 8 | **Хранение в БД** | SQLite (`students.db`) | `models/database.py` |
| 9 | **Дерево (лист = поле записи)** | `QTreeWidget` — запись → поля | `views/main_window.py` |
| 10 | **Сохранение/загрузка (файл + БД)** | `QFileDialog` + XML/SQLite | `controllers/main_controller.py` |
| 11 | **XML: DOM для записи, SAX для чтения** | `xml.dom.minidom` / `xml.sax` | `models/xml_handler.py` |
| 12 | **Правильные типы данных** | `INTEGER` для пропусков, `TEXT` для ФИО | `models/database.py` |
| 13 | **Пагинация (10 записей)** | `PaginationWidget` | `widgets/pagination_window.py` |
| 14 | **Первая/последняя/пред./след. страница** | 4 кнопки навигации | `widgets/pagination_window.py` |
| 15 | **Изменение размера страницы** | `QSpinBox` (5-100) | `widgets/pagination_window.py` |
| 16 | **Номер страницы / всего страниц** | `lbl_page_info` | `widgets/pagination_window.py` |
| 17 | **Всего записей** | `lbl_total` | `widgets/pagination_window.py` |
| 18 | **Условия поиска (3 варианта)** | Все 3 вкладки реализованы | `views/dialogs/search_dialog.py` |

---

## 📁 Структура проекта (MVC)

```
lab2/student_absences/
├── main.py                     # ТОЧКА ВХОДА
│
├── controllers/                # CONTROLLER (MVC)
│   └── main_controller.py      # MainController — связывает Model и View
│
├── models/                     # MODEL (MVC)
│   ├── config.py               # Константы и настройки
│   ├── record.py               # StudentRecord — модель данных
│   ├── criteria.py             # SearchCriteria — критерии поиска
│   ├── database.py             # Database — работа с SQLite
│   ├── xml_handler.py          # XMLWriter (DOM), XMLReader (SAX)
│   └── generate_data.py        # Генератор тестовых данных
│
├── views/                      # VIEW (MVC)
│   ├── main_window.py          # MainWindow — главное окно
│   └── dialogs/
│       ├── input_dialog.py     # InputDialog — ввод/редактирование
│       ├── search_dialog.py    # SearchDialog — поиск
│       └── delete_dialog.py    # DeleteDialog — удаление
│
├── widgets/                    # Виджеты
│   └── pagination_window.py    # PaginationWidget — пагинация
│
└── resources/
    └── data/
        ├── students.db         # SQLite база данных
        └── students.xml        # XML файл
```

---

## 🏗 Архитектура MVC

### Где что находится:

```
┌─────────────────────────────────────────────────────────────────┐
│ VIEW (Представление) — папка views/                             │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│ │ MainWindow   │  │ InputDialog  │  │ SearchDialog         │   │
│ │ main_window. │  │ input_dialog.│  │ search_dialog.py     │   │
│ │ py           │  │ py           │  │                      │   │
│ └──────────────┘  └──────────────┘  └──────────────────────┘   │
│ ┌──────────────┐  ┌──────────────┐                             │
│ │ DeleteDialog │  │ Pagination   │                             │
│ │ delete_dialog│  │ pagination_  │                             │
│ │ .py          │  │ window.py    │                             │
│ └──────────────┘  └──────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
                              │
              Сигналы PyQt6 (pyqtSignal, slots)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ CONTROLLER (Контроллер) — controllers/                          │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ main_controller.py — MainController                          │ │
│ │ • on_menu_action() — обработка меню                          │ │
│ │ • load_data() — загрузка данных                              │ │
│ │ • add_record() — добавление                                  │ │
│ │ • search_records() — поиск                                   │ │
│ │ • delete_records() — удаление                                │ │
│ │ • save_xml() / load_xml() — XML                              │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ MODEL (Модель) — models/                                        │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│ │ StudentRecord│  │ Database     │  │ XML Handler          │   │
│ │ record.py    │  │ database.py  │  │ xml_handler.py       │   │
│ └──────────────┘  └──────────────┘  └──────────────────────┘   │
│ ┌──────────────┐  ┌──────────────┐                             │
│ │ SearchCriteria│ │ Config       │                             │
│ │ criteria.py  │ │ config.py    │                             │
│ └──────────────┘  └──────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Как работает каждый файл

### **main.py** — Точка входа

```python
controller = MainController()  # Создаёт контроллер
controller.run()               # Запускает приложение
```

**Что делает:**
1. Создаёт экземпляр `MainController`
2. Вызывает `run()`, который показывает главное окно
3. Запускает главный цикл событий PyQt6 (`app.exec()`)

---

### **controllers/main_controller.py** — КОНТРОЛЛЕР

**Класс `MainController`** — связующее звено между Model и View.

#### Методы контроллера:

| Метод | Что делает |
|-------|------------|
| `__init__()` | Создаёт `QApplication`, `Database`, `MainWindow`, подключает сигналы |
| `connect_signals()` | Подключает сигналы пагинации к слотам |
| `on_menu_action(action_name)` | Обрабатывает действия меню (add, search, delete, save_xml, load_xml) |
| `load_data()` | Загружает данные из БД и отображает в View (таблица или дерево) |
| `on_page_changed(page)` | Обработка смены страницы → перезагружает данные |
| `on_page_size_changed(size)` | Обработка изменения размера страницы → сброс на страницу 1 |
| `add_record()` | Открывает `InputDialog` → создаёт запись в БД → обновляет View |
| `search_records()` | Открывает `SearchDialog` → подключает обработчик поиска |
| `perform_search(dialog)` | Получает критерии → ищет в БД → показывает результаты в диалоге |
| `delete_records()` | Открывает `DeleteDialog` → удаляет по условию → показывает результат |
| `save_xml()` | Диалог сохранения → экспортирует все записи в XML (DOM) |
| `load_xml()` | Диалог загрузки → импортирует из XML (SAX) → обновляет БД |
| `run()` | Показывает окно → запускает цикл событий |

**Как работает контроллер:**
```
1. Пользователь нажимает кнопку в View
   ↓
2. View отправляет сигнал (или вызывает callback)
   ↓
3. Контроллер получает сигнал → вызывает метод Model
   ↓
4. Model выполняет операцию (БД/XML)
   ↓
5. Контроллер получает результат → обновляет View
```

---

### **models/record.py** — Модель данных

**Класс `StudentRecord`** (dataclass):

```python
@dataclass
class StudentRecord:
    id: int = 0
    full_name: str = ""          # ФИО студента
    group: str = ""              # Группа
    absences_illness: int = 0    # Пропуски по болезни
    absences_other: int = 0      # Пропуски по другим причинам
    absences_unexcused: int = 0  # Пропуски без уважительной причины
```

| Метод/Свойство | Что делает |
|----------------|------------|
| `__post_init__()` | Автоматическая очистка: `full_name.title()`, `group.upper()` |
| `total_absences` (property) | Возвращает сумму всех пропусков |
| `surname` (property) | Возвращает фамилию (первое слово ФИО) |
| `validate()` | Проверяет корректность данных → `(True, None)` или `(False, "ошибка")` |
| `to_dict()` | Преобразует в словарь |
| `from_dict()` | Создаёт из словаря |

---

### **models/criteria.py** — Критерии поиска

**Класс `SearchCriteria`** (dataclass):

```python
@dataclass
class SearchCriteria:
    group: Optional[str] = None           # Номер группы
    surname: Optional[str] = None         # Фамилия
    absence_type: Optional[str] = None    # 'illness', 'other', 'unexcused'
    min_absences: Optional[int] = None    # Мин. количество
    max_absences: Optional[int] = None    # Макс. количество
```

| Метод | Что делает |
|-------|------------|
| `__post_init__()` | Очищает пробелы в `group` и `surname` |
| `is_valid()` | Проверяет: заполнено ли хотя бы одно условие |
| `to_dict()` | Возвращает словарь без `None` значений |

---

### **models/config.py** — Конфигурация

**Что хранит:**
- `DATABASE_PATH` — путь к SQLite БД
- `XML_DEFAULT_PATH` — путь к XML файлу
- `PAGE_SIZE_DEFAULT` — размер страницы по умолчанию (10)
- `FIELDS` — схема полей для БД

---

### **models/database.py** — Работа с SQLite

**Класс `Database`**:

| Метод | Что делает | SQL запрос |
|-------|------------|------------|
| `__init__(db_path)` | Создаёт директорию, инициализирует БД | — |
| `get_connection()` | Возвращает подключение к SQLite | — |
| `init_db()` | Создаёт таблицу `students` если нет | `CREATE TABLE IF NOT EXISTS...` |
| `create(record)` | Добавляет запись | `INSERT INTO students... VALUES (?, ?, ...)` |
| `get_all_paged(page, page_size)` | Получает страницу записей | `SELECT... LIMIT ? OFFSET ?` |
| `search_paged(criteria, page, page_size)` | Поиск с пагинацией | `SELECT... WHERE... LIMIT ? OFFSET ?` |
| `delete_by_criteria(criteria)` | Удаление по условию | `DELETE FROM students WHERE...` |
| `clear_all()` | Очищает все записи | `DELETE FROM students` |
| `get_all()` | Получает все записи | `SELECT... ORDER BY id` |

**Как работает пагинация:**
```python
offset = (page - 1) * page_size
# Страница 1, размер 10 → OFFSET 0
# Страница 2, размер 10 → OFFSET 10
# Страница 3, размер 10 → OFFSET 20
```

---

### **models/xml_handler.py** — XML парсеры

#### **XMLWriter** (DOM — для записи)

| Метод | Что делает |
|-------|------------|
| `write(records, filepath)` | Создаёт XML документ через `minidom` |

**Формат XML:**
```xml
<?xml version="1.0" ?>
<students>
  <student id="1">
    <full_name type="string">Иванов Иван Иванович</full_name>
    <group type="string">ПИ-201</group>
    <absences_illness type="int">5</absences_illness>
    <absences_other type="int">3</absences_other>
    <absences_unexcused type="int">1</absences_unexcused>
  </student>
</students>
```

#### **XMLReader** (SAX — для чтения)

| Метод | Что делает |
|-------|------------|
| `read(filepath)` | Парсит XML файл через SAX |

**Как работает SAX:**
```
1. startElement('student', attrs) → создаёт current_record = {'id': 1}
2. startElement('full_name') → запоминает текущее поле
3. characters("Иванов...") → накапливает текст
4. endElement('full_name') → сохраняет в current_record['full_name']
5. endElement('student') → создаёт StudentRecord, добавляет в список
```

---

### **models/generate_data.py** — Генератор данных

**Функция `generate_test_data(num_records=50)`**:
- Генерирует случайные ФИО (фамилия + имя + отчество)
- Случайная группа из списка
- Случайные пропуски (0-15, 0-10, 0-5)
- Сохраняет в БД

---

### **views/main_window.py** — Главное окно (VIEW)

**Класс `MainWindow`** (наследник `QMainWindow`):

| Метод | Что делает |
|-------|------------|
| `__init__()` | Создаёт окно 1200x700, инициализирует UI |
| `init_ui()` | Создаёт таблицу, дерево, пагинацию, меню, toolbar |
| `create_menu()` | Меню: Файл, Операции, Вид |
| `create_toolbar()` | Панель с кнопками |
| `set_table_data(records)` | Заполняет `QTableWidget` записями |
| `set_tree_data(records)` | Заполняет `QTreeWidget` (запись → поля) |
| `switch_to_table()` | Показывает таблицу, скрывает дерево |
| `switch_to_tree()` | Показывает дерево, скрывает таблицу |
| `on_action(action_name)` | Пустой обработчик (контроллер подключается) |

**Структура дерева:**
```
Записи
├── Студент #1: Иванов Иван Иванович
│   ├── ФИО: Иванов Иван Иванович
│   ├── Группа: ПИ-201
│   ├── По болезни: 5
│   ├── По другим причинам: 3
│   ├── Без уважительной причины: 1
│   └── Итого: 9
├── Студент #2: Петров...
```

---

### **views/dialogs/input_dialog.py** — Диалог ввода (VIEW)

**Класс `InputDialog`** (наследник `QDialog`):

| Метод | Что делает |
|-------|------------|
| `__init__(record)` | Если `record` есть — режим редактирования |
| `init_ui()` | Создаёт форму: ФИО, Группа, 3 счётчика пропусков |
| `update_total()` | Обновляет метку "Итого пропусков" |
| `on_save()` | Валидирует запись → `accept()` или показывает ошибку |
| `get_record()` | Возвращает `StudentRecord` из полей формы |

---

### **views/dialogs/search_dialog.py** — Диалог поиска (VIEW)

**Класс `SearchDialog`** (наследник `QDialog`):

| Метод | Что делает |
|-------|------------|
| `init_ui()` | Создаёт 3 вкладки с условиями + таблица результатов + пагинация |
| `on_search()` | Пустой обработчик (контроллер подключается через `btn_search.clicked`) |
| `set_search_results(records, total)` | Заполняет таблицу результатами |
| `get_criteria()` | Возвращает `SearchCriteria` на основе активной вкладки |

**Вкладки:**
1. **Группа или фамилия** — два текстовых поля
2. **Фамилия или вид пропуска** — фамилия + ComboBox (По болезни/По другим/Без уважит.)
3. **Фамилия или диапазон** — фамилия + тип + от/до

---

### **views/dialogs/delete_dialog.py** — Диалог удаления (VIEW)

**Класс `DeleteDialog`** (наследник `QDialog`):

| Метод | Что делает |
|-------|------------|
| `init_ui()` | Создаёт 3 вкладки (как в search_dialog) + предупреждение |
| `show_result(count)` | Показывает сообщение: "Удалено записей: X" или "Записи не найдены" |
| `get_criteria()` | Возвращает `SearchCriteria` для удаления |

---

### **widgets/pagination_window.py** — Пагинация (VIEW)

**Класс `PaginationWidget`** (наследник `QWidget`):

**Сигналы:**
- `page_changed(int)` — изменилась страница
- `page_size_changed(int)` — изменился размер страницы

| Метод | Что делает |
|-------|------------|
| `init_ui()` | Создаёт 4 кнопки, 2 метки, ComboBox |
| `update_info(current_page, page_size, total_records)` | Обновляет состояние: номер страницы, всего страниц, кнопки |
| `go_to_page(page)` | Переход на страницу → испускает `page_changed` |
| `prev_page()` | Предыдущая страница |
| `next_page()` | Следующая страница |
| `go_to_last_page()` | Последняя страница |
| `on_page_size_changed(value)` | Изменение размера → испускает `page_size_changed` |

**Элементы управления:**
```
[⏮ Первая] [◀ Пред.] [Страница 1 из 5] [След. ▶] [Послед. ⏭]
Записей на странице: [10 ▼]  Всего записей: 50
```

---

## 🔄 Полный pipeline работы программы

### 1. Запуск приложения

```
main.py
  ↓
MainController.__init__()
  ├─ QApplication([])
  ├─ Database() → init_db() → CREATE TABLE
  ├─ MainWindow()
  └─ connect_signals()
  ↓
MainController.load_data()
  ├─ Database.get_all_paged(page=1, page_size=10)
  │   └─ SELECT ... LIMIT 10 OFFSET 0
  └─ MainWindow.set_table_data(records)
  ↓
MainController.run()
  ├─ MainWindow.show()
  └─ app.exec() → главный цикл событий
```

### 2. Добавление записи

```
Пользователь: Меню "Операции" → "Добавить запись"
  ↓
MainController.on_menu_action("add")
  ↓
MainController.add_record()
  ├─ InputDialog(self.view)
  ├─ dialog.exec() → пользователь вводит данные
  ├─ InputDialog.on_save()
  │   └─ StudentRecord.validate()
  ├─ dialog.get_record() → StudentRecord
  ├─ Database.create(record)
  │   └─ INSERT INTO students (full_name, group_number, ...) VALUES (?, ?, ...)
  ├─ MainController.load_data() → обновление таблицы
  └─ QMessageBox.information("Запись добавлена!")
```

### 3. Поиск записей

```
Пользователь: Меню "Операции" → "Поиск записей"
  ↓
MainController.on_menu_action("search")
  ↓
MainController.search_records()
  ├─ SearchDialog(self.view)
  ├─ dialog.btn_search.clicked.connect(perform_search)
  ├─ dialog.exec() → пользователь вводит условия
  │
  Пользователь нажимает "🔍 Найти"
  ↓
SearchDialog.on_search() (пустой)
  ↓
Контроллер (через сигнал btn_search.clicked):
  ↓
MainController.perform_search(dialog)
  ├─ dialog.get_criteria() → SearchCriteria
  ├─ criteria.is_valid() → проверка
  ├─ Database.search_paged(criteria, page=1, page_size=10)
  │   ├─ WHERE group_number = ? OR full_name LIKE ? OR ...
  │   └─ SELECT ... LIMIT 10 OFFSET 0
  ├─ dialog.set_search_results(records, total)
  │   └─ заполняет QTableWidget в диалоге
  └─ dialog.pagination.update_info(1, page_size, total)
```

### 4. Удаление записей

```
Пользователь: Меню "Операции" → "Удалить записи"
  ↓
MainController.on_menu_action("delete")
  ↓
MainController.delete_records()
  ├─ DeleteDialog(self.view)
  ├─ dialog.exec() → пользователь вводит условия
  ├─ dialog.get_criteria() → SearchCriteria
  ├─ criteria.is_valid() → проверка
  ├─ Database.delete_by_criteria(criteria)
  │   └─ DELETE FROM students WHERE group_number = ? OR full_name LIKE ?
  ├─ dialog.show_result(count) → QMessageBox
  └─ MainController.load_data() → обновление таблицы
```

### 5. Сохранение в XML (DOM)

```
Пользователь: Меню "Файл" → "Сохранить в XML..."
  ↓
MainController.on_menu_action("save_xml")
  ↓
MainController.save_xml()
  ├─ QFileDialog.getSaveFileName() → filepath
  ├─ Database.get_all() → [StudentRecord, ...]
  ├─ XMLWriter.write(records, filepath)
  │   ├─ minidom.Document()
  │   ├─ createElement('students')
  │   ├─ для каждой записи:
  │   │   ├─ createElement('student', id="1")
  │   │   └─ для каждого поля:
  │   │       ├─ createElement('field', name="full_name")
  │   │       └─ appendChild(textNode)
  │   └─ writexml(filepath)
  └─ QMessageBox.information("Данные сохранены")
```

### 6. Загрузка из XML (SAX)

```
Пользователь: Меню "Файл" → "Загрузить из XML..."
  ↓
MainController.on_menu_action("load_xml")
  ↓
MainController.load_xml()
  ├─ QFileDialog.getOpenFileName() → filepath
  ├─ XMLReader.read(filepath)
  │   ├─ xml.sax.make_parser()
  │   ├─ setContentHandler(XMLReader())
  │   ├─ parser.parse(filepath)
  │   │   ├─ startElement('student') → current_record = {'id': 1}
  │   │   ├─ characters(...) → current_data += ...
  │   │   └─ endElement('student') → StudentRecord.from_dict()
  │   └─ return [StudentRecord, ...]
  ├─ Database.clear_all() → DELETE FROM students
  ├─ для каждой записи: Database.create(record)
  ├─ MainController.load_data() → обновление таблицы
  └─ QMessageBox.information("Загружено N записей")
```

### 7. Пагинация

```
Пользователь нажимает "След. ▶"
  ↓
PaginationWidget.btn_next.clicked
  ↓
PaginationWidget.next_page()
  ├─ current_page += 1
  ├─ update_info() → обновляет метки
  └─ испускает сигнал page_changed(2)
  ↓
MainController.on_page_changed(2)
  ├─ current_page = 2
  └─ load_data()
      ├─ Database.get_all_paged(page=2, page_size=10)
      │   └─ SELECT ... LIMIT 10 OFFSET 10
      └─ MainWindow.set_table_data(records)
```

---

## 🚀 Запуск

```bash
cd lab2/student_absences

# Установка зависимостей
pip install -r requirements.txt   # PyQt6, pydantic

# Генерация тестовых данных (50 записей)
python models/generate_data.py

# Запуск приложения
python main.py
```

---

## 📊 Модель данных

**Таблица `students`:**

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | INTEGER PRIMARY KEY | Автоинкремент |
| `full_name` | TEXT NOT NULL | ФИО (мин. 2 слова) |
| `group_number` | TEXT NOT NULL | Номер группы |
| `absences_illness` | INTEGER DEFAULT 0 | По болезни (0-999) |
| `absences_other` | INTEGER DEFAULT 0 | По другим причинам (0-999) |
| `absences_unexcused` | INTEGER DEFAULT 0 | Без уважительной (0-999) |

**Индексы:**
- `idx_group` — для быстрого поиска по группе
- `idx_name` — для быстрого поиска по фамилии

---

**Версия:** 1.0  
**Курс:** Проектирование ПО интеллектуальных систем  
**Лабораторная работа №2**
