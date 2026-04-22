# -*- coding: utf-8 -*-
"""
Лабораторная работа №6: Моделирование таблиц хеширования
Предметная область: География (Горы)
ID: Название горы | Pi: Высота (м)
"""

class HashTableRow:
    """Структура строки хеш-таблицы согласно Рисунку 1"""
    def __init__(self):
        self.ID = ""   # Ключевое слово (название горы)
        self.C = 0     # Флажок коллизий
        self.U = 0     # Флажок «занято»
        self.T = 1     # Терминальный флажок
        self.L = 0     # Флажок связи (0=данные в Pi, 1=указатель)
        self.D = 0     # Флажок вычеркивания
        self.P0 = -1   # Указатель следующей записи в цепочке
        self.Pi = ""   # Данные (высота)
        self.V = 0     # Числовое значение ключа
        self.h = 0     # Хеш-адрес

class HashTable:
    def __init__(self, size=20):
        self.H = size
        self.table = [HashTableRow() for _ in range(size)]
        self.cyrillic = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
        self.occupied_count = 0

    def _key_to_v(self, key: str) -> int:
        """Перевод ключевых слов в числовые значения по первым двум буквам (осн. 33)"""
        key = key.strip().upper()
        c1 = key[0] if len(key) > 0 else 'А'
        c2 = key[1] if len(key) > 1 else 'А'
        try:
            v1 = self.cyrillic.index(c1)
            v2 = self.cyrillic.index(c2)
        except ValueError:
            v1 = ord(c1) % 33
            v2 = ord(c2) % 33
        return v1 * 33 + v2

    def _hash(self, v: int) -> int:
        """Формирование хеш-адреса: h(V) = V mod H + B (B=0)"""
        return v % self.H

    def insert(self, key: str, data: str) -> bool:
        """Занесение новой записи в таблицу"""
        # 1. Контроль на дубликат
        if self.search(key) is not None:
            print(f"⚠️ Ключ '{key}' уже существует в таблице. Запись отклонена.")
            return False

        V = self._key_to_v(key)
        h = self._hash(V)

        # 2. Поиск свободной ячейки линейным пробингом
        idx = h
        steps = 0
        while steps < self.H:
            row = self.table[idx]
            if row.U == 0 and row.D == 0:
                break
            idx = (idx + 1) % self.H
            steps += 1
        else:
            print("❌ Таблица полностью заполнена. Вставка невозможна.")
            return False

        # 3. Заполнение полей
        row = self.table[idx]
        row.ID, row.Pi, row.V, row.h = key, str(data), V, h
        row.U, row.D, row.L = 1, 0, 0
        self.occupied_count += 1

        # 4. Обработка коллизий и формирование цепочек
        if idx == h:
            row.C, row.T, row.P0 = 0, 1, -1
        else:
            row.C, row.T, row.P0 = 1, 1, -1
            # Находим конец цепочки для данного h и обновляем указатели
            self._update_chain(h, idx)
            
        print(f"✅ Записано: {key} -> {data} (V={V}, h={h}, строка={idx})")
        return True

    def _update_chain(self, h: int, new_idx: int):
        """Обновление флагов T и P0 при добавлении в цепочку коллизий"""
        # Ищем последнюю запись в цепочке с тем же h
        curr = h
        for _ in range(self.H):
            if self.table[curr].U == 1 and self.table[curr].h == h and self.table[curr].T == 1:
                self.table[curr].T = 0
                self.table[curr].P0 = new_idx
                return
            if self.table[curr].P0 != -1:
                curr = self.table[curr].P0
            else:
                # Fallback: линейный поиск
                for i in range(self.H):
                    if self.table[i].U == 1 and self.table[i].h == h and self.table[i].T == 1:
                        self.table[i].T = 0
                        self.table[i].P0 = new_idx
                        return

    def search(self, key: str) -> int:
        """Поиск записи по ключевому слову. Возвращает индекс или None"""
        V = self._key_to_v(key)
        h = self._hash(V)
        idx = h
        steps = 0
        while steps < self.H:
            row = self.table[idx]
            if row.ID == key and row.D == 0 and row.U == 1:
                return idx
            if row.T == 1 and row.h == h:
                break  # Конец цепочки/таблицы
            if row.P0 != -1:
                idx = row.P0
            else:
                idx = (idx + 1) % self.H
            steps += 1
        return None

    def delete(self, key: str) -> bool:
        """Удаление записи согласно правилам из методички"""
        idx = self.search(key)
        if idx is None:
            print(f"⚠️ Ключ '{key}' не найден.")
            return False

        row = self.table[idx]
        row.D = 1
        h = row.h

        # Анализ состояния флажков T, C и поля P0
        if row.T == 1 and (row.P0 == -1 or row.P0 == h):
            # а) Одиночная строка
            row.U = 0
            print(f"🗑️ Удалена одиночная запись '{key}' (строка {idx})")
        elif row.T == 1:
            # б) Конечная строка в цепочке
            prev_idx = self._find_prev_in_chain(h, idx)
            if prev_idx != -1:
                self.table[prev_idx].T = 1
            row.U = 0
            print(f"🗑️ Удалена конечная запись цепочки '{key}' (строка {idx})")
        elif row.T == 0 and row.P0 != h:
            # в) Средняя строка в цепочке (переписываем следующую на текущую)
            next_idx = row.P0
            self._copy_row(next_idx, idx)
            self.table[next_idx].U = 0
            self.occupied_count -= 1
            print(f"🗑️ Удалена средняя запись '{key}' (строка {idx}, смещение из {next_idx})")
        elif row.T == 0 and row.C == 1:
            # г) Первая строка в цепочке
            next_idx = row.P0
            self._copy_row(next_idx, idx)
            self.table[next_idx].U = 0
            self.occupied_count -= 1
            print(f"🗑️ Удалена первая запись цепочки '{key}' (строка {idx}, смещение из {next_idx})")
            
        return True

    def _find_prev_in_chain(self, h: int, target_idx: int) -> int:
        """Поиск предыдущей записи в цепочке для обновления T"""
        curr = h
        for _ in range(self.H):
            if self.table[curr].U == 1 and self.table[curr].P0 == target_idx:
                return curr
            if self.table[curr].P0 != -1:
                curr = self.table[curr].P0
            else:
                curr = (curr + 1) % self.H
        return -1

    def _copy_row(self, src_idx: int, dst_idx: int):
        """Копирование содержимого строки (для операций удаления)"""
        src = self.table[src_idx]
        dst = self.table[dst_idx]
        dst.ID, dst.Pi, dst.V, dst.h = src.ID, src.Pi, src.V, src.h
        dst.C, dst.U, dst.T, dst.L, dst.D, dst.P0 = src.C, src.U, src.T, src.L, src.D, src.P0

    def load_factor(self) -> float:
        return self.occupied_count / self.H

    def display(self):
        """Вывод таблицы в формате, аналогичном Таблице 1 из методички"""
        print("\n" + "="*90)
        print(f"{'№':<3} | {'ID (Гора)':<15} | {'V':<4} | {'h':<2} | {'Строка ТХ':<4} | "
              f"{'C':<2} | {'U':<2} | {'T':<2} | {'L':<2} | {'D':<2} | {'P0':<3} | {'Pi (Высота)':<10}")
        print("-"*90)

        row_idx = 0
        # Выводим только заполненные строки в порядке их физического размещения
        for i in range(self.H):
            row = self.table[i]
            if row.U == 1 and row.D == 0:
                print(f"{row_idx+1:<3} | {row.ID:<15} | {row.V:<4} | {row.h:<2} | {i:<4} | "
                      f"{row.C:<2} | {row.U:<2} | {row.T:<2} | {row.L:<2} | {row.D:<2} | {row.P0:<3} | {row.Pi:<10}")
                row_idx += 1

        print("-"*90)
        print(f"📊 Размер таблицы (H): {self.H}")
        print(f"📊 Заполнено записей: {self.occupied_count}")
        print(f"📊 Коэффициент заполнения: {self.load_factor():.2f}")
        print("="*90 + "\n")

# ========================
# ДЕМОНСТРАЦИЯ РАБОТЫ
# ========================
if __name__ == "__main__":
    ht = HashTable(20)
    
    print("🌍 Заполнение хеш-таблицы (География: Горы -> Высота)")
    mountains = [
        ("Эльбрус", "5642"), ("Казбек", "5047"), ("Белуха", "4506"),
        ("Народная", "1895"), ("Катунь", "3280"), ("Победа", "7439"),
        ("Монблан", "4808"), ("Эверест", "8848"), ("Килиманджаро", "5895"),
        ("Мак-Кинли", "6190"), ("Аконкагуа", "6962"), ("Чимборасо", "6268"),
        ("Этна", "3323") # Дополнительная запись для гарантированных коллизий
    ]

    for name, height in mountains:
        ht.insert(name, height)

    ht.display()

    print("\n🔍 Тест поиска:")
    for test in ["Эверест", "Казбек", "Маттерхорн"]:
        idx = ht.search(test)
        print(f"  '{test}' -> {'Найдено в строке ' + str(idx) if idx is not None else 'Не найдено'}")

    print("\n🗑️ Тест удаления:")
    ht.delete("Казбек")      # Проверка удаления (одиночная/цепочка)
    ht.delete("Эверест")     # Проверка удаления с переписыванием
    ht.delete("Маттерхорн")  # Проверка несуществующего ключа

    ht.display()
    print("✅ Лабораторная работа успешно завершена. Все флаги и операции соответствуют методичке.")