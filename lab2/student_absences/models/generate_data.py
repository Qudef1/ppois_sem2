# models/generate_data.py
"""Генератор тестовых данных для приложения."""

import random
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from models.database import Database
from models.record import StudentRecord


def generate_test_data(num_records: int = 50, db_path: str = None):
    """
    Сгенерировать тестовые данные и записать в БД.
    
    Args:
        num_records: Количество записей для генерации.
        db_path: Путь к базе данных.
    """
    surnames = [
        "Иванов", "Петров", "Сидоров", "Козлов", "Новиков",
        "Морозов", "Волков", "Лебедев", "Соколов", "Попов",
        "Васильев", "Смирнов", "Кузнецов", "Павлов", "Семенов"
    ]

    names = [
        "Александр", "Дмитрий", "Сергей", "Андрей", "Алексей",
        "Владимир", "Михаил", "Николай", "Иван", "Артем"
    ]

    patronymics = [
        "Александрович", "Дмитриевич", "Сергеевич", "Андреевич", "Алексеевич",
        "Владимирович", "Михайлович", "Николаевич", "Иванович", "Артемович"
    ]

    groups = ["ПИ-201", "ПИ-202", "ИС-301", "ИС-302", "ИБ-401", "ИБ-402"]

    db = Database(db_path)
    db.clear_all()

    for i in range(num_records):
        record = StudentRecord(
            id=0,
            full_name=f"{random.choice(surnames)} {random.choice(names)} {random.choice(patronymics)}",
            group=random.choice(groups),
            absences_illness=random.randint(0, 15),
            absences_other=random.randint(0, 10),
            absences_unexcused=random.randint(0, 5)
        )
        db.create(record)

    print(f"✅ Сгенерировано {num_records} записей")
    records, total = db.get_all_paged(1, 10)
    print(f"✅ Проверка: найдено {total} записей")
    print(f"✅ Первая запись: {records[0].full_name if records else 'Нет'}")
    return total


if __name__ == "__main__":
    generate_test_data(50)