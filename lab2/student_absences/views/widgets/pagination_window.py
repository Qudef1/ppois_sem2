from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSpinBox
from PyQt6.QtCore import pyqtSignal

class PaginationWidget(QWidget):
    page_changed = pyqtSignal(int)
    page_size_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 1
        self.page_size = 10
        self.total_records = 0
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_first = QPushButton("<-- Первая")
        self.btn_prev = QPushButton("<- Пред.")
        self.btn_next = QPushButton("След. ->")
        self.btn_last = QPushButton("Послед. -->")
        
        self.btn_first.clicked.connect(lambda: self.go_to_page(1))
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        self.btn_last.clicked.connect(self.go_to_last_page)
        
        self.lbl_page_info = QLabel("Страница 1 из 1")
        
        self.lbl_page_size = QLabel("Записей на странице:")
        self.spin_page_size = QSpinBox()
        self.spin_page_size.setRange(5, 100)
        self.spin_page_size.setValue(10)
        self.spin_page_size.valueChanged.connect(self.on_page_size_changed)
        
        self.lbl_total = QLabel("Всего записей: 0")
        
        layout.addWidget(self.btn_first)
        layout.addWidget(self.btn_prev)
        layout.addWidget(self.lbl_page_info)
        layout.addWidget(self.btn_next)
        layout.addWidget(self.btn_last)
        layout.addWidget(self.lbl_page_size)
        layout.addWidget(self.spin_page_size)
        layout.addWidget(self.lbl_total)
        layout.addStretch()
    
    def update_info(self, current_page: int, page_size: int, total_records: int):
        self.current_page = current_page
        self.page_size = page_size
        self.total_records = total_records
        
        total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 1
        
        self.lbl_page_info.setText(f"Страница {current_page} из {total_pages}")
        self.lbl_total.setText(f"Всего записей: {total_records}")
        
        self.btn_first.setEnabled(current_page > 1)
        self.btn_prev.setEnabled(current_page > 1)
        self.btn_next.setEnabled(current_page < total_pages)
        self.btn_last.setEnabled(current_page < total_pages)
    
    def go_to_page(self, page: int):
        if page != self.current_page:
            self.current_page = page
            self.page_changed.emit(page)
    
    def prev_page(self):
        if self.current_page > 1:
            self.go_to_page(self.current_page - 1)
    
    def next_page(self):
        total_pages = (self.total_records + self.page_size - 1) // self.page_size
        if self.current_page < total_pages:
            self.go_to_page(self.current_page + 1)
    
    def go_to_last_page(self):
        total_pages = (self.total_records + self.page_size - 1) // self.page_size
        self.go_to_page(total_pages)
    
    def on_page_size_changed(self, value: int):
        self.page_size = value
        self.page_size_changed.emit(value)