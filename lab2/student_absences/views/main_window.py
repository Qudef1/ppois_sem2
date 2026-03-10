# views/main_window.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QMenuBar, QToolBar, QStatusBar, QTreeWidget, QTreeWidgetItem, QSplitter
from PyQt6.QtCore import Qt
from ..widgets.pagination_window import PaginationWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Учет пропусков студентов")
        self.setGeometry(100, 100, 1200, 700)
        self.current_view = "table"  # "table" или "tree"
        self.init_ui()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Контейнер для переключения видов
        self.view_container = QWidget()
        self.view_layout = QVBoxLayout(self.view_container)
        self.view_layout.setContentsMargins(0, 0, 0, 0)
        
        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ФИО", "Группа", "По болезни", "По др. причинам", 
            "Без уважит. причины", "Итого"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        
        # Дерево (скрыто по умолчанию)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Поле", "Значение"])
        self.tree.hide()
        
        self.view_layout.addWidget(self.table)
        self.view_layout.addWidget(self.tree)
        
        layout.addWidget(self.view_container)
        
        # Пагинация
        self.pagination = PaginationWidget()
        layout.addWidget(self.pagination)
        
        self.create_menu()
        self.create_toolbar()
        
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Готово")
    
    def create_menu(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("Файл")
        file_menu.addAction("Загрузить из XML...").triggered.connect(lambda: self.on_action("load_xml"))
        file_menu.addAction("Сохранить в XML...").triggered.connect(lambda: self.on_action("save_xml"))
        file_menu.addSeparator()
        file_menu.addAction("Выход").triggered.connect(lambda: self.on_action("exit"))
        
        ops_menu = menubar.addMenu("Операции")
        ops_menu.addAction("Добавить запись...").triggered.connect(lambda: self.on_action("add"))
        ops_menu.addAction("Поиск записей...").triggered.connect(lambda: self.on_action("search"))
        ops_menu.addAction("Удалить записи...").triggered.connect(lambda: self.on_action("delete"))
        
        view_menu = menubar.addMenu("Вид")
        view_menu.addAction("Показать как таблицу").triggered.connect(lambda: self.on_action("view_table"))
        view_menu.addAction("Показать как дерево").triggered.connect(lambda: self.on_action("view_tree"))
    
    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        toolbar.addAction("➕ Добавить").triggered.connect(lambda: self.on_action("add"))
        toolbar.addAction("🔍 Поиск").triggered.connect(lambda: self.on_action("search"))
        toolbar.addAction("🗑️ Удалить").triggered.connect(lambda: self.on_action("delete"))
        toolbar.addSeparator()
        toolbar.addAction("📥 Загрузить XML").triggered.connect(lambda: self.on_action("load_xml"))
        toolbar.addAction("📤 Сохранить XML").triggered.connect(lambda: self.on_action("save_xml"))
    
    def on_action(self, action_name):
        # Контроллер будет обрабатывать через сигнал
        pass
    
    def set_table_data(self, records):
        self.table.setRowCount(len(records))
        for row, record in enumerate(records):
            self.table.setItem(row, 0, QTableWidgetItem(record.full_name))
            self.table.setItem(row, 1, QTableWidgetItem(record.group))
            self.table.setItem(row, 2, QTableWidgetItem(str(record.absences_illness)))
            self.table.setItem(row, 3, QTableWidgetItem(str(record.absences_other)))
            self.table.setItem(row, 4, QTableWidgetItem(str(record.absences_unexcused)))
            self.table.setItem(row, 5, QTableWidgetItem(str(record.total_absences)))
    
    def set_tree_data(self, records):
        self.tree.clear()
        for record in records:
            item = QTreeWidgetItem(self.tree)
            item.setText(0, f"Студент #{record.id}: {record.full_name}")
            
            QTreeWidgetItem(item, ["ФИО", record.full_name])
            QTreeWidgetItem(item, ["Группа", record.group])
            QTreeWidgetItem(item, ["По болезни", str(record.absences_illness)])
            QTreeWidgetItem(item, ["По другим причинам", str(record.absences_other)])
            QTreeWidgetItem(item, ["Без уважительной причины", str(record.absences_unexcused)])
            QTreeWidgetItem(item, ["Итого", str(record.total_absences)])
            
            item.setExpanded(True)
    
    def switch_to_table(self):
        self.table.show()
        self.tree.hide()
        self.current_view = "table"
    
    def switch_to_tree(self):
        self.tree.show()
        self.table.hide()
        self.current_view = "tree"