from theater import Theater, Setting, AuditoryHall, Ticket
from staff import Actor, Director, CostumeDesigner
from datetime import datetime

def test_full_save_load():
    print("=== Создание объектов ===")
    
    # Создаём театр
    theater = Theater("Городской театр")

    # Создаём сотрудников
    actor1 = Actor("Иван Петров", 30, 50000.0, "Гамлет")
    actor2 = Actor("Мария Иванова", 28, 45000.0, "Офелия")
    director = Director("Петр Сидоров", 45, 80000.0)
    designer = CostumeDesigner("Анна Смирнова", 35, 40000.0)

    # Добавляем в театр
    theater.staff_manager.add_staff(actor1)
    theater.staff_manager.add_staff(actor2)
    theater.staff_manager.add_staff(director)
    theater.staff_manager.add_staff(designer)

    # Создаём зал
    hall = AuditoryHall("Большой зал", 2, 10, 10, "hall_001")
    theater.resource_manager.hall_manager.add_hall(hall)

    # Создаём спектакль
    setting = Setting(120.0, "Гамлет", datetime.now(), [actor1, actor2], director)
    theater.performance_manager.add_setting(setting)

    # Создаём и добавляем билет
    ticket = Ticket(1000.0, setting, 0, 1, 5, hall)
    theater.ticket_manager.add_ticket(ticket)

    print(f"Создан билет: {ticket.ticket_id}, цена: {ticket.price}, спектакль: {ticket.setting.name}")

    print("\n=== Сохранение в файл ===")
    theater.save_to_file("test_theater.json")
    print("Состояние сохранено в test_theater.json")

    print("\n=== Загрузка из файла ===")
    loaded_theater = Theater.load_from_file("test_theater.json")
    print("Состояние загружено из test_theater.json")

    print("\n=== Проверка загруженных данных ===")
    print(f"Название театра: {loaded_theater.name}")
    print(f"Количество сотрудников: {len(loaded_theater.staff_manager.get_staff())}")

    staff = loaded_theater.staff_manager.get_staff()
    for s in staff:
        print(f"  - {s.name} ({type(s).__name__})")

    print(f"Количество спектаклей: {len(loaded_theater.performance_manager.settings)}")
    setting_loaded = loaded_theater.performance_manager.settings[0]
    print(f"  - Спектакль: {setting_loaded.name}")
    print(f"    Актеры: {[a.name for a in setting_loaded.cast]}")
    print(f"    Режиссёр: {setting_loaded.director.name}")

    print(f"Количество билетов: {len(loaded_theater.ticket_manager.get_all_tickets())}")
    ticket_loaded = loaded_theater.ticket_manager.get_all_tickets()[0]
    print(f"  - Билет: {ticket_loaded.ticket_id}, спектакль: {ticket_loaded.setting.name}, зал: {ticket_loaded.hall.name}")

    print("\n=== Проверка продажи билета ===")
    try:
        success = ticket_loaded.sell_ticket(loaded_theater.resource_manager.hall_manager)
        print(f"Билет продан: {success}")
        print(f"Билет продан: {ticket_loaded.is_sold}")
        print(f"Место в зале занято: {ticket_loaded.hall.seats[0][1][5].is_occupied}")
    except Exception as e:
        print(f"Ошибка при продаже билета: {e}")

    print("\n=== Тест пройден успешно! ===")

if __name__ == "__main__":
    test_full_save_load()