"""Тест для генерации сложного JSON с данными театра."""

import unittest
import sys
import os
import tempfile
import shutil
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from theater import Theater
from actions import Setting, Repetition
from halls import AuditoryHall
from resources import Costume, Stage, CostumeRoom
from staff import Actor, Director
from seats import Ticket


def reset_ticket_counter():
    """Сброс счётчика билетов."""
    Ticket._counter = 0


class TestGenerateComplexTheater(unittest.TestCase):
    """Генерация театра со сложными данными."""

    def test_generate_complex_theater_json(self):
        """
        Создаёт театр с данными:
        - 4 постановки
        - 3 зала
        - 12 актёров
        - 3 режиссёра
        - 20 костюмов
        - 3 костюмерные
        - 2 сцены
        - 3 репетиции

        Сохраняет в JSON и проверяет загрузку.
        """
        reset_ticket_counter()

        # Создаём театр
        theater = Theater("Большой Театр Драмы")

        # ==================== СОТРУДНИКИ ====================
        # 12 актёров
        actors_data = [
            ("Иванов Иван", 35, "Гамлет"),
            ("Петров Пётр", 42, "Король Лир"),
            ("Сидоров Сидор", 28, "Ромео"),
            ("Кузнецов Алексей", 31, "Макбет"),
            ("Смирнов Дмитрий", 45, "Отелло"),
            ("Попов Андрей", 38, "Генрих V"),
            ("Васильев Василий", 33, "Ричард III"),
            ("Михайлов Михаил", 29, "Перикл"),
            ("Новиков Николай", 40, "Тимон Афинский"),
            ("Фёдоров Фёдор", 36, "Кориолан"),
            ("Морозов Мороз", 44, "Антоний"),
            ("Волков Волк", 32, "Брут"),
        ]

        actors = []
        for name, age, role in actors_data:
            actor = Actor(name, age, 75000.0, role)
            theater.add_staff(actor)
            actors.append(actor)

        # 3 режиссёра
        directors_data = [
            ("Сергей Михалков", 55),
            ("Анна Каренина", 48),
            ("Дмитрий Хармс", 62),
        ]

        directors = []
        for name, age in directors_data:
            director = Director(name, age, 120000.0)
            theater.add_staff(director)
            directors.append(director)

        # ==================== ЗАЛЫ ====================
        halls_data = [
            ("Большой зал", "main_hall", 5, 20, 30),
            ("Малый зал", "small_hall", 3, 15, 20),
            ("Экспериментальный", "exp_hall", 2, 10, 15),
        ]

        halls = []
        for name, hall_id, sectors, rows, seats in halls_data:
            hall = AuditoryHall(name, sectors, rows, seats, hall_id)
            theater.add_hall(hall)
            halls.append(hall)

        # ==================== КОСТЮМЫ ====================
        costumes_data = [
            ("Королевская мантия", "XL", "Пурпурный"),
            ("Рыцарские латы", "L", "Серебряный"),
            ("Платье Джульетты", "M", "Розовый"),
            ("Плащ Гамлета", "L", "Чёрный"),
            ("Одеяние короля", "XXL", "Золотой"),
            ("Костюм шута", "M", "Разноцветный"),
            ("Доспехи воина", "L", "Стальной"),
            ("Платье королевы", "M", "Изумрудный"),
            ("Мантия волшебника", "L", "Синий"),
            ("Костюм слуги", "S", "Серый"),
            ("Одеяние жреца", "L", "Белый"),
            ("Плащ убийцы", "M", "Тёмно-зелёный"),
            ("Платье крестьянки", "M", "Коричневый"),
            ("Костюм торговца", "L", "Оранжевый"),
            ("Мантия судьи", "XL", "Красный"),
            ("Одеяние врача", "L", "Бордовый"),
            ("Костюм музыканта", "M", "Голубой"),
            ("Плащ путешественника", "L", "Зелёный"),
            ("Платье принцессы", "S", "Нежно-розовый"),
            ("Доспехи капитана", "XL", "Чёрно-золотой"),
        ]

        costumes = []
        for name, size, color in costumes_data:
            costume = theater.create_costume(name, size, color)
            costumes.append(costume)

        # ==================== КОСТЮМЕРНЫЕ ====================
        costume_rooms_data = [
            ("Основная костюмерная", 0),
            ("Костюмерная для актёров", 1),
            ("Исторические костюмы", 2),
        ]

        for name, start_idx in costume_rooms_data:
            room = CostumeRoom(name)
            for i in range(5):
                idx = (start_idx * 5 + i) % len(costumes)
                room.costume_ids.append(costumes[idx].name)
            theater.resource_manager.add_costume_room(room)

        # ==================== СЦЕНЫ ====================
        stages_data = [
            ("Главная сцена", 500, ["Прожекторы", "Подъёмник", "Поворотный круг"]),
            ("Камерная сцена", 150, ["Проектор", "Звуковая система"]),
        ]

        for name, capacity, equipment in stages_data:
            stage = Stage(name, capacity, equipment)
            theater.resource_manager.add_stage(stage)

        # ==================== ПОСТАНОВКИ ====================
        settings_data = [
            ("Гамлет", datetime(2025, 6, 15), 0, ["Гамлет", "Король Лир", "Ромео"]),
            ("Король Лир", datetime(2025, 7, 20), 1, ["Король Лир", "Гамлет", "Макбет"]),
            ("Ромео и Джульетта", datetime(2025, 8, 10), 2, ["Ромео", "Гамлет"]),
            ("Макбет", datetime(2025, 9, 5), 0, ["Макбет", "Король Лир", "Отелло"]),
        ]

        settings = []
        for name, date, director_idx, cast_roles in settings_data:
            director = directors[director_idx]
            setting = Setting(2.5, name, date, director)

            for role in cast_roles:
                for actor in actors:
                    if actor.role == role:
                        setting.add_cast(actor)
                        # Назначаем костюм
                        if actor.role == "Гамлет":
                            theater.assign_costume_to_actor(costumes[3], actor)
                        elif actor.role == "Король Лир":
                            theater.assign_costume_to_actor(costumes[4], actor)
                        elif actor.role == "Ромео":
                            theater.assign_costume_to_actor(costumes[2], actor)

            theater.add_setting(setting)
            settings.append(setting)

        # ==================== РЕПЕТИЦИИ ====================
        for i, setting in enumerate(settings[:3]):
            rep_date = setting.date - timedelta(days=7)
            rep = Repetition(3.0, f"Репетиция: {setting.name}", rep_date, setting)

            for actor in setting.cast:
                rep.check_list(actor)

            theater.performance_manager.add_repetition(rep)

        # ==================== БИЛЕТЫ ====================
        for setting in settings:
            for hall in halls:
                base_price = 500.0 if hall.hall_id == "main_hall" else (300.0 if hall.hall_id == "small_hall" else 200.0)
                theater.bind_setting_to_hall(setting.name, hall.hall_id, base_price)

        # Продаём ~30% билетов
        all_tickets = theater.ticket_manager.tickets
        sold_count = len(all_tickets) // 3
        for i in range(sold_count):
            if i < len(all_tickets):
                try:
                    theater.sell_ticket(all_tickets[i].ticket_id)
                except Exception:
                    pass

        # ==================== СОХРАНЕНИЕ ====================
        temp_dir = tempfile.mkdtemp()
        filepath = os.path.join(temp_dir, "complex_theater.json")
        theater.save_to_file(filepath)

        # ==================== ПРОВЕРКА ====================
        loaded = Theater("Temp")
        loaded.load_from_file(filepath)

        self.assertEqual(loaded.name, "Большой Театр Драмы")
        self.assertEqual(len(loaded.staff_manager.staff), 15)  # 12 + 3
        self.assertEqual(len(loaded.resource_manager.hall_manager.halls), 3)
        self.assertEqual(len(loaded.performance_manager.settings), 4)
        self.assertEqual(len(loaded.performance_manager.repetitions), 3)
        self.assertEqual(len(loaded.resource_manager.costumes), 20)
        self.assertEqual(len(loaded.resource_manager.costume_rooms), 3)
        self.assertEqual(len(loaded.resource_manager.stages), 2)

        self.assertGreater(len(loaded.ticket_manager.tickets), 0)

        sold = sum(1 for t in loaded.ticket_manager.tickets if t.is_sold)
        self.assertGreater(sold, 0)

        # Проверка синхронизации: проданные билеты == занятые места
        for hall in loaded.resource_manager.hall_manager.halls:
            occupied_in_hall = sum(
                1 for sector in hall.seats
                for row in sector
                for seat in row
                if seat.is_occupied
            )
            occupied_by_tickets = sum(
                1 for t in loaded.ticket_manager.tickets
                if t.hall_id == hall.hall_id and t.is_sold
            )
            self.assertEqual(occupied_in_hall, occupied_by_tickets,
                f"Зал {hall.name}: места ({occupied_in_hall}) != билеты ({occupied_by_tickets})")

        # ==================== СТАТИСТИКА ====================
        print("\n" + "=" * 60)
        print("СТАТИСТИКА ТЕАТРА")
        print("=" * 60)
        print(f"Название: {loaded.name}")
        print(f"Сотрудников: {len(loaded.staff_manager.staff)}")
        print(f"  - Актёров: {sum(1 for s in loaded.staff_manager.staff if isinstance(s, Actor))}")
        print(f"  - Режиссёров: {sum(1 for s in loaded.staff_manager.staff if isinstance(s, Director))}")
        print(f"Залов: {len(loaded.resource_manager.hall_manager.halls)}")
        print(f"Постановок: {len(loaded.performance_manager.settings)}")
        print(f"Репетиций: {len(loaded.performance_manager.repetitions)}")
        print(f"Костюмов: {len(loaded.resource_manager.costumes)}")
        print(f"Костюмерных: {len(loaded.resource_manager.costume_rooms)}")
        print(f"Сцен: {len(loaded.resource_manager.stages)}")
        print(f"Билетов всего: {len(loaded.ticket_manager.tickets)}")
        print(f"Продано билетов: {sold}")
        print(f"Выручка: {sum(t.price for t in loaded.ticket_manager.tickets if t.is_sold):.2f} руб.")
        print("=" * 60)
        print(f"Файл сохранён: {filepath}")
        print("=" * 60)

        # Копируем файл в data/
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        dest_path = os.path.join(data_dir, "complex_theater.json")
        shutil.copy(filepath, dest_path)
        print(f"Копия сохранена: {dest_path}")


if __name__ == '__main__':
    unittest.main()
