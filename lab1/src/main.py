import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
from theater import Theater
from exceptions import (
    TheaterException, InvalidSeatException, InvalidDateException, TicketNotFoundException
)

def main():
    parser = argparse.ArgumentParser(description="Театральная система управления")
    parser.add_argument("--load", action="store_true", help="Загрузить состояние из файла")
    parser.add_argument("--save", action="store_true", help="Сохранить состояние в файл")
    parser.add_argument("--reset", action="store_true", help="Создать новый театр")
    parser.add_argument("command", nargs="?", choices=[
        "add_actor", "add_actors", "add_director", "add_costumedesigner", "list_staff",
        "create_hall", "create_ticket", "sell_ticket", "list_tickets", "create_costume",
        "assign_costume", "add_setting", "assign_actor_setting", "assign_director_setting", "create_setup"
    ], help="Команда")

    args = parser.parse_args()
    
    # Загрузка или создание театра
    if args.reset:
        theater = Theater("Городской театр")
        print("Создан новый театр.")
    elif args.load:
        try:
            theater = Theater.load_from_file()
            print("Состояние загружено.")
        except FileNotFoundError:
            print("Файл состояния не найден. Создаём новый театр.")
            theater = Theater("Городской театр")
    else:
        theater = Theater("Городской театр")
        print("Создан новый театр.")

    # Обработка команд
    if args.command == "add_actor":
        name = input("Имя актёра: ")
        age = int(input("Возраст: "))
        salary = float(input("Зарплата: "))
        role = input("Роль (опционально): ") or None
        from staff import Actor
        actor = Actor(name, age, salary, role)
        theater.staff_manager.add_staff(actor)
        print(f"Актёр {name} добавлен!")

    elif args.command == "add_actors":
        count = int(input("Сколько актёров добавить: "))
        from staff import Actor
        for i in range(count):
            print(f"Актёр #{i+1}")
            name = input("  Имя: ")
            age = int(input("  Возраст: "))
            salary = float(input("  Зарплата: "))
            role = input("  Роль (опционально): ") or None
            actor = Actor(name, age, salary, role)
            theater.staff_manager.add_staff(actor)
            print(f"  Добавлен: {name}")

    elif args.command == "add_director":
        name = input("Имя режиссёра: ")
        age = int(input("Возраст: "))
        salary = float(input("Зарплата: "))
        from staff import Director
        director = Director(name, age, salary)
        theater.staff_manager.add_staff(director)
        print(f"Режиссёр {name} добавлен!")

    
    elif args.command == "add_costumedesigner":
        name = input("Имя костюмера: ")
        age = int(input("Возраст: "))
        salary = float(input("Зарплата: "))
        from staff import CostumeDesigner
        cd = CostumeDesigner(name, age, salary)
        theater.staff_manager.add_staff(cd)
        print(f"Костюмер {name} добавлен!")

    elif args.command == "list_staff":
        for s in theater.staff_manager.get_staff():
            role_info = f", роль: {s.role}" if hasattr(s, 'role') and s.role else ""
            print(f"- {s.name} ({type(s).__name__}){role_info}")

    elif args.command == "create_hall":
        name = input("Название зала: ")
        hall_id = input("ID зала: ")
        sectors = int(input("Количество секторов: "))
        rows = int(input("Количество рядов: "))
        seats = int(input("Количество мест в ряду: "))
        from theater import AuditoryHall
        hall = AuditoryHall(name, sectors, rows, seats, hall_id)
        theater.resource_manager.hall_manager.add_hall(hall)
        print(f"Зал '{name}' создан и добавлен.")

    elif args.command == "create_ticket":
        ticket_id = input("ID билета: ")
        price = float(input("Цена: "))
        setting_id = input("ID спектакля: ")
        hall_id = input("ID зала: ")
        sector = int(input("Сектор: "))
        row = int(input("Ряд: "))
        seat = int(input("Место: "))
        from theater import Ticket
        ticket = Ticket(ticket_id, price, setting_id, sector, row, seat, hall_id)
        theater.ticket_manager.add_ticket(ticket)
        print(f"Билет {ticket_id} создан.")

    elif args.command == "sell_ticket":
        try:
            ticket_id = input("ID билета: ")
            sold = theater.ticket_manager.sell_ticket(ticket_id, theater.resource_manager.hall_manager)
            if sold:
                print("✓ Билет продан!")
        except TicketNotFoundException as e:
            print(f"✗ Ошибка: {e}")
        except InvalidSeatException as e:
            print(f"✗ Ошибка: {e}")
        except TheaterException as e:
            print(f"✗ Неизвестная ошибка при продаже билета: {e}")

    elif args.command == "list_tickets":
        for t in theater.ticket_manager.get_all_tickets():
            status = "продан" if t.is_sold else "не продан"
            print(f"- Билет {t.ticket_id}: {status}, цена: {t.price}")
    elif args.command == "create_costume":
                name = input("Название костюма: ")
                size = input("Размер: ")
                color = input("Цвет: ")
                room_name = input("Имя гардеробной (оставьте пустым, чтобы не класть в комнату): ") or None
                from theater import Costume, CostumeRoom
                costume = Costume(name, size, color)
                theater.resource_manager.add_costume(costume)
                if room_name:
                    # найти существующую комнату или создать новую
                    room = next((r for r in theater.resource_manager.costume_rooms if r.name == room_name), None)
                    if not room:
                        room = CostumeRoom(room_name)
                        theater.resource_manager.add_costume_room(room)
                    room.costume_ids.append(costume.name)
                print(f"Костюм '{name}' создан и добавлен.")
    elif args.command == "assign_costume":
        actor_name = input("Имя актёра для привязки костюма: ")
        costume_name = input("Название костюма: ")
        actor = next((s for s in theater.staff_manager.get_staff() if s.name == actor_name), None)
        costume = next((c for c in theater.resource_manager.costumes if c.name == costume_name), None)
        if not actor:
            print("Актёр не найден.")
        elif not costume:
            print("Костюм не найден.")
        else:
            if hasattr(actor, 'assign_costume'):
                actor.assign_costume(costume.name)
            else:
                actor.assigned_costume = costume.name
            print(f"Костюм '{costume.name}' закреплён за актёром {actor.name}.")

    elif args.command == "add_setting":
        try:
            name = input("Название постановки: ")
            durability = float(input("Долговечность (число): "))
            date_str = input("Дата (YYYY-MM-DD HH:MM:SS или YYYY-MM-DD): ")
            from theater import Setting
            
            try:
                if len(date_str) == 10:
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                else:
                    date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                raise InvalidDateException(
                    f"Неверный формат даты: '{date_str}'. Используйте YYYY-MM-DD или YYYY-MM-DD HH:MM:SS"
                )
            
            setting = Setting(durability, name, date)
            theater.performance_manager.add_setting(setting)
            print(f"✓ Постановка '{name}' создана на {date.strftime('%Y-%m-%d %H:%M:%S')}")
        except InvalidDateException as e:
            print(f"✗ Ошибка даты: {e}")
        except ValueError as e:
            print(f"✗ Ошибка ввода: {e}")

    elif args.command == "assign_actor_setting":
        try:
            setting_name = input("Название постановки: ")
            actor_name = input("Имя актёра: ")
            setting = next((s for s in theater.performance_manager.settings if s.name == setting_name), None)
            actor = next((s for s in theater.staff_manager.get_staff() if s.name == actor_name), None)
            
            if not setting:
                raise TheaterException(
                    f"Постановка '{setting_name}' не найдена в системе"
                )
            if not actor:
                raise TheaterException(
                    f"Актёр '{actor_name}' не найден в системе"
                )
            
            setting.cast_ids.append(actor.name)
            print(f"✓ Актёр {actor.name} добавлен в постановку {setting.name}")
        except TheaterException as e:
            print(f"✗ Ошибка: {e}")

    elif args.command == "assign_director_setting":
        try:
            setting_name = input("Название постановки: ")
            director_name = input("Имя режиссёра: ")
            setting = next((s for s in theater.performance_manager.settings if s.name == setting_name), None)
            director = next((s for s in theater.staff_manager.get_staff() if s.name == director_name and type(s).__name__ == 'Director'), None)
            
            if not setting:
                raise TheaterException(
                    f"Постановка '{setting_name}' не найдена в системе"
                )
            if not director:
                raise TheaterException(
                    f"Режиссёр '{director_name}' не найден в системе"
                )
            
            setting.director_id = director.name
            if hasattr(director, 'direct_setting'):
                director.direct_setting(setting.name)
            print(f"✓ Режиссёр {director.name} закреплён за постановкой {setting.name}")
        except TheaterException as e:
            print(f"✗ Ошибка: {e}")

    elif args.command == "create_setup":
        # минимальная рабочая версия: Ромео и Джульетта
        from staff import Actor, Director
        from theater import Costume, CostumeRoom, Setting, Repetition, AuditoryHall

        # создаём режиссёра
        director = Director("Director1", 45, 3000.0)
        theater.staff_manager.add_staff(director)

        # создаём актёров
        a1 = Actor("Romeo", 25, 1500.0, "Romeo")
        a2 = Actor("Juliette", 23, 1500.0, "Juliette")
        theater.staff_manager.add_staff(a1)
        theater.staff_manager.add_staff(a2)

        # костюмы
        c1 = Costume("Romeo_costume", "M", "red")
        c2 = Costume("Juliette_costume", "S", "white")
        theater.resource_manager.add_costume(c1)
        theater.resource_manager.add_costume(c2)

        # закрепляем костюмы за актёрами
        a1.assign_costume(c1.name)
        a2.assign_costume(c2.name)

        # создаём постановку и привязываем актёров и режиссёра
        premiere_date = datetime(2026, 2, 12, 19, 30, 0)
        setting = Setting(1.0, "Romeo and Juliette", premiere_date, [a1.name, a2.name], director.name)
        theater.performance_manager.add_setting(setting)
        director.direct_setting(setting.name)

        # 10 репетиций
        for i in range(1, 11):
            rep_date = premiere_date - timedelta(days=11-i)
            rep = Repetition(0.1, setting.name, "normal", rep_date)
            theater.performance_manager.add_repetition(rep)

        # зал
        hall = AuditoryHall("Main Hall", 4, 10, 10, "main_hall")
        theater.resource_manager.hall_manager.add_hall(hall)

        # Сохранить немедленно
        theater.save_to_file()
        print("Сценарий 'Romeo and Juliette' создан и сохранён в theater_state.json")
    # Сохранение
    if args.save:
        theater.save_to_file()
        print("Состояние сохранено в theater_state.json")

if __name__ == "__main__":
    while True:
        try:
            main()
            break  # Выходим после успешного выполнения
        except TheaterException as e:
            print(f"Ошибка: {e}")
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")
