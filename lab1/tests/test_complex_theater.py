"""Тест для генерации сложного JSON с данными театра."""

import unittest
import sys
import os
import tempfile
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from theater import Theater, Setting, Repetition, AuditoryHall, Costume, Stage, CostumeRoom
from staff import Actor, Director, CostumeDesigner
from managers import StaffManager


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
        Ticket_reset_counter()
        
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
        
        # 2 костюмера
        designers_data = [
            ("Елена Прекрасная", 40),
            ("Мария Искусная", 35),
        ]
        
        designers = []
        for name, age in designers_data:
            designer = CostumeDesigner(name, age, 65000.0)
            theater.add_staff(designer)
            designers.append(designer)
        
        # ==================== ЗАЛЫ ====================
        # 3 зала
        halls_data = [
            ("Большой зал", "main_hall", 5, 20, 30),    # 3000 мест
            ("Малый зал", "small_hall", 3, 15, 20),     # 900 мест
            ("Экспериментальный", "exp_hall", 2, 10, 15), # 300 мест
        ]
        
        halls = []
        for name, hall_id, sectors, rows, seats in halls_data:
            hall = AuditoryHall(name, sectors, rows, seats, hall_id)
            theater.add_hall(hall)
            halls.append(hall)
        
        # ==================== КОСТЮМЫ ====================
        # 20 костюмов
        costumes_data = [
            ("Королевская мантия", "XL", "Пурпурный"),
            ("Рыцарские латы", "L", "Серебряный"),
            ("Платьо Джульетты", "M", "Розовый"),
            ("Плащ Гамлета", "L", "Чёрный"),
            ("Одеяние короля", "XXL", "Золотой"),
            ("Костюм шута", "M", "Разноцветный"),
            ("Доспехи воина", "L", "Стальной"),
            ("Платьо королевы", "M", "Изумрудный"),
            ("Мантия волшебника", "L", "Синий"),
            ("Костюм слуги", "S", "Серый"),
            ("Одеяние жреца", "L", "Белый"),
            ("Плащ убийцы", "M", "Тёмно-зелёный"),
            ("Платьо крестьянки", "M", "Коричневый"),
            ("Костюм торговца", "L", "Оранжевый"),
            ("Мантия судьи", "XL", "Красный"),
            ("Одеяние врача", "L", "Бордовый"),
            ("Костюм музыканта", "M", "Голубой"),
            ("Плащ путешественника", "L", "Зелёный"),
            ("Платьо принцессы", "S", "Нежно-розовый"),
            ("Доспехи капитана", "XL", "Чёрно-золотой"),
        ]
        
        costumes = []
        for name, size, color in costumes_data:
            costume = Costume(name, size, color)
            theater.resource_manager.add_costume(costume)
            costumes.append(costume)
            
            # Добавляем костюмеру
            if len(designers) > 0:
                designers[0].create_costume(costume)
        
        # ==================== КОСТЮМЕРНЫЕ ====================
        # 3 костюмерные
        costume_rooms_data = [
            ("Основная костюмерная", 0),
            ("Костюмерная для актёров", 1),
            ("Исторические костюмы", 2),
        ]
        
        for name, start_idx in costume_rooms_data:
            room = CostumeRoom(name)
            # Добавляем по 5-7 костюмов в каждую
            for i in range(5):
                idx = (start_idx * 5 + i) % len(costumes)
                room.costume_ids.append(costumes[idx].name)
            theater.resource_manager.add_costume_room(room)
        
        # ==================== СЦЕНЫ ====================
        # 2 сцены
        stages_data = [
            ("Главная сцена", 500, ["Прожекторы", "Подъёмник", "Поворотный круг"]),
            ("Камерная сцена", 150, ["Проектор", "Звуковая система"]),
        ]
        
        for name, capacity, equipment in stages_data:
            stage = Stage(name, capacity, equipment)
            theater.resource_manager.add_stage(stage)
        
        # ==================== ПОСТАНОВКИ ====================
        # 4 постановки
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
            
            # Добавляем актёров по ролям
            for role in cast_roles:
                for actor in actors:
                    if actor.role == role:
                        setting.add_cast(actor)
                        # Назначаем костюм
                        if actor.role == "Гамлет":
                            actor.assign_costume(costumes[3])  # Плащ Гамлета
                        elif actor.role == "Король Лир":
                            actor.assign_costume(costumes[4])  # Одеяние короля
                        elif actor.role == "Ромео":
                            actor.assign_costume(costumes[2])  # Платьо Джульетты (для актёра на роли)
            
            theater.add_setting(setting)
            settings.append(setting)
        
        # Убираем циклическую ссылку: Director.directed_settings не сериализуем
        for director in directors:
            director.directed_settings = []
        
        # ==================== РЕПЕТИЦИИ ====================
        # 3 репетиции
        for i, setting in enumerate(settings[:3]):
            rep_date = setting.date - timedelta(days=7)
            rep = Repetition(3.0, f"Репетиция: {setting.name}", rep_date, setting)
            
            # Добавляем актёров из постановки
            for actor in setting.cast:
                rep.check_list(actor)
            
            theater.performance_manager.add_repetition(rep)
        
        # ==================== БИЛЕТЫ ====================
        # Создаём билеты для каждой постановки в каждом зале
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
                    pass  # Некоторые билеты уже могут быть проданы
        
        # ==================== СОХРАНЕНИЕ ====================
        temp_dir = tempfile.mkdtemp()
        filepath = os.path.join(temp_dir, "complex_theater.json")
        theater.save_to_file(filepath)
        
        # ==================== ПРОВЕРКА ====================
        # Загружаем и проверяем
        loaded = Theater("Temp")
        loaded.load_from_file(filepath)
        
        # Проверка количества
        self.assertEqual(loaded.name, "Большой Театр Драмы")
        self.assertEqual(len(loaded.staff_manager.staff), 17)  # 12 + 3 + 2
        self.assertEqual(len(loaded.resource_manager.hall_manager.halls), 3)
        self.assertEqual(len(loaded.performance_manager.settings), 4)
        self.assertEqual(len(loaded.performance_manager.repetitions), 3)
        self.assertEqual(len(loaded.resource_manager.costumes), 20)
        self.assertEqual(len(loaded.resource_manager.costume_rooms), 3)
        self.assertEqual(len(loaded.resource_manager.stages), 2)
        
        # Проверка что билеты созданы
        self.assertGreater(len(loaded.ticket_manager.tickets), 0)
        
        # Проверка проданных билетов
        sold = sum(1 for t in loaded.ticket_manager.tickets if t.is_sold)
        self.assertGreater(sold, 0)

        # Вывод статистики
        print("\n" + "=" * 60)
        print("СТАТИСТИКА ТЕАТРА")
        print("=" * 60)
        print(f"Название: {loaded.name}")
        print(f"Сотрудников: {len(loaded.staff_manager.staff)}")
        print(f"  - Актёров: {sum(1 for s in loaded.staff_manager.staff if isinstance(s, Actor))}")
        print(f"  - Режиссёров: {sum(1 for s in loaded.staff_manager.staff if isinstance(s, Director))}")
        print(f"  - Костюмеров: {sum(1 for s in loaded.staff_manager.staff if isinstance(s, CostumeDesigner))}")
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
        
        # Копируем файл в data/ для наглядности
        import shutil
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        dest_path = os.path.join(data_dir, "complex_theater.json")
        shutil.copy(filepath, dest_path)
        print(f"Копия сохранена: {dest_path}")


def Ticket_reset_counter():
    """Сброс счётчика билетов."""
    from theater import Ticket
    Ticket._counter = 0


if __name__ == '__main__':
    unittest.main()
