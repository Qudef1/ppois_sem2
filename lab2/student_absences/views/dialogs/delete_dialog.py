# views/dialogs/delete_dialog.py
"""Диалог удаления записей."""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton, QTabWidget, QWidget, QFormLayout, QComboBox, QMessageBox
from models.criteria import SearchCriteria

class DeleteDialog(QDialog):
    """Диалог удаления записей по условиям."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Удаление записей")
        self.setModal(True)
        self.resize(550, 400)
        self.init_ui()

    def init_ui(self):
        """Инициализация UI диалога."""
        layout = QVBoxLayout(self)

        # Предупреждение
        warning = QLabel("Внимание: удаление записей необратимо!")
        warning.setStyleSheet("color: red; font-weight: bold; font-size: 13px;")
        layout.addWidget(warning)

        # Вкладки с условиями
        self.tabs = QTabWidget()

        # Вкладка 1: Группа или фамилия
        tab1 = QWidget()
        tab1_layout = QFormLayout(tab1)
        self.delete1_group = QLineEdit()
        self.delete1_group.setPlaceholderText("Например: ПИ-201")
        self.delete1_surname = QLineEdit()
        self.delete1_surname.setPlaceholderText("Например: Иванов")
        tab1_layout.addRow("Номер группы:", self.delete1_group)
        tab1_layout.addRow("Фамилия студента:", self.delete1_surname)
        self.tabs.addTab(tab1, "Группа или фамилия")

        # Вкладка 2: Пропуски и вид
        tab2 = QWidget()
        tab2_layout = QFormLayout(tab2)
        self.delete2_min_absences = QSpinBox()
        self.delete2_min_absences.setRange(0, 999)
        self.delete2_min_absences.setValue(1)
        self.delete2_type = QComboBox()
        self.delete2_type.addItems(["По болезни", "По другим причинам", "Без уважительной причины"])
        tab2_layout.addRow("Мин. количество пропусков:", self.delete2_min_absences)
        tab2_layout.addRow("Вид пропуска:", self.delete2_type)
        self.tabs.addTab(tab2, "Пропуски и вид")

        # Вкладка 3: Фамилия + диапазон по виду
        tab3 = QWidget()
        tab3_layout = QFormLayout(tab3)
        self.delete3_surname = QLineEdit()
        self.delete3_surname.setPlaceholderText("Например: Иванов")
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
        self.tabs.addTab(tab3, "Фамилия + диапазон по виду")

        layout.addWidget(self.tabs)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.btn_delete = QPushButton("Удалить")
        self.btn_delete.clicked.connect(self.accept)

        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def show_result(self, deleted_count: int):
        """
        Показать результат удаления.

        Args:
            deleted_count: Количество удалённых записей.
        """
        if deleted_count > 0:
            QMessageBox.information(self, "Удаление", f"Удалено записей: {deleted_count}")
        else:
            QMessageBox.warning(self, "Удаление", "Записи не найдены")

    def get_criteria(self) -> SearchCriteria:
        """
        Получить критерии удаления из активной вкладки.

        Returns:
            SearchCriteria с заполненными условиями.
        """
        current_tab = self.tabs.currentIndex()
        type_map = {0: 'illness', 1: 'other', 2: 'unexcused'}

        if current_tab == 0:
            # Вкладка 1: Группа или фамилия
            return SearchCriteria(
                group=self.delete1_group.text().strip() or None,
                surname=self.delete1_surname.text().strip() or None,
                tab_index=0
            )
        elif current_tab == 1:
            # Вкладка 2: Пропуски и вид
            return SearchCriteria(
                min_absences=self.delete2_min_absences.value(),
                absence_type=type_map.get(self.delete2_type.currentIndex()),
                tab_index=1
            )
        else:
            # Вкладка 3: Фамилия + диапазон по виду
            return SearchCriteria(
                surname=self.delete3_surname.text().strip() or None,
                absence_type=type_map.get(self.delete3_type.currentIndex()),
                min_absences=self.delete3_min.value(),
                max_absences=self.delete3_max.value(),
                tab_index=2
            )
