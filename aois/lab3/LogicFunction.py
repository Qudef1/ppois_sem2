import re
from typing import List, Dict, Tuple, Optional

class LogicFunction:
    def __init__(self, input_expr: str = "~((x2+~x3)*~(x1*x3))", n_vars: int = 3):
        self.input_expr = input_expr
        self.n_vars = n_vars
        self.truth_table = []
        self.values = []
        self.sdnf_indices = []
        self.sknf_indices = []
        self.sdnf_str = ""
        self.sknf_str = ""
        
        self._build_truth_table()
        self._generate_forms()

    def _build_truth_table(self):
        """Построение таблицы истинности"""
        py_expr = self.input_expr
        py_expr = py_expr.replace('~', ' not ')
        py_expr = py_expr.replace('+', ' or ')
        py_expr = py_expr.replace('*', ' and ')
        py_expr = " ".join(py_expr.split())
        
        self.truth_table = []
        self.values = []
        
        for i in range(2 ** self.n_vars):
            bits = []
            vars_dict = {}
            for j in range(self.n_vars):
                # Для 3 переменных: i=4 (100) -> x1=1, x2=0, x3=0
                bit = (i >> (self.n_vars - 1 - j)) & 1
                bits.append(bit)
                vars_dict[f'x{j+1}'] = bool(bit)
            
            try:
                result = eval(py_expr, {"__builtins__": None}, vars_dict)
                val = 1 if result else 0
            except Exception as e:
                print(f"Ошибка вычисления выражения: {e}")
                val = 0

            self.truth_table.append({'index': i, 'bits': bits, 'value': val})
            self.values.append(val)

    def _generate_forms(self):
        """Генерация СДНФ и СКНФ строк и списков индексов"""
        self.sdnf_indices = []
        self.sknf_indices = []
        sdnf_terms = []
        sknf_terms = []
        
        vars_names = [f'x{j+1}' for j in range(self.n_vars)]
        
        for row in self.truth_table:
            term = []
            for j, bit in enumerate(row['bits']):
                if bit == 0:
                    term.append(f"~{vars_names[j]}")
                else:
                    term.append(vars_names[j])
            
            if row['value'] == 1:
                self.sdnf_indices.append(row['index'])
                sdnf_terms.append("*".join(term))
            else:
                self.sknf_indices.append(row['index'])
                sknf_terms.append("(" + "+".join(term) + ")")
        
        self.sdnf_str = " + ".join(sdnf_terms) if sdnf_terms else "0"
        self.sknf_str = "*".join(sknf_terms) if sknf_terms else "1"

    def get_data_for_minimization(self) -> Dict:
        """
        Возвращает данные для лабораторной работы №3.
        Используется методами минимизации (Квайна, Карно и т.д.)
        """
        return {
            'n_vars': self.n_vars,
            'minterms': self.sdnf_indices,      # Для минимизации СДНФ
            'maxterms': self.sknf_indices,      # Для минимизации СКНФ
            'sdnf_str': self.sdnf_str,
            'sknf_str': self.sknf_str,
            'truth_values': self.values
        }

    def validate_perfect_form(self, form_str: str, form_type: str) -> bool:
        """
        Требование №1: Проверка, что форма является совершенной (СДНФ/СКНФ).
        Все переменные должны присутствовать в каждом члене.
        """
        if form_str == "0" or form_str == "1":
            return True
            
        vars_names = [f'x{j+1}' for j in range(self.n_vars)]
        
        if form_type == 'SDNF':
            # Разделяем по + (дизъюнкция)
            terms = form_str.split(' + ')
            for term in terms:
                term = term.strip()
                # Проверка: каждая переменная (x1, x2, x3) должна быть в терме
                # либо как x, либо как ~x
                for var in vars_names:
                    if var not in term and f"~{var}" not in term:
                        print(f"Ошибка СДНФ: В терме '{term}' отсутствует переменная {var}")
                        return False
        elif form_type == 'SKNF':
            # Разделяем по * (конъюнкция), убираем скобки
            terms = form_str.split('*')
            for term in terms:
                term = term.strip().strip('()')
                for var in vars_names:
                    if var not in term and f"~{var}" not in term:
                        print(f"Ошибка СКНФ: В терме '{term}' отсутствует переменная {var}")
                        return False
        return True

    def check_equivalence(self, terms_dnf: List[str], terms_cnf: List[str]) -> bool:
        """
        Требование №4: Сравнение ТДНФ и ТКНФ на равенство.
        Строит таблицы истинности для обеих минимизированных форм и сравнивает их.
        """
        def evaluate_terms(terms: List[str], form_type: str, n: int) -> List[int]:
            results = []
            for i in range(2 ** n):
                bits = [(i >> (n - 1 - j)) & 1 for j in range(n)]
                vars_dict = {f'x{j+1}': bool(bits[j]) for j in range(n)}
                
                if form_type == 'DNF':
                    # Дизъюнкция: достаточно одного истинного терма
                    overall = False
                    for term in terms:
                        # Парсим терм вида "~x1*x2"
                        term_val = True
                        literals = term.split('*')
                        for lit in literals:
                            lit = lit.strip()
                            if lit.startswith('~'):
                                var_name = lit[1:]
                                lit_val = not vars_dict.get(var_name, False)
                            else:
                                var_name = lit
                                lit_val = vars_dict.get(var_name, False)
                            term_val = term_val and lit_val
                        overall = overall or term_val
                    results.append(1 if overall else 0)
                    
                elif form_type == 'CNF':
                    # Конъюнкция: все термы должны быть истинны
                    overall = True
                    for term in terms:
                        # Парсим терм вида "(x1+~x2)"
                        term = term.strip('()')
                        term_val = False
                        literals = term.split('+')
                        for lit in literals:
                            lit = lit.strip()
                            if lit.startswith('~'):
                                var_name = lit[1:]
                                lit_val = not vars_dict.get(var_name, False)
                            else:
                                var_name = lit
                                lit_val = vars_dict.get(var_name, False)
                            term_val = term_val or lit_val
                        overall = overall and term_val
                    results.append(1 if overall else 0)
            return results

        vals_dnf = evaluate_terms(terms_dnf, 'DNF', self.n_vars)
        vals_cnf = evaluate_terms(terms_cnf, 'CNF', self.n_vars)
        
        return vals_dnf == vals_cnf

    def print_report(self):
        """Вывод результатов для отчета (Лабораторная №2 + база для №3)"""
        print("=" * 60)
        print("ОТЧЕТ ПО ЛОГИЧЕСКОЙ ФУНКЦИИ")
        print("=" * 60)
        print(f"Исходное выражение: {self.input_expr}")
        print(f"Количество переменных: {self.n_vars}")
        print()
        
        print("Таблица истинности:")
        header = f"{'№':<3} | " + " ".join([f"x{j+1}" for j in range(self.n_vars)]) + f" | f"
        print(header)
        print("-" * len(header))
        
        for row in self.truth_table:
            bits_str = " ".join([str(b) for b in row['bits']])
            print(f"{row['index']:<3} | {bits_str} | {row['value']}")
        
        print()
        print("-" * 60)
        print("ФОРМЫ ДЛЯ МИНИМИЗАЦИИ (Лабораторная №3 входные данные):")
        print("-" * 60)
        
        # Валидация
        is_sdnf_valid = self.validate_perfect_form(self.sdnf_str, 'SDNF')
        is_sknf_valid = self.validate_perfect_form(self.sknf_str, 'SKNF')
        
        print(f"1. СДНФ: {self.sdnf_str}")
        print(f"   Индексы минтермов: V({', '.join(map(str, self.sdnf_indices))})")
        print(f"   Корректность СДНФ: {'✓' if is_sdnf_valid else '✗'}")
        print()
        print(f"2. СКНФ: {self.sknf_str}")
        print(f"   Индексы макстермов: ∧({', '.join(map(str, self.sknf_indices))})")
        print(f"   Корректность СКНФ: {'✓' if is_sknf_valid else '✗'}")
        print()
        
        func_index = int("".join(map(str, self.values)), 2)
        print(f"3. Индекс функции: {func_index}")
        print(f"   Двоичный код: {''.join(map(str, self.values))}")
        print("=" * 60)

def solve_logic_function(input_expr: str = "~((x2+~x3)*~(x1*x3))"):
    """Обертка для совместимости со старым кодом"""
    func = LogicFunction(input_expr)
    func.print_report()
    return func.get_data_for_minimization()

if __name__ == "__main__":
    data = solve_logic_function()
    print("\nДанные для передачи в минимизатор:")
    print(data)