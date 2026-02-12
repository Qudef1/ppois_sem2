import argparse
from theater import Theater

def main():
    parser = argparse.ArgumentParser(description="Театральная система управления")
    parser.add_argument("--load", action="store_true", help="Загрузить состояние из файла")
    parser.add_argument("--save", action="store_true", help="Сохранить состояние в файл")
    parser.add_argument("--reset", action="store_true", help="Создать новый театр")
    parser.add_argument("command", nargs="?", choices=[
        "add_actor", "list_staff", "create_hall", "create_ticket", "sell_ticket", "list_tickets"
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
        ticket_id = input("ID билета: ")
        sold = theater.ticket_manager.sell_ticket(ticket_id, theater.resource_manager.hall_manager)
        if sold:
            print("Билет продан!")
        else:
            print("Не удалось продать билет (место занято или не существует).")

    elif args.command == "list_tickets":
        for t in theater.ticket_manager.get_all_tickets():
            status = "продан" if t.is_sold else "не продан"
            print(f"- Билет {t.ticket_id}: {status}, цена: {t.price}")

    # Сохранение
    if args.save:
        theater.save_to_file()
        print("Состояние сохранено в theater_state.json")

if __name__ == "__main__":
    main()