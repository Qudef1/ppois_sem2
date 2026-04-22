import sympy
from sympy import symbols
from sympy.logic.boolalg import SOPform

class DownCounterSynthesisLab5:
    """
    Синтез вычитающего счетчика на 8 состояний (3 бита).
    Вариант 2 из задания.
    Базис: НЕ, И, ИЛИ.
    Переменные: q2, q1, q0.
    """
    
    def __init__(self):
        self.truth_table = []
        self.h0_vals = []
        self.h1_vals = []
        self.h2_vals = []

    def generate_truth_table(self):
        """Генерация таблицы переходов и возбуждения"""
        print("=" * 75)
        print("СИНТЕЗ ВЫЧИТАЮЩЕГО СЧЕТЧИКА (8 состояний)")
        print("Базис: НЕ, И, ИЛИ. Тип триггера: Т.")
        print("=" * 75)
        
        # Заголовки: q* (состояние t-1), V, q (состояние t), h (возбуждение)
        print(f"{'q2*':<4} {'q1*':<4} {'q0*':<4} {'V':<4} | {'q2':<4} {'q1':<4} {'q0':<4} | {'h2':<4} {'h1':<4} {'h0':<4}")
        print("-" * 75)
        
        self.truth_table = []
        
        # Перебор всех 16 комбинаций (3 бита + V)
        # Порядок битов в индексе i: q2* q1* q0* V
        for i in range(16):
            q2_s = (i >> 3) & 1
            q1_s = (i >> 2) & 1
            q0_s = (i >> 1) & 1
            V    = i & 1
            
            current = (q2_s << 2) | (q1_s << 1) | q0_s
            
            if V == 0:
                # Режим хранения
                next_state = current
                h2, h1, h0 = 0, 0, 0
            else:
                # Режим вычитания (current - 1) % 8
                next_state = (current - 1) % 8
                
                # h = q(t-1) XOR q(t) => q* XOR q
                h2 = q2_s ^ ((next_state >> 2) & 1)
                h1 = q1_s ^ ((next_state >> 1) & 1)
                h0 = q0_s ^ (next_state & 1)
            
            q2 = (next_state >> 2) & 1
            q1 = (next_state >> 1) & 1
            q0 = next_state & 1
            
            row = {'q2*': q2_s, 'q1*': q1_s, 'q0*': q0_s, 'V': V, 
                   'q2': q2, 'q1': q1, 'q0': q0,
                   'h2': h2, 'h1': h1, 'h0': h0}
            self.truth_table.append(row)
            
            print(f"{q2_s}    {q1_s}    {q0_s}    {V}    | {q2}    {q1}    {q0}    | {h2}    {h1}    {h0}")
        
        print("=" * 75)
        
        # Сохраняем столбцы для карт и минимизации
        self.h0_vals = [r['h0'] for r in self.truth_table]
        self.h1_vals = [r['h1'] for r in self.truth_table]
        self.h2_vals = [r['h2'] for r in self.truth_table]

    def print_karnaugh_map(self, values, func_name):
        """
        Отрисовка карты Карно 4x4.
        Строки: q2* q1*
        Столбцы: q0* V
        """
        print(f"\nДИАГРАММА ВЕЙЧА-КАРНО для {func_name}")
        print("-" * 45)
        print("        q0*V")
        print("      00  01  11  10")
        print("    +---+---+---+---+")
        
        # Код Грея для строк (q2* q1*) и столбцов (q0* V)
        gray = [(0,0), (0,1), (1,1), (1,0)]
        
        for r_q2, r_q1 in gray:
            print(f"q2*q1* {r_q2}{r_q1} |", end=" ")
            for c_q0, c_V in gray:
                # Находим индекс в таблице: q2* q1* q0* V
                idx = (r_q2 << 3) | (r_q1 << 2) | (c_q0 << 1) | c_V
                val = values[idx]
                marker = "1" if val == 1 else "0"
                print(f" {marker} |", end=" ")
            print()
            print("    +---+---+---+---+")

    def minimize_and_print(self):
        """Минимизация и вывод результатов в базисе НЕ-И-ИЛИ"""
        
        # 1. Рисуем карты
        self.print_karnaugh_map(self.h0_vals, "h0(q2*, q1*, q0*, V)")
        self.print_karnaugh_map(self.h1_vals, "h1(q2*, q1*, q0*, V)")
        self.print_karnaugh_map(self.h2_vals, "h2(q2*, q1*, q0*, V)")
        
        # 2. Считаем через sympy (получаем ДНФ)
        # Переменные в порядке старшинства битов индекса i: q2* q1* q0* V
        q2_s, q1_s, q0_s, V = symbols('q2_s q1_s q0_s V')
        vars_list = [q2_s, q2_s, q1_s, q0_s, V] # Исправление: нужно передать список переменных
        vars_list = [q2_s, q1_s, q0_s, V]
        
        m0 = [i for i, v in enumerate(self.h0_vals) if v == 1]
        m1 = [i for i, v in enumerate(self.h1_vals) if v == 1]
        m2 = [i for i, v in enumerate(self.h2_vals) if v == 1]
        
        h0_expr = SOPform(vars_list, m0)
        h1_expr = SOPform(vars_list, m1)
        h2_expr = SOPform(vars_list, m2)
        
        print("\n" + "=" * 75)
        print("АНАЛИТИЧЕСКИЕ ВЫРАЖЕНИЯ (Тупиковые ДНФ)")
        print("Базис: Отрицание (НЕ), Конъюнкция (И), Дизъюнкция (ИЛИ)")
        print("=" * 75)
        
        # Форматирование вывода под требования пользователя
        def format_expr(expr):
            s = str(expr)
            # Преобразуем синтаксис sympy в обычный математический
            s = s.replace('&', ' · ') # Конъюнкция
            s = s.replace('|', ' + ') # Дизъюнкция
            s = s.replace('~', ' NOT ') # Отрицание
            
            # Заменяем имена переменных sympy на принятые в схеме
            s = s.replace('q2_s', "q2*")
            s = s.replace('q1_s', "q1*")
            s = s.replace('q0_s', "q0*")
            s = s.replace('V', "V")
            return s

        print(f"h0 = {format_expr(h0_expr)}")
        print(f"h1 = {format_expr(h1_expr)}")
        print(f"h2 = {format_expr(h2_expr)}")
        
        print("\n" + "=" * 75)
        print("СХЕМА РЕАЛИЗАЦИИ (Логическое описание)")
        print("=" * 75)
        print("Для реализации в базисе НЕ-И-ИЛИ используйте:")
        print("1. Инверторы (НЕ) для получения q0*` и q1*`")
        print("2. Элементы И (конъюнкторы) для формирования слагаемых")
        print("3. Элементы ИЛИ (дизъюнкторы) для суммирования слагаемых")
        print("---------------------------------------------------------")
        print("Уравнения:")
        print("h0 = V")
        print("h1 = V · NOT(q0*)")
        print("h2 = V · NOT(q0*) · NOT(q1*)")
        print("=" * 75)

if __name__ == "__main__":
    lab = DownCounterSynthesisLab5()
    lab.generate_truth_table()
    lab.minimize_and_print()