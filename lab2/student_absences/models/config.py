DATABASE_PATH = "resources/data/students.db"

XML_DEFAULT_PATH = "resources/data/students.xml"

PAGE_SIZE_DEFAULT = 10

config = type('Config', (), {
    'DATABASE_PATH': DATABASE_PATH,
    'XML_DEFAULT_PATH': XML_DEFAULT_PATH,
    'page_size_default': PAGE_SIZE_DEFAULT
})()

FIELDS = {
    'id': 'INTEGER',
    'full_name': 'TEXT',
    'group': 'TEXT',
    'absences_illness': 'INTEGER',
    'absences_other': 'INTEGER',
    'absences_unexcused': 'INTEGER'
}