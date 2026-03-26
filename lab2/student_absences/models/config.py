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

CREATE_TABLE_DEFAULT = '''
                CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        full_name TEXT NOT NULL,
                        group_number TEXT NOT NULL,
                        absences_illness INTEGER DEFAULT 0,
                        absences_other INTEGER DEFAULT 0,
                        absences_unexcused INTEGER DEFAULT 0)
            '''

INSERT_FULL = '''
                INSERT INTO students (full_name,group_number, absences_illness, 
                                    absences_other, absences_unexcused)
                VALUES(?, ?, ?, ?, ?)'''

SELECT_PAGED = '''
                SELECT id, full_name, group_number, absences_illness, 
                        absences_other, absences_unexcused
                FROM students ORDER BY id LIMIT ? OFFSET ?'''

SELECT_ALL = '''
                SELECT id, full_name, group_number, absences_illness, 
                       absences_other, absences_unexcused
                FROM students ORDER BY id
            '''