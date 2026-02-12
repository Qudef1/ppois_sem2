from theater import Theater, Setting, AuditoryHall, Ticket
from staff import Actor, Director, CostumeDesigner
from datetime import datetime

class TheaterMenu:
    def __init__(self):
        self.theater = None
        self.running = True

    def run(self):
        while self.running:
            self.show_main_menu()
            choice = input("Выберите действие: ").strip()
            self.handle_main_choice(choice)

    def show_main_menu(self):
        print("\n" + "="*40)
        print("           МЕНЮ ТЕАТРА")
        print("="*40)
        if self.theater:
            print(f"Текущий театр: {self.theater.name}")
        else:
            print("Театр не загружен")
        print("1. Создать новый театр")
        print("2. Загрузить театр из файла")
        print("3. Сохранить театр в файл")
        print("4. Управление сотрудниками")
        print("5. Управление ресурсами (залы, сцены)")
        print("6. Управление спектаклями")
        print("7. Управление билетами")
        print("8. Показать статистику")
        print("0. Выход")
        print("="*40)

    def handle_main_choice(self, choice):
        if choice == "1":
            self.create_new_theater()
        elif choice == "2":
            self.load_theater()
        elif choice == "3":
            self.save_theater()
        elif choice == "4":
            self.staff_menu()
        elif choice == "5":
            self.resources_menu()
        elif choice == "6":
            self.performances_menu()
        elif choice == "7":
            self.tickets_menu()
        elif choice == "8":
            self.show_stats()
        elif choice == "0":
            self.exit_program()
        else:
            print("Неверный выбор. Попробуйте снова.")

    def create_new_theater(self):
        name = input("Введите название театра: ").strip()
        if name:
            self.theater = Theater(name)
            print(f"Создан театр: {name}")
        else:
            print("Название не может быть пустым.")

    def load_theater(self):
        filename = input("Введите имя файла (по умолчанию theater_state.json): ").strip()
        if not filename:
            filename = "theater_state.json"
        try:
            self.theater = Theater.load_from_file(filename)
            print(f"Театр загружен из {filename}")
        except Exception as e:
            print(f"Ошибка загрузки: {e}")

    def save_theater(self):
        if not self.theater:
            print("Сначала загрузите или создайте театр.")
            return
        filename = input("Введите имя файла (по умолчанию theater_state.json): ").strip()
        if not filename:
            filename = "theater_state.json"
        try:
            self.theater.save_to_file(filename)
            print(f"Театр сохранён в {filename}")
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

    def staff_menu(self):
        if not self.theater:
            print("Сначала загрузите или создайте театр.")
            return

        while True:
            print("\n--- Управление сотрудниками ---")
            print("1. Добавить актёра")
            print("2. Добавить режиссёра")
            print("3. Добавить костюмера")
            print("4. Показать всех сотрудников")
            print("0. Назад")
            
            choice = input("Выберите действие: ").strip()
            
            if choice == "1":
                self.add_actor()
            elif choice == "2":
                self.add_director()
            elif choice == "3":
                self.add_costume_designer()
            elif choice == "4":
                self.list_staff()
            elif choice == "0":
                break
            else:
                print("Неверный выбор.")

    def add_actor(self):
        name = input("Имя актёра: ").strip()
        age = int(input("Возраст: "))
        salary = float(input("Зарплата: "))
        role = input("Роль (опционально): ").strip() or None
        actor = Actor(name, age, salary, role)
        self.theater.staff_manager.add_staff(actor)
        print(f"Актёр {name} добавлен.")

    def add_director(self):
        name = input("Имя режиссёра: ").strip()
        age = int(input("Возраст: "))
        salary = float(input("Зарплата: "))
        director = Director(name, age, salary)
        self.theater.staff_manager.add_staff(director)
        print(f"Режиссёр {name} добавлен.")

    def add_costume_designer(self):
        name = input("Имя костюмера: ").strip()
        age = int(input("Возраст: "))
        salary = float(input("Зарплата: "))
        designer = CostumeDesigner(name, age, salary)
        self.theater.staff_manager.add_staff(designer)
        print(f"Костюмер {name} добавлен.")

    def list_staff(self):
        staff = self.theater.staff_manager.get_staff()
        if not staff:
            print("Сотрудники отсутствуют.")
        else:
            for s in staff:
                role_info = f", роль: {s.role}" if hasattr(s, 'role') and s.role else ""
                print(f"- {s.name} ({type(s).__name__}){role_info}")

    def resources_menu(self):
        if not self.theater:
            print("Сначала загрузите или создайте театр.")
            return

        while True:
            print("\n--- Управление ресурсами ---")
            print("1. Добавить зал")
            print("2. Показать залы")
            print("0. Назад")
            
            choice = input("Выберите действие: ").strip()
            
            if choice == "1":
                self.add_hall()
            elif choice == "2":
                self.list_halls()
            elif choice == "0":
                break
            else:
                print("Неверный выбор.")

    def add_hall(self):
        name = input("Название зала: ").strip()
        hall_id = input("ID зала: ").strip()
        sectors = int(input("Количество секторов: "))
        rows = int(input("Количество рядов: "))
        seats = int(input("Количество мест в ряду: "))
        hall = AuditoryHall(name, sectors, rows, seats, hall_id)
        self.theater.resource_manager.hall_manager.add_hall(hall)
        print(f"Зал '{name}' добавлен.")

    def list_halls(self):
        halls = self.theater.resource_manager.hall_manager.halls
        if not halls:
            print("Залы отсутствуют.")
        else:
            for h in halls:
                print(f"- {h.name} (ID: {h.hall_id}), места: {h.capacity}")

    def performances_menu(self):
        if not self.theater:
            print("Сначала загрузите или создайте театр.")
            return

        while True:
            print("\n--- Управление спектаклями ---")
            print("1. Добавить спектакль")
            print("2. Показать спектакли")
            print("0. Назад")
            
            choice = input("Выберите действие: ").strip()
            
            if choice == "1":
                self.add_setting()
            elif choice == "2":
                self.list_settings()
            elif choice == "0":
                break
            else:
                print("Неверный выбор.")

    def add_setting(self):
        name = input("Название спектакля: ").strip()
        date_input = input("Дата (YYYY-MM-DD HH:MM:SS) или Enter для текущей: ").strip()
        if date_input:
            try:
                date = datetime.fromisoformat(date_input)
            except ValueError:
                print("Неверный формат даты.")
                return
        else:
            date = datetime.now()
        
        durability = float(input("Продолжительность (мин): "))
        
        # Показать актёров
        actors = [s for s in self.theater.staff_manager.get_staff() if isinstance(s, Actor)]
        if not actors:
            print("Нет доступных актёров.")
            return
        
        print("Доступные актёры:")
        for i, a in enumerate(actors):
            print(f"{i}. {a.name} (роль: {a.role or 'не назначена'})")
        
        cast_indices = input("Введите номера актёров через запятую: ").strip()
        if cast_indices:
            indices = [int(x.strip()) for x in cast_indices.split(',')]
            cast = [actors[i] for i in indices if 0 <= i < len(actors)]
        else:
            cast = []
        
        # Показать режиссёров
        directors = [s for s in self.theater.staff_manager.get_staff() if isinstance(s, Director)]
        if not directors:
            print("Нет доступных режиссёров.")
            return
        
        print("Доступные режиссёры:")
        for i, d in enumerate(directors):
            print(f"{i}. {d.name}")
        
        dir_index = int(input("Введите номер режиссёра: "))
        if 0 <= dir_index < len(directors):
            director = directors[dir_index]
        else:
            print("Неверный номер режиссёра.")
            return
        
        setting = Setting(durability, name, date, cast, director)
        self.theater.performance_manager.add_setting(setting)
        print(f"Спектакль '{name}' добавлен.")

    def list_settings(self):
        settings = self.theater.performance_manager.settings
        if not settings:
            print("Спектакли отсутствуют.")
        else:
            for s in settings:
                print(f"- {s.name} (режиссёр: {s.director.name})")

    def tickets_menu(self):
        if not self.theater:
            print("Сначала загрузите или создайте театр.")
            return

        while True:
            print("\n--- Управление билетами ---")
            print("1. Создать билет")
            print("2. Продать билет")
            print("3. Показать билеты")
            print("0. Назад")
            
            choice = input("Выберите действие: ").strip()
            
            if choice == "1":
                self.create_ticket()
            elif choice == "2":
                self.sell_ticket()
            elif choice == "3":
                self.list_tickets()
            elif choice == "0":
                break
            else:
                print("Неверный выбор.")

    def create_ticket(self):
        # Показать спектакли
        settings = self.theater.performance_manager.settings
        if not settings:
            print("Нет доступных спектаклей.")
            return
        
        print("Доступные спектакли:")
        for i, s in enumerate(settings):
            print(f"{i}. {s.name}")
        
        setting_index = int(input("Введите номер спектакля: "))
        if 0 <= setting_index < len(settings):
            setting = settings[setting_index]
        else:
            print("Неверный номер спектакля.")
            return
        
        # Показать залы
        halls = self.theater.resource_manager.hall_manager.halls
        if not halls:
            print("Нет доступных залов.")
            return
        
        print("Доступные залы:")
        for i, h in enumerate(halls):
            print(f"{i}. {h.name}")
        
        hall_index = int(input("Введите номер зала: "))
        if 0 <= hall_index < len(halls):
            hall = halls[hall_index]
        else:
            print("Неверный номер зала.")
            return
        
        price = float(input("Цена билета: "))
        sector = int(input("Сектор (0-based): "))
        row = int(input("Ряд (0-based): "))
        seat = int(input("Место (0-based): "))
        
        ticket = Ticket(price, setting, sector, row, seat, hall)
        self.theater.ticket_manager.add_ticket(ticket)
        print(f"Билет {ticket.ticket_id} создан.")

    def sell_ticket(self):
        tickets = self.theater.ticket_manager.get_all_tickets()
        if not tickets:
            print("Нет доступных билетов.")
            return
        
        print("Доступные билеты:")
        for i, t in enumerate(tickets):
            status = "продан" if t.is_sold else "не продан"
            print(f"{i}. {t.ticket_id} - {t.setting.name} - {status}")
        
        ticket_index = int(input("Введите номер билета для продажи: "))
        if 0 <= ticket_index < len(tickets):
            ticket = tickets[ticket_index]
            try:
                success = ticket.sell_ticket(self.theater.resource_manager.hall_manager)
                if success:
                    print(f"Билет {ticket.ticket_id} продан!")
                else:
                    print("Не удалось продать билет.")
            except Exception as e:
                print(f"Ошибка при продаже: {e}")
        else:
            print("Неверный номер билета.")

    def list_tickets(self):
        tickets = self.theater.ticket_manager.get_all_tickets()
        if not tickets:
            print("Билеты отсутствуют.")
        else:
            for t in tickets:
                status = "продан" if t.is_sold else "не продан"
                print(f"- {t.ticket_id} ({t.setting.name}) - {status}")

    def show_stats(self):
        if not self.theater:
            print("Сначала загрузите или создайте театр.")
            return
        
        print(f"\n--- Статистика театра '{self.theater.name}' ---")
        print(f"Сотрудников: {len(self.theater.staff_manager.get_staff())}")
        print(f"Спектаклей: {len(self.theater.performance_manager.settings)}")
        print(f"Билетов: {len(self.theater.ticket_manager.get_all_tickets())}")
        print(f"Залов: {len(self.theater.resource_manager.hall_manager.halls)}")

    def exit_program(self):
        print("До свидания!")
        self.running = False

if __name__ == "__main__":
    menu = TheaterMenu()
    menu.run()