import json
from typing import Optional
from theater import Theater, Setting, AuditoryHall, Ticket
from staff import Director, Actor
from managers import StaffManager, HallManager, PerformanceManager, TicketManager


class TheaterCLI:
    def __init__(self):
        self.theater = Theater("Default Theater")
        self.current_hall: Optional[AuditoryHall] = None
        self.current_setting: Optional[Setting] = None

    def display_menu(self):
        print("\n" + "="*50)
        print("УПРАВЛЕНИЕ ТЕАТРОМ")
        print("="*50)
        print("1. Добавить зал")
        print("2. Добавить постановку")
        print("3. Добавить актера")
        print("4. Добавить режиссера")
        print("5. Продать билет")
        print("6. Показать информацию о театре")
        print("7. Сохранить состояние театра")
        print("8. Загрузить состояние театра")
        print("9. Показать список залов")
        print("10. Показать список постановок")
        print("11. Показать список сотрудников")
        print("12. Создать билет")
        print("0. Выход")
        print("="*50)

    def get_user_input(self, prompt: str) -> str:
        return input(prompt).strip()

    def add_hall(self):
        print("\n--- Добавление нового зала ---")
        try:
            name = self.get_user_input("Введите название зала: ")
            sectors = int(self.get_user_input("Введите количество секторов: "))
            rows_per_sector = int(self.get_user_input("Введите количество рядов в секторе: "))
            seats_per_row = int(self.get_user_input("Введите количество мест в ряду: "))
            hall_id = self.get_user_input("Введите ID зала: ")

            hall = AuditoryHall(name, sectors, rows_per_sector, seats_per_row, hall_id)
            self.theater.add_hall(hall)
            print(f"Зал '{name}' успешно добавлен!")
        except ValueError:
            print("Ошибка: Некорректный ввод числовых значений")
        except Exception as e:
            print(f"Ошибка при добавлении зала: {e}")

    def add_setting(self):
        print("\n--- Добавление новой постановки ---")
        try:
            name = self.get_user_input("Введите название постановки: ")
            durability = float(self.get_user_input("Введите продолжительность (в часах): "))
            
            # Временно создаем дату как строку, позже можно улучшить
            date_str = self.get_user_input("Введите дату показа (ГГГГ-ММ-ДД): ")
            
            # Выбираем директора (или создаем временного)
            directors = [s for s in self.theater.staff_manager.staff if isinstance(s, Director)]
            if not directors:
                print("Нет доступных режиссеров. Сначала добавьте режиссера.")
                return
                
            print("Доступные режиссеры:")
            for i, director in enumerate(directors):
                print(f"{i+1}. {director.name}")
                
            director_choice = int(self.get_user_input("Выберите номер режиссера: ")) - 1
            if 0 <= director_choice < len(directors):
                selected_director = directors[director_choice]
            else:
                print("Неверный выбор")
                return
            
            from datetime import datetime
            date = datetime.fromisoformat(date_str.replace('/', '-'))
            
            setting = Setting(durability, name, date, selected_director)
            self.theater.add_setting(setting)
            print(f"Постановка '{name}' успешно добавлена!")
        except ValueError:
            print("Ошибка: Некорректный ввод данных")
        except Exception as e:
            print(f"Ошибка при добавлении постановки: {e}")

    def add_actor(self):
        print("\n--- Добавление актера ---")
        try:
            name = self.get_user_input("Введите имя актера: ")
            birth_date_str = self.get_user_input("Введите дату рождения (ГГГГ-ММ-ДД): ")
            salary = float(self.get_user_input("Введите зарплату: "))
            
            from datetime import datetime
            birth_date = datetime.fromisoformat(birth_date_str.replace('/', '-'))
            
            actor = Actor(name, birth_date, salary)
            self.theater.add_staff(actor)
            print(f"Актер '{name}' успешно добавлен!")
        except ValueError:
            print("Ошибка: Некорректный ввод данных")
        except Exception as e:
            print(f"Ошибка при добавлении актера: {e}")

    def add_director(self):
        print("\n--- Добавление режиссера ---")
        try:
            name = self.get_user_input("Введите имя режиссера: ")
            birth_date_str = self.get_user_input("Введите дату рождения (ГГГГ-ММ-ДД): ")
            salary = float(self.get_user_input("Введите зарплату: "))
            
            from datetime import datetime
            birth_date = datetime.fromisoformat(birth_date_str.replace('/', '-'))
            
            director = Director(name, birth_date, salary)
            self.theater.add_staff(director)
            print(f"Режиссер '{name}' успешно добавлен!")
        except ValueError:
            print("Ошибка: Некорректный ввод данных")
        except Exception as e:
            print(f"Ошибка при добавлении режиссера: {e}")

    def sell_ticket(self):
        print("\n--- Продажа билета ---")
        try:
            ticket_id = self.get_user_input("Введите ID билета для продажи: ")
            
            result = self.theater.sell_ticket(ticket_id)
            if result:
                print(f"Билет {ticket_id} успешно продан!")
            else:
                print(f"Не удалось продать билет {ticket_id}")
        except Exception as e:
            print(f"Ошибка при продаже билета: {e}")

    def show_theater_info(self):
        print("\n--- Информация о театре ---")
        print(f"Название театра: {self.theater.name}")
        print(f"Количество сотрудников: {len(self.theater.staff_manager.staff)}")
        print(f"Количество залов: {len(self.theater.resource_manager.hall_manager.halls)}")
        print(f"Количество постановок: {len(self.theater.performance_manager.settings)}")
        print(f"Количество билетов: {len(self.theater.ticket_manager.tickets)}")

    def save_theater(self):
        print("\n--- Сохранение состояния театра ---")
        filepath = self.get_user_input("Введите путь для сохранения (например, 'theater_state.json'): ")
        try:
            self.theater.save_to_file(filepath)
            print(f"Состояние театра успешно сохранено в {filepath}")
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")

    def load_theater(self):
        print("\n--- Загрузка состояния театра ---")
        filepath = self.get_user_input("Введите путь к файлу для загрузки: ")
        try:
            self.theater.load_from_file(filepath)
            print(f"Состояние театра успешно загружено из {filepath}")
        except Exception as e:
            print(f"Ошибка при загрузке: {e}")

    def show_halls(self):
        print("\n--- Список залов ---")
        halls = self.theater.resource_manager.hall_manager.halls
        if not halls:
            print("Залы отсутствуют")
        else:
            for i, hall in enumerate(halls):
                print(f"{i+1}. {hall.name} (ID: {hall.hall_id}) - "
                      f"Секторов: {hall.sectors}, Рядов: {hall.rows_per_sector}, Мест в ряду: {hall.seats_per_row}")

    def show_settings(self):
        print("\n--- Список постановок ---")
        settings = self.theater.performance_manager.settings
        if not settings:
            print("Постановки отсутствуют")
        else:
            for i, setting in enumerate(settings):
                print(f"{i+1}. {setting.name} - Продолжительность: {setting.durability}ч, "
                      f"Дата: {setting.date.strftime('%Y-%m-%d')}")

    def show_staff(self):
        print("\n--- Список сотрудников ---")
        staff = self.theater.staff_manager.staff
        if not staff:
            print("Сотрудники отсутствуют")
        else:
            for i, staff_member in enumerate(staff):
                staff_type = staff_member.__class__.__name__
                print(f"{i+1}. {staff_member.name} ({staff_type}) - Зарплата: {staff_member.salary}")

    def create_ticket(self):
        print("\n--- Создание билета ---")
        try:
            # Выбор постановки
            settings = self.theater.performance_manager.settings
            if not settings:
                print("Нет доступных постановок. Сначала добавьте постановку.")
                return
                
            print("Доступные постановки:")
            for i, setting in enumerate(settings):
                print(f"{i+1}. {setting.name}")
                
            setting_choice = int(self.get_user_input("Выберите номер постановки: ")) - 1
            if not (0 <= setting_choice < len(settings)):
                print("Неверный выбор")
                return
            selected_setting = settings[setting_choice]

            # Выбор зала
            halls = self.theater.resource_manager.hall_manager.halls
            if not halls:
                print("Нет доступных залов. Сначала добавьте зал.")
                return
                
            print("Доступные залы:")
            for i, hall in enumerate(halls):
                print(f"{i+1}. {hall.name}")
                
            hall_choice = int(self.get_user_input("Выберите номер зала: ")) - 1
            if not (0 <= hall_choice < len(halls)):
                print("Неверный выбор")
                return
            selected_hall = halls[hall_choice]

            price = float(self.get_user_input("Введите цену билета: "))
            sector = int(self.get_user_input("Введите номер сектора: "))
            row = int(self.get_user_input("Введите номер ряда: "))
            seat = int(self.get_user_input("Введите номер места: "))
            ticket_id = self.get_user_input("Введите ID билета: ")

            # Проверяем, доступно ли место
            if not selected_hall.is_seat_available(sector, row, seat):
                print(f"Место в секторе {sector}, ряду {row}, месте {seat} уже занято!")
                return

            ticket = Ticket(price, selected_setting, sector, row, seat, selected_hall.hall_id, selected_hall)
            ticket.set_ticket_id(ticket_id)
            self.theater.add_ticket(ticket)
            print(f"Билет '{ticket_id}' успешно создан!")
        except ValueError:
            print("Ошибка: Некорректный ввод данных")
        except Exception as e:
            print(f"Ошибка при создании билета: {e}")

    def run(self):
        while True:
            self.display_menu()
            choice = self.get_user_input("Выберите действие (0-12): ")

            if choice == "1":
                self.add_hall()
            elif choice == "2":
                self.add_setting()
            elif choice == "3":
                self.add_actor()
            elif choice == "4":
                self.add_director()
            elif choice == "5":
                self.sell_ticket()
            elif choice == "6":
                self.show_theater_info()
            elif choice == "7":
                self.save_theater()
            elif choice == "8":
                self.load_theater()
            elif choice == "9":
                self.show_halls()
            elif choice == "10":
                self.show_settings()
            elif choice == "11":
                self.show_staff()
            elif choice == "12":
                self.create_ticket()
            elif choice == "0":
                print("Выход из программы...")
                break
            else:
                print("Неверный выбор. Пожалуйста, выберите число от 0 до 12.")


if __name__ == "__main__":
    cli = TheaterCLI()
    cli.run()