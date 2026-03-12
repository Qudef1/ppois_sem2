import re

def solve_logic_function(input_expr: str = "~((x2+~x3)*~(x1*x3))"):
    
    print(f"Исходная функция: {input_expr}")
    print("-" * 40)
    
    py_expr = input_expr
    py_expr = py_expr.replace('~', ' not ')
    py_expr = py_expr.replace('+', ' or ')
    py_expr = py_expr.replace('*', ' and ')
    
    py_expr = " ".join(py_expr.split())
    
    truth_table = []
    values = []
    
    print("Таблица истинности:")
    print(f"{'№':<3} | {'x1':<2} {'x2':<2} {'x3':<2} | {'f':<2}")
    print("-" * 20)
    
    for i in range(8):
        b1 = (i >> 2) & 1
        b2 = (i >> 1) & 1
        b3 = (i >> 0) & 1
        
        vars_dict = {
            'x1': bool(b1),
            'x2': bool(b2),
            'x3': bool(b3)
        }
        
        try:
            result = eval(py_expr, {"__builtins__": None}, vars_dict)
            val = 1 if result else 0
        except Exception as e:
            print(f"Ошибка вычисления выражения: {e}")
            return

        truth_table.append({'index': i, 'bits': [b1, b2, b3], 'value': val})
        values.append(val)
        
        print(f"{i:<3} | {b1:<2} {b2:<2} {b3:<2} | {val:<2}")

    sdnf_terms = []
    sdnf_indices = []
    for row in truth_table:
        if row['value'] == 1:
            sdnf_indices.append(row['index'])
            term = []
            vars_names = ['x1', 'x2', 'x3']
            for j, bit in enumerate(row['bits']):
                if bit == 0:
                    term.append(f"~{vars_names[j]}")
                else:
                    term.append(vars_names[j])
            sdnf_terms.append("/\\".join(term))
    
    sdnf_str = " + ".join(sdnf_terms) if sdnf_terms else "0"
    
    sknf_terms = []
    sknf_indices = []
    for row in truth_table:
        if row['value'] == 0:
            sknf_indices.append(row['index'])
            term = []
            vars_names = ['x1', 'x2', 'x3']
            for j, bit in enumerate(row['bits']):
                if bit == 1:
                    term.append(f"~{vars_names[j]}")
                else:
                    term.append(vars_names[j])
            sknf_terms.append("(" + " + ".join(term) + ")")
            
    sknf_str = "/\\".join(sknf_terms) if sknf_terms else "1"
    
    func_index = 0
    for j, val in enumerate(values):
        weight = 2 ** (7 - j)
        func_index += val * weight
        
    # 7. Вывод результатов
    print("-" * 40)
    print("РЕЗУЛЬТАТЫ ДЛЯ ОТЧЕТА:")
    print("-" * 40)
    print(f"1. СДНФ: {sdnf_str}")
    print(f"   Числовая форма (Минтермы): V({', '.join(map(str, sdnf_indices))})")
    print()
    print(f"2. СКНФ: {sknf_str}")
    print(f"   Числовая форма (Макстермы): /\\({', '.join(map(str, sknf_indices))})")
    print()
    print(f"3. Индекс функции (i): {func_index}")
    print(f"   (Двоичный код функции: {''.join(map(str, values))})")
    print("-" * 40)

    

if __name__ == "__main__":
    solve_logic_function()