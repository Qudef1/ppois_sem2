from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QMenuBar, QToolBar, QStatusBar
from .widgets.pagination_window import PaginationWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Учет пропусков студентов")
        self.setGeometry(100, 100, 1200, 700)
        self.init_ui()

    def init_ui(self):
        """Инициализация UI главного окна."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ФИО", "Группа", "По болезни", "По др. причинам",
            "Без уважит. причины", "Итого"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table)

        # Пагинация
        self.pagination = PaginationWidget()
        layout.addWidget(self.pagination)

        self.create_menu()
        self.create_toolbar()

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Готово")

    def create_menu(self):
        """Создание меню приложения."""
        menubar = self.menuBar()

        # Меню Файл
        file_menu = menubar.addMenu("Файл")
        file_menu.addAction("Загрузить из XML...").triggered.connect(lambda: self.on_action("load_xml"))
        file_menu.addAction("Сохранить в XML...").triggered.connect(lambda: self.on_action("save_xml"))
        file_menu.addSeparator()
        file_menu.addAction("Выход").triggered.connect(lambda: self.on_action("exit"))

        # Меню Операции
        ops_menu = menubar.addMenu("Операции")
        ops_menu.addAction("Добавить запись...").triggered.connect(lambda: self.on_action("add"))
        ops_menu.addAction("Поиск записей...").triggered.connect(lambda: self.on_action("search"))
        ops_menu.addAction("Удалить записи...").triggered.connect(lambda: self.on_action("delete"))
        ops_menu.addSeparator()
        ops_menu.addAction("Группы и студенты...").triggered.connect(lambda: self.on_action("groups"))

    def create_toolbar(self):
        """Создание панели инструментов."""
        toolbar = QToolBar("Основная")
        self.addToolBar(toolbar)

        toolbar.addAction("Добавить").triggered.connect(lambda: self.on_action("add"))
        toolbar.addAction("Поиск").triggered.connect(lambda: self.on_action("search"))
        toolbar.addAction("Удалить").triggered.connect(lambda: self.on_action("delete"))
        toolbar.addSeparator()
        toolbar.addAction("Группы").triggered.connect(lambda: self.on_action("groups"))

    def on_action(self, action_name):
        """
        Обработчик действий меню.
        
        Args:
            action_name: Имя действия.
        """
        pass  # Контроллер подключается через сигнал

    def set_table_data(self, records):
        """
        Установить данные в таблицу.
        
        Args:
            records: Список записей StudentRecord.
        """
        self.table.setRowCount(len(records))
        for row, record in enumerate(records):
            self.table.setItem(row, 0, QTableWidgetItem(record.full_name))
            self.table.setItem(row, 1, QTableWidgetItem(record.group))
            self.table.setItem(row, 2, QTableWidgetItem(str(record.absences_illness)))
            self.table.setItem(row, 3, QTableWidgetItem(str(record.absences_other)))
            self.table.setItem(row, 4, QTableWidgetItem(str(record.absences_unexcused)))
            self.table.setItem(row, 5, QTableWidgetItem(str(record.total_absences)))
