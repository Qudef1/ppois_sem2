import json
import os
import glob
from typing import Optional
from theater import Theater, Setting, AuditoryHall, Ticket, Costume, Stage
from staff import Director, Actor
from managers import StaffManager, HallManager, PerformanceManager, TicketManager
from exception import *
from datetime import datetime

class TheaterCLI:
    def __init__(self):
        name = input("Введите название театра (Enter для 'Default Theater'): ").strip()
        self.theater = Theater(name if name else "Default Theater")
        self.current_hall: Optional[AuditoryHall] = None
        self.current_setting: Optional[Setting] = None

    def display_menu(self):
        print("\n" + "="*50)
        print(f"УПРАВЛЕНИЕ ТЕАТРОМ: {self.theater.name}")
        print("="*50)
        print("1. Добавить зал")
        print("2. Добавить постановку")
        print("3. Добавить актера")
        print("4. Добавить режиссера")
        print("5. Продать билет")
        print("6. Показать информацию о театре")
        print("7. Сохранить состояние театра")
        print("8. Загрузить состояние театра")
        print("9. Привязать постановку к залу (создать билеты)")
        print("10. Изменить название театра")
        print("11. Добавить актера к постановке")
        print("12. Создать костюм")
        print("13. Назначить костюм актеру")
        print("14. Показать доступные билеты")
        print("15. Выступление актера на сцене")
        print("0. Выход")
        print("="*50)

    def get_user_input(self, msg: str) -> str:
        return input(msg).strip()

    def get_validated_int(self, msg: str, min_val: int = None, max_val: int = None, allow_empty: bool = False) -> Optional[int]:
        """Запрашивает целое число с проверкой ввода."""
        while True:
            value = self.get_user_input(msg)
            if allow_empty and value == "":
                return None
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

    def get_validated_float(self, msg: str, min_val: float = None, max_val: float = None, allow_empty: bool = False) -> Optional[float]:
        """Запрашивает число с плавающей точкой с проверкой ввода."""
        while True:
            value = self.get_user_input(msg)
            if allow_empty and value == "":
                return None
            try:
                result = float(value)
                if min_val is not None and result < min_val:
                    print(f"Ошибка: значение должно быть не меньше {min_val}")
                    continue
                if max_val is not None and result > max_val:
                    print(f"Ошибка: значение должно быть не больше {max_val}")
                    continue
                return result
            except ValueError:
                print("Ошибка: введите число (например, 100.50)")

    def get_validated_date(self, msg: str, allow_empty: bool = False) -> Optional[datetime]:
        """Запрашивает дату в формате ГГГГ-ММ-ДД с проверкой ввода."""
        while True:
            value = self.get_user_input(msg)
            if allow_empty and value == "":
                return None
            try:
                return datetime.fromisoformat(value.replace('/', '-'))
            except ValueError:
                print("Ошибка: введите дату в формате ГГГГ-ММ-ДД (например, 2025-06-15)")

    def get_validated_choice(self, msg: str, options: list, allow_empty: bool = False) -> Optional[int]:
        """Запрашивает выбор из списка опций с проверкой ввода."""
        while True:
            value = self.get_user_input(msg)
            if allow_empty and value == "":
                return None
            try:
                result = int(value)
                if 1 <= result <= len(options):
                    return result - 1  # Возвращаем индекс (0-based)
                else:
                    print(f"Ошибка: выберите число от 1 до {len(options)}")
            except ValueError:
                print(f"Ошибка: введите число от 1 до {len(options)}")

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

        # Выбираем директора (или создаем временного)
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

        director_choice = self.get_validated_choice("Выберите номер режиссера: ", directors)
        if director_choice is None:
            return
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
        
        birth_date = self.get_validated_date("Введите дату рождения (ГГГГ-ММ-ДД): ")
        salary = self.get_validated_float("Введите зарплату: ", min_val=0)
        
        role = self.get_user_input("Введите роль актера (Enter для пропуска): ")
        if not role:
            role = None

        actor = Actor(name, birth_date, salary, role)
        self.theater.add_staff(actor)
        print(f"Актер '{name}' успешно добавлен!")

    def add_director(self):
        print("\n--- Добавление режиссера ---")
        name = self.get_user_input("Введите имя режиссера: ")
        if not name:
            print("Ошибка: имя режиссера не может быть пустым")
            return
        
        birth_date = self.get_validated_date("Введите дату рождения (ГГГГ-ММ-ДД): ")
        salary = self.get_validated_float("Введите зарплату: ", min_val=0)

        director = Director(name, birth_date, salary)
        self.theater.add_staff(director)
        print(f"Режиссер '{name}' успешно добавлен!")

    def sell_ticket(self):
        print("\n--- Продажа билета ---")
        ticket_id = self.get_user_input("Введите ID билета для продажи: ")
        if not ticket_id:
            print("Ошибка: ID билета не может быть пустым")
            return

        try:
            result = self.theater.sell_ticket(ticket_id)
            if result:
                print(f"Билет {ticket_id} успешно продан!")
            else:
                print(f"Не удалось продать билет {ticket_id}")
        except TheaterException as e:
            print(f"Ошибка: {e}")
        except Exception as e:
            print(f"Ошибка при продаже билета: {e}")

    def show_theater_info(self):
        while True:
            print("\n" + "="*50)
            print("ИНФОРМАЦИЯ О ТЕАТРЕ")
            print("="*50)
            print(f"Название театра: {self.theater.name}")
            print("-"*50)
            print("Выберите раздел для подробной информации:")
            print("1. Общая сводка")
            print("2. Сотрудники (подробно)")
            print("3. Залы (подробно)")
            print("4. Постановки (подробно)")
            print("5. Билеты (подробно)")
            print("6. Ресурсы (сцены, костюмерные, костюмы)")
            print("0. Назад в главное меню")
            print("="*50)

            choice = self.get_user_input("Выберите раздел (0-6): ")

            if choice == "1":
                self._show_summary()
            elif choice == "2":
                self._show_staff_detailed()
            elif choice == "3":
                self._show_halls_detailed()
            elif choice == "4":
                self._show_settings_detailed()
            elif choice == "5":
                self._show_tickets_detailed()
            elif choice == "6":
                self._show_resources_detailed()
            elif choice == "0":
                break
            else:
                print("Неверный выбор. Пожалуйста, выберите число от 0 до 6.")

    def _show_summary(self):
        print("\n--- Общая сводка ---")
        print(f"Название театра: {self.theater.name}")
        print(f"Количество сотрудников: {len(self.theater.staff_manager.staff)}")
        halls = self.theater.resource_manager.hall_manager.halls
        print(f"Количество залов: {len(halls)}")
        total_capacity = sum(h.capacity for h in halls)
        print(f"Общая вместимость залов: {total_capacity}")
        print(f"Количество постановок: {len(self.theater.performance_manager.settings)}")
        print(f"Количество репетиций: {len(self.theater.performance_manager.repetitions)}")
        tickets = self.theater.ticket_manager.tickets
        print(f"Количество билетов: {len(tickets)}")
        sold = sum(1 for t in tickets if t.is_sold)
        print(f"  - Продано: {sold}")
        print(f"  - Не продано: {len(tickets) - sold}")
        print(f"Количество сцен: {len(self.theater.resource_manager.stages)}")
        print(f"Количество костюмерных: {len(self.theater.resource_manager.costume_rooms)}")
        print(f"Количество костюмов: {len(self.theater.resource_manager.costumes)}")

    def _show_staff_detailed(self):
        print("\n--- Подробная информация о сотрудниках ---")
        staff_list = self.theater.staff_manager.staff
        if not staff_list:
            print("Сотрудники отсутствуют")
            return

        actors = [s for s in staff_list if isinstance(s, Actor)]
        directors = [s for s in staff_list if isinstance(s, Director)]
        from staff import CostumeDesigner
        designers = [s for s in staff_list if isinstance(s, CostumeDesigner)]
        others = [s for s in staff_list if not isinstance(s, (Actor, Director, CostumeDesigner))]

        print(f"Всего сотрудников: {len(staff_list)}")
        print(f"  Актёров: {len(actors)}, Режиссёров: {len(directors)}, "
              f"Костюмеров: {len(designers)}, Прочих: {len(others)}")

        if actors:
            print("\n  Актёры:")
            for i, a in enumerate(actors, 1):
                role_info = f", Роль: {a.role}" if a.role else ""
                costumes = a.get_costumes()
                costume_info = f", Костюмы: {', '.join(costumes.keys())}" if costumes else ""
                print(f"    {i}. {a.name} (возраст: {a.get_age()}, зарплата: {a.get_salary()}{role_info}{costume_info})")

        if directors:
            print("\n  Режиссёры:")
            for i, d in enumerate(directors, 1):
                settings_count = len(d.directed_settings)
                print(f"    {i}. {d.name} (возраст: {d.get_age()}, зарплата: {d.get_salary()}, "
                      f"поставленных спектаклей: {settings_count})")

        if designers:
            print("\n  Костюмеры:")
            for i, cd in enumerate(designers, 1):
                costumes_count = len(cd.created_costumes)
                print(f"    {i}. {cd.name} (возраст: {cd.get_age()}, зарплата: {cd.get_salary()}, "
                      f"созданных костюмов: {costumes_count})")

        if others:
            print("\n  Прочие сотрудники:")
            for i, s in enumerate(others, 1):
                print(f"    {i}. {s.name} (возраст: {s.get_age()}, зарплата: {s.get_salary()})")

    def _show_halls_detailed(self):
        print("\n--- Подробная информация о залах ---")
        halls = self.theater.resource_manager.hall_manager.halls
        if not halls:
            print("Залы отсутствуют")
            return

        for i, hall in enumerate(halls, 1):
            occupied = sum(
                1 for sector in hall.seats
                for row in sector
                for seat in row
                if seat.is_occupied
            )
            print(f"\n  Зал {i}: {hall.name}")
            print(f"    ID: {hall.hall_id}")
            print(f"    Секторов: {hall.sectors}")
            print(f"    Рядов в секторе: {hall.rows_per_sector}")
            print(f"    Мест в ряду: {hall.seats_per_row}")
            print(f"    Общая вместимость: {hall.capacity}")
            print(f"    Занято мест: {occupied}")
            print(f"    Свободно мест: {hall.capacity - occupied}")
            print(f"    Зрителей (audience_count): {hall.audience_count}")

    def _show_settings_detailed(self):
        print("\n--- Подробная информация о постановках ---")
        settings = self.theater.performance_manager.settings
        if not settings:
            print("Постановки отсутствуют")
            return

        for i, setting in enumerate(settings, 1):
            date_str = setting.date.strftime('%Y-%m-%d') if hasattr(setting.date, 'strftime') else str(setting.date)
            print(f"\n  Постановка {i}: {setting.name}")
            print(f"    Продолжительность: {setting.durability} ч")
            print(f"    Дата: {date_str}")
            director_name = setting.director.name if setting.director else "Не назначен"
            print(f"    Режиссёр: {director_name}")
            if hasattr(setting, 'cast') and setting.cast:
                cast_names = ", ".join(a.name for a in setting.cast)
                print(f"    Актёрский состав ({len(setting.cast)}): {cast_names}")
            else:
                print(f"    Актёрский состав: не назначен")

        repetitions = self.theater.performance_manager.repetitions
        if repetitions:
            print(f"\n  --- Репетиции ({len(repetitions)}) ---")
            for i, rep in enumerate(repetitions, 1):
                date_str = rep.date.strftime('%Y-%m-%d') if hasattr(rep.date, 'strftime') else str(rep.date)
                print(f"    Репетиция {i}: {rep.name}")
                print(f"      Продолжительность: {rep.durability} ч")
                print(f"      Дата: {date_str}")
                if hasattr(rep, 'setting') and rep.setting:
                    print(f"      Постановка: {rep.setting.name}")
                if hasattr(rep, 'attendance_list') and rep.attendance_list:
                    names = ", ".join(s.name for s in rep.attendance_list)
                    print(f"      Присутствующие ({len(rep.attendance_list)}): {names}")

    def _show_tickets_detailed(self):
        print("\n--- Подробная информация о билетах ---")
        tickets = self.theater.ticket_manager.tickets
        if not tickets:
            print("Билеты отсутствуют")
            return

        sold = [t for t in tickets if t.is_sold]
        unsold = [t for t in tickets if not t.is_sold]
        total_revenue = sum(t.price for t in sold)

        print(f"  Всего билетов: {len(tickets)}")
        print(f"  Продано: {len(sold)}")
        print(f"  Не продано: {len(unsold)}")
        print(f"  Общая выручка (проданные): {total_revenue:.2f}")

        for i, ticket in enumerate(tickets, 1):
            status = "ПРОДАН" if ticket.is_sold else "НЕ ПРОДАН"
            setting_name = ticket.setting.name if ticket.setting else "Неизвестно"
            print(f"\n  Билет {i}:")
            print(f"    ID: {ticket.ticket_id}")
            print(f"    Цена: {ticket.price:.2f}")
            print(f"    Статус: {status}")
            print(f"    Постановка: {setting_name}")
            print(f"    Зал ID: {ticket.hall_id}")
            print(f"    Сектор: {ticket.sector}, Ряд: {ticket.row}, Место: {ticket.seat}")

    def _show_resources_detailed(self):
        print("\n--- Подробная информация о ресурсах ---")
        rm = self.theater.resource_manager

        # Сцены
        print(f"\n  Сцены ({len(rm.stages)}):")
        if not rm.stages:
            print("    Сцены отсутствуют")
        else:
            for i, stage in enumerate(rm.stages, 1):
                available = "Доступна" if stage.is_available else "Занята"
                equipment_str = ", ".join(stage.equipment) if stage.equipment else "нет"
                print(f"    {i}. {stage.name}")
                print(f"       Вместимость: {stage.capacity}")
                print(f"       Статус: {available}")
                print(f"       Оборудование: {equipment_str}")

        # Костюмерные
        print(f"\n  Костюмерные ({len(rm.costume_rooms)}):")
        if not rm.costume_rooms:
            print("    Костюмерные отсутствуют")
        else:
            for i, room in enumerate(rm.costume_rooms, 1):
                costumes_count = len(room.costume_ids)
                print(f"    {i}. {room.name} (костюмов: {costumes_count})")
                if room.costume_ids:
                    print(f"       ID костюмов: {', '.join(room.costume_ids)}")

        # Костюмы
        print(f"\n  Костюмы ({len(rm.costumes)}):")
        if not rm.costumes:
            print("    Костюмы отсутствуют")
        else:
            for i, costume in enumerate(rm.costumes, 1):
                print(f"    {i}. {costume.name} (размер: {costume.size}, цвет: {costume.color})")

    def save_theater(self):
        print("\n--- Сохранение состояния театра ---")
        filepath = self.get_user_input("Введите путь для сохранения (например, 'theater_state.json'): ")
        try:
            self.theater.save_to_file(filepath)
            print(f"Состояние театра успешно сохранено в {filepath}")
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")

    def _list_available_files(self) -> list:
        """Ищет JSON-файлы в текущей директории и в ../data/"""
        search_dirs = [
            ".",
            "..",
            "../data",
            "data",
        ]
        found_files = []
        for d in search_dirs:
            pattern = os.path.join(d, "*.json")
            found_files.extend(glob.glob(pattern))
        # Убираем дубликаты и сортируем
        found_files = sorted(set(os.path.normpath(f) for f in found_files))
        return found_files

    def load_theater(self):
        print("\n--- Загрузка состояния театра ---")

        available = self._list_available_files()
        if available:
            print("Доступные файлы для загрузки:")
            for i, f in enumerate(available, 1):
                print(f"  {i}. {f}")
            print(f"  0. Ввести путь вручную")
            
            choice = self.get_validated_int("Выберите файл (номер) или 0 для ручного ввода: ", min_val=0, max_val=len(available))
            if choice is None:
                return
            if choice == 0:
                filepath = self.get_user_input("Введите путь к файлу для загрузки: ")
            else:
                filepath = available[choice - 1]
        else:
            print("JSON-файлы не найдены в стандартных директориях.")
            filepath = self.get_user_input("Введите путь к файлу для загрузки: ")

        if not filepath:
            print("Ошибка: путь к файлу не может быть пустым")
            return

        try:
            self.theater.load_from_file(filepath)
            print(f"Состояние театра успешно загружено из {filepath}")
        except FileNotFoundError:
            print(f"Ошибка: файл '{filepath}' не найден")
        except json.JSONDecodeError:
            print(f"Ошибка: файл '{filepath}' содержит некорректный JSON")
        except Exception as e:
            print(f"Ошибка при загрузке: {e}")

    def bind_setting_to_hall(self):
        print("\n--- Привязка постановки к залу (создание билетов) ---")
        # Выбор постановки
        settings = self.theater.performance_manager.settings
        if not settings:
            print("Нет доступных постановок. Сначала добавьте постановку.")
            return

        print("Доступные постановки:")
        for i, setting in enumerate(settings):
            hall_info = f"(зал: {setting.hall.name})" if setting.hall else "(без зала)"
            tickets_info = f", билетов: {len(setting.tickets)}" if setting.tickets else ""
            print(f"{i+1}. {setting.name} {hall_info}{tickets_info}")

        setting_choice = self.get_validated_choice("Выберите номер постановки: ", settings)
        if setting_choice is None:
            return
        selected_setting = settings[setting_choice]

        if selected_setting.hall:
            print(f"Постановка '{selected_setting.name}' уже привязана к залу '{selected_setting.hall.name}'")
            confirm = self.get_user_input("Перепривязать? Y/N: ")
            if confirm.upper() != 'Y':
                return

        # Выбор зала
        halls = self.theater.resource_manager.hall_manager.halls
        if not halls:
            print("Нет доступных залов. Сначала добавьте зал.")
            return

        print("Доступные залы:")
        for i, hall in enumerate(halls):
            print(f"{i+1}. {hall.name} (вместимость: {hall.capacity})")

        hall_choice = self.get_validated_choice("Выберите номер зала: ", halls)
        if hall_choice is None:
            return
        selected_hall = halls[hall_choice]

        base_price = self.get_validated_float("Введите базовую цену билета (руб): ", min_val=1)

        # Привязываем постановку к залу и создаём билеты
        tickets = self.theater.bind_setting_to_hall(selected_setting.name, selected_hall.hall_id, base_price)
        print(f"Создано {len(tickets)} билетов для постановки '{selected_setting.name}' в зале '{selected_hall.name}'!")

    def add_actor_to_setting(self):
        print("\n--- Добавление актера к постановке ---")
        # Выбор актера
        actors = [s for s in self.theater.staff_manager.staff if isinstance(s, Actor)]
        if not actors:
            print("Нет доступных актеров. Сначала добавьте актера.")
            return

        print("Доступные актеры:")
        for i, actor in enumerate(actors):
            role_info = f" ({actor.role})" if actor.role else ""
            print(f"{i+1}. {actor.name}{role_info}")

        actor_choice = self.get_validated_choice("Выберите номер актера: ", actors)
        if actor_choice is None:
            return
        selected_actor = actors[actor_choice]

        # Выбор постановки
        settings = self.theater.performance_manager.settings
        if not settings:
            print("Нет доступных постановок. Сначала добавьте постановку.")
            return

        print("Доступные постановки:")
        for i, setting in enumerate(settings):
            cast_count = len(setting.cast) if hasattr(setting, 'cast') else 0
            print(f"{i+1}. {setting.name} (актеров в постановке: {cast_count})")

        setting_choice = self.get_validated_choice("Выберите номер постановки: ", settings)
        if setting_choice is None:
            return
        selected_setting = settings[setting_choice]

        # Добавляем актера к постановке
        selected_setting.add_cast(selected_actor)
        print(f"Актер '{selected_actor.name}' добавлен к постановке '{selected_setting.name}'!")

    def create_costume(self):
        print("\n--- Создание костюма ---")
        name = self.get_user_input("Введите название костюма: ")
        if not name:
            print("Ошибка: название костюма не может быть пустым")
            return
        
        size = self.get_user_input("Введите размер (S/M/L/XL): ").upper()
        if size not in ['S', 'M', 'L', 'XL', 'XXL']:
            print("Предупреждение: размер может быть некорректным")
        
        color = self.get_user_input("Введите цвет: ")
        if not color:
            print("Ошибка: цвет не может быть пустым")
            return

        costume = Costume(name, size, color)
        self.theater.resource_manager.add_costume(costume)
        print(f"Костюм '{name}' успешно создан!")

    def assign_costume_to_actor(self):
        print("\n--- Назначение костюма актеру ---")
        # Выбор актера
        actors = [s for s in self.theater.staff_manager.staff if isinstance(s, Actor)]
        if not actors:
            print("Нет доступных актеров. Сначала добавьте актера.")
            return

        print("Доступные актеры:")
        for i, actor in enumerate(actors):
            costumes = actor.get_costumes()
            costume_count = len(costumes) if costumes else 0
            print(f"{i+1}. {actor.name} (костюмов: {costume_count})")

        actor_choice = self.get_validated_choice("Выберите номер актера: ", actors)
        if actor_choice is None:
            return
        selected_actor = actors[actor_choice]

        # Выбор костюма
        costumes = self.theater.resource_manager.costumes
        if not costumes:
            print("Нет доступных костюмов. Сначала создайте костюм.")
            return

        print("Доступные костюмы:")
        for i, costume in enumerate(costumes):
            print(f"{i+1}. {costume.name} (размер: {costume.size}, цвет: {costume.color})")

        costume_choice = self.get_validated_choice("Выберите номер костюма: ", costumes)
        if costume_choice is None:
            return
        selected_costume = costumes[costume_choice]

        # Назначаем костюм актеру
        selected_actor.assign_costume(selected_costume)
        print(f"Костюм '{selected_costume.name}' назначен актеру '{selected_actor.name}'!")

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

        if available:
            print("\nДоступные билеты (первые 20):")
            print("-" * 80)
            print(f"{'ID билета':<15} {'Постановка':<20} {'Сектор':<8} {'Ряд':<6} {'Место':<6} {'Цена':<10}")
            print("-" * 80)
            for ticket in available[:20]:
                setting_name = ticket.setting.name if ticket.setting else "Неизвестно"
                print(f"{ticket.ticket_id:<15} {setting_name:<20} {ticket.sector:<8} {ticket.row:<6} {ticket.seat:<6} {ticket.price:.0f} руб.")
            
            if len(available) > 20:
                print(f"... и ещё {len(available) - 20} билетов")

    def actor_performance(self):
        print("\n--- Выступление актера на сцене ---")
        # Выбор актера
        actors = [s for s in self.theater.staff_manager.staff if isinstance(s, Actor)]
        if not actors:
            print("Нет доступных актеров. Сначала добавьте актера.")
            return

        print("Доступные актеры:")
        for i, actor in enumerate(actors):
            role_info = f" ({actor.role})" if actor.role else ""
            print(f"{i+1}. {actor.name}{role_info}")

        actor_choice = self.get_validated_choice("Выберите номер актера: ", actors)
        if actor_choice is None:
            return
        selected_actor = actors[actor_choice]

        # Выбор сцены
        stages = self.theater.resource_manager.stages
        if not stages:
            print("Нет доступных сцен. Создадим сцену по умолчанию.")
            default_stage = Stage("Main Stage", 500, ["Lights", "Sound"])
            self.theater.resource_manager.add_stage(default_stage)
            stages = self.theater.resource_manager.stages
            print("Сцена 'Main Stage' создана автоматически.")

        print("Доступные сцены:")
        for i, stage in enumerate(stages):
            status = "Доступна" if stage.is_available else "Занята"
            print(f"{i+1}. {stage.name} ({status})")

        stage_choice = self.get_validated_choice("Выберите номер сцены: ", stages)
        if stage_choice is None:
            return
        selected_stage = stages[stage_choice]

        # Выбор постановки (опционально)
        settings = self.theater.performance_manager.settings
        selected_setting = None
        if settings:
            print("\nДоступные постановки:")
            for i, setting in enumerate(settings):
                print(f"{i+1}. {setting.name}")

            setting_choice = self.get_validated_choice("Выберите номер постановки (Enter для пропуска): ", settings, allow_empty=True)
            if setting_choice is not None:
                selected_setting = settings[setting_choice]

        # Выступление актера
        print("\n" + "="*60)
        if selected_setting:
            output = selected_actor.perform_on_stage(selected_stage, selected_setting)
        else:
            output = selected_actor.perform_on_stage(selected_stage)
        print(output)
        print("="*60)

    def change_theater_name(self):
        print("\n--- Изменение названия театра ---")
        print(f"Текущее название: {self.theater.name}")
        new_name = self.get_user_input("Введите новое название театра: ")
        if new_name:
            old_name = self.theater.name
            self.theater.name = new_name
            print(f"Название театра изменено: '{old_name}' → '{new_name}'")
        else:
            print("Название не может быть пустым. Изменение отменено.")

    def run(self):
        while True:
            self.display_menu()
            choice = self.get_validated_int("Выберите действие (0-15): ", min_val=0, max_val=15)
            if choice is None:
                continue

            if choice == 1:
                self.add_hall()
            elif choice == 2:
                self.add_setting()
            elif choice == 3:
                self.add_actor()
            elif choice == 4:
                self.add_director()
            elif choice == 5:
                self.sell_ticket()
            elif choice == 6:
                self.show_theater_info()
            elif choice == 7:
                self.save_theater()
            elif choice == 8:
                self.load_theater()
            elif choice == 9:
                self.bind_setting_to_hall()
            elif choice == 10:
                self.change_theater_name()
            elif choice == 11:
                self.add_actor_to_setting()
            elif choice == 12:
                self.create_costume()
            elif choice == 13:
                self.assign_costume_to_actor()
            elif choice == 14:
                self.show_available_tickets()
            elif choice == 15:
                self.actor_performance()
            elif choice == 0:
                print("Выход из программы...")
                break


if __name__ == "__main__":
    cli = TheaterCLI()
    cli.run()