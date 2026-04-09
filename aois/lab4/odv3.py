import itertools

class LogicSynthesizer:
    def __init__(self, inputs, output_names):
        self.inputs = inputs
        self.output_names = output_names
        self.tt = []

    def generate_truth_table(self, func_logic, dc_indices=None):
        self.tt = []
        n = len(self.inputs)
        for i in range(2**n):
            row = [(i >> (n - 1 - j)) & 1 for j in range(n)]
            results = func_logic(row)
            is_dc = (dc_indices is not None and i in dc_indices)
            out_vals = ['x'] * len(results) if is_dc else results
            self.tt.append({
                'index': i,
                'inputs': row,
                'outputs': out_vals,
                'is_dc': is_dc
            })

    def get_sdnf(self, out_idx):
        terms = []
        for row_data in self.tt:
            if row_data['is_dc']: continue
            if row_data['outputs'][out_idx] == 1:
                term_parts = []
                for j, val in enumerate(row_data['inputs']):
                    term_parts.append(self.inputs[j] if val == 1 else f"{self.inputs[j]}'")
                terms.append("·".join(term_parts))
        return " + ".join(terms) if terms else "0"

    def minimize_function(self, out_idx):
        n = len(self.inputs)
        minterms = []
        dont_cares = []
        for row_data in self.tt:
            if row_data['is_dc']:
                dont_cares.append(row_data['index'])
            elif row_data['outputs'][out_idx] == 1:
                minterms.append(row_data['index'])

        primes = self._qm_get_primes(minterms, dont_cares, n)
        return self._qm_get_min_cover(minterms, primes, n)

    def _qm_get_primes(self, minterms, dont_cares, n):
        all_terms = minterms + dont_cares
        groups = {}
        for m in all_terms:
            b = format(m, f'0{n}b')
            groups.setdefault(b.count('1'), []).append((b, frozenset([m])))

        primes = set()

        while True:
            new_groups = {}
            used = set()  # Будем хранить кортежи (mask, cov)

            keys = sorted(groups.keys())
            for i in range(len(keys) - 1):
                for mask1, cov1 in groups[keys[i]]:
                    for mask2, cov2 in groups[keys[i+1]]:
                        diff_count = sum(1 for j in range(n) if mask1[j] != mask2[j])
                        if diff_count == 1:
                            new_mask_list = list(mask1)
                            diff_idx = next(j for j in range(n) if mask1[j] != mask2[j])
                            new_mask_list[diff_idx] = '-'
                            new_mask = "".join(new_mask_list)
                            new_cov = cov1 | cov2
                            new_groups.setdefault(new_mask.count('1'), []).append((new_mask, new_cov))
                            used.add((mask1, cov1))
                            used.add((mask2, cov2))

            for g in groups.values():
                for mask, cov in g:
                    if (mask, cov) not in used:
                        primes.add((mask, cov))

            if not new_groups:
                break
            groups = new_groups

        return primes

    def _qm_get_min_cover(self, minterms, primes, n):
        remaining = set(minterms)
        selected = []

        # Жадный выбор покрытия
        while remaining:
            best = None
            best_cov = set()
            for mask, cov in primes:
                covered = cov & remaining
                if len(covered) > len(best_cov):
                    best = (mask, cov)
                    best_cov = covered
            if best is None:
                break
            selected.append(best)
            remaining -= best_cov

        # Преобразование покрытия в аналитическую форму
        expr_parts = []
        for mask, cov in selected:
            term = []
            for idx, ch in enumerate(mask):
                if ch == '1':
                    term.append(self.inputs[idx])
                elif ch == '0':
                    term.append(f"{self.inputs[idx]}'")
            if term:
                expr_parts.append("·".join(term))
            else:
                expr_parts.append("1")
        return " + ".join(expr_parts)

    def count_transistors(self, expression):
        if expression == "0": return 0
        transistors = 0
        inv_count = expression.count("'")
        transistors += inv_count * 2  # НЕ = 2 транзистора

        terms = expression.split(" + ")
        and_cost = 0
        for term in terms:
            if "·" in term:
                n_vars = len(term.split("·"))
                if n_vars == 2: and_cost += 6
                elif n_vars == 3: and_cost += 8
                elif n_vars >= 4: and_cost += 10

        n_terms = len(terms)
        or_cost = 0
        if n_terms > 1:
            if n_terms == 2: or_cost += 6
            elif n_terms == 3: or_cost += 8
            elif n_terms >= 4: or_cost += 10

        return transistors + and_cost + or_cost

    def print_report(self):
        print("="*60)
        print("ОТЧЕТ ПО ЛАБОРАТОРНОЙ РАБОТЕ №4")
        print("="*60)
        print("\n[1] ТАБЛИЦА ИСТИННОСТИ")
        header = "№ | " + " ".join(self.inputs) + " | " + " | ".join(self.output_names) + " | Статус"
        print(header)
        print("-" * len(header))
        for row in self.tt:
            print(f"{row['index']:<3} | {' '.join(map(str, row['inputs']))} | {' | '.join(map(str, row['outputs']))} | {'Избыточный' if row['is_dc'] else 'Рабочий'}")

        print("\n[2] АНАЛИТИЧЕСКОЕ ОПИСАНИЕ")
        total_transistors = 0
        for i, name in enumerate(self.output_names):
            print(f"\n--- Выход: {name} ---")
            sdnf = self.get_sdnf(i)
            print(f"СДНФ: {name} = {sdnf}")
            minimized = self.minimize_function(i)
            print(f"Минимизированная: {name} = {minimized}")
            trans = self.count_transistors(minimized)
            total_transistors += trans
            print(f"Транзисторы (КМОП): {trans}")
        print("\n" + "="*60)
        print(f"ОБЩЕЕ КОЛИЧЕСТВО ТРАНЗИСТОРОВ: {total_transistors}")
        print("="*60)

def setup_subtractor():
    inputs = ["X1", "X2", "X3"]
    outputs = ["d", "b"]
    def logic(row):
        x1, x2, x3 = row
        d = x1 ^ x2 ^ x3
        b = (not x1 and x2) or (not x1 and x3) or (x2 and x3)
        return [int(d), int(b)]
    synth = LogicSynthesizer(inputs, outputs)
    synth.generate_truth_table(logic)
    return synth

def setup_bcd_converter():
    inputs = ["X3", "X2", "X1", "X0"]
    outputs = ["Y3", "Y2", "Y1", "Y0"]
    dc_indices = [10, 11, 12, 13, 14, 15]
    def logic(row):
        val = (row[0] << 3) + (row[1] << 2) + (row[2] << 1) + row[3]
        res = val + 6
        return [(res >> 3) & 1, (res >> 2) & 1, (res >> 1) & 1, res & 1]
    synth = LogicSynthesizer(inputs, outputs)
    synth.generate_truth_table(logic, dc_indices=dc_indices)
    return synth


if __name__ == "__main__":
    TASK_ID = 2  # 1 для ОДВ-3, 2 для Преобразователя
    
    if TASK_ID == 1:
        print("Запуск синтеза ОДВ-3 (Вычитатель)...")
        synthesizer = setup_subtractor()
    else:
        print("Запуск синтеза Преобразователя Д8421 -> Д8421+6...")
        synthesizer = setup_bcd_converter()
        
    synthesizer.print_report()