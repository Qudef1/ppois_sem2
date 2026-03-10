# views/dialogs/delete_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton, QTabWidget, QWidget, QFormLayout, QComboBox, QMessageBox
from ...models.criteria import SearchCriteria

class DeleteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Удаление записей")
        self.setModal(True)
        self.resize(500, 350)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        
        # Tab 1
        tab1 = QWidget()
        tab1_layout = QFormLayout(tab1)
        self.delete1_group = QLineEdit()
        self.delete1_surname = QLineEdit()
        tab1_layout.addRow("Номер группы:", self.delete1_group)
        tab1_layout.addRow("Фамилия студента:", self.delete1_surname)
        self.tabs.addTab(tab1, "Группа или фамилия")
        
        # Tab 2
        tab2 = QWidget()
        tab2_layout = QFormLayout(tab2)
        self.delete2_surname = QLineEdit()
        self.delete2_type = QComboBox()
        self.delete2_type.addItems(["По болезни", "По другим причинам", "Без уважительной причины"])
        tab2_layout.addRow("Фамилия студента:", self.delete2_surname)
        tab2_layout.addRow("Вид пропуска:", self.delete2_type)
        self.tabs.addTab(tab2, "Фамилия или вид пропуска")
        
        # Tab 3
        tab3 = QWidget()
        tab3_layout = QFormLayout(tab3)
        self.delete3_surname = QLineEdit()
        self.delete3_type = QComboBox()
        self.delete3_type.addItems(["По болезни", "По другим причинам", "Без уважительной причины"])
        self.delete3_min = QSpinBox()
        self.delete3_min.setRange(0, 999)
        self.delete3_max = QSpinBox()
        self.delete3_max.setRange(0, 999)
        self.delete3_max.setValue(999)
        
        tab3_layout.addRow("Фамилия студента:", self.delete3_surname)
        tab3_layout.addRow("Тип пропусков:", self.delete3_type)
        tab3_layout.addRow("От:", self.delete3_min)
        tab3_layout.addRow("До:", self.delete3_max)
        self.tabs.addTab(tab3, "Фамилия или диапазон")
        
        layout.addWidget(self.tabs)
        
        warning = QLabel("⚠️ Внимание: удаление необратимо!")
        warning.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(warning)
        
        btn_layout = QHBoxLayout()
        self.btn_delete = QPushButton("🗑️ Удалить")
        self.btn_cancel = QPushButton("❌ Отмена")
        
        self.btn_delete.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)
    
    def show_result(self, deleted_count: int):
        if deleted_count > 0:
            QMessageBox.information(self, "Удаление", f"✅ Удалено записей: {deleted_count}")
        else:
            QMessageBox.warning(self, "Удаление", "❌ Записи не найдены")
    
    def get_criteria(self) -> SearchCriteria:
        current_tab = self.tabs.currentIndex()
        
        if current_tab == 0:
            return SearchCriteria(
                group=self.delete1_group.text().strip() or None,
                surname=self.delete1_surname.text().strip() or None
            )
        elif current_tab == 1:
            type_map = {0: 'illness', 1: 'other', 2: 'unexcused'}
            return SearchCriteria(
                surname=self.delete2_surname.text().strip() or None,
                absence_type=type_map.get(self.delete2_type.currentIndex())
            )
        else:
            return SearchCriteria(
                surname=self.delete3_surname.text().strip() or None,
                min_absences=self.delete3_min.value(),
                max_absences=self.delete3_max.value()
            )