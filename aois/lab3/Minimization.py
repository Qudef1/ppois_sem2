"""
Лабораторная работа №3: Минимизация логических функций
Реализует три метода минимизации:
1. Расчетный метод (алгебраические преобразования)
2. Метод Квайна-Мак-Класски (расчетно-табличный)
3. Метод Вейча-Карно (табличный)
"""

from typing import List, Dict, Set, Tuple, Optional
from itertools import combinations
from LogicFunction import LogicFunction


# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================

def bits_to_term(bits: List[int], n_vars: int) -> str:
    """
    Преобразует набор битов в терм СДНФ.
    -1 означает, что переменная удалена (не существенна)
    0 -> ~xN, 1 -> xN
    """
    term = []
    for i, bit in enumerate(bits):
        if bit == -1:
            continue  # переменная удалена
        elif bit == 0:
            term.append(f"~x{i+1}")
        else:
            term.append(f"x{i+1}")
    return "*".join(term) if term else "1"


def term_to_bits(term: str, n_vars: int) -> List[int]:
    """
    Преобразует терм СДНФ в набор битов.
    Возвращает список где 0/1 - значение, -1 - переменная отсутствует
    """
    bits = [-1] * n_vars
    if term == "1":
        return bits
    
    literals = term.split("*")
    for lit in literals:
        lit = lit.strip()
        if lit.startswith("~"):
            var_num = int(lit[2:])  # ~xN -> N
            bits[var_num - 1] = 0
        else:
            var_num = int(lit[1:])  # xN -> N
            bits[var_num - 1] = 1
    return bits


def bits_to_cnf_term(bits: List[int], n_vars: int) -> str:
    """
    Преобразует набор битов в терм СКНФ (для 0 функции).
    Для СКНФ: 0 -> xN, 1 -> ~xN (инверсия по сравнению со СДНФ)
    """
    term = []
    for i, bit in enumerate(bits):
        if bit == -1:
            continue
        elif bit == 0:
            term.append(f"x{i+1}")
        else:
            term.append(f"~x{i+1}")
    return "(" + "+".join(term) + ")" if term else "(0)"


def count_ones(bits: List[int]) -> int:
    """Подсчитывает количество единиц (игнорируя -1)"""
    return sum(1 for b in bits if b == 1)


def differs_by_one(bits1: List[int], bits2: List[int]) -> Tuple[bool, int]:
    """
    Проверяет, отличаются ли два набора битов ровно в одной позиции.
    Возвращает (True, индекс_различия) или (False, -1)
    """
    diff_index = -1
    diff_count = 0
    for i, (b1, b2) in enumerate(zip(bits1, bits2)):
        if b1 != b2:
            if b1 != -1 and b2 != -1:  # оба не -1
                diff_count += 1
                diff_index = i
    return (diff_count == 1, diff_index)


def merge_bits(bits1: List[int], bits2: List[int]) -> List[int]:
    """
    Объединяет два набора битов, заменяя различающуюся позицию на -1
    """
    result = []
    for b1, b2 in zip(bits1, bits2):
        if b1 != b2:
            result.append(-1)
        else:
            result.append(b1)
    return result


# ============================================================================
# КЛАСС 1: РАСЧЕТНЫЙ МЕТОД (AlgebraicMinimizer)
# ============================================================================

class AlgebraicMinimizer:
    """
    Расчетный метод минимизации:
    1. Склеивание (ab + a~b = a)
    2. Поглощение (a + ab = a)
    3. Удаление лишних импликант
    
    Реализует полный цикл склеивания до получения простых импликант,
    затем строит минимальное покрытие.
    """
    
    def __init__(self, n_vars: int):
        self.n_vars = n_vars
    
    def minimize_dnf(self, minterms: List[int]) -> List[str]:
        """
        Минимизация СДНФ расчетным методом.
        Вход: список индексов минтермов
        Выход: список термов минимальной ДНФ
        """
        if not minterms:
            return ["0"]
        
        # Преобразуем минтермы в наборы битов
        terms = []
        for m in minterms:
            bits = []
            for i in range(self.n_vars - 1, -1, -1):
                bits.append((m >> i) & 1)
            terms.append(tuple(bits))
        
        # Получаем все простые импликанты через полное склеивание
        prime_implicants = self._get_all_prime_implicants(terms)
        
        # Строим минимальное покрытие
        minimal_cover = self._get_minimal_cover(prime_implicants, set(minterms))
        
        # Преобразуем в строки
        result = []
        for bits in minimal_cover:
            term_str = bits_to_term(list(bits), self.n_vars)
            if term_str and term_str not in result:
                result.append(term_str)
        
        return result if result else ["0"]
    
    def minimize_cnf(self, maxterms: List[int]) -> List[str]:
        """
        Минимизация СКНФ расчетным методом.
        Для СКНФ: объединяем макстермы, где функция = 0.
        Результат - конъюнкция дизъюнктов.
        """
        if not maxterms:
            return ["1"]
        
        # Преобразуем макстермы в наборы битов
        terms = []
        for m in maxterms:
            bits = []
            for i in range(self.n_vars - 1, -1, -1):
                bits.append((m >> i) & 1)
            terms.append(tuple(bits))
        
        # Получаем все простые импликанты через полное склеивание
        prime_implicants = self._get_all_prime_implicants(terms)
        
        # Строим минимальное покрытие
        minimal_cover = self._get_minimal_cover(prime_implicants, set(maxterms))
        
        # Преобразуем в строки СКНФ
        # Для СКНФ: 0 -> x, 1 -> ~x (инверсия по сравнению со СДНФ)
        result = []
        for bits in minimal_cover:
            term_str = bits_to_cnf_term(list(bits), self.n_vars)
            if term_str and term_str not in result:
                result.append(term_str)
        
        return result if result else ["1"]
    
    def _get_all_prime_implicants(self, terms: List[tuple]) -> List[tuple]:
        """
        Получение всех простых импликант через полное склеивание.
        Алгоритм Квайна: на каждой итерации склеиваем пары,
        немаркированные термы добавляем в простые импликанты.
        """
        if not terms:
            return []
        
        current = list(set(terms))
        all_prime_implicants = set()
        
        while True:
            if not current:
                break
                
            next_round = set()
            used = set()
            
            # Склеиваем все возможные пары
            for i in range(len(current)):
                for j in range(i + 1, len(current)):
                    t1, t2 = current[i], current[j]
                    
                    # Проверяем, можно ли склеить (отличаются в одной позиции)
                    can_merge, _ = self._differs_by_one_tuple(t1, t2)
                    if can_merge:
                        merged = self._merge_tuples(t1, t2)
                        next_round.add(merged)
                        used.add(t1)
                        used.add(t2)
            
            # Немаркированные термы - это простые импликанты
            for t in current:
                if t not in used:
                    all_prime_implicants.add(t)
            
            # Переходим к следующей итерации с объединенными термами
            current = list(next_round)
        
        return list(all_prime_implicants)
    
    def _differs_by_one_tuple(self, t1: tuple, t2: tuple) -> Tuple[bool, int]:
        """
        Проверяет отличие в одной позиции.
        -1 считается как "любое значение", поэтому:
        - (-1, x) где x != -1 - это различие
        - (-1, -1) - это не различие
        - (0, 1) или (1, 0) - это различие
        """
        diff_index = -1
        diff_count = 0
        for i, (b1, b2) in enumerate(zip(t1, t2)):
            if b1 != b2:
                # Если оба не -1, это различие
                # Если один из них -1, а другой нет, это тоже различие
                diff_count += 1
                diff_index = i
        return (diff_count == 1, diff_index)
    
    def _merge_tuples(self, t1: tuple, t2: tuple) -> tuple:
        """Объединяет два набора, заменяя различающуюся позицию на -1"""
        result = []
        for b1, b2 in zip(t1, t2):
            if b1 != b2:
                result.append(-1)
            else:
                result.append(b1)
        return tuple(result)
    
    def _get_minimal_cover(self, prime_implicants: List[tuple], minterms: Set[int]) -> List[tuple]:
        """
        Построение минимального покрытия с помощью таблицы покрытия.
        """
        if not prime_implicants:
            return []
        
        # Вычисляем покрытие для каждой импликанты
        coverage = {}
        for pi in prime_implicants:
            covered = set()
            for m in minterms:
                bits = tuple((m >> i) & 1 for i in range(self.n_vars - 1, -1, -1))
                if self._covers_tuple(pi, bits):
                    covered.add(m)
            coverage[pi] = covered
        
        # Находим существенные импликанты (покрывают уникальные минтермы)
        result = []
        uncovered = set(minterms)
        
        # Сначала добавляем существенные импликанты
        essential = set()
        for m in minterms:
            covering_pis = [pi for pi, cov in coverage.items() if m in cov]
            if len(covering_pis) == 1:
                essential.add(covering_pis[0])
        
        result = list(essential)
        for pi in essential:
            uncovered -= coverage[pi]
        
        # Жадный алгоритм для оставшихся
        while uncovered:
            best_pi = None
            best_count = 0
            
            for pi in prime_implicants:
                if pi in result:
                    continue
                new_covered = coverage[pi] & uncovered
                if len(new_covered) > best_count:
                    best_count = len(new_covered)
                    best_pi = pi
            
            if best_pi is None:
                break
            
            result.append(best_pi)
            uncovered -= coverage[best_pi]
        
        return result
    
    def _covers_tuple(self, term: tuple, bits: tuple) -> bool:
        """Проверяет, покрывает ли терм данный набор битов"""
        for t, b in zip(term, bits):
            if t != -1 and t != b:
                return False
        return True


# ============================================================================
# КЛАСС 2: МЕТОД КВАЙНА-МАК-КЛАССКИ (QuineMcCluskeyMinimizer)
# ============================================================================

class QuineMcCluskeyMinimizer:
    """
    Метод Квайна-Мак-Класски:
    1. Группировка минтермов по количеству единиц
    2. Последовательное склеивание групп
    3. Построение таблицы покрытия
    4. Выбор минимального покрытия
    """
    
    def __init__(self, n_vars: int):
        self.n_vars = n_vars
    
    def minimize_dnf(self, minterms: List[int]) -> List[str]:
        """Минимизация СДНФ методом Квайна-Мак-Класски"""
        if not minterms:
            return ["0"]
        
        # Шаг 1: Группировка по количеству единиц
        groups = self._group_by_ones(minterms)
        
        # Шаг 2: Последовательное склеивание
        prime_implicants, _ = self._find_prime_implicants(groups)
        
        # Шаг 3: Построение таблицы покрытия и выбор минимального
        minimal_cover = self._find_minimal_cover(prime_implicants, minterms)
        
        # Преобразуем в строки
        result = []
        for bits in minimal_cover:
            term_str = bits_to_term(list(bits), self.n_vars)
            if term_str:
                result.append(term_str)
        
        return result if result else ["0"]
    
    def minimize_cnf(self, maxterms: List[int]) -> List[str]:
        """Минимизация СКНФ методом Квайна-Мак-Класски"""
        if not maxterms:
            return ["1"]
        
        # Группировка по количеству единиц (для макстермов)
        groups = {}
        for m in maxterms:
            bits = tuple((m >> i) & 1 for i in range(self.n_vars - 1, -1, -1))
            ones_count = sum(bits)
            if ones_count not in groups:
                groups[ones_count] = []
            groups[ones_count].append(bits)
        
        # Склеивание
        prime_implicants, _ = self._find_prime_implicants(groups)
        
        # Минимальное покрытие
        minimal_cover = self._find_minimal_cover(prime_implicants, maxterms)
        
        # Преобразуем в строки СКНФ
        result = []
        for bits in minimal_cover:
            term_str = bits_to_cnf_term(list(bits), self.n_vars)
            if term_str:
                result.append(term_str)
        
        return result if result else ["1"]
    
    def _group_by_ones(self, minterms: List[int]) -> Dict[int, List[tuple]]:
        """Группировка минтермов по количеству единиц"""
        groups = {}
        for m in minterms:
            bits = tuple((m >> i) & 1 for i in range(self.n_vars - 1, -1, -1))
            ones_count = sum(bits)
            if ones_count not in groups:
                groups[ones_count] = []
            groups[ones_count].append(bits)
        return groups
    
    def _find_prime_implicants(self, groups: Dict[int, List[tuple]]) -> Tuple[Set[tuple], Set[tuple]]:
        """
        Поиск простых импликант путем последовательного склеивания.
        Возвращает (простые импликанты, все промежуточные).
        """
        all_generated = set()
        prime_implicants = set()

        current = set()
        for group in groups.values():
            current.update(group)

        while True:
            next_round = set()
            used = set()

            # Сортируем для последовательного склеивания
            current_list = sorted(current, key=lambda x: (sum(x), x))

            for i, t1 in enumerate(current_list):
                for j, t2 in enumerate(current_list):
                    if j <= i:
                        continue

                    # Проверяем отличие в одной позиции (с учетом -1)
                    diff_count = 0
                    diff_idx = -1
                    for k, (b1, b2) in enumerate(zip(t1, t2)):
                        if b1 != b2:
                            diff_count += 1
                            diff_idx = k

                    if diff_count == 1:
                        # Склеиваем
                        merged = tuple(
                            -1 if k == diff_idx else b1
                            for k, b1 in enumerate(t1)
                        )
                        next_round.add(merged)
                        used.add(t1)
                        used.add(t2)
                        all_generated.add(merged)

            # Немаркированные добавляем в простые импликанты
            for t in current:
                if t not in used:
                    prime_implicants.add(t)

            if not next_round:
                break

            current = next_round

        return prime_implicants, all_generated
    
    def _find_minimal_cover(self, prime_implicants: Set[tuple], 
                           minterms: List[int]) -> List[tuple]:
        """
        Поиск минимального покрытия с помощью таблицы Квайна
        """
        if not prime_implicants:
            return []
        
        # Построение таблицы покрытия
        coverage = {}
        for pi in prime_implicants:
            covered = set()
            for m in minterms:
                bits = tuple((m >> i) & 1 for i in range(self.n_vars - 1, -1, -1))
                if self._covers(pi, bits):
                    covered.add(m)
            coverage[pi] = covered
        
        # Находим существенные импликанты
        result = set()
        uncovered = set(minterms)
        
        # Существенные импликанты (единственные покрывающие некоторые минтермы)
        for m in minterms:
            covering = [pi for pi, cov in coverage.items() if m in cov]
            if len(covering) == 1:
                result.add(covering[0])
        
        for pi in result:
            uncovered -= coverage[pi]
        
        # Жадный алгоритм для остальных
        while uncovered:
            best_pi = None
            best_count = 0
            
            for pi in prime_implicants:
                if pi in result:
                    continue
                new_covered = coverage[pi] & uncovered
                if len(new_covered) > best_count:
                    best_count = len(new_covered)
                    best_pi = pi
            
            if best_pi is None:
                break
            
            result.add(best_pi)
            uncovered -= coverage[best_pi]
        
        return list(result)
    
    def _covers(self, term: tuple, bits: tuple) -> bool:
        """Проверяет, покрывает ли терм данный набор битов"""
        for t, b in zip(term, bits):
            if t != -1 and t != b:
                return False
        return True


# ============================================================================
# КЛАСС 3: МЕТОД ВЕЙЧА-КАРНО (KarnaughMinimizer)
# ============================================================================

class KarnaughMinimizer:
    """
    Метод Вейча-Карно:
    1. Построение карты Карно с кодом Грея
    2. Объединение соседних клеток в прямоугольники 2^k
    3. Чтение минимальной формы
    """
    
    def __init__(self, n_vars: int):
        self.n_vars = n_vars
        # Код Грея для 2 бит: 00, 01, 11, 10
        self.gray_code_2 = [0, 1, 3, 2]  # в десятичном: 00=0, 01=1, 11=3, 10=2
    
    def minimize_dnf(self, minterms: List[int]) -> List[str]:
        """Минимизация СДНФ методом Вейча-Карно"""
        if not minterms:
            return ["0"]
        
        # Получаем все простые импликанты через карту Карно
        implicants = self._find_all_prime_implicants(minterms)
        
        # Выбор минимального покрытия
        minimal_cover = self._select_minimal_cover(implicants, set(minterms))
        
        # Преобразуем в строки
        result = []
        for bits in minimal_cover:
            term_str = bits_to_term(list(bits), self.n_vars)
            if term_str:
                result.append(term_str)
        
        return result if result else ["0"]
    
    def minimize_cnf(self, maxterms: List[int]) -> List[str]:
        """Минимизация СКНФ методом Вейча-Карно"""
        if not maxterms:
            return ["1"]
        
        # Для СКНФ работаем напрямую с макстермами
        implicants = self._find_all_prime_implicants(maxterms)
        minimal_cover = self._select_minimal_cover(implicants, set(maxterms))
        
        # Преобразуем в строки СКНФ
        result = []
        for bits in minimal_cover:
            term_str = bits_to_cnf_term(list(bits), self.n_vars)
            if term_str:
                result.append(term_str)
        
        return result if result else ["1"]
    
    def _find_all_prime_implicants(self, minterms: List[int]) -> List[tuple]:
        """
        Поиск всех простых импликант через перебор объединений.
        Для 3-4 переменных можно перебрать все возможные прямоугольники.
        """
        minterm_set = set(minterms)
        n_cells = 2 ** self.n_vars
        implicants = set()
        
        # Для каждой клетки пробуем создать максимальное объединение
        for start in minterms:
            # Пробуем размеры от наибольшего к наименьшему
            for size_power in range(self.n_vars, -1, -1):
                size = 2 ** size_power
                
                # Проверяем все возможные группы этого размера
                groups = self._find_groups_containing(start, size, minterm_set)
                for group in groups:
                    if group not in implicants:
                        # Проверяем, не покрывается ли эта группа уже существующей
                        is_covered = False
                        for existing in implicants:
                            if self._is_subset(group, existing):
                                is_covered = True
                                break
                        if not is_covered:
                            # Удаляем подмножества
                            implicants = {imp for imp in implicants if not self._is_subset(imp, group)}
                            implicants.add(group)
        
        return list(implicants)
    
    def _is_subset(self, g1: tuple, g2: tuple) -> bool:
        """Проверяет, является ли g1 подмножеством g2"""
        for b1, b2 in zip(g1, g2):
            if b2 != -1 and b1 != b2:
                return False
        # Проверяем, что g1 более специфична (имеет меньше -1)
        g1_specific = sum(1 for b in g1 if b != -1)
        g2_specific = sum(1 for b in g2 if b != -1)
        return g1_specific > g2_specific
    
    def _find_groups_containing(self, minterm: int, size: int, minterm_set: Set[int]) -> List[tuple]:
        """
        Находит все группы данного размера, содержащие данный минтерм.
        """
        groups = []
        bits = tuple((minterm >> i) & 1 for i in range(self.n_vars - 1, -1, -1))
        
        if size == 1:
            groups.append(bits)
            return groups
        
        # Для размера 2^k пробуем комбинировать k направлений
        from itertools import combinations
        
        # Находим всех соседей (отличающихся в 1 бите)
        neighbors = []
        for i in range(self.n_vars):
            new_bits = list(bits)
            new_bits[i] = 1 - new_bits[i]
            neighbor_idx = sum(b * (2 ** (self.n_vars - 1 - j)) for j, b in enumerate(new_bits))
            if neighbor_idx in minterm_set:
                neighbors.append((i, tuple(new_bits)))
        
        # Для размера 2: просто соседи
        if size == 2:
            for _, neighbor_bits in neighbors:
                # Создаем объединенный терм
                merged = tuple(
                    -1 if bits[j] != neighbor_bits[j] else bits[j]
                    for j in range(self.n_vars)
                )
                groups.append(merged)
        
        # Для больших размеров: рекурсивно объединяем
        elif size > 2:
            # Пробуем объединить несколько направлений
            k = size.bit_length() - 1  # log2(size)
            for dirs in combinations(range(len(neighbors)), k):
                # Проверяем, можно ли объединить эти направления
                test_bits = list(bits)
                valid = True
                for d in dirs:
                    dir_idx, _ = neighbors[d]
                    test_bits[dir_idx] = -1  # Помечаем как варьируемое
                
                # Проверяем, все ли клетки группы в minterm_set
                group_valid = True
                for i in range(2 ** k):
                    check_bits = list(bits)
                    for j, d in enumerate(dirs):
                        dir_idx, _ = neighbors[d]
                        if (i >> j) & 1:
                            check_bits[dir_idx] = 1 - check_bits[dir_idx]
                    
                    check_idx = sum((1 if b == 1 else 0) * (2 ** (self.n_vars - 1 - j)) 
                                   for j, b in enumerate(check_bits))
                    if check_idx not in minterm_set:
                        group_valid = False
                        break
                
                if group_valid:
                    merged = tuple(
                        -1 if j in [neighbors[d][0] for d in dirs] else bits[j]
                        for j in range(self.n_vars)
                    )
                    groups.append(merged)
        
        return groups
    
    def _select_minimal_cover(self, implicants: List[tuple], 
                              minterms: Set[int]) -> List[tuple]:
        """Выбор минимального покрытия (жадный алгоритм)"""
        if not implicants:
            return []
        
        # Вычисляем, какие минтермы покрывает каждая импликанта
        coverage = {}
        for imp in implicants:
            covered = set()
            for m in minterms:
                bits = tuple((m >> i) & 1 for i in range(self.n_vars - 1, -1, -1))
                if self._covers(imp, bits):
                    covered.add(m)
            coverage[tuple(imp)] = covered
        
        # Находим существенные импликанты
        result = set()
        uncovered = set(minterms)
        
        for m in minterms:
            covering = [imp for imp, cov in coverage.items() if m in cov]
            if len(covering) == 1:
                result.add(covering[0])
        
        for imp in result:
            uncovered -= coverage[imp]
        
        # Жадный выбор для остальных
        while uncovered:
            best_imp = None
            best_count = 0
            
            for imp, covered in coverage.items():
                if imp in result:
                    continue
                new_covered = covered & uncovered
                if len(new_covered) > best_count:
                    best_count = len(new_covered)
                    best_imp = imp
            
            if best_imp is None:
                break
            
            result.add(best_imp)
            uncovered -= coverage[best_imp]
        
        return [list(imp) for imp in result]
    
    def _covers(self, term: tuple, bits: tuple) -> bool:
        """Проверяет, покрывает ли терм данный набор битов"""
        for t, b in zip(term, bits):
            if t != -1 and t != b:
                return False
        return True


# ============================================================================
# ГЛАВНЫЙ КЛАСС: LogicMinimizer
# ============================================================================

class LogicMinimizer:
    """
    Главный класс для минимизации логических функций.
    Запускает все три метода, сравнивает результаты, генерирует отчет.
    """
    
    def __init__(self, logic_func: LogicFunction):
        self.func = logic_func
        self.n_vars = logic_func.n_vars
        self.minterms = logic_func.sdnf_indices
        self.maxterms = logic_func.sknf_indices
        self.sdnf_str = logic_func.sdnf_str
        self.sknf_str = logic_func.sknf_str
        
        # Результаты минимизации
        self.algebraic_dnf = []
        self.algebraic_cnf = []
        self.quine_dnf = []
        self.quine_cnf = []
        self.karnaugh_dnf = []
        self.karnaugh_cnf = []
        
        # Инициализация минимизаторов
        self.algebraic = AlgebraicMinimizer(self.n_vars)
        self.quine = QuineMcCluskeyMinimizer(self.n_vars)
        self.karnaugh = KarnaughMinimizer(self.n_vars)
    
    def minimize_all(self):
        """Запуск всех методов минимизации"""
        # СДНФ
        self.algebraic_dnf = self.algebraic.minimize_dnf(self.minterms)
        self.quine_dnf = self.quine.minimize_dnf(self.minterms)
        self.karnaugh_dnf = self.karnaugh.minimize_dnf(self.minterms)
        
        # СКНФ
        self.algebraic_cnf = self.algebraic.minimize_cnf(self.maxterms)
        self.quine_cnf = self.quine.minimize_cnf(self.maxterms)
        self.karnaugh_cnf = self.karnaugh.minimize_cnf(self.maxterms)
    
    def _terms_to_string_dnf(self, terms: List[str]) -> str:
        """Преобразует список термов ДНФ в строку"""
        if terms == ["0"] or not terms:
            return "0"
        return " + ".join(terms)
    
    def _terms_to_string_cnf(self, terms: List[str]) -> str:
        """Преобразует список термов КНФ в строку"""
        if terms == ["1"] or not terms:
            return "1"
        return "*".join(terms)
    
    def check_dnf_methods_match(self) -> bool:
        """Проверяет, совпадают ли результаты всех методов для СДНФ"""
        dnf_strings = [
            self._terms_to_string_dnf(self.algebraic_dnf),
            self._terms_to_string_dnf(self.quine_dnf),
            self._terms_to_string_dnf(self.karnaugh_dnf)
        ]
        return len(set(dnf_strings)) == 1
    
    def check_cnf_methods_match(self) -> bool:
        """Проверяет, совпадают ли результаты всех методов для СКНФ"""
        cnf_strings = [
            self._terms_to_string_cnf(self.algebraic_cnf),
            self._terms_to_string_cnf(self.quine_cnf),
            self._terms_to_string_cnf(self.karnaugh_cnf)
        ]
        return len(set(cnf_strings)) == 1
    
    def check_dnf_cnf_equivalence(self) -> bool:
        """
        Проверяет эквивалентность ТДНФ и ТКНФ через таблицу истинности.
        Использует метод из LogicFunction.
        """
        return self.func.check_equivalence(self.algebraic_dnf, self.algebraic_cnf)
    
    def generate_report(self) -> str:
        """Генерация полного отчета"""
        self.minimize_all()
        
        report = []
        report.append("=" * 60)
        report.append("ОТЧЕТ ПО ЛАБОРАТОРНОЙ РАБОТЕ №3")
        report.append("Минимизация логических функций")
        report.append("=" * 60)
        report.append(f"Вариант: {self.func.input_expr}")
        report.append(f"Переменных: {self.n_vars}")
        report.append("")
        
        # Исходные формы
        report.append("ИСХОДНЫЕ ФОРМЫ:")
        report.append(f"СДНФ: {self.sdnf_str}")
        report.append(f"    Индексы: V({', '.join(map(str, self.minterms))})")
        report.append(f"СКНФ: {self.sknf_str}")
        report.append(f"    Индексы: ∧({', '.join(map(str, self.maxterms))})")
        report.append("")
        
        # Минимизация СДНФ
        report.append("=" * 60)
        report.append("МИНИМИЗАЦИЯ СДНФ (ТДНФ)")
        report.append("=" * 60)
        
        dnf_alg = self._terms_to_string_dnf(self.algebraic_dnf)
        dnf_quine = self._terms_to_string_dnf(self.quine_dnf)
        dnf_karnaugh = self._terms_to_string_dnf(self.karnaugh_dnf)
        
        report.append(f"1. Расчетный метод:        {dnf_alg}")
        report.append(f"2. Квайна-Мак-Класски:     {dnf_quine}")
        report.append(f"3. Вейча-Карно:            {dnf_karnaugh}")
        
        dnf_match = self.check_dnf_methods_match()
        report.append(f"✓ Все методы совпали: {'TRUE' if dnf_match else 'FALSE'}")
        report.append("")
        
        # Минимизация СКНФ
        report.append("=" * 60)
        report.append("МИНИМИЗАЦИЯ СКНФ (ТКНФ)")
        report.append("=" * 60)
        
        cnf_alg = self._terms_to_string_cnf(self.algebraic_cnf)
        cnf_quine = self._terms_to_string_cnf(self.quine_cnf)
        cnf_karnaugh = self._terms_to_string_cnf(self.karnaugh_cnf)
        
        report.append(f"1. Расчетный метод:        {cnf_alg}")
        report.append(f"2. Квайна-Мак-Класски:     {cnf_quine}")
        report.append(f"3. Вейча-Карно:            {cnf_karnaugh}")
        
        cnf_match = self.check_cnf_methods_match()
        report.append(f"✓ Все методы совпали: {'TRUE' if cnf_match else 'FALSE'}")
        report.append("")
        
        # Проверка эквивалентности
        report.append("=" * 60)
        report.append("ПРОВЕРКА ЭКВИВАЛЕНТНОСТИ")
        report.append("=" * 60)
        
        dnf_cnf_equiv = self.check_dnf_cnf_equivalence()
        report.append(f"ТДНФ = ТКНФ: {'TRUE' if dnf_cnf_equiv else 'FALSE'} (проверено через таблицу истинности)")
        report.append("")
        
        # Итоговая форма
        report.append("=" * 60)
        report.append("ИТОГОВАЯ МИНИМАЛЬНАЯ ФОРМА")
        report.append("=" * 60)
        report.append(f"ТДНФ: {dnf_alg}")
        report.append(f"ТКНФ: {cnf_alg}")
        report.append("=" * 60)
        
        return "\n".join(report)


# ============================================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ============================================================================

def solve_lab3(input_expr: str = "~((x2+~x3)*~(x1*x3))"):
    """
    Основная функция для запуска лабораторной работы №3.
    
    Args:
        input_expr: Логическое выражение для минимизации
    
    Returns:
        LogicMinimizer: Объект с результатами минимизации
    """
    # Создаем логическую функцию
    logic_func = LogicFunction(input_expr)
    
    # Создаем минимизатор
    minimizer = LogicMinimizer(logic_func)
    
    # Генерируем и выводим отчет
    report = minimizer.generate_report()
    print(report)
    
    return minimizer


# ============================================================================
# ЗАПУСК
# ============================================================================

if __name__ == "__main__":
    minimizer = solve_lab3()
