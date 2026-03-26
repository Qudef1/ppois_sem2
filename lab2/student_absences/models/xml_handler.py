import xml.dom.minidom
import xml.sax
from typing import List
from models.record import StudentRecord

class XMLWriter:
    """Запись в XML используя DOM"""
    
    @staticmethod
    def write(records: List[StudentRecord], filepath: str):
        doc = xml.dom.minidom.Document()
        root = doc.createElement('students')
        doc.appendChild(root)
        
        for record in records:
            student_elem = doc.createElement('student')
            student_elem.setAttribute('id', str(record.id))
            
            fields = [
                ('full_name', record.full_name, 'string'),
                ('group', record.group, 'string'),
                ('absences_illness', str(record.absences_illness), 'int'),
                ('absences_other', str(record.absences_other), 'int'),
                ('absences_unexcused', str(record.absences_unexcused), 'int')
            ]
            
            for field_name, value, type_attr in fields:
                elem = doc.createElement(field_name)
                elem.setAttribute('type', type_attr)
                value_text = doc.createTextNode(value)
                elem.appendChild(value_text)
                student_elem.appendChild(elem)
            
            root.appendChild(student_elem)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(doc.toprettyxml(indent="    ", encoding='utf-8').decode('utf-8'))

class XMLReader(xml.sax.ContentHandler):
    """Чтение из XML используя SAX"""
    
    def __init__(self):
        super().__init__()
        self.records = []
        self.current_record = {}
        self.current_field = ""
        self.current_data = ""
    
    def startElement(self, name, attrs):
        if name == 'student':
            self.current_record = {'id': int(attrs.get('id', 0))}
        elif name in ['full_name', 'group', 'absences_illness', 'absences_other', 'absences_unexcused']:
            self.current_field = name
            self.current_data = ""
    
    def characters(self, content):
        self.current_data += content
    
    def endElement(self, name):
        if name == 'student':
            try:
                # Конвертация типов
                for key in ['absences_illness', 'absences_other', 'absences_unexcused']:
                    if key in self.current_record:
                        self.current_record[key] = int(self.current_record[key])

                record = StudentRecord.from_dict(self.current_record)
                self.records.append(record)
            except Exception as e:
                print(f"Пропущена невалидная запись: {e}")

            self.current_record = {}
        elif name in ['full_name', 'group']:
            self.current_record[name] = self.current_data.strip()
        elif name in ['absences_illness', 'absences_other', 'absences_unexcused']:
            self.current_record[name] = self.current_data.strip()

        self.current_field = ""
    
    @staticmethod
    def read(filepath: str) -> List[StudentRecord]:
        handler = XMLReader()
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse(filepath)
        return handler.records