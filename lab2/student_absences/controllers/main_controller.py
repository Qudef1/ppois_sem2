from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
from ..views.main_window import MainWindow
from ..views.dialogs.input_dialog import InputDialog
from ..views.dialogs.search_dialog import SearchDialog
from ..views.dialogs.delete_dialog import DeleteDialog
from ..views.dialogs.groups_dialog import GroupsDialog
from ..models.database import Database
from ..models.xml_handler import XMLWriter, XMLReader
from ..models.criteria import SearchCriteria
from ..models.config import config

class MainController:
    def __init__(self):
        self.app = QApplication([])
        self.db = Database()
        self.view = MainWindow()
        self.current_page = 1
        self.page_size = config.page_size_default
        
        self.connect_signals()
        self.load_data()
    
    def connect_signals(self):
        self.view.pagination.page_changed.connect(self.on_page_changed)
        self.view.pagination.page_size_changed.connect(self.on_page_size_changed)
        
        self.view.on_action = self.on_menu_action
    
    def on_menu_action(self, action_name):
        """
        Обработка действий меню.
        
        Args:
            action_name: Имя действия.
        """
        if action_name == "add":
            self.add_record()
        elif action_name == "search":
            self.search_records()
        elif action_name == "delete":
            self.delete_records()
        elif action_name == "groups":
            self.show_groups()
        elif action_name == "load_xml":
            self.load_xml()
        elif action_name == "save_xml":
            self.save_xml()
        elif action_name == "view_table":
            self.view.switch_to_table()
            self.load_data()
        elif action_name == "view_tree":
            self.view.switch_to_tree()
            self.load_data()
        elif action_name == "about":
            self.show_about()
        elif action_name == "exit":
            self.app.quit()
    
    def load_data(self):
        if self.view.current_view == "table":
            records, total = self.db.get_all_paged(self.current_page, self.page_size)
            self.view.set_table_data(records)
        else:
            records, _ = self.db.get_all_paged(1, 10000)
            self.view.set_tree_data(records)
        
        self.view.pagination.update_info(self.current_page, self.page_size, total)
    
    def on_page_changed(self, page):
        self.current_page = page
        self.load_data()
    
    def on_page_size_changed(self, size):
        self.page_size = size
        self.current_page = 1
        self.load_data()
    
    def add_record(self):
        dialog = InputDialog(self.view)
        if dialog.exec() == 1:
            record = dialog.get_record()
            self.db.create(record)
            self.load_data()
            QMessageBox.information(self.view, "Успех", "Запись добавлена!")
    
    def search_records(self):
        """Открыть диалог поиска записей."""
        dialog = SearchDialog(self.view)
        dialog.btn_search.clicked.connect(lambda: self.perform_search(dialog))
        dialog.exec()

    def perform_search(self, dialog):
        """
        Выполнить поиск по критериям из диалога.
        
        Args:
            dialog: Экземпляр SearchDialog.
        """
        criteria = dialog.get_criteria()
        if not criteria.is_valid():
            QMessageBox.warning(dialog, "Предупреждение", "Заполните хотя бы одно условие поиска")
            return

        # Получаем все результаты поиска (без пагинации)
        records, total = self.db.search_paged(criteria, 1, 10000)  # Большой лимит для всех записей
        dialog.set_search_results(records, total)
    
    def delete_records(self):
        """Открыть диалог удаления записей."""
        dialog = DeleteDialog(self.view)
        if dialog.exec() == 1:
            criteria = dialog.get_criteria()
            if criteria.is_valid():
                count = self.db.delete_by_criteria(criteria)
                dialog.show_result(count)
                self.load_data()
            else:
                QMessageBox.warning(dialog, "Предупреждение", "Заполните хотя бы одно условие удаления")

    def show_groups(self):
        """Открыть диалог просмотра групп и студентов."""
        # Получаем все записи
        all_records = self.db.get_all()
        
        # Группируем по номеру группы
        groups_data = {}
        for record in all_records:
            group = record.group
            if group not in groups_data:
                groups_data[group] = []
            groups_data[group].append(record)
        
        # Открываем диалог
        dialog = GroupsDialog(self.view)
        dialog.set_groups_data(groups_data)
        dialog.exec()
    
    def save_xml(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self.view, "Сохранить в XML", 
            config.xml_default_path, "XML Files (*.xml)"
        )
        if filepath:
            all_records = self.db.get_all()
            XMLWriter.write(all_records, filepath)
            QMessageBox.information(self.view, "Успех", f"Данные сохранены в {filepath}")
    
    def load_xml(self):
        """Загрузить данные из XML файла."""
        filepath, _ = QFileDialog.getOpenFileName(
            self.view, "Загрузить из XML",
            config.xml_default_path, "XML Files (*.xml)"
        )
        if filepath:
            try:
                records = XMLReader.read(filepath)
                self.db.clear_all()
                for record in records:
                    record.id = 0
                    self.db.create(record)
                self.load_data()
                QMessageBox.information(self.view, "Успех", f"Загружено {len(records)} записей")
            except Exception as e:
                QMessageBox.critical(self.view, "Ошибка", f"Ошибка загрузки: {str(e)}")

    def show_about(self):
        """Показать диалог о программе."""
        QMessageBox.about(
            self.view,
            "О программе",
            "Учет пропусков студентов\n\n"
            "Версия: 1.0\n"
            "Курс: Проектирование ПО интеллектуальных систем\n"
            "Лабораторная работа №2\n\n"
            "Архитектура: MVC (Model-View-Controller)\n"
            "GUI: PyQt6\n"
            "БД: SQLite\n"
            "XML: SAX (чтение) / DOM (запись)"
        )

    def run(self):
        self.view.show()
        return self.app.exec()