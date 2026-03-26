import re

class LogicMinimizer:
    def __init__(self, input_expr: str, var_names: list = None):
        self.original_expr = input_expr
        self.var_names = var_names if var_names else ['x1', 'x2', 'x3']
        self.n_vars = len(self.var_names)
        
        self.truth_table = []
        self.values = []
        self.minterms = []
        self.maxterms = []
        
        self.reduced_dnf_terms = []
        self.deadend_dnf_terms = []
        self.reduced_knf_terms = []
        self.deadend_knf_terms = []

        self._build_truth_table()

    def _build_truth_table(self):
        py_expr = self.original_expr
        py_expr = py_expr.replace('~', ' not ')
        py_expr = py_expr.replace('+', ' or ')
        py_expr = py_expr.replace('*', ' and ')
        py_expr = " ".join(py_expr.split())

        self.truth_table = []
        self.values = []
        self.minterms = []
        self.maxterms = []

        for i in range(2 ** self.n_vars):
            bits = []
            vars_dict = {}
            for j in range(self.n_vars):
                bit = (i >> (self.n_vars - 1 - j)) & 1
                bits.append(bit)
                vars_dict[self.var_names[j]] = bool(bit)

            try:
                result = eval(py_expr, {"__builtins__": None}, vars_dict)
                val = 1 if result else 0
            except Exception as e:
                print(f"Ошибка вычисления выражения: {e}")
                return

            self.truth_table.append({'index': i, 'bits': bits, 'value': val})
            self.values.append(val)

            if val == 1:
                self.minterms.append(i)
            else:
                self.maxterms.append(i)

    def print_truth_table(self):
        print("Таблица истинности:")
        header = f"{'№':<3} | " + " ".join([f"{v:<2}" for v in self.var_names]) + f" | {'f':<2}"
        print(header)
        print("-" * len(header))

        for row in self.truth_table:
            bits_str = " ".join([str(b) for b in row['bits']])
            print(f"{row['index']:<3} | {bits_str:<8} | {row['value']:<2}")

    # =========================================================================
    # ПРЕОБРАЗОВАНИЕ БИТОВ В ТЕРМЫ
    # =========================================================================
    
    def bits_to_term_str_dnf(self, bits_str):
        """ДНФ: 0=~x, 1=x, соединение через *"""
        term = []
        for i, bit in enumerate(bits_str):
            if bit == '1':
                term.append(self.var_names[i])
            elif bit == '0':
                term.append(f"~{self.var_names[i]}")
        return "*".join(term) if term else "1"

    def bits_to_term_str_knf(self, bits_str):
        """КНФ: 0=x, 1=~x, соединение через + в скобках"""
        term = []
        for i, bit in enumerate(bits_str):
            if bit == '0':
                term.append(self.var_names[i])
            elif bit == '1':
                term.append(f"~{self.var_names[i]}")
        return "(" + " + ".join(term) + ")" if term else "(0)"

    def term_str_to_dnf(self, terms_list):
        return " + ".join(terms_list) if terms_list else "0"

    def term_str_to_knf(self, terms_list):
        return "*".join(terms_list) if terms_list else "1"

    # =========================================================================
    # ЭТАП 1: ПОИСК ПРОСТЫХ ИМПЛИКАНТ (склеивание)
    # =========================================================================
    
    def _find_prime_implicants(self, indices):
        """
        Переход от совершенной формы к сокращённой.
        Работает одинаково для минтермов (ДНФ) и макстермов (КНФ).
        """
        if not indices:
            return []
        
        terms = [format(m, f'0{self.n_vars}b') for m in indices]
        prime_implicants = []
        
        while True:
            marked = [False] * len(terms)
            new_terms = []
            
            for i in range(len(terms)):
                for j in range(i + 1, len(terms)):
                    diff_pos = -1
                    diff_count = 0
                    for k in range(self.n_vars):
                        if terms[i][k] != terms[j][k]:
                            if terms[i][k] != '-' and terms[j][k] != '-':
                                diff_count += 1
                                diff_pos = k
                            else:
                                diff_count = 2
                    if diff_count == 1:
                        marked[i] = True
                        marked[j] = True
                        glued = terms[i][:diff_pos] + '-' + terms[i][diff_pos+1:]
                        if glued not in new_terms:
                            new_terms.append(glued)
            
            for i, t in enumerate(terms):
                if not marked[i] and t not in prime_implicants:
                    prime_implicants.append(t)
            
            if not new_terms:
                break
            terms = new_terms
        
        return prime_implicants

    # =========================================================================
    # ЭТАП 2: ПРОВЕРКА НА ЛИШНОСТЬ (расчётный метод)
    # =========================================================================
    
    def _check_implicant_redundant(self, implicant, other_implicants, indices):
        """
        Проверка импликанты на лишность (методичка, стр. 2).
        
        Для ДНФ: импликанта = 1, проверяем остальную часть
        Для КНФ: импликанта = 0, проверяем остальную часть
        """
        # Находим макстермы, которые покрывает эта импликанта
        covered_indices = []
        for idx in indices:
            idx_bits = format(idx, f'0{self.n_vars}b')
            match = True
            for k in range(self.n_vars):
                if implicant[k] != '-' and implicant[k] != idx_bits[k]:
                    match = False
                    break
            if match:
                covered_indices.append(idx)
        
        if not covered_indices:
            return True  # Ничего не покрывает → лишняя
        
        # Для каждого покрытого макстерма проверить, покрывается ли другими
        for idx in covered_indices:
            idx_bits = format(idx, f'0{self.n_vars}b')
            covered_by_others = False
            
            for other in other_implicants:
                if other == implicant:
                    continue
                match = True
                for k in range(self.n_vars):
                    if other[k] != '-' and other[k] != idx_bits[k]:
                        match = False
                        break
                if match:
                    covered_by_others = True
                    break
            
            # Если хотя бы один макстерм НЕ покрыт другими → НЕ лишняя
            if not covered_by_others:
                return False
        
        # Все макстермы покрываются другими → лишняя
        return True

    def _remove_redundant_calculation(self, prime_implicants, indices):
        """
        Переход от сокращённой формы к тупиковой (расчётный метод, стр. 2).
        Прямая проверка каждой импликанты на лишность.
        """
        if not prime_implicants:
            return []
        
        result = prime_implicants.copy()
        
        for implicant in prime_implicants:
            others = [p for p in result if p != implicant]
            if self._check_implicant_redundant(implicant, others, indices):
                result.remove(implicant)
        
        return result

    # =========================================================================
    # ЭТАП 2: ТАБЛИЦА ПОКРЫТИЯ (расчётно-табличный метод)
    # =========================================================================
    
    def _build_coverage_table(self, prime_implicants, indices):
        """
        Построение таблицы покрытия (методичка, стр. 3, Таблица 2-3).
        """
        table = {}
        for i, imp in enumerate(prime_implicants):
            table[i] = {}
            for idx in indices:
                idx_bits = format(idx, f'0{self.n_vars}b')
                match = True
                for k in range(self.n_vars):
                    if imp[k] != '-' and imp[k] != idx_bits[k]:
                        match = False
                        break
                table[i][idx] = 'X' if match else ''
        
        # Найти лишние импликанты
        redundant = []
        for i, imp in enumerate(prime_implicants):
            others = [p for j, p in enumerate(prime_implicants) if j != i]
            if self._check_implicant_redundant(imp, others, indices):
                redundant.append(i)
        
        return table, redundant

    def _remove_redundant_table_method(self, prime_implicants, indices):
        """
        Переход от сокращённой к тупиковой (расчётно-табличный метод, стр. 3).
        """
        if not prime_implicants:
            return []
        
        table, redundant = self._build_coverage_table(prime_implicants, indices)
        
        # Вывод таблицы покрытия
        print("\nТаблица покрытия:")
        header = "Импликанты\\Конституэнты | " + " | ".join([str(idx) for idx in indices])
        print(header)
        print("-" * len(header))
        
        for i, imp in enumerate(prime_implicants):
            # Для КНФ выводим в формате (x1 + ~x2)
            if imp in self.reduced_knf_terms or prime_implicants == self.reduced_knf_terms:
                row_str = f"{self.bits_to_term_str_knf(imp):<25} | "
            else:
                row_str = f"{self.bits_to_term_str_dnf(imp):<25} | "
            row_str += " | ".join([table[i][idx] if idx in table[i] else '' for idx in indices])
            if i in redundant:
                row_str += " ← ЛИШНЯЯ"
            print(row_str)
        
        # Удалить лишние
        result = [p for i, p in enumerate(prime_implicants) if i not in redundant]
        return result

    # =========================================================================
    # ЭТАП 2: КАРТА КАРНО (табличный метод)
    # =========================================================================
    
    def _get_kmap_layout(self):
        """Генерация кодов Грея для карты Карно."""
        def get_gray(n):
            if n == 1:
                return ['0', '1']
            prev = get_gray(n - 1)
            return ['0' + x for x in prev] + ['1' + x for x in prev[::-1]]
        
        if self.n_vars == 2:
            return get_gray(1), get_gray(1)
        elif self.n_vars == 3:
            return get_gray(1), get_gray(2)
        elif self.n_vars == 4:
            return get_gray(2), get_gray(2)
        else:
            return None, None

    def _minimize_kmap(self, indices, is_dnf=True):
        """
        Табличный метод (Карты Вейча-Карно, стр. 3-4).
        Прямая минимизация для ДНФ (единицы) или КНФ (нули).
        """
        if self.n_vars > 4:
            print("Warning: Карты Карно для N > 4 не реализованы. Используем метод Куайна.")
            prime = self._find_prime_implicants(indices)
            return self._remove_redundant_calculation(prime, indices)
        
        row_gray, col_gray = self._get_kmap_layout()
        if row_gray is None:
            prime = self._find_prime_implicants(indices)
            return self._remove_redundant_calculation(prime, indices)
        
        n_rows = len(row_gray)
        n_cols = len(col_gray)
        
        # Заполнение карты
        kmap = {}
        for idx in indices:
            b = format(idx, f'0{self.n_vars}b')
            if self.n_vars == 2:
                r_bits, c_bits = b[0], b[1]
            elif self.n_vars == 3:
                r_bits, c_bits = b[0], b[1:]
            elif self.n_vars == 4:
                r_bits, c_bits = b[:2], b[2:]
            
            r_idx = row_gray.index(r_bits) if r_bits in row_gray else 0
            c_idx = col_gray.index(c_bits) if c_bits in col_gray else 0
            kmap[(r_idx, c_idx)] = 1
        
        # Вывод карты Карно
        print("\nКарта Карно:")
        print("    " + "  ".join(col_gray))
        for r_idx, r_code in enumerate(row_gray):
            row_str = f"{r_code}: "
            for c_idx in range(n_cols):
                row_str += " 1  " if kmap.get((r_idx, c_idx)) else " 0  "
            print(row_str)
        
        # Поиск простых импликант и удаление лишних
        prime = self._find_prime_implicants(indices)
        return self._remove_redundant_calculation(prime, indices)

    # =========================================================================
    # МЕТОД 1: РАСЧЁТНЫЙ (прямая минимизация ДНФ и КНФ)
    # =========================================================================
    
    def minimize_calculation_method(self):
        print("\n" + "="*50)
        print("МЕТОД 1: РАСЧЁТНЫЙ")
        print("="*50)
        
        # --- ДНФ (прямая минимизация по минтермам) ---
        print("\n[ДНФ - прямая минимизация]")
        self.reduced_dnf_terms = self._find_prime_implicants(self.minterms)
        self.deadend_dnf_terms = self._remove_redundant_calculation(self.reduced_dnf_terms, self.minterms)
        
        reduced_str = self.term_str_to_dnf([self.bits_to_term_str_dnf(p) for p in self.reduced_dnf_terms])
        deadend_str = self.term_str_to_dnf([self.bits_to_term_str_dnf(p) for p in self.deadend_dnf_terms])
        
        print(f"ТДНФ: {reduced_str}")
        print(f"МДНФ: {deadend_str}")
        print(f"Соответствие ТДНФ/МДНФ: {'ДА' if reduced_str == deadend_str else 'НЕТ'}")
        
        # --- КНФ (прямая минимизация по макстермам) ---
        print("\n[КНФ - прямая минимизация]")
        self.reduced_knf_terms = self._find_prime_implicants(self.maxterms)
        self.deadend_knf_terms = self._remove_redundant_calculation(self.reduced_knf_terms, self.maxterms)
        
        reduced_str = self.term_str_to_knf([self.bits_to_term_str_knf(p) for p in self.reduced_knf_terms])
        deadend_str = self.term_str_to_knf([self.bits_to_term_str_knf(p) for p in self.deadend_knf_terms])
        
        print(f"ТКНФ: {reduced_str}")
        print(f"МКНФ: {deadend_str}")
        print(f"Соответствие ТКНФ/МКНФ: {'ДА' if reduced_str == deadend_str else 'НЕТ'}")

    # =========================================================================
    # МЕТОД 2: РАСЧЁТНО-ТАБЛИЧНЫЙ (прямая минимизация ДНФ и КНФ)
    # =========================================================================
    
    def minimize_calculation_table_method(self):
        print("\n" + "="*50)
        print("МЕТОД 2: РАСЧЁТНО-ТАБЛИЧНЫЙ")
        print("="*50)
        
        # --- ДНФ (прямая минимизация по минтермам) ---
        print("\n[ДНФ - прямая минимизация]")
        self.reduced_dnf_terms = self._find_prime_implicants(self.minterms)
        self.deadend_dnf_terms = self._remove_redundant_table_method(self.reduced_dnf_terms, self.minterms)
        
        reduced_str = self.term_str_to_dnf([self.bits_to_term_str_dnf(p) for p in self.reduced_dnf_terms])
        deadend_str = self.term_str_to_dnf([self.bits_to_term_str_dnf(p) for p in self.deadend_dnf_terms])
        
        print(f"ТДНФ: {reduced_str}")
        print(f"МДНФ: {deadend_str}")
        print(f"Соответствие ТДНФ/МДНФ: {'ДА' if reduced_str == deadend_str else 'НЕТ'}")
        
        # --- КНФ (прямая минимизация по макстермам) ---
        print("\n[КНФ - прямая минимизация]")
        self.reduced_knf_terms = self._find_prime_implicants(self.maxterms)
        self.deadend_knf_terms = self._remove_redundant_table_method(self.reduced_knf_terms, self.maxterms)
        
        reduced_str = self.term_str_to_knf([self.bits_to_term_str_knf(p) for p in self.reduced_knf_terms])
        deadend_str = self.term_str_to_knf([self.bits_to_term_str_knf(p) for p in self.deadend_knf_terms])
        
        print(f"ТКНФ: {reduced_str}")
        print(f"МКНФ: {deadend_str}")
        print(f"Соответствие ТКНФ/МКНФ: {'ДА' if reduced_str == deadend_str else 'НЕТ'}")

    # =========================================================================
    # МЕТОД 3: ТАБЛИЧНЫЙ (прямая минимизация ДНФ и КНФ)
    # =========================================================================
    
    def minimize_table_method(self):
        print("\n" + "="*50)
        print("МЕТОД 3: ТАБЛИЧНЫЙ (КАРТЫ КАРНО)")
        print("="*50)
        
        # --- ДНФ (прямая минимизация по минтермам) ---
        print("\n[ДНФ - прямая минимизация]")
        self.deadend_dnf_terms = self._minimize_kmap(self.minterms, is_dnf=True)
        self.reduced_dnf_terms = self._find_prime_implicants(self.minterms)
        
        reduced_str = self.term_str_to_dnf([self.bits_to_term_str_dnf(p) for p in self.reduced_dnf_terms])
        deadend_str = self.term_str_to_dnf([self.bits_to_term_str_dnf(p) for p in self.deadend_dnf_terms])
        
        print(f"ТДНФ: {reduced_str}")
        print(f"МДНФ: {deadend_str}")
        print(f"Соответствие ТДНФ/МДНФ: {'ДА' if reduced_str == deadend_str else 'НЕТ'}")
        
        # --- КНФ (прямая минимизация по макстермам) ---
        print("\n[КНФ - прямая минимизация]")
        self.deadend_knf_terms = self._minimize_kmap(self.maxterms, is_dnf=False)
        self.reduced_knf_terms = self._find_prime_implicants(self.maxterms)
        
        reduced_str = self.term_str_to_knf([self.bits_to_term_str_knf(p) for p in self.reduced_knf_terms])
        deadend_str = self.term_str_to_knf([self.bits_to_term_str_knf(p) for p in self.deadend_knf_terms])
        
        print(f"ТКНФ: {reduced_str}")
        print(f"МКНФ: {deadend_str}")
        print(f"Соответствие ТКНФ/МКНФ: {'ДА' if reduced_str == deadend_str else 'НЕТ'}")


if __name__ == "__main__":
    expr = "~((x2+~x3)*~(x1*x3))"
    
    lm = LogicMinimizer(expr)
    
    # Таблица истинности
    lm.print_truth_table()
    
    # Все три метода минимизации (прямая минимизация ДНФ и КНФ)
    lm.minimize_calculation_method()
    lm.minimize_calculation_table_method()
    lm.minimize_table_method()