import sqlite3
from pathlib import Path
from typing import List, Tuple
from models.record import StudentRecord
from models.criteria import SearchCriteria
from models.config import *

class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        # Создаём директорию если не существует
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        with self.get_connection() as conn:
            conn.execute(CREATE_TABLE_DEFAULT)

            conn.execute('CREATE INDEX IF NOT EXISTS idx_group ON students(group_number)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_name ON students(full_name)')
            conn.commit()

    def create(self,record: StudentRecord) -> int:
        with self.get_connection() as conn:
            cursor = conn.execute(INSERT_FULL,(record.full_name,record.group,
                                          record.absences_illness,record.absences_other,record.absences_unexcused))
            conn.commit()
            return cursor.lastrowid
        
    def get_all_paged(self,page:int,page_size: int) -> Tuple[List[StudentRecord], int]:
        offset = (page - 1) * page_size
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT COUNT(*) FROM students')
            total = cursor.fetchone()[0]

            cursor = conn.execute(SELECT_PAGED,(page_size,offset))
            
            records = [StudentRecord(
                id=row['id'],
                full_name=row['full_name'],
                group=row['group_number'],
                absences_illness=row['absences_illness'],
                absences_other=row['absences_other'],
                absences_unexcused=row['absences_unexcused']
            ) for row in cursor.fetchall()]

            return records, total
        
    def search_paged(self, criteria: SearchCriteria, page: int, page_size: int) -> Tuple[List[StudentRecord], int]:
        """
        Поиск записей с пагинацией.
        
        Args:
            criteria: Критерии поиска.
            page: Номер страницы.
            page_size: Размер страницы.
            
        Returns:
            Кортеж (список записей, общее количество).
        """
        conditions = []
        params = []

        if criteria.group:
            conditions.append('group_number = ?')
            params.append(criteria.group)

        if criteria.surname:
            conditions.append("full_name LIKE ?")
            params.append(f"{criteria.surname}%")

        if criteria.absence_type:
            field_map = {
                'illness': 'absences_illness',
                'other': 'absences_other',
                'unexcused': 'absences_unexcused'
            }
            field = field_map.get(criteria.absence_type)
            if field:
                conditions.append(f"{field} > 0")

        if criteria.min_absences is not None and criteria.max_absences is not None:
            conditions.append("(absences_illness + absences_other + absences_unexcused) BETWEEN ? AND ?")
            params.extend([criteria.min_absences, criteria.max_absences])

        if not conditions:
            return self.get_all_paged(page, page_size)

        # Используем AND для пересечения условий (все условия должны выполняться)
        where_clause = ' AND '.join(conditions)
        offset = (page - 1) * page_size

        with self.get_connection() as conn:
            cursor = conn.execute(f'SELECT COUNT(*) FROM students WHERE {where_clause}', params)
            total = cursor.fetchone()[0]

            cursor = conn.execute(f'''
                SELECT id, full_name, group_number, absences_illness,
                       absences_other, absences_unexcused
                FROM students WHERE {where_clause}
                ORDER BY id LIMIT ? OFFSET ?
            ''', params + [page_size, offset])

            records = [StudentRecord(
                id=row['id'],
                full_name=row['full_name'],
                group=row['group_number'],
                absences_illness=row['absences_illness'],
                absences_other=row['absences_other'],
                absences_unexcused=row['absences_unexcused']
            ) for row in cursor.fetchall()]

            return records, total

    def delete_by_criteria(self, criteria: SearchCriteria) -> int:
        conditions = []
        params = []

        if criteria.group:
            conditions.append("group_number = ?")
            params.append(criteria.group)
        
        if criteria.surname:
            conditions.append("full_name LIKE ?")
            params.append(f"{criteria.surname}%")
        
        if not conditions:
            return 0
        
        where_clause = " OR ".join(conditions)
        
        with self.get_connection() as conn:
            cursor = conn.execute(f'DELETE FROM students WHERE {where_clause}', params)
            conn.commit()
            return cursor.rowcount
        
    def clear_all(self):
        with self.get_connection() as conn:
            conn.execute('DELETE FROM students')
            conn.commit()

    
    def get_all(self) -> List[StudentRecord]:
        with self.get_connection() as conn:
            cursor = conn.execute(SELECT_ALL)
            return [StudentRecord(
                id=row['id'],
                full_name=row['full_name'],
                group=row['group_number'],
                absences_illness=row['absences_illness'],
                absences_other=row['absences_other'],
                absences_unexcused=row['absences_unexcused']
            ) for row in cursor.fetchall()]
    


            
