from pathlib import Path

# Базовый путь — директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = str(BASE_DIR / "resources" / "data" / "students.db")
XML_DEFAULT_PATH = str(BASE_DIR / "resources" / "data" / "students.xml")

PAGE_SIZE_DEFAULT = 10

config = type('Config', (), {
    'DATABASE_PATH': DATABASE_PATH,
    'XML_DEFAULT_PATH': XML_DEFAULT_PATH,
    'xml_default_path': XML_DEFAULT_PATH,  # для совместимости
    'page_size_default': PAGE_SIZE_DEFAULT,
    'BASE_DIR': BASE_DIR
})()

FIELDS = {
    'id': 'INTEGER',
    'full_name': 'TEXT',
    'group': 'TEXT',
    'absences_illness': 'INTEGER',
    'absences_other': 'INTEGER',
    'absences_unexcused': 'INTEGER'
}