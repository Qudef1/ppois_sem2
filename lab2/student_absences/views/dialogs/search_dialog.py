# views/dialogs/search_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton, QTabWidget, QWidget, QFormLayout, QComboBox, QTableWidget, QTableWidgetItem, QGroupBox
from ...widgets.pagination_window import PaginationWidget
from ...models.criteria import SearchCriteria

class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Поиск записей")
        self.setModal(True)
        self.resize(900, 600)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        
        # Tab 1: Group or Surname
        tab1 = QWidget()
        tab1_layout = QFormLayout(tab1)
        self.search1_group = QLineEdit()
        self.search1_surname = QLineEdit()
        tab1_layout.addRow("Номер группы:", self.search1_group)
        tab1_layout.addRow("Фамилия студента:", self.search1_surname)
        self.tabs.addTab(tab1, "Группа или фамилия")
        
        # Tab 2: Surname or Absence Type
        tab2 = QWidget()
        tab2_layout = QFormLayout(tab2)
        self.search2_surname = QLineEdit()
        self.search2_type = QComboBox()
        self.search2_type.addItems(["По болезни", "По другим причинам", "Без уважительной причины"])
        tab2_layout.addRow("Фамилия студента:", self.search2_surname)
        tab2_layout.addRow("Вид пропуска:", self.search2_type)
        self.tabs.addTab(tab2, "Фамилия или вид пропуска")
        
        # Tab 3: Surname or Range
        tab3 = QWidget()
        tab3_layout = QFormLayout(tab3)
        self.search3_surname = QLineEdit()
        self.search3_type = QComboBox()
        self.search3_type.addItems(["По болезни", "По другим причинам", "Без уважительной причины"])
        self.search3_min = QSpinBox()
        self.search3_min.setRange(0, 999)
        self.search3_max = QSpinBox()
        self.search3_max.setRange(0, 999)
        self.search3_max.setValue(999)
        
        tab3_layout.addRow("Фамилия студента:", self.search3_surname)
        tab3_layout.addRow("Тип пропусков:", self.search3_type)
        tab3_layout.addRow("От:", self.search3_min)
        tab3_layout.addRow("До:", self.search3_max)
        self.tabs.addTab(tab3, "Фамилия или диапазон")
        
        layout.addWidget(self.tabs)
        
        self.btn_search = QPushButton("🔍 Найти")
        self.btn_search.clicked.connect(self.on_search)
        layout.addWidget(self.btn_search)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "ФИО", "Группа", "По болезни", "По др. причинам", 
            "Без уважит.", "Итого"
        ])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.results_table)
        
        self.pagination = PaginationWidget()
        layout.addWidget(self.pagination)
        
        self.btn_close = QPushButton("Закрыть")
        self.btn_close.clicked.connect(self.accept)
        layout.addWidget(self.btn_close)
    
    def on_search(self):
        pass  # Контроллер обработает
    
    def set_search_results(self, records, total):
        self.results_table.setRowCount(len(records))
        for row, record in enumerate(records):
            self.results_table.setItem(row, 0, QTableWidgetItem(record.full_name))
            self.results_table.setItem(row, 1, QTableWidgetItem(record.group))
            self.results_table.setItem(row, 2, QTableWidgetItem(str(record.absences_illness)))
            self.results_table.setItem(row, 3, QTableWidgetItem(str(record.absences_other)))
            self.results_table.setItem(row, 4, QTableWidgetItem(str(record.absences_unexcused)))
            self.results_table.setItem(row, 5, QTableWidgetItem(str(record.total_absences)))
    
    def get_criteria(self) -> SearchCriteria:
        current_tab = self.tabs.currentIndex()
        
        if current_tab == 0:
            return SearchCriteria(
                group=self.search1_group.text().strip() or None,
                surname=self.search1_surname.text().strip() or None
            )
        elif current_tab == 1:
            type_map = {0: 'illness', 1: 'other', 2: 'unexcused'}
            return SearchCriteria(
                surname=self.search2_surname.text().strip() or None,
                absence_type=type_map.get(self.search2_type.currentIndex())
            )
        else:
            type_map = {0: 'illness', 1: 'other', 2: 'unexcused'}
            return SearchCriteria(
                surname=self.search3_surname.text().strip() or None,
                min_absences=self.search3_min.value(),
                max_absences=self.search3_max.value()
            )