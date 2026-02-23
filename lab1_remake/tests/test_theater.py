import unittest
import json
import sys
import os
import tempfile
import shutil
from datetime import datetime
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from theater import Theater, Setting, Repetition, Seat, Ticket, AuditoryHall, Stage, Costume, CostumeRoom
from staff import Person, Staff, Actor, Director, CostumeDesigner
from managers import StaffManager, HallManager, PerformanceManager, TicketManager, ResourceManager
from exception import TheaterException, InvalidSeatException, TicketNotFoundException


class TestModels(unittest.TestCase):
    """Тесты основных моделей — 4 теста вместо 9"""

    def test_staff_and_serialization(self):
        """Тест сотрудников и сериализации"""
        # Person
        p = Person("John", 30)
        self.assertEqual(p.name, "John")
        
        # Staff
        s = Staff("Worker", 40, 50000.0)
        self.assertEqual(s.get_salary(), 50000.0)
        d = s.to_dict()
        self.assertEqual(s.from_dict(d).name, "Worker")
        
        # Actor
        actor = Actor("Leo", 48, 80000.0, "Romeo")
        self.assertEqual(actor.role, "Romeo")
        costume = Costume("Robe", "M", "Red")
        actor.assign_costume(costume)
        self.assertIn("Robe", actor.assigned_costumes)
        
        # Director
        director = Director("Dir", 50, 100000.0)
        director.direct_setting(MagicMock())
        self.assertEqual(len(director.directed_settings), 1)

    def test_setting_and_repetition(self):
        """Тест постановок и репетиций"""
        director = Director("Dir", 50, 100000.0)
        actor = Actor("Actor", 30, 50000.0)
        setting = Setting(2.0, "Play", datetime(2025, 1, 1), director)
        setting.add_cast(actor=actor)
        
        self.assertEqual(setting.name, "Play")
        self.assertEqual(len(setting.cast), 1)
        
        # Сериализация
        d = setting.to_dict()
        restored = Setting.from_dict(d)
        self.assertEqual(restored.name, "Play")
        
        # Репетиция
        rep = Repetition(1.5, "Rehearsal", datetime.now(), setting)
        rep.check_list(actor)
        self.assertEqual(len(rep.attendance_list), 1)

    def test_hall_and_seats(self):
        """Тест зала и мест"""
        hall = AuditoryHall("Main Hall", 3, 10, 15, "hall_001")
        self.assertEqual(hall.capacity, 450)
        self.assertTrue(hall.is_seat_available(0, 0, 0))
        
        hall.occupy_seat(0, 0, 0)
        self.assertFalse(hall.is_seat_available(0, 0, 0))
        self.assertEqual(hall.audience_count, 1)
        
        # Сериализация
        d = hall.to_dict()
        restored = AuditoryHall.from_dict(d)
        self.assertEqual(restored.capacity, 450)

    def test_ticket_and_sell(self):
        """Тест билетов и продажи"""
        Ticket.reset_counter()
        director = Director("Dir", 50, 100000.0)
        setting = Setting(2.0, "Play", datetime.now(), director)
        hall = AuditoryHall("Hall", 2, 5, 10, "h1")
        
        # Создание билетов через привязку
        tickets = setting.bind_to_hall(hall, base_price=150.0)
        self.assertEqual(len(tickets), 100)
        
        ticket = tickets[0]
        self.assertEqual(ticket.price, 150.0)
        self.assertFalse(ticket.is_sold)
        
        # Продажа
        result = ticket.sell_ticket()
        self.assertTrue(result)
        self.assertTrue(ticket.is_sold)
        
        # Повторная продажа должна вызвать ошибку
        with self.assertRaises(TheaterException):
            ticket.sell_ticket()


class TestManagers(unittest.TestCase):
    """Тесты менеджеров — 2 теста вместо 4"""

    def test_staff_and_hall_managers(self):
        """Тест StaffManager и HallManager"""
        sm = StaffManager()
        sm.add_staff(Actor("Actor", 30, 50000.0))
        sm.add_staff(Director("Dir", 50, 100000.0))
        self.assertEqual(len(sm.get_staff()), 2)
        
        # Сериализация
        d = sm.to_dict()
        restored = StaffManager.from_dict(d)
        self.assertEqual(len(restored.get_staff()), 2)
        
        hm = HallManager()
        hall = AuditoryHall("Hall1", 2, 5, 10, "h1")
        hm.add_hall(hall)
        self.assertEqual(hm.get_hall_by_id("h1").name, "Hall1")

    def test_resource_manager(self):
        """Тест ResourceManager"""
        rm = ResourceManager()
        rm.add_stage(Stage("Stage1", 500, ["Lights"]))
        rm.add_costume(Costume("Dress", "M", "Red"))
        rm.add_costume_room(CostumeRoom("Room1"))
        rm.hall_manager.add_hall(AuditoryHall("Hall1", 2, 5, 10, "h1"))
        
        self.assertEqual(len(rm.stages), 1)
        self.assertEqual(len(rm.costumes), 1)
        
        # Сериализация
        d = rm.to_dict()
        restored = ResourceManager.from_dict(d)
        self.assertEqual(len(restored.stages), 1)


class TestTheater(unittest.TestCase):
    """Тесты Theater — 4 теста вместо 6"""

    def setUp(self):
        Ticket.reset_counter()
        self.theater = Theater("Test Theater")

    def test_theater_basic_operations(self):
        """Базовые операции театра"""
        self.assertEqual(self.theater.name, "Test Theater")
        
        # Добавление сотрудников
        self.theater.add_staff(Actor("Actor", 30, 50000.0))
        self.theater.add_staff(Director("Dir", 50, 100000.0))
        self.assertEqual(len(self.theater.staff_manager.get_staff()), 2)
        
        # Добавление зала
        hall = AuditoryHall("Hall", 2, 5, 10, "h1")
        self.theater.add_hall(hall)
        self.assertEqual(len(self.theater.resource_manager.hall_manager.halls), 1)
        
        # Добавление постановки
        setting = Setting(2.0, "Play", datetime.now(), 
                         self.theater.staff_manager.get_staff()[1])
        self.theater.add_setting(setting)
        self.assertEqual(len(self.theater.performance_manager.settings), 1)

    def test_bind_setting_and_sell_tickets(self):
        """Привязка постановки к залу и продажа билетов"""
        director = Director("Dir", 50, 100000.0)
        hall = AuditoryHall("Hall", 2, 5, 10, "h1")
        setting = Setting(2.0, "Play", datetime.now(), director)
        
        self.theater.add_staff(director)
        self.theater.add_hall(hall)
        self.theater.add_setting(setting)
        
        # Привязка и создание билетов
        self.theater.bind_setting_to_hall("Play", "h1", base_price=100.0)
        self.assertEqual(len(self.theater.ticket_manager.tickets), 100)
        
        # Продажа первого билета
        first_ticket = self.theater.ticket_manager.tickets[0]
        result = self.theater.sell_ticket(first_ticket.ticket_id)
        self.assertTrue(result)
        self.assertTrue(first_ticket.is_sold)

    def test_save_load_theater(self):
        """Сохранение и загрузка театра"""
        director = Director("Director", 50, 100000.0)
        hall = AuditoryHall("Main Hall", 3, 10, 15, "main_001")
        setting = Setting(180.0, "Grand Play", datetime(2025, 6, 1), director)
        
        self.theater.add_staff(director)
        self.theater.add_hall(hall)
        self.theater.add_setting(setting)
        self.theater.bind_setting_to_hall("Grand Play", "main_001", base_price=200.0)
        
        # Продажа билета
        self.theater.sell_ticket(self.theater.ticket_manager.tickets[0].ticket_id)
        
        # Сохранение и загрузка
        temp_dir = tempfile.mkdtemp()
        try:
            filepath = os.path.join(temp_dir, "theater.json")
            self.theater.save_to_file(filepath)
            
            new_theater = Theater("Restored")
            new_theater.load_from_file(filepath)
            
            self.assertEqual(new_theater.name, "Test Theater")
            self.assertEqual(len(new_theater.staff_manager.get_staff()), 1)
            self.assertEqual(len(new_theater.resource_manager.hall_manager.halls), 1)
            self.assertEqual(len(new_theater.ticket_manager.tickets), 450)
            
            # Проверка проданного билета
            loaded_hall = new_theater.resource_manager.hall_manager.get_hall_by_id("main_001")
            self.assertFalse(loaded_hall.is_seat_available(0, 0, 0))
        finally:
            shutil.rmtree(temp_dir)

    def test_exceptions(self):
        """Тест исключений"""
        # InvalidSeatException
        hall = AuditoryHall("Test", 1, 1, 1, "t1")
        with self.assertRaises(InvalidSeatException):
            hall.is_seat_available(10, 10, 10)
        
        # TicketNotFoundException
        tm = TicketManager()
        with self.assertRaises(TicketNotFoundException):
            tm.sell_ticket("nonexistent", HallManager())


if __name__ == '__main__':
    unittest.main()
