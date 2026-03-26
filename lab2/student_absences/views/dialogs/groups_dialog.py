# views/dialogs/groups_dialog.py
"""Диалог просмотра групп и студентов."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QFormLayout,
    QWidget, QGroupBox
)
from PyQt6.QtCore import Qt
from typing import List, Dict, Any


class GroupsDialog(QDialog):
    """Диалог отображения групп и студентов по группам."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Группы и студенты")
        self.setModal(True)
        self.resize(800, 600)
        self._groups_data: Dict[str, List[Any]] = {}
        self.init_ui()

    def init_ui(self):
        """Инициализация UI диалога."""
        layout = QVBoxLayout(self)

        # Верхняя панель с выбором группы
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Выпадающий список групп
        top_layout.addWidget(QLabel("Выберите группу:"))
        self.combo_groups = QComboBox()
        self.combo_groups.setMinimumWidth(200)
        self.combo_groups.currentTextChanged.connect(self._on_group_changed)
        top_layout.addWidget(self.combo_groups)
        top_layout.addStretch()

        # Метка с количеством студентов
        self.lbl_count = QLabel("")
        self.lbl_count.setStyleSheet("font-weight: bold; color: #0066cc;")
        top_layout.addWidget(self.lbl_count)

        layout.addWidget(top_widget)

        # Группа с информацией
        info_group = QGroupBox("Информация о группе")
        info_layout = QFormLayout(info_group)
        self.lbl_total_students = QLabel("0")
        self.lbl_total_absences = QLabel("0")
        self.lbl_avg_absences = QLabel("0")
        info_layout.addRow("Всего студентов:", self.lbl_total_students)
        info_layout.addRow("Всего пропусков:", self.lbl_total_absences)
        info_layout.addRow("Среднее кол-во пропусков:", self.lbl_avg_absences)
        layout.addWidget(info_group)

        # Таблица студентов
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(6)
        self.students_table.setHorizontalHeaderLabels([
            "ФИО", "По болезни", "По др. причинам",
            "Без уважит.", "Итого", "Средний балл"
        ])
        self.students_table.horizontalHeader().setStretchLastSection(True)
        self.students_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.students_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.students_table)

        # Кнопка закрытия
        self.btn_close = QPushButton("Закрыть")
        self.btn_close.clicked.connect(self.accept)
        layout.addWidget(self.btn_close)

    def set_groups_data(self, groups_data: Dict[str, List[Any]]):
        """
        Установить данные о группах и студентах.

        Args:
            groups_data: Словарь {название_группы: [список_студентов]}.
        """
        self._groups_data = groups_data

        # Заполняем ComboBox названиями групп
        self.combo_groups.clear()
        if groups_data:
            sorted_groups = sorted(groups_data.keys())
            self.combo_groups.addItems(sorted_groups)
            # Выбираем первую группу по умолчанию
            if sorted_groups:
                self._on_group_changed(sorted_groups[0])
        else:
            self.lbl_count.setText("")
            self._clear_info()

    def _on_group_changed(self, group_name: str):
        """
        Обработчик изменения выбранной группы.

        Args:
            group_name: Название выбранной группы.
        """
        if not group_name or group_name not in self._groups_data:
            return

        students = self._groups_data[group_name]
        self._display_students(students)

        # Обновляем счётчики
        self.lbl_count.setText(f"Студентов: {len(students)}")

        # Обновляем информацию о группе
        self._update_group_info(students)

    def _display_students(self, students: List[Any]):
        """
        Отобразить студентов в таблице.

        Args:
            students: Список записей студентов.
        """
        self.students_table.setRowCount(len(students))

        for row, student in enumerate(students):
            # ФИО
            item = QTableWidgetItem(student.full_name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.students_table.setItem(row, 0, item)

            # По болезни
            item = QTableWidgetItem(str(student.absences_illness))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.students_table.setItem(row, 1, item)

            # По другим причинам
            item = QTableWidgetItem(str(student.absences_other))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.students_table.setItem(row, 2, item)

            # Без уважительной причины
            item = QTableWidgetItem(str(student.absences_unexcused))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.students_table.setItem(row, 3, item)

            # Итого
            total = student.total_absences
            item = QTableWidgetItem(str(total))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if total > 10:
                item.setForeground(Qt.GlobalColor.red)
            elif total > 5:
                item.setForeground(Qt.GlobalColor.darkYellow)
            self.students_table.setItem(row, 4, item)

            # Средний балл (заглушка, если нет данных)
            item = QTableWidgetItem("—")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.students_table.setItem(row, 5, item)

        # Автоподбор ширины колонок
        self.students_table.resizeColumnsToContents()

    def _update_group_info(self, students: List[Any]):
        """
        Обновить информацию о группе.

        Args:
            students: Список записей студентов.
        """
        if not students:
            self._clear_info()
            return

        total_students = len(students)
        total_absences = sum(s.total_absences for s in students)
        avg_absences = total_absences / total_students if total_students > 0 else 0

        self.lbl_total_students.setText(str(total_students))
        self.lbl_total_absences.setText(str(total_absences))
        self.lbl_avg_absences.setText(f"{avg_absences:.1f}")

    def _clear_info(self):
        """Очистить информацию о группе."""
        self.lbl_total_students.setText("0")
        self.lbl_total_absences.setText("0")
        self.lbl_avg_absences.setText("0")
        self.students_table.setRowCount(0)
