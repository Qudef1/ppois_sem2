# models/test_record.py
from record import StudentRecord

# Тест успешного создания
record = StudentRecord(
    id=1,
    full_name="иванов иван иванович",
    group="пи-201",
    absences_illness=5,
    absences_other=2,
    absences_unexcused=1
)
print(f"✅ Запись создана: {record.full_name}, Группа: {record.group}")
print(f"✅ Итого пропусков: {record.total_absences}")
print(f"✅ Фамилия: {record.surname}")

# Тест валидации (должен вызвать ошибку)
try:
    bad_record = StudentRecord(full_name="Иван", group="ПИ-201")
except Exception as e:
    print(f"✅ Валидация работает: {e}")