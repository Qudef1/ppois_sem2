import random
import sys

class AssociativeProcessor:
    """
    Модель ассоциативного процессора (АП) с параллельной обработкой по словам 
    и последовательной (рекуррентной) обработкой по разрядам.
    Вариант 3: Упорядоченная выборка (сортировка по возрастанию и убыванию)
    """
    def __init__(self, m, n, verbose_comparator=False):
        self.m = m
        self.n = n
        self.memory = []
        self.active = [True] * m
        self.verbose_comparator = verbose_comparator
        self.clock_cycles = 0

    def generate_memory(self):
        """Формирование двоичного массива размером m слов по n разрядов (п.2 методики)"""
        max_val = (1 << self.n) - 1
        self.memory = [random.randint(0, max_val) for _ in range(self.m)]
        print(f"\n[Инициализация] Сгенерирована ассоциативная память: {self.m} слов по {self.n} разрядов.")
        self._print_state()

    def _print_state(self):
        for j, word in enumerate(self.memory):
            bin_repr = format(word, f'0{self.n}b')
            status = "АКТИВНО" if self.active[j] else "ИСКЛЮЧЕНО"
            print(f"  S[{j}] = {bin_repr} ({word:3d}) [{status}]")

    def recurrent_compare(self, candidate, word_idx):
        """
        Вычисление логических переменных g[j,i] и l[j,i] по рекуррентным формулам (1) из методички.
        Обработка идёт от старшего разряда (i=n) к младшему (i=1).
        Начальные условия: g[j,n+1] = 0, l[j,n+1] = 0.
        """
        word = self.memory[word_idx]
        g = 0
        l = 0

        if self.verbose_comparator:
            print(f"    >>> Сравнение S[{word_idx}]={word:0{self.n}b} с аргументом {candidate:0{self.n}b}:")

        for i in range(self.n - 1, -1, -1):
            self.clock_cycles += 1
            a_i = (candidate >> i) & 1
            s_i = (word >> i) & 1

            g_new = g | ((1 ^ a_i) & s_i & (1 ^ l))
            l_new = l | (a_i & (1 ^ s_i) & (1 ^ g))
            g, l = g_new, l_new

            if self.verbose_comparator:
                print(f"      Такт {self.n-i} (разряд {i}): a={a_i}, S={s_i} -> g={g}, l={l}")

        if g == 1 and l == 0: return 1   # S[j] > A
        if g == 0 and l == 1: return -1  # S[j] < A
        return 0                         # S[j] == A (g=0, l=0)

    def _find_extremum(self, find_max=True):
        """
        Поиск максимального/минимального значения методом последовательного построения 
        поискового аргумента (описано в методичке в разделе "Поиск максимального(минимального) значения").
        Внешний аргумент не нужен. Разряды регистра аргумента устанавливаются последовательно.
        """
        n = self.n
        candidate = 0 if find_max else (1 << n) - 1

        for i in range(n - 1, -1, -1):
            if find_max:
                candidate |= (1 << i)
            else:
                candidate &= ~(1 << i)

            found = False
            for j in range(self.m):
                if not self.active[j]: continue
                rel = self.recurrent_compare(candidate, j)
                if (find_max and rel >= 0) or (not find_max and rel <= 0):
                    found = True
                    break

            if not found:
                if find_max:
                    candidate &= ~(1 << i)
                else:
                    candidate |= (1 << i)
        return candidate

    def sort_desc(self):
        """Упорядоченная выборка по убыванию (Вариант 3)"""
        print("\n" + "="*60)
        print("СОРТИРОВКА ПО УБЫВАНИЮ (АССОЦИАТИВНЫЙ ПРОЦЕССОР)")
        print("="*60)
        self.active = [True] * self.m
        result = []

        for step in range(self.m):
            print(f"\n[Итерация {step+1}/{self.m}]")
            val = self._find_extremum(find_max=True)
            
            idx = self.memory.index(val)
            self.active[idx] = False
            result.append(val)
            
            print(f"  >> Найдено MAX: {format(val, f'0{self.n}b')} ({val}). Слово исключено из пула.")
            self._print_state()
            
        print("\nИтог (убывание):", [f"{x:0{self.n}b}({x})" for x in result])
        return result

    def sort_asc(self):
        """Упорядоченная выборка по возрастанию (Вариант 3)"""
        print("\n" + "="*60)
        print("СОРТИРОВКА ПО ВОЗРАСТАНИЮ (АССОЦИАТИВНЫЙ ПРОЦЕССОР)")
        print("="*60)
        self.active = [True] * self.m
        result = []

        for step in range(self.m):
            print(f"\n[Итерация {step+1}/{self.m}]")
            val = self._find_extremum(find_max=False)
            
            idx = self.memory.index(val)
            self.active[idx] = False
            result.append(val)
            
            print(f"  >> Найдено MIN: {format(val, f'0{self.n}b')} ({val}). Слово исключено из пула.")
            self._print_state()
            
        print("\nИтог (возрастание):", [f"{x:0{self.n}b}({x})" for x in result])
        return result


def main():
    M_WORDS = 5
    N_BITS  = 4

    ap = AssociativeProcessor(M_WORDS, N_BITS, verbose_comparator=False)

    ap.generate_memory()
    
    ap.verbose_comparator = True
    
    ap.sort_desc()
    
    ap.verbose_comparator = False
    ap.sort_asc()
    
    print("\n" + "="*60)
    print("СТАТИСТИКА МОДЕЛИРОВАНИЯ")
    print(f"  Тактов сравнения (AP Clock Cycles): {ap.clock_cycles}")
    print(f"  Итераций сортировки: {M_WORDS} (на каждый проход)")
    print("  Модель корректно имитирует: параллелизм по словам, последовательность по разрядам,")
    print("  рекуррентные формулы (1), память результатов (флаги active).")

if __name__ == "__main__":
    main()