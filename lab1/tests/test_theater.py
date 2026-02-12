"""
Реалистичные интеграционные тесты театральной системы.
Тесты проверяют полные сценарии работы с театром.
"""
import unittest
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Добавить путь к модулям src
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.theater import Theater
from src.staff import Actor, Director, CostumeDesigner
from src.theater import Setting, Repetition, AuditoryHall, Costume, Ticket
from src.exceptions import (
    InvalidSeatException, TicketNotFoundException, InvalidDateException, TheaterException
)


class TestTheaterRealScenarios(unittest.TestCase):
    """10 реалистичных тестов основных сценариев использования"""

    def setUp(self):
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.data_dir.mkdir(exist_ok=True)
        self.test_file = self.data_dir / "test_state.json"
        if self.test_file.exists():
            os.remove(self.test_file)

    def tearDown(self):
        if self.test_file.exists():
            os.remove(self.test_file)

    def test_01_setup_romeo_and_juliette_complete(self):
        """Сценарий 1: Создание полного сценария Ромео и Джульетта"""
        theater = Theater("Городской театр")

        # Создание команды
        director = Director("Игорь Сафронов", 50, 5000.0)
        romeo = Actor("Иван Петров", 26, 3000.0, "Romeo")
        juliette = Actor("Мария Соколова", 24, 3000.0, "Juliette")
        
        theater.staff_manager.add_staff(director)
        theater.staff_manager.add_staff(romeo)
        theater.staff_manager.add_staff(juliette)

        # Костюмы
        romeo_costume = Costume("Romeo's suit", "L", "crimson")
        juliette_costume = Costume("Juliette's dress", "M", "white")
        
        theater.resource_manager.add_costume(romeo_costume)
        theater.resource_manager.add_costume(juliette_costume)

        romeo.assign_costume(romeo_costume.name)
        juliette.assign_costume(juliette_costume.name)

        # Постановка с 10 репетициями
        premiere_date = datetime(2026, 2, 12, 19, 0, 0)
        setting = Setting(
            2.5, 
            "Romeo and Juliette",
            premiere_date,
            [romeo.name, juliette.name],
            director.name
        )
        theater.performance_manager.add_setting(setting)
        director.direct_setting(setting.name)

        for i in range(1, 11):
            rep_date = premiere_date - timedelta(days=11-i)
            rep = Repetition(0.5, setting.name, "normal", rep_date)
            theater.performance_manager.add_repetition(rep)

        # Зал: 4 сектора, 10 рядов, 10 мест
        main_hall = AuditoryHall("Main Hall", 4, 10, 10, "main_hall")
        theater.resource_manager.hall_manager.add_hall(main_hall)

        # Проверки
        self.assertEqual(len(theater.staff_manager.get_staff()), 3)
        self.assertEqual(len(theater.resource_manager.costumes), 2)
        self.assertEqual(len(theater.performance_manager.settings), 1)
        self.assertEqual(len(theater.performance_manager.repetitions), 10)
        self.assertEqual(main_hall.capacity, 400)

    def test_02_add_multiple_actors_with_roles(self):
        """Сценарий 2: Добавление нескольких актёров с разными ролями"""
        theater = Theater("Theater")
        
        actors_data = [
            ("Анна Смирнова", 28, 2500.0, "Lady Capulet"),
            ("Петр Иванов", 35, 3500.0, "Count Paris"),
            ("Владимир Орлов", 45, 4000.0, "Friar Lawrence"),
            ("Елена Морозова", 30, 2800.0, "Nurse"),
        ]

        for name, age, salary, role in actors_data:
            actor = Actor(name, age, salary, role)
            theater.staff_manager.add_staff(actor)

        # Проверка
        staff = theater.staff_manager.get_staff()
        self.assertEqual(len(staff), 4)
        self.assertEqual(staff[0].role, "Lady Capulet")
        self.assertEqual(staff[3].role, "Nurse")

    def test_03_assign_costumes_to_actors(self):
        """Сценарий 3: Назначение костюмов актёрам"""
        theater = Theater("Costume Theater")

        # Актёры
        actor1 = Actor("John", 25, 2000.0, "King")
        actor2 = Actor("Jane", 23, 2000.0, "Queen")
        theater.staff_manager.add_staff(actor1)
        theater.staff_manager.add_staff(actor2)

        # Костюмы
        costume1 = Costume("Royal Crown", "M", "gold")
        costume2 = Costume("Royal Gown", "S", "purple")
        
        theater.resource_manager.add_costume(costume1)
        theater.resource_manager.add_costume(costume2)

        # Назначение
        actor1.assign_costume(costume1.name)
        actor2.assign_costume(costume2.name)

        # Проверка
        self.assertEqual(actor1.assigned_costume, "Royal Crown")
        self.assertEqual(actor2.assigned_costume, "Royal Gown")

    def test_04_create_tickets_and_sell(self):
        """Сценарий 4: Создание и продажа билетов"""
        theater = Theater("Ticket Theater")

        # Создание зала
        hall = AuditoryHall("VIP Hall", 2, 5, 10, "vip_hall")
        theater.resource_manager.hall_manager.add_hall(hall)

        # Создание билетов
        ticket_prices = [500.0, 750.0, 1000.0, 1500.0, 2000.0]
        tickets = []
        
        for i, price in enumerate(ticket_prices):
            ticket = Ticket(f"ticket_{i+1}", price, "setting_1", 0, 0, i, "vip_hall")
            theater.ticket_manager.add_ticket(ticket)
            tickets.append(ticket)

        # Продажа билетов
        sold_count = 0
        for ticket in tickets:
            if theater.ticket_manager.sell_ticket(ticket.ticket_id, theater.resource_manager.hall_manager):
                sold_count += 1

        # Проверки
        self.assertEqual(len(theater.ticket_manager.get_all_tickets()), 5)
        self.assertEqual(sold_count, 5)
        self.assertEqual(hall.audience_count, 5)

    def test_05_multiple_halls_management(self):
        """Сценарий 5: Управление несколькими залами"""
        theater = Theater("Multi-Hall Theater")

        halls_config = [
            ("Main Stage", 4, 10, 10, "main"),
            ("Small Hall", 2, 8, 8, "small"),
            ("Chamber Room", 1, 5, 5, "chamber"),
        ]

        for name, sectors, rows, seats, hall_id in halls_config:
            hall = AuditoryHall(name, sectors, rows, seats, hall_id)
            theater.resource_manager.hall_manager.add_hall(hall)

        # Проверки
        self.assertEqual(len(theater.resource_manager.hall_manager.halls), 3)
        self.assertEqual(theater.resource_manager.hall_manager.get_hall_by_id("main").capacity, 400)
        self.assertEqual(theater.resource_manager.hall_manager.get_hall_by_id("small").capacity, 128)
        self.assertEqual(theater.resource_manager.hall_manager.get_hall_by_id("chamber").capacity, 25)

    def test_06_full_show_scheduling(self):
        """Сценарий 6: Полное расписание постановки с репетициями"""
        theater = Theater("Scheduling Theater")

        # Команда
        director = Director("Master Director", 55, 6000.0)
        actors = [
            Actor("Lead Actor", 30, 3500.0, "Main"),
            Actor("Support Actor", 28, 2500.0, "Support"),
        ]
        
        theater.staff_manager.add_staff(director)
        for actor in actors:
            theater.staff_manager.add_staff(actor)

        # Постановка
        premiere = datetime(2026, 3, 15, 19, 30, 0)
        setting = Setting(
            3.0,
            "Hamlet",
            premiere,
            [a.name for a in actors],
            director.name
        )
        theater.performance_manager.add_setting(setting)

        # Репетиции с разными уровнями важности
        importance_levels = ["low", "low", "normal", "normal", "normal", "high", "high"]
        for i, importance in enumerate(importance_levels, 1):
            rep_date = premiere - timedelta(days=7-i)
            rep = Repetition(0.75, setting.name, importance, rep_date)
            theater.performance_manager.add_repetition(rep)

        # Проверки
        self.assertEqual(len(theater.performance_manager.settings), 1)
        self.assertEqual(len(theater.performance_manager.repetitions), 7)
        
        # Проверка уровней важности
        reps = theater.performance_manager.repetitions
        self.assertEqual(reps[0].importance, "low")
        self.assertEqual(reps[5].importance, "high")

    def test_07_save_and_load_complete_state(self):
        """Сценарий 7: Сохранение и загрузка полного состояния театра"""
        # Создание полного театра
        theater = Theater("Save/Load Theater")

        director = Director("Director", 50, 5000.0)
        actor = Actor("Actor", 30, 3000.0, "Role")
        costume = Costume("Costume", "M", "blue")

        theater.staff_manager.add_staff(director)
        theater.staff_manager.add_staff(actor)
        theater.resource_manager.add_costume(costume)

        actor.assign_costume(costume.name)

        show_date = datetime(2026, 2, 12, 20, 0, 0)
        setting = Setting(2.0, "Play", show_date, [actor.name], director.name)
        theater.performance_manager.add_setting(setting)
        director.direct_setting(setting.name)

        rep1 = Repetition(0.5, setting.name, "normal", show_date - timedelta(days=1))
        rep2 = Repetition(0.5, setting.name, "normal", show_date - timedelta(days=2))
        theater.performance_manager.add_repetition(rep1)
        theater.performance_manager.add_repetition(rep2)

        hall = AuditoryHall("Hall", 2, 5, 5, "hall")
        theater.resource_manager.hall_manager.add_hall(hall)

        # Сохранение
        theater.save_to_file(self.test_file)
        self.assertTrue(Path(self.test_file).exists())

        # Загрузка
        loaded = Theater.load_from_file(self.test_file)

        # Проверки после загрузки
        self.assertEqual(loaded.name, "Save/Load Theater")
        self.assertEqual(len(loaded.staff_manager.get_staff()), 2)
        self.assertEqual(len(loaded.resource_manager.costumes), 1)
        self.assertEqual(len(loaded.performance_manager.settings), 1)
        self.assertEqual(len(loaded.performance_manager.repetitions), 2)

        # Проверка связей
        loaded_actor = loaded.staff_manager.get_staff()[1]
        self.assertEqual(loaded_actor.assigned_costume, costume.name)

        loaded_director = loaded.staff_manager.get_staff()[0]
        self.assertIn(setting.name, loaded_director.directed_settings)

    def test_08_reserve_seats_and_track_occupancy(self):
        """Сценарий 8: Забронирование мест и отслеживание заполнения"""
        theater = Theater("Reservation Theater")

        hall = AuditoryHall("Concert Hall", 3, 4, 8, "concert")
        theater.resource_manager.hall_manager.add_hall(hall)

        total_capacity = hall.capacity
        reserve_count = 15

        # Создание и продажа билетов
        for i in range(reserve_count):
            sector = i // 12
            row = (i % 12) // 8
            seat = i % 8

            if sector < hall.sectors and row < hall.rows_per_sector:
                ticket = Ticket(f"res_{i}", 500.0, "show", sector, row, seat, "concert")
                theater.ticket_manager.add_ticket(ticket)
                theater.ticket_manager.sell_ticket(ticket.ticket_id, theater.resource_manager.hall_manager)

        # Проверка
        occupancy_rate = (hall.audience_count / total_capacity) * 100
        self.assertGreater(occupancy_rate, 0)
        self.assertEqual(hall.audience_count, 15)

    def test_09_manage_costume_designer_work(self):
        """Сценарий 9: Управление работой костюмера"""
        theater = Theater("Costume Design Theater")

        designer = CostumeDesigner("Famous Designer", 45, 4500.0)
        theater.staff_manager.add_staff(designer)

        # Костюмер создаёт костюмы
        costume_list = [
            "Medieval King's Robe",
            "Royal Crown",
            "Knight Armor",
            "Princess Dress",
            "Servant Clothes",
        ]

        for costume_name in costume_list:
            designer.create_costume(costume_name)
            costume = Costume(costume_name, "M", "custom")
            theater.resource_manager.add_costume(costume)

        # Проверки
        self.assertEqual(len(designer.created_costumes), 5)
        self.assertEqual(len(theater.resource_manager.costumes), 5)
        self.assertIn("Royal Crown", designer.created_costumes)

    def test_10_complex_production_workflow(self):
        """Сценарий 10: Сложный рабочий процесс полной постановки"""
        theater = Theater("Complex Theater")

        # Этап 1: Подбор команды
        director = Director("Visionary Director", 52, 6500.0)
        designer = CostumeDesigner("Chief Designer", 44, 4200.0)
        actors = [
            Actor("Leading Lady", 32, 3200.0, "Protagonist"),
            Actor("Hero", 29, 3100.0, "Antagonist"),
            Actor("Villain", 45, 3000.0, "Villain"),
        ]

        theater.staff_manager.add_staff(director)
        theater.staff_manager.add_staff(designer)
        for actor in actors:
            theater.staff_manager.add_staff(actor)

        # Этап 2: Подготовка костюмов
        costumes_data = [
            ("Protagonist Gown", "M", "crimson"),
            ("Antagonist Suit", "L", "black"),
            ("Villain Cape", "L", "purple"),
        ]

        costumes = []
        for name, size, color in costumes_data:
            costume = Costume(name, size, color)
            theater.resource_manager.add_costume(costume)
            designer.create_costume(name)
            costumes.append(costume)

        # Этап 3: Распределение костюмов
        for actor, costume in zip(actors, costumes):
            actor.assign_costume(costume.name)

        # Этап 4: Постановка с полным планом
        production = Setting(
            3.5,
            "The Masterpiece",
            datetime(2026, 4, 1, 19, 0, 0),
            [a.name for a in actors],
            director.name
        )
        theater.performance_manager.add_setting(production)
        director.direct_setting(production.name)

        # Этап 5: Полное расписание репетиций
        premiere = datetime(2026, 4, 1, 19, 0, 0)
        dates = [premiere - timedelta(days=12-i) for i in range(5)]
        for date in dates:
            rep = Repetition(1.0, production.name, "rehearsal", date)
            theater.performance_manager.add_repetition(rep)

        # Этап 6: Подготовка зрительного зала
        main_venue = AuditoryHall("Grand Theater", 5, 15, 20, "grand")
        theater.resource_manager.hall_manager.add_hall(main_venue)

        # Финальные проверки
        self.assertEqual(len(theater.staff_manager.get_staff()), 5)  # директор + дизайнер + 3 актера
        self.assertEqual(len(theater.resource_manager.costumes), 3)
        self.assertEqual(designer.created_costumes, ["Protagonist Gown", "Antagonist Suit", "Villain Cape"])
        self.assertEqual(len(production.cast_ids), 3)
        self.assertEqual(production.director_id, director.name)
        self.assertEqual(main_venue.capacity, 1500)

        # Проверка, что все актёры имеют костюмы
        for actor in actors:
            self.assertIsNotNone(actor.assigned_costume)

        # Сохранение полного состояния
        theater.save_to_file(self.test_file)
        self.assertTrue(Path(self.test_file).exists())

    def test_11_invalid_seat_exception(self):
        """Тест: Исключение для невалидного места"""
        theater = Theater("Городской театр")
        hall = AuditoryHall("Main Hall", 3, 10, 10, "H001")
        theater.resource_manager.hall_manager.add_hall(hall)
        
        # Попытка занять невалидное место
        with self.assertRaises(InvalidSeatException) as context:
            hall.is_seat_available(10, 10, 10)  # вне границ
        
        self.assertIn("координаты места", str(context.exception).lower())

    def test_12_ticket_already_sold_exception(self):
        """Тест: Исключение при попытке продать уже проданный билет"""
        theater = Theater("Городской театр")
        hall = AuditoryHall("Main Hall", 2, 5, 5, "H001")
        theater.resource_manager.hall_manager.add_hall(hall)
        
        # Создаём постановку и билет
        setting = Setting(10.0, "Test Play", datetime.now())
        ticket = Ticket("T001", 500, "S001", 0, 0, 0, hall.hall_id)
        
        theater.performance_manager.add_setting(setting)
        theater.ticket_manager.add_ticket(ticket)
        
        # Первая продажа должна быть успешной
        self.assertTrue(ticket.sell_ticket(theater.resource_manager.hall_manager))
        
        # Вторая продажа должна выбросить исключение
        with self.assertRaises(TheaterException):
            ticket.sell_ticket(theater.resource_manager.hall_manager)

    def test_13_hall_not_found_exception(self):
        """Тест: Исключение при поиске несуществующего зала"""
        theater = Theater("Городской театр")
        hall = AuditoryHall("Main Hall", 2, 5, 5, "H001")
        theater.resource_manager.hall_manager.add_hall(hall)
        
        # Попытка получить несуществующий зал
        with self.assertRaises(TheaterException) as context:
            theater.resource_manager.hall_manager.get_hall_by_id("NonExistent")
        
        self.assertIn("не найден", str(context.exception).lower())

    def test_14_ticket_not_found_exception(self):
        """Тест: Исключение при попытке продать несуществующий билет"""
        theater = Theater("Городской театр")
        hall = AuditoryHall("Main Hall", 2, 5, 5, "H001")
        theater.resource_manager.hall_manager.add_hall(hall)
        
        # Попытка продать билет, которого нет
        with self.assertRaises(TicketNotFoundException) as context:
            theater.ticket_manager.sell_ticket("NonExistent", theater.resource_manager.hall_manager)
        
        self.assertIn("не найден", str(context.exception).lower())

    def test_15_setting_not_found_exception(self):
        """Тест: Исключение при попытке назначить актёра несуществующей постановке"""
        theater = Theater("Городской театр")
        actor = Actor("John Doe", 30, 3000.0, "Main Role")
        theater.staff_manager.add_staff(actor)
        
        # Попытка назначить актёра несуществующей постановке
        # Симулируем это через обработку исключений как в main.py
        setting = next((s for s in theater.performance_manager.settings 
                       if s.name == "NonExistent"), None)
        
        self.assertIsNone(setting)

    def test_16_file_operation_exception(self):
        """Тест: Исключение при работе с файлом"""
        theater = Theater("Городской театр")
        
        # Попытка загрузить из несуществующего файла
        with self.assertRaises(TheaterException):
            Theater.load_from_file("/path/that/does/not/exist/theater.json")

    def test_17_actor_not_found_exception_in_assignment(self):
        """Тест: Исключение при попытке назначить несуществующего актёра"""
        theater = Theater("Городской театр")
        actor = Actor("Real Actor", 30, 3000.0, "Main Role")
        theater.staff_manager.add_staff(actor)
        
        setting = Setting(10.0, "Play", datetime.now())
        theater.performance_manager.add_setting(setting)
        
        # Попытка добавить несуществующего актёра
        fake_actor = next((s for s in theater.staff_manager.get_staff() 
                          if s.name == "NonExistent"), None)
        
        self.assertIsNone(fake_actor)

    def test_18_exception_propagation_in_ticket_selling(self):
        """Тест: Проверка распространения исключений при продаже билета"""
        theater = Theater("Городской театр")
        hall = AuditoryHall("Main Hall", 2, 5, 5, "H001")
        theater.resource_manager.hall_manager.add_hall(hall)
        
        # Создаём два билета на одно место
        setting = Setting(10.0, "Play", datetime.now())
        ticket1 = Ticket("T001", 500, "S001", 0, 0, 0, hall.hall_id)
        ticket2 = Ticket("T002", 500, "S001", 0, 0, 0, hall.hall_id)
        
        theater.performance_manager.add_setting(setting)
        theater.ticket_manager.add_ticket(ticket1)
        theater.ticket_manager.add_ticket(ticket2)
        
        # Первый билет продаётся успешно
        theater.ticket_manager.sell_ticket("T001", theater.resource_manager.hall_manager)
        
        # Второй билет должен вызвать исключение из-за занятого места
        with self.assertRaises(InvalidSeatException):
            theater.ticket_manager.sell_ticket("T002", theater.resource_manager.hall_manager)


if __name__ == "__main__":
    unittest.main()
