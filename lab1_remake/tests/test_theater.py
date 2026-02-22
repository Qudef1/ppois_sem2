import unittest
import json
import sys
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from theater import Theater, Setting, Repetition, Seat, Ticket, AuditoryHall, Stage, Costume, CostumeRoom, Action
from staff import Person, Staff, Actor, Director, CostumeDesigner
from managers import StaffManager, HallManager, PerformanceManager, TicketManager, ResourceManager
from exception import TheaterException, InvalidSeatException, TicketNotFoundException


class TestCoreModels(unittest.TestCase):
    """Tests for core model classes"""

    def test_person_creation(self):
        p = Person("John", 30)
        self.assertEqual(p.name, "John")
        self.assertEqual(p.get_age(), 30)
        d = p.to_dict()
        self.assertEqual(d, {"name": "John", "age": 30})
        p_restored = Person.from_dict(d)
        self.assertEqual(p_restored.name, "John")

    def test_staff_creation(self):
        s = Staff("Worker", 40, 50000.0)
        self.assertEqual(s.name, "Worker")
        self.assertEqual(s.get_age(), 40)
        self.assertEqual(s.get_salary(), 50000.0)
        d = s.to_dict()
        self.assertEqual(d["name"], "Worker")
        self.assertEqual(d["salary"], 50000.0)

    def test_actor_creation_and_features(self):
        actor = Actor("Leo", 48, 80000.0, "Romeo")
        self.assertEqual(actor.name, "Leo")
        self.assertEqual(actor.role, "Romeo")
        self.assertEqual(actor.assigned_costumes, {})
        
        # Test costume assignment
        costume = Costume("Robe", "M", "Red")
        actor.assign_costume(costume)
        self.assertIn("Robe", actor.assigned_costumes)
        
        # Test removing costume
        actor.remove_costume("Robe")
        self.assertEqual(len(actor.assigned_costumes), 0)
        
        # Test serialization
        actor.assign_costume(costume)
        d = actor.to_dict()
        restored = Actor.from_dict(d)
        self.assertIn("Robe", restored.assigned_costumes)

    def test_actor_new_methods(self):
        Ticket.reset_counter()
        actor = Actor("Actor", 30, 50000.0)
        hall = AuditoryHall("Hall", 2, 5, 10, "h1")
        
        # Test check seat
        self.assertTrue(actor.check_seat_in_hall(hall, 0, 0, 0))
        hall.occupy_seat(0, 0, 0)
        self.assertFalse(actor.check_seat_in_hall(hall, 0, 0, 0))
        
        # Test attend repetition
        director = Director("Dir", 50, 100000.0)
        setting = Setting(2.0, "Play", datetime.now(), director)
        rep = Repetition(1.5, "Rehearsal", datetime.now(), setting)
        result = actor.attend_repetition(rep)
        self.assertTrue(result)
        self.assertEqual(len(rep.attendance_list), 1)

    def test_director_creation(self):
        director = Director("Spielberg", 77, 200000.0)
        self.assertEqual(director.name, "Spielberg")
        self.assertEqual(director.directed_settings, [])
        
        setting = MagicMock()
        director.direct_setting(setting)
        self.assertEqual(len(director.directed_settings), 1)

    def test_action_datetime_serialization(self):
        dt = datetime(2025, 1, 1)
        a = Action(2.0, "Test Action", dt)
        d = a.to_dict()
        self.assertIsInstance(d["date"], str)
        restored = Action.from_dict(d)
        self.assertEqual(restored.name, "Test Action")
        self.assertEqual(restored.durability, 2.0)

    def test_setting_creation_and_serialization(self):
        director = Director("Dir", 50, 100000.0)
        setting = Setting(2.0, "Play", datetime(2025, 1, 1), director)
        
        actor = Actor("Actor", 30, 50000.0)
        setting.add_cast(actor)
        
        self.assertEqual(setting.name, "Play")
        self.assertEqual(len(setting.cast), 1)
        
        d = setting.to_dict()
        restored = Setting.from_dict(d)
        self.assertEqual(restored.name, "Play")
        self.assertEqual(restored.director.name, "Dir")
        self.assertEqual(len(restored.cast), 1)

    def test_repetition_serialization(self):
        director = Director("Dir", 50, 100000.0)
        setting = Setting(2.0, "Play", datetime(2025, 3, 1), director)
        rep = Repetition(1.5, "Rehearsal", datetime(2025, 2, 20), setting)
        
        d = rep.to_dict()
        self.assertIsNotNone(d)
        self.assertEqual(d["name"], "Rehearsal")
        
        restored = Repetition.from_dict(d)
        self.assertEqual(restored.name, "Rehearsal")
        self.assertEqual(restored.durability, 1.5)

    def test_seat_serialization(self):
        s = Seat(5)
        self.assertEqual(s.seat_number, 5)
        self.assertFalse(s.is_occupied)
        
        d = s.to_dict()
        self.assertEqual(d, {"seat_number": 5, "is_occupied": False})
        
        restored = Seat.from_dict(d)
        self.assertEqual(restored.seat_number, 5)
        self.assertFalse(restored.is_occupied)


class TestTheaterInfrastructure(unittest.TestCase):
    """Tests for theater infrastructure components"""

    def test_auditory_hal(self):
        hall = AuditoryHall("Main Hall", 3, 10, 15, "hall_001")
        
        self.assertEqual(hall.name, "Main Hall")
        self.assertEqual(hall.capacity, 450)
        self.assertTrue(hall.is_seat_available(0, 0, 0))
        
        # Test occupying seat
        hall.occupy_seat(0, 0, 0)
        self.assertFalse(hall.is_seat_available(0, 0, 0))
        self.assertEqual(hall.audience_count, 1)
        
        # Test serialization
        d = hall.to_dict()
        restored = AuditoryHall.from_dict(d)
        self.assertEqual(restored.name, "Main Hall")
        self.assertEqual(restored.capacity, 450)

    def test_ticket_auto_id_generation(self):
        Ticket.reset_counter()
        
        t1 = Ticket(100.0, None, 0, 0, 0, "h1")
        t2 = Ticket(200.0, None, 0, 0, 1, "h1")
        
        self.assertEqual(t1.ticket_id, "TKT-000001")
        self.assertEqual(t2.ticket_id, "TKT-000002")

    def test_ticket_functionality(self):
        Ticket.reset_counter()
        director = Director("Dir", 50, 100000.0)
        setting = Setting(2.0, "Play", datetime.now(), director)
        hall = AuditoryHall("Hall", 2, 5, 10, "h1")

        # Привязываем постановку к залу — билеты создаются автоматически
        tickets = setting.bind_to_hall(hall, base_price=150.0)

        self.assertEqual(len(tickets), hall.capacity)  # Все места зала
        ticket = tickets[0]

        self.assertEqual(ticket.price, 150.0)
        self.assertEqual(ticket.hall_id, "h1")
        self.assertFalse(ticket.is_sold)  # Билет ещё не продан

        # Test selling ticket
        result = ticket.sell_ticket()
        self.assertTrue(result)
        self.assertTrue(ticket.is_sold)
        self.assertFalse(hall.is_seat_available(0, 0, 0))

        # Test selling same ticket again (should fail)
        try:
            ticket.sell_ticket()
            self.fail("Ожидалось TheaterException")
        except TheaterException:
            pass  # Ожидаемое поведение

    def test_ticket_hall_linking(self):
        director = Director("Dir", 50, 100000.0)
        setting = Setting(2.0, "Play", datetime.now(), director)
        hall = AuditoryHall("Hall", 2, 5, 10, "h1")

        # Билеты создаются при привязке к залу
        tickets = setting.bind_to_hall(hall, base_price=100.0)
        ticket = tickets[0]
        
        # После привязки hall уже связан
        self.assertEqual(ticket.hall, hall)

    def test_setting_bind_to_hall_creates_tickets(self):
        """Тест привязки постановки к залу и автоматического создания билетов."""
        Ticket.reset_counter()
        director = Director("Dir", 50, 100000.0)
        setting = Setting(2.0, "Play", datetime.now(), director)
        hall = AuditoryHall("Hall", 2, 5, 10, "h1")  # 2 * 5 * 10 = 100 мест
        
        # Привязываем постановку к залу
        tickets = setting.bind_to_hall(hall, base_price=150.0)
        
        # Проверяем количество билетов
        self.assertEqual(len(tickets), hall.capacity)
        self.assertEqual(len(tickets), 100)
        
        # Проверяем связь с залом
        for ticket in tickets:
            self.assertEqual(ticket.hall, hall)
            self.assertFalse(ticket.is_sold)
        
        # Проверяем ценообразование (зависит от сектора)
        # Сектор 0: полная цена 150.0
        # Сектор 1: цена со скидкой 20% = 120.0
        sector_0_tickets = [t for t in tickets if t.sector == 0]
        sector_1_tickets = [t for t in tickets if t.sector == 1]
        
        self.assertEqual(sector_0_tickets[0].price, 150.0)
        self.assertEqual(sector_1_tickets[0].price, 120.0)  # 150 * 0.8
        
        # Проверяем сериализацию
        d = setting.to_dict()
        self.assertEqual(d["hall_id"], "h1")
        self.assertEqual(d["base_price"], 150.0)
        self.assertEqual(len(d["tickets"]), 100)

    def test_actor_play_method(self):
        """Тест метода play() у актёра."""
        # Актёр с ролью
        actor_hamlet = Actor("Ivanov", 30, 50000.0, "Hamlet")
        replika = actor_hamlet.play()
        self.assertIn("Ivanov", replika)
        self.assertIn("Hamlet", replika)
        self.assertIn("Быть или не быть", replika)
        
        # Актёр без роли
        actor_no_role = Actor("Sidorov", 25, 45000.0)
        replika_no_role = actor_no_role.play()
        self.assertIn("Sidorov", replika_no_role)
        self.assertIn("поклон", replika_no_role)
        
        # Актёр с постановкой
        director = Director("Dir", 50, 100000.0)
        setting = Setting(2.0, "Test Play", datetime.now(), director)
        replika_with_setting = actor_no_role.play(setting)
        self.assertIn("Test Play", replika_with_setting)
        self.assertIn("импровизирует", replika_with_setting)

    def test_actor_perform_on_stage(self):
        """Тест метода perform_on_stage() у актёра."""
        actor = Actor("Petrov", 35, 55000.0, "King")
        stage = Stage("Main Stage", 500, ["Lights"])
        
        # Выступление на доступной сцене
        output = actor.perform_on_stage(stage)
        self.assertIn("Main Stage", output)
        self.assertIn("King", output)
        self.assertIn("ВЫСТУПЛЕНИЕ", output)
        
        # Выступление на недоступной сцене
        stage.is_available = False
        output_unavailable = actor.perform_on_stage(stage)
        self.assertIn("недоступна", output_unavailable)

    def test_stage_serialization(self):
        stage = Stage("Main Stage", 500, ["Lights", "Sound"])
        self.assertEqual(stage.name, "Main Stage")
        self.assertEqual(stage.capacity, 500)
        
        d = stage.to_dict()
        restored = Stage.from_dict(d)
        self.assertEqual(restored.name, "Main Stage")
        self.assertTrue(restored.is_available)

    def test_costume_serialization(self):
        costume = Costume("Romeo Costume", "M", "Red and Gold")
        self.assertEqual(costume.name, "Romeo Costume")
        
        d = costume.to_dict()
        restored = Costume.from_dict(d)
        self.assertEqual(restored.name, "Romeo Costume")
        self.assertEqual(restored.color, "Red and Gold")

    def test_costume_room_serialization(self):
        room = CostumeRoom("Main Room")
        self.assertEqual(room.name, "Main Room")
        self.assertEqual(room.costume_ids, [])
        
        room.costume_ids.append("costume1")
        d = room.to_dict()
        restored = CostumeRoom.from_dict(d)
        self.assertEqual(restored.name, "Main Room")
        self.assertEqual(restored.costume_ids, ["costume1"])


class TestManagers(unittest.TestCase):
    """Tests for manager classes"""

    def test_staff_manager(self):
        sm = StaffManager()
        actor = Actor("Actor", 30, 50000.0)
        director = Director("Dir", 50, 100000.0)
        
        sm.add_staff(actor)
        sm.add_staff(director)
        
        self.assertEqual(len(sm.get_staff()), 2)
        
        # Test serialization
        d = sm.to_dict()
        restored = StaffManager.from_dict(d)
        self.assertEqual(len(restored.get_staff()), 2)

    def test_hall_manager(self):
        hm = HallManager()
        hall = AuditoryHall("Hall1", 2, 5, 10, "h1")
        hm.add_hall(hall)
        
        self.assertEqual(len(hm.halls), 1)
        found = hm.get_hall_by_id("h1")
        self.assertEqual(found.name, "Hall1")
        
        # Test serialization
        d = hm.to_dict()
        restored = HallManager.from_dict(d)
        self.assertEqual(len(restored.halls), 1)

    def test_ticket_manager(self):
        Ticket.reset_counter()
        tm = TicketManager()
        director = Director("Dir", 50, 100000.0)
        setting = Setting(2.0, "Play", datetime.now(), director)
        hall = AuditoryHall("Hall", 2, 5, 10, "h1")
        
        t = Ticket(100.0, setting, 0, 0, 0, "h1", hall)
        t.set_ticket_id("t1")
        tm.add_ticket(t)
        
        self.assertEqual(len(tm.get_all_tickets()), 1)
        
        # Test selling via manager
        hm = HallManager()
        hm.add_hall(hall)
        result = tm.sell_ticket("t1", hm)
        self.assertTrue(result)

    def test_resource_manager(self):
        rm = ResourceManager()
        self.assertEqual(len(rm.stages), 0)
        self.assertEqual(len(rm.costumes), 0)
        self.assertEqual(len(rm.costume_rooms), 0)
        
        # Add some resources
        rm.add_stage(Stage("Stage1", 500, ["Lights"]))
        rm.add_costume(Costume("Dress", "M", "Red"))
        rm.add_costume_room(CostumeRoom("Room1"))
        rm.hall_manager.add_hall(AuditoryHall("Hall1", 2, 5, 10, "h1"))
        
        self.assertEqual(len(rm.stages), 1)
        self.assertEqual(len(rm.costumes), 1)
        self.assertEqual(len(rm.costume_rooms), 1)
        
        # Test serialization
        d = rm.to_dict()
        restored = ResourceManager.from_dict(d)
        self.assertEqual(len(restored.stages), 1)
        self.assertEqual(len(restored.costumes), 1)
        self.assertEqual(len(restored.costume_rooms), 1)
        self.assertEqual(len(restored.hall_manager.halls), 1)


class TestTheater(unittest.TestCase):
    """Tests for main Theater class"""

    def setUp(self):
        Ticket.reset_counter()
        self.theater = Theater("Test Theater")

    def test_theater_creation(self):
        self.assertEqual(self.theater.name, "Test Theater")
        self.assertIsNotNone(self.theater.staff_manager)

    def test_theater_operations(self):
        # Add staff
        actor = Actor("Actor", 30, 50000.0)
        director = Director("Dir", 50, 100000.0)
        self.theater.add_staff(actor)
        self.theater.add_staff(director)
        
        self.assertEqual(len(self.theater.staff_manager.get_staff()), 2)
        
        # Add hall
        hall = AuditoryHall("Hall", 2, 5, 10, "h1")
        self.theater.add_hall(hall)
        self.assertEqual(len(self.theater.resource_manager.hall_manager.halls), 1)
        
        # Add setting
        setting = Setting(2.0, "Play", datetime.now(), director)
        self.theater.add_setting(setting)
        self.assertEqual(len(self.theater.performance_manager.settings), 1)

        # Bind setting to hall - tickets are created automatically
        self.theater.bind_setting_to_hall("Play", "h1", base_price=100.0)
        
        # Check that tickets were created
        self.assertEqual(len(self.theater.ticket_manager.tickets), hall.capacity)
        
        # Sell first ticket
        first_ticket = self.theater.ticket_manager.tickets[0]
        result = self.theater.sell_ticket(first_ticket.ticket_id)
        self.assertTrue(result)
        self.assertTrue(first_ticket.is_sold)

    def test_save_load_complex_scene(self):
        temp_dir = tempfile.mkdtemp()
        try:
            # Create complex scene
            actor = Actor("Actor", 30, 50000.0, "Lead")
            director = Director("Director", 50, 100000.0)
            costume = Costume("Royal Gown", "M", "Gold")

            hall = AuditoryHall("Main Hall", 3, 10, 15, "main_001")
            setting = Setting(180.0, "Grand Play", datetime(2025, 6, 1), director)
            setting.add_cast(actor)

            # Add to theater
            self.theater.add_staff(actor)
            self.theater.add_staff(director)
            self.theater.add_hall(hall)
            self.theater.add_setting(setting)
            
            # Bind setting to hall - tickets created automatically
            self.theater.bind_setting_to_hall("Grand Play", "main_001", base_price=200.0)
            
            # Check tickets were created
            total_tickets = hall.capacity  # 3 * 10 * 15 = 450
            self.assertEqual(len(self.theater.ticket_manager.tickets), total_tickets)

            # Sell first ticket
            first_ticket = self.theater.ticket_manager.tickets[0]
            self.theater.sell_ticket(first_ticket.ticket_id)

            # Save and load
            filepath = os.path.join(temp_dir, "theater.json")
            self.theater.save_to_file(filepath)

            new_theater = Theater("Restored")
            new_theater.load_from_file(filepath)

            # Verify restoration
            self.assertEqual(new_theater.name, "Test Theater")
            self.assertEqual(len(new_theater.staff_manager.get_staff()), 2)
            self.assertEqual(len(new_theater.resource_manager.hall_manager.halls), 1)
            self.assertEqual(len(new_theater.performance_manager.settings), 1)
            self.assertEqual(len(new_theater.ticket_manager.tickets), total_tickets)

            loaded_hall = new_theater.resource_manager.hall_manager.get_hall_by_id("main_001")
            self.assertFalse(loaded_hall.is_seat_available(0, 0, 0))

        finally:
            shutil.rmtree(temp_dir)


class TestExceptions(unittest.TestCase):
    """Tests for custom exceptions"""

    def test_theater_exception(self):
        with self.assertRaises(TheaterException):
            raise TheaterException("Test error")

    def test_invalid_seat_exception(self):
        hall = AuditoryHall("Test", 1, 1, 1, "t1")
        try:
            hall.is_seat_available(10, 10, 10)  # Invalid coords
            self.fail("Ожидалось InvalidSeatException")
        except InvalidSeatException:
            pass  # Ожидаемое поведение


if __name__ == '__main__':
    unittest.main()
