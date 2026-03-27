# Учет пропусков студентов — Полная документация

**MVC-приложение** для учёта пропусков занятий студентами.



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

