from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton, QFormLayout, QGroupBox, QMessageBox
from models.record import StudentRecord

class InputDialog(QDialog):
    def __init__(self, parent=None, record: StudentRecord = None):
        super().__init__(parent)
        self.record = record
        self.setWindowTitle("Добавление записи" if not record else "Редактирование записи")
        self.setModal(True)
        self.resize(400, 350)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        student_group = QGroupBox("Информация о студенте")
        student_layout = QFormLayout()
        
        self.edit_full_name = QLineEdit()
        self.edit_group = QLineEdit()
        
        student_layout.addRow("ФИО:", self.edit_full_name)
        student_layout.addRow("Группа:", self.edit_group)
        student_group.setLayout(student_layout)
        layout.addWidget(student_group)
        
        absences_group = QGroupBox("Пропуски занятий")
        absences_layout = QFormLayout()
        
        self.spin_illness = QSpinBox()
        self.spin_illness.setRange(0, 999)
        self.spin_other = QSpinBox()
        self.spin_other.setRange(0, 999)
        self.spin_unexcused = QSpinBox()
        self.spin_unexcused.setRange(0, 999)
        
        absences_layout.addRow("По болезни:", self.spin_illness)
        absences_layout.addRow("По другим причинам:", self.spin_other)
        absences_layout.addRow("Без уважительной причины:", self.spin_unexcused)
        absences_group.setLayout(absences_layout)
        layout.addWidget(absences_group)
        
        self.lbl_total = QLabel("Итого пропусков: 0")
        self.lbl_total.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(self.lbl_total)
        
        self.spin_illness.valueChanged.connect(self.update_total)
        self.spin_other.valueChanged.connect(self.update_total)
        self.spin_unexcused.valueChanged.connect(self.update_total)
        
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Сохранить")
        self.btn_cancel = QPushButton("Отмена")
        
        self.btn_save.clicked.connect(self.on_save)
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)
        
        if self.record:
            self.edit_full_name.setText(self.record.full_name)
            self.edit_group.setText(self.record.group)
            self.spin_illness.setValue(self.record.absences_illness)
            self.spin_other.setValue(self.record.absences_other)
            self.spin_unexcused.setValue(self.record.absences_unexcused)
        
        self.update_total()
    
    def update_total(self):
        total = self.spin_illness.value() + self.spin_other.value() + self.spin_unexcused.value()
        self.lbl_total.setText(f"Итого пропусков: {total}")
    
    def on_save(self):
        """Обработка сохранения записи."""
        record = StudentRecord(
            id=self.record.id if self.record else 0,
            full_name=self.edit_full_name.text(),
            group=self.edit_group.text(),
            absences_illness=self.spin_illness.value(),
            absences_other=self.spin_other.value(),
            absences_unexcused=self.spin_unexcused.value()
        )
        
        is_valid, error = record.validate()
        if not is_valid:
            QMessageBox.warning(self, "Ошибка валидации", error)
            return
        
        self.accept()
    
    def get_record(self) -> StudentRecord:
        return StudentRecord(
            id=self.record.id if self.record else 0,
            full_name=self.edit_full_name.text(),
            group=self.edit_group.text(),
            absences_illness=self.spin_illness.value(),
            absences_other=self.spin_other.value(),
            absences_unexcused=self.spin_unexcused.value()
        )