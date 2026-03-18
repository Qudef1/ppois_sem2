from CnfChecker import CNFParser


def test_cnf(formula, expected, description=""):
    parser = CNFParser(formula)
    result = parser.check()
    status = "✓" if result == expected else "✗"
    error_info = f" ({parser.get_error()})" if parser.get_error() else ""
    desc = f" # {description}" if description else ""
    print(f"{status} {formula:35} -> {result:5} (ожидалось {expected:5}){desc}{error_info}")
    return result == expected


def run_tests():
    print("=" * 90)
    print("ТЕСТЫ НА ПРОВЕРКУ КНФ")
    print("=" * 90)

    passed = 0
    total = 0

    print("\n--- ПРАВИЛЬНЫЕ ФОРМУЛЫ (True) ---")
    tests_true = [
        ("A", True, "Простая переменная"),
        ("(!A)", True, "Отрицание"),
        ("(A\\/B)", True, "Дизъюнкция"),
        ("(A/\\B)", True, "Конъюнкция"),
        ("((!A)\\/B)", True, "Отрицание + дизъюнкция"),
        ("((A\\/B)/\\(C\\/D))", True, "КНФ: 2 дизъюнкта"),
        ("(A1\\/B2)", True, "Переменные с цифрами"),
        ("(((A\\/B)/\\(C\\/D))/\\(E\\/F))", True, "КНФ: 3 дизъюнкта"),
        ("((!A1)\\/B2)", True, "Отрицание + переменные с цифрами"),
        ("((!A)\\/(!B))", True, "Два отрицания"),
    ]

    for formula, expected, desc in tests_true:
        total += 1
        if test_cnf(formula, expected, desc):
            passed += 1

    print("\n--- НЕПРАВИЛЬНЫЕ ФОРМУЛЫ (False) ---")
    tests_false = [
        ("(A)", False, "Лишние скобки"),
        ("((A))", False, "Двойные скобки"),
        ("((A1)\\/(B2))", False, "Лишние скобки вокруг переменных"),
        ("(A\\/B\\/C)", False, "Нет скобок для каждой операции"),
        ("(!A\\/B)", False, "! без скобок"),
        ("(A0)", False, "Цифра 0"),
        ("(1)", False, "Только цифра"),
        ("(a)", False, "Строчная буква"),
        ("(!((A)\\/(B)))", False, "Отрицание выражения"),
        ("(A)/\\(B)", False, "Нет скобок для /\\"),
        ("(!(A))", False, "Отрицание скобки"),
        ("((A/\\B)\\/(C/\\D))", False, "Дизъюнкция конъюнктов (ДНФ)"),
        ("(A/\\B)\\/C", False, "Дизъюнкция на верхнем уровне"),
    ]

    for formula, expected, desc in tests_false:
        total += 1
        if test_cnf(formula, expected, desc):
            passed += 1

    print("\n" + "=" * 90)
    print(f"РЕЗУЛЬТАТЫ: {passed}/{total} тестов пройдено")
    print("=" * 90)

    return passed == total


if __name__ == "__main__":
    success = run_tests()
    