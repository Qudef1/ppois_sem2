"""Диалог отображения данных в виде дерева (студент → поля)."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem,
    QLabel
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from typing import Dict, List, Any


class TreeViewDialog(QDialog):
    """Диалог отображения записей в виде дерева.

    Структура дерева:
        ├── Иванов Иван Иванович
        │   ├── ФИО: Иванов Иван Иванович
        │   ├── Группа: ПИ-21
        │   ├── Пропуски по болезни: 5
        │   ├── Пропуски по др. причинам: 2
        │   ├── Пропуски без уважит.: 1
        │   └── Итого пропусков: 8
        └── Петров Пётр Петрович
            ...
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Дерево записей")
        self.setModal(False)
        self.resize(900, 700)
        self._groups_data: Dict[str, List[Any]] = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Панель кнопок
        top_layout = QHBoxLayout()

        self.btn_expand = QPushButton("Развернуть всё")
        top_layout.addWidget(self.btn_expand)

        self.btn_collapse = QPushButton("Свернуть всё")
        top_layout.addWidget(self.btn_collapse)

        top_layout.addStretch()

        layout.addLayout(top_layout)

        # Дерево
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Поле", "Значение"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setIndentation(25)
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.tree.currentItemChanged.connect(self._on_item_selected)
        layout.addWidget(self.tree)

        # Подключение кнопок
        self.btn_expand.clicked.connect(self.tree.expandAll)
        self.btn_collapse.clicked.connect(self.tree.collapseAll)

        # Информационная панель
        self.lbl_info = QLabel("Выберите элемент дерева")
        self.lbl_info.setStyleSheet(
            "font-weight: bold; color: #0066cc; padding: 5px;"
        )
        layout.addWidget(self.lbl_info)

        # Кнопка закрытия
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_close = QPushButton("Закрыть")
        self.btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

    def set_groups_data(self, groups_data: Dict[str, List[Any]]):
        self._groups_data = groups_data
        self._build_tree()

    def _build_tree(self):
        """Построить дерево: каждый студент — узел верхнего уровня."""
        self.tree.clear()

        # Собираем всех студентов в один список
        all_students: List[Any] = []
        for students in self._groups_data.values():
            all_students.extend(students)

        for student in sorted(all_students, key=lambda s: s.full_name):
            self._add_student_node(self.tree, student)

    def _add_student_node(self, parent: QTreeWidgetItem, student: Any):
        """Добавить студента с раскрывающимися полями."""
        student_item = QTreeWidgetItem(parent)
        student_item.setText(0, student.full_name)
        student_item.setText(1, student.group)
        student_item.setData(0, Qt.ItemDataRole.UserRole, "student")
        student_item.setData(1, Qt.ItemDataRole.UserRole, student)
        student_item.setFont(0, QFont("Arial", 10, QFont.Weight.Bold))

        # Листовые элементы — поля записи
        fields = [
            ("Группа", student.group),
            ("Пропуски по болезни", str(student.absences_illness)),
            ("Пропуски по др. причинам", str(student.absences_other)),
            ("Пропуски без уважит.", str(student.absences_unexcused)),
            ("Итого пропусков", str(student.total_absences)),
        ]

        for label, value in fields:
            leaf = QTreeWidgetItem(student_item)
            leaf.setText(0, label)
            leaf.setText(1, value)
            leaf.setFlags(leaf.flags() & ~Qt.ItemFlag.ItemIsSelectable)

    def _on_item_selected(self, current: QTreeWidgetItem, _previous: QTreeWidgetItem):
        if not current:
            return
        data = current.data(1, Qt.ItemDataRole.UserRole)
        node_type = current.data(0, Qt.ItemDataRole.UserRole)

        if node_type == "student" and data:
            self.lbl_info.setText(
                f"{data.full_name} ({data.group}) | "
                f"Пропуски: {data.absences_illness} + {data.absences_other} + "
                f"{data.absences_unexcused} = {data.total_absences}"
            )
        else:
            self.lbl_info.setText(current.text(0))
