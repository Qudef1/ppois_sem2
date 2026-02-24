import json
import os
import glob
from typing import Optional
from datetime import datetime

from theater import Theater
from actions import Setting, Repetition
from halls import AuditoryHall
from staff import Director, Actor
from exception import TheaterException


class TheaterCLI:
    def __init__(self):
        name = input("Введите название театра (Enter для 'Default Theater'): ").strip()
        self.theater = Theater(name if name else "Default Theater")
        self.current_hall: Optional[AuditoryHall] = None
        self.current_setting: Optional[Setting] = None

    def display_menu(self):
        print("\n" + "=" * 50)
        print(f"УПРАВЛЕНИЕ ТЕАТРОМ: {self.theater.name}")
        print("=" * 50)
        print("1. Добавить сущность")
        print("2. Работа с билетами")
        print("3. Работа с актерами")
        print("4. Показать информацию о театре")
        print("5. Сохранить/Загрузить")
        print("6. Привязать постановку к залу")
        print("7. Репетиции")
        print("8. Изменить название театра")
        print("0. Выход")
        print("=" * 50)

    def display_add_menu(self):
        print("\n" + "=" * 50)
        print("ДОБАВИТЬ СУЩНОСТЬ")
        print("=" * 50)
        print("1. Зал")
        print("2. Постановку")
        print("3. Актера")
        print("4. Режиссера")
        print("5. Костюм")
        print("0. Назад")
        print("=" * 50)

    def display_tickets_menu(self):
        print("\n" + "=" * 50)
        print("РАБОТА С БИЛЕТАМИ")
        print("=" * 50)
        print("1. Продать билет")
        print("2. Показать доступные билеты")
        print("0. Назад")
        print("=" * 50)

    def display_actors_menu(self):
        print("\n" + "=" * 50)
        print("РАБОТА С АКТЕРАМИ")
        print("=" * 50)
        print("1. Добавить актера к постановке")
        print("2. Назначить костюм актеру")
        print("0. Назад")
        print("=" * 50)

    def display_save_load_menu(self):
        print("\n" + "=" * 50)
        print("СОХРАНИТЬ/ЗАГРУЗИТЬ")
        print("=" * 50)
        print("1. Сохранить состояние")
        print("2. Загрузить состояние")
        print("0. Назад")
        print("=" * 50)

    def display_repetition_menu(self):
        print("\n" + "=" * 50)
        print("РЕПЕТИЦИИ")
        print("=" * 50)
        print("1. Добавить репетицию")
        print("2. Отметить актеров на репетиции")
        print("0. Назад")
        print("=" * 50)

    def get_user_input(self, msg: str) -> str:
        return input(msg).strip()

    def get_validated_int(self, msg: str, min_val: int = None, max_val: int = None) -> int:
        while True:
            value = self.get_user_input(msg)
            try:
                result = int(value)
                if min_val is not None and result < min_val:
                    print(f"Ошибка: значение должно быть не меньше {min_val}")
                    continue
                if max_val is not None and result > max_val:
                    print(f"Ошибка: значение должно быть не больше {max_val}")
                    continue
                return result
            except ValueError:
                print("Ошибка: введите целое число")

    def get_validated_float(self, msg: str, min_val: float = None) -> float:
        while True:
            value = self.get_user_input(msg)
            try:
                result = float(value)
                if min_val is not None and result < min_val:
                    print(f"Ошибка: значение должно быть не меньше {min_val}")
                    continue
                return result
            except ValueError:
                print("Ошибка: введите число (например, 100.50)")

    def get_validated_date(self, msg: str) -> datetime:
        while True:
            value = self.get_user_input(msg)
            try:
                return datetime.fromisoformat(value.replace('/', '-'))
            except ValueError:
                print("Ошибка: введите дату в формате ГГГГ-ММ-ДД (например, 2025-06-15)")

    def get_validated_choice(self, msg: str, options_count: int) -> int:
        while True:
            value = self.get_user_input(msg)
            try:
                result = int(value)
                if 1 <= result <= options_count:
                    return result - 1
                else:
                    print(f"Ошибка: выберите число от 1 до {options_count}")
            except ValueError:
                print(f"Ошибка: введите число от 1 до {options_count}")

    def add_hall(self):
        print("\n--- Добавление нового зала ---")
        name = self.get_user_input("Введите название зала: ")
        if not name:
            print("Ошибка: название зала не может быть пустым")
            return

        sectors = self.get_validated_int("Введите количество секторов: ", min_val=1)
        rows_per_sector = self.get_validated_int("Введите количество рядов в секторе: ", min_val=1)
        seats_per_row = self.get_validated_int("Введите количество мест в ряду: ", min_val=1)
        hall_id = self.get_user_input("Введите ID зала: ")
        if not hall_id:
            print("Ошибка: ID зала не может быть пустым")
            return

        hall = AuditoryHall(name, sectors, rows_per_sector, seats_per_row, hall_id)
        self.theater.add_hall(hall)
        print(f"Зал '{name}' успешно добавлен!")

    def add_setting(self):
        print("\n--- Добавление новой постановки ---")
        name = self.get_user_input("Введите название постановки: ")
        if not name:
            print("Ошибка: название постановки не может быть пустым")
            return

        durability = self.get_validated_float("Введите продолжительность (в часах): ", min_val=0.1)
        date = self.get_validated_date("Введите дату показа (ГГГГ-ММ-ДД): ")

        directors = [s for s in self.theater.staff_manager.staff if isinstance(s, Director)]
        if not directors:
            print("Нет доступных режиссеров. Сначала добавьте режиссера.")
            choice = self.get_user_input("Создать нового режиссера? Y/N: ")
            if choice.upper() == "Y":
                self.add_director()
                directors = [s for s in self.theater.staff_manager.staff if isinstance(s, Director)]
                if not directors:
                    return
            else:
                return

        print("Доступные режиссеры:")
        for i, director in enumerate(directors):
            print(f"{i+1}. {director.name}")

        director_choice = self.get_validated_choice("Выберите номер режиссера: ", len(directors))
        selected_director = directors[director_choice]

        setting = Setting(durability, name, date, selected_director)
        self.theater.add_setting(setting)
        print(f"Постановка '{name}' успешно добавлена!")

    def add_actor(self):
        print("\n--- Добавление актера ---")
        name = self.get_user_input("Введите имя актера: ")
        if not name:
            print("Ошибка: имя актера не может быть пустым")
            return

        age = self.get_validated_int("Введите возраст актера: ", min_val=18, max_val=100)
        salary = self.get_validated_float("Введите зарплату: ", min_val=0)

        role = self.get_user_input("Введите роль актера (Enter для пропуска): ")
        if not role:
            role = None

        actor = Actor(name, age, salary, role)
        self.theater.add_staff(actor)
        print(f"Актер '{name}' успешно добавлен!")

    def add_director(self):
        print("\n--- Добавление режиссера ---")
        name = self.get_user_input("Введите имя режиссера: ")
        if not name:
            print("Ошибка: имя режиссера не может быть пустым")
            return

        age = self.get_validated_int("Введите возраст режиссера: ", min_val=25, max_val=100)
        salary = self.get_validated_float("Введите зарплату: ", min_val=0)

        director = Director(name, age, salary)
        self.theater.add_staff(director)
        print(f"Режиссер '{name}' успешно добавлен!")

    def add_repetition(self):
        print("\n--- Добавление репетиции ---")
        settings = self.theater.performance_manager.settings
        if not settings:
            print("Нет доступных постановок. Сначала добавьте постановку.")
            return

        print("Доступные постановки:")
        for i, setting in enumerate(settings):
            print(f"{i+1}. {setting.name}")

        setting_choice = self.get_validated_choice("Выберите постановку: ", len(settings))
        selected_setting = settings[setting_choice]

        date = self.get_validated_date("Введите дату репетиции (ГГГГ-ММ-ДД): ")
        durability = self.get_validated_float("Введите продолжительность (в часах): ", min_val=0.1)

        rep = Repetition(durability, f"Репетиция: {selected_setting.name}", date, selected_setting)
        self.theater.performance_manager.add_repetition(rep)
        print(f"Репетиция для '{selected_setting.name}' добавлена!")

    def mark_actors_at_repetition(self):
        print("\n--- Отметка актеров на репетиции ---")
        repetitions = self.theater.performance_manager.repetitions
        if not repetitions:
            print("Нет доступных репетиций.")
            return

        print("Доступные репетиции:")
        for i, rep in enumerate(repetitions):
            count = len(rep.attendance_list) if hasattr(rep, 'attendance_list') else 0
            print(f"{i+1}. {rep.name} (отмечено: {count})")

        rep_choice = self.get_validated_choice("Выберите репетицию: ", len(repetitions))
        selected_rep = repetitions[rep_choice]

        actors = [s for s in self.theater.staff_manager.staff if isinstance(s, Actor)]
        if not actors:
            print("Нет доступных актеров.")
            return

        print("\nДоступные актеры:")
        for i, actor in enumerate(actors):
            is_present = actor in selected_rep.attendance_list
            status = "+" if is_present else " "
            print(f"{i+1}. [{status}] {actor.name}")

        print("\nОтметьте актеров (введите номера через пробел):")
        choices = self.get_user_input("> ").split()
        
        for choice in choices:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(actors):
                    actor = actors[idx]
                    selected_rep.check_list(actor)
                    print(f"  {actor.name} отмечен")
            except ValueError:
                continue
        
        print(f"\nВсего отмечено: {len(selected_rep.attendance_list)} актеров")

    def sell_ticket(self):
        print("\n--- Продажа билета ---")
        
        tickets = self.theater.ticket_manager.tickets
        available = [t for t in tickets if not t.is_sold]
        
        if not available:
            print("Нет доступных билетов для продажи.")
            return
        
        settings_map = {}
        for t in available:
            if t.setting and t.setting.name not in settings_map:
                settings_map[t.setting.name] = t.setting
        
        if len(settings_map) == 0:
            print("Нет доступных постановок")
            return
        
        print("Доступные постановки:")
        settings_list = list(settings_map.items())
        for i, (name, setting) in enumerate(settings_list, 1):
            count = sum(1 for t in available if t.setting and t.setting.name == name)
            print(f"  {i}. {name} ({count} билетов)")
        
        setting_choice = self.get_validated_choice("Выберите постановку: ", len(settings_list))
        selected_setting_name = settings_list[setting_choice][0]
        
        setting_tickets = [t for t in available if t.setting and t.setting.name == selected_setting_name]
        
        halls_map = {}
        for t in setting_tickets:
            if t.hall_id not in halls_map:
                halls_map[t.hall_id] = t.hall_id
        
        selected_hall_id = list(halls_map.keys())[0]
        if len(halls_map) > 1:
            print("\nДоступные залы:")
            halls_list = list(halls_map.items())
            for i, (hall_id, _) in enumerate(halls_list, 1):
                count = sum(1 for t in setting_tickets if t.hall_id == hall_id)
                print(f"  {i}. Зал {hall_id} ({count} билетов)")
            
            hall_choice = self.get_validated_choice("Выберите зал: ", len(halls_list))
            selected_hall_id = halls_list[hall_choice][0]
        
        setting_tickets = [t for t in setting_tickets if t.hall_id == selected_hall_id]
        
        sectors = sorted(set(t.sector for t in setting_tickets))
        if not sectors:
            print("Нет доступных мест.")
            return
        
        print("\nДоступные сектора:")
        for i, sector in enumerate(sectors, 1):
            count = sum(1 for t in setting_tickets if t.sector == sector)
            print(f"  {i}. Сектор {sector} ({count} билетов)")
        
        sector_choice = self.get_validated_choice("Выберите сектор: ", len(sectors))
        selected_sector = sectors[sector_choice]
        
        sector_tickets = [t for t in setting_tickets if t.sector == selected_sector]
        
        rows = sorted(set(t.row for t in sector_tickets))
        
        print("\nДоступные ряды:")
        for i, row in enumerate(rows, 1):
            count = sum(1 for t in sector_tickets if t.row == row)
            print(f"  {i}. Ряд {row} ({count} билетов)")
        
        row_choice = self.get_validated_choice("Выберите ряд: ", len(rows))
        selected_row = rows[row_choice]
        
        row_tickets = [t for t in sector_tickets if t.row == selected_row]
        
        seats = sorted(set(t.seat for t in row_tickets))
        
        print("\nДоступные места:")
        for i, seat in enumerate(seats, 1):
            ticket = next(t for t in row_tickets if t.seat == seat)
            print(f"  {i}. Место {seat} (цена: {ticket.price:.0f} руб.)")
        
        seat_choice = self.get_validated_choice("Выберите место: ", len(seats))
        selected_seat = seats[seat_choice]
        
        ticket_to_sell = next(t for t in row_tickets if t.seat == selected_seat)
        
        print(f"\nБилет: сектор {selected_sector}, ряд {selected_row}, место {selected_seat}")
        print(f"Цена: {ticket_to_sell.price:.0f} руб.")
        confirm = self.get_user_input("Продать билет? Y/N: ")
        
        if confirm.upper() != 'Y':
            print("Продажа отменена.")
            return
        
        try:
            result = self.theater.sell_ticket(ticket_to_sell.ticket_id)
            if result:
                print(f"Билет успешно продан!")
            else:
                print(f"Не удалось продать билет")
        except TheaterException as e:
            print(f"Ошибка: {e}")
        except Exception as e:
            print(f"Ошибка при продаже билета: {e}")

    def show_available_tickets(self):
        print("\n--- Доступные билеты для продажи ---")
        tickets = self.theater.ticket_manager.tickets
        if not tickets:
            print("Билеты отсутствуют. Сначала привяжите постановку к залу.")
            return

        available = [t for t in tickets if not t.is_sold]
        sold = [t for t in tickets if t.is_sold]

        print(f"Всего билетов: {len(tickets)}")
        print(f"Доступно: {len(available)}")
        print(f"Продано: {len(sold)}")

        if not available:
            print("\nВсе билеты проданы.")
            return

        settings_map = {}
        for t in available:
            if t.setting:
                name = t.setting.name
                if name not in settings_map:
                    settings_map[name] = []
                settings_map[name].append(t)

        print("\n" + "=" * 70)
        for setting_name, setting_tickets in settings_map.items():
            print(f"\nПостановка: {setting_name}")
            print("-" * 70)
            
            halls_map = {}
            for t in setting_tickets:
                if t.hall_id not in halls_map:
                    halls_map[t.hall_id] = []
                halls_map[t.hall_id].append(t)
            
            for hall_id, hall_tickets in halls_map.items():
                print(f"\nЗал: {hall_id}")
                
                sectors_map = {}
                for t in hall_tickets:
                    if t.sector not in sectors_map:
                        sectors_map[t.sector] = []
                    sectors_map[t.sector].append(t)
                
                for sector, sector_tickets in sorted(sectors_map.items()):
                    print(f"\n    Сектор {sector}: {len(sector_tickets)} билетов")
                    
                    preview = sector_tickets[:10]
                    for t in preview:
                        print(f"      Ряд {t.row}, Место {t.seat} — {t.price:.0f} руб.")
                    
                    if len(sector_tickets) > 10:
                        print(f"      ... и ещё {len(sector_tickets) - 10} билетов")

    def show_theater_info(self):
        while True:
            print("\n" + "="*50)
            print("ИНФОРМАЦИЯ О ТЕАТРЕ")
            print("="*50)
            print(f"Название театра: {self.theater.name}")
            print("-"*50)
            print("1. Общая сводка")
            print("2. Сотрудники")
            print("3. Залы")
            print("4. Постановки")
            print("5. Билеты")
            print("6. Ресурсы")
            print("0. Назад")
            print("="*50)

            choice = self.get_validated_int("Выберите раздел (0-6): ", min_val=0, max_val=6)

            if choice == 1:
                self._show_summary()
            elif choice == 2:
                self._show_staff_detailed()
            elif choice == 3:
                self._show_halls_detailed()
            elif choice == 4:
                self._show_settings_detailed()
            elif choice == 5:
                self._show_tickets_detailed()
            elif choice == 6:
                self._show_resources_detailed()
            elif choice == 0:
                break

    def _show_summary(self):
        print("\n--- Общая сводка ---")
        print(f"Название театра: {self.theater.name}")
        print(f"Сотрудников: {len(self.theater.staff_manager.staff)}")
        halls = self.theater.resource_manager.hall_manager.halls
        print(f"Залов: {len(halls)}")
        total_capacity = sum(h.capacity for h in halls)
        print(f"Вместимость: {total_capacity}")
        print(f"Постановок: {len(self.theater.performance_manager.settings)}")
        print(f"Репетиций: {len(self.theater.performance_manager.repetitions)}")
        tickets = self.theater.ticket_manager.tickets
        print(f"Билетов: {len(tickets)}")
        sold = sum(1 for t in tickets if t.is_sold)
        print(f" - Продано: {sold}")
        print(f" - В продаже: {len(tickets) - sold}")
        print(f"Сцен: {len(self.theater.resource_manager.stages)}")
        print(f"Костюмерных: {len(self.theater.resource_manager.costume_rooms)}")
        print(f"Костюмов: {len(self.theater.resource_manager.costumes)}")

    def _show_staff_detailed(self):
        print("\n--- Сотрудники ---")
        staff_list = self.theater.staff_manager.staff
        if not staff_list:
            print("Сотрудники отсутствуют")
            return

        actors = [s for s in staff_list if isinstance(s, Actor)]
        directors = [s for s in staff_list if isinstance(s, Director)]

        print(f"Всего: {len(staff_list)} | Актёров: {len(actors)} | Режиссёров: {len(directors)}")

        if actors:
            print("\nАктёры:")
            for i, a in enumerate(actors, 1):
                role_info = f"({a.role})" if a.role else ""
                print(f"  {i}. {a.name} {role_info}")

        if directors:
            print("\nРежиссёры:")
            for i, d in enumerate(directors, 1):
                print(f"  {i}. {d.name}")

    def _show_halls_detailed(self):
        print("\n--- Залы ---")
        halls = self.theater.resource_manager.hall_manager.halls
        if not halls:
            print("Залы отсутствуют")
            return

        for i, hall in enumerate(halls, 1):
            occupied = sum(1 for sector in hall.seats for row in sector for seat in row if seat.is_occupied)
            print(f"\n{i}. {hall.name} (ID: {hall.hall_id})")
            print(f"   Вместимость: {hall.capacity} | Занято: {occupied} | Свободно: {hall.capacity - occupied}")

    def _show_settings_detailed(self):
        print("\n--- Постановки ---")
        settings = self.theater.performance_manager.settings
        if not settings:
            print("Постановки отсутствуют")
            return

        for i, setting in enumerate(settings, 1):
            date_str = setting.date.strftime('%Y-%m-%d') if hasattr(setting.date, 'strftime') else str(setting.date)
            cast_count = len(setting.cast) if hasattr(setting, 'cast') else 0
            print(f"\n{i}. {setting.name}")
            print(f"   Дата: {date_str} | Режиссёр: {setting.director.name if setting.director else 'Н/Д'}")
            print(f"   Актёров: {cast_count}")

        repetitions = self.theater.performance_manager.repetitions
        if repetitions:
            print(f"\n--- Репетиции ({len(repetitions)}) ---")
            for i, rep in enumerate(repetitions, 1):
                date_str = rep.date.strftime('%Y-%m-%d') if hasattr(rep.date, 'strftime') else str(rep.date)
                count = len(rep.attendance_list) if hasattr(rep, 'attendance_list') else 0
                print(f"  {i}. {rep.name} ({date_str}) - отмечено: {count}")

    def _show_tickets_detailed(self):
        print("\n--- Билеты ---")
        tickets = self.theater.ticket_manager.tickets
        if not tickets:
            print("Билеты отсутствуют")
            return

        sold = [t for t in tickets if t.is_sold]
        total_revenue = sum(t.price for t in sold)

        print(f"Всего: {len(tickets)} | Продано: {len(sold)} | Выручка: {total_revenue:.0f} руб.")

    def _show_resources_detailed(self):
        print("\n--- Ресурсы ---")
        rm = self.theater.resource_manager

        print(f"\nСцены ({len(rm.stages)}):")
        for stage in rm.stages:
            status = "Доступна" if stage.is_available else "Занята"
            print(f"  - {stage.name} ({stage.capacity} мест, {status})")

        print(f"\nКостюмерные ({len(rm.costume_rooms)}):")
        for room in rm.costume_rooms:
            print(f"  - {room.name} ({len(room.costume_ids)} костюмов)")

        print(f"\nКостюмы ({len(rm.costumes)}):")
        for costume in rm.costumes:
            print(f"  - {costume.name} ({costume.size}, {costume.color})")

    def save_theater(self):
        print("\n--- Сохранение ---")
        filepath = self.get_user_input("Путь для сохранения: ")
        try:
            self.theater.save_to_file(filepath)
            print(f"Сохранено в {filepath}")
        except Exception as e:
            print(f"Ошибка: {e}")

    def _list_available_files(self) -> list:
        search_dirs = [".", "..", "../data", "data"]
        found_files = []
        for d in search_dirs:
            pattern = os.path.join(d, "*.json")
            found_files.extend(glob.glob(pattern))
        return sorted(set(os.path.normpath(f) for f in found_files))

    def load_theater(self):
        print("\n--- Загрузка ---")

        available = self._list_available_files()
        if available:
            print("Доступные файлы:")
            for i, f in enumerate(available, 1):
                print(f"  {i}. {f}")
            print(f"  0. Ввести путь вручную")

            choice = self.get_validated_int("Выберите файл (0 для ручного ввода): ", min_val=0, max_val=len(available))
            if choice == 0:
                filepath = self.get_user_input("Путь к файлу: ")
            else:
                filepath = available[choice - 1]
        else:
            filepath = self.get_user_input("Путь к файлу: ")

        if not filepath:
            print("Ошибка: путь не может быть пустым")
            return

        try:
            self.theater.load_from_file(filepath)
            print(f"Загружено из {filepath}")
        except FileNotFoundError:
            print(f"Ошибка: файл не найден")
        except json.JSONDecodeError:
            print(f"Ошибка: некорректный JSON")
        except Exception as e:
            print(f"Ошибка: {e}")

    def bind_setting_to_hall(self):
        print("\n--- Привязка постановки к залу ---")
        settings = self.theater.performance_manager.settings
        if not settings:
            print("Нет постановок.")
            return

        print("Постановки:")
        for i, setting in enumerate(settings):
            hall_info = f"(зал: {setting.hall.name})" if setting.hall else "(без зала)"
            print(f"{i+1}. {setting.name} {hall_info}")

        setting_choice = self.get_validated_choice("Выберите постановку: ", len(settings))
        selected_setting = settings[setting_choice]

        if selected_setting.hall:
            print(f"Уже привязана к залу '{selected_setting.hall.name}'")
            confirm = self.get_user_input("Перепривязать? Y/N: ")
            if confirm.upper() != 'Y':
                return

        halls = self.theater.resource_manager.hall_manager.halls
        if not halls:
            print("Нет залов.")
            return

        print("Залы:")
        for i, hall in enumerate(halls):
            print(f"{i+1}. {hall.name} (вместимость: {hall.capacity})")

        hall_choice = self.get_validated_choice("Выберите зал: ", len(halls))
        selected_hall = halls[hall_choice]

        base_price = self.get_validated_float("Базовая цена билета (руб): ", min_val=1)

        tickets = self.theater.bind_setting_to_hall(selected_setting.name, selected_hall.hall_id, base_price)
        print(f"Создано {len(tickets)} билетов!")

    def add_actor_to_setting(self):
        print("\n--- Добавление актера к постановке ---")
        actors = [s for s in self.theater.staff_manager.staff if isinstance(s, Actor)]
        if not actors:
            print("Нет актеров.")
            return

        print("Актеры:")
        for i, actor in enumerate(actors):
            role_info = f" ({actor.role})" if actor.role else ""
            print(f"{i+1}. {actor.name}{role_info}")

        actor_choice = self.get_validated_choice("Выберите актера: ", len(actors))
        selected_actor = actors[actor_choice]

        settings = self.theater.performance_manager.settings
        if not settings:
            print("Нет постановок.")
            return

        print("Постановки:")
        for i, setting in enumerate(settings):
            cast_count = len(setting.cast) if hasattr(setting, 'cast') else 0
            print(f"{i+1}. {setting.name} (актёров: {cast_count})")

        setting_choice = self.get_validated_choice("Выберите постановку: ", len(settings))
        selected_setting = settings[setting_choice]

        selected_setting.add_cast(selected_actor)
        print(f"Актер '{selected_actor.name}' добавлен к постановке!")

    def create_costume(self):
        print("\n--- Создание костюма ---")
        name = self.get_user_input("Название: ")
        if not name:
            print("Ошибка: название не может быть пустым")
            return

        size = self.get_user_input("Размер (S/M/L/XL): ").upper()
        color = self.get_user_input("Цвет: ")
        if not color:
            print("Ошибка: цвет не может быть пустым")
            return

        costume = self.theater.create_costume(name, size, color)
        print(f"Костюм '{name}' создан!")

    def assign_costume_to_actor(self):
        print("\n--- Назначение костюма актеру ---")
        actors = [s for s in self.theater.staff_manager.staff if isinstance(s, Actor)]
        if not actors:
            print("Нет актеров.")
            return

        print("Актеры:")
        for i, actor in enumerate(actors):
            costumes = actor.get_costumes()
            count = len(costumes) if costumes else 0
            print(f"{i+1}. {actor.name} (костюмов: {count})")

        actor_choice = self.get_validated_choice("Выберите актера: ", len(actors))
        selected_actor = actors[actor_choice]

        costumes = self.theater.resource_manager.costumes
        if not costumes:
            print("Нет костюмов.")
            return

        print("Костюмы:")
        for i, costume in enumerate(costumes):
            print(f"{i+1}. {costume.name} ({costume.size}, {costume.color})")

        costume_choice = self.get_validated_choice("Выберите костюм: ", len(costumes))
        selected_costume = costumes[costume_choice]

        self.theater.assign_costume_to_actor(selected_costume, selected_actor)
        print(f"Костюм '{selected_costume.name}' назначен актеру '{selected_actor.name}'!")

    def handle_add_entity(self):
        while True:
            self.display_add_menu()
            choice = self.get_validated_int("Выберите действие (0-5): ", min_val=0, max_val=5)

            if choice == 1:
                self.add_hall()
            elif choice == 2:
                self.add_setting()
            elif choice == 3:
                self.add_actor()
            elif choice == 4:
                self.add_director()
            elif choice == 5:
                self.create_costume()
            elif choice == 0:
                break

    def handle_tickets(self):
        while True:
            self.display_tickets_menu()
            choice = self.get_validated_int("Выберите действие (0-2): ", min_val=0, max_val=2)

            if choice == 1:
                self.sell_ticket()
            elif choice == 2:
                self.show_available_tickets()
            elif choice == 0:
                break

    def handle_actors(self):
        while True:
            self.display_actors_menu()
            choice = self.get_validated_int("Выберите действие (0-2): ", min_val=0, max_val=2)

            if choice == 1:
                self.add_actor_to_setting()
            elif choice == 2:
                self.assign_costume_to_actor()
            elif choice == 0:
                break

    def handle_save_load(self):
        while True:
            self.display_save_load_menu()
            choice = self.get_validated_int("Выберите действие (0-2): ", min_val=0, max_val=2)

            if choice == 1:
                self.save_theater()
            elif choice == 2:
                self.load_theater()
            elif choice == 0:
                break

    def handle_repetitions(self):
        while True:
            self.display_repetition_menu()
            choice = self.get_validated_int("Выберите действие (0-2): ", min_val=0, max_val=2)

            if choice == 1:
                self.add_repetition()
            elif choice == 2:
                self.mark_actors_at_repetition()
            elif choice == 0:
                break

    def run(self):
        while True:
            self.display_menu()
            choice = self.get_validated_int("Выберите действие (0-8): ", min_val=0, max_val=8)

            if choice == 1:
                self.handle_add_entity()
            elif choice == 2:
                self.handle_tickets()
            elif choice == 3:
                self.handle_actors()
            elif choice == 4:
                self.show_theater_info()
            elif choice == 5:
                self.handle_save_load()
            elif choice == 6:
                self.bind_setting_to_hall()
            elif choice == 7:
                self.handle_repetitions()
            elif choice == 8:
                self.change_theater_name()
            elif choice == 0:
                print("Выход из программы...")
                break

    def change_theater_name(self):
        print("\n--- Изменение названия ---")
        print(f"Текущее: {self.theater.name}")
        new_name = self.get_user_input("Новое название: ")
        if new_name:
            self.theater.name = new_name
            print(f"Название изменено на '{new_name}'")
        else:
            print("Название не может быть пустым")

if __name__ == "__main__":
    cli = TheaterCLI()
    cli.run()