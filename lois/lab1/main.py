from CnfChecker import CNFParser


def print_help():
    print("""
==========================================================================================
ПРОВЕРКА ФОРМУЛЫ НА КНФ (Конъюнктивная Нормальная Форма)
==========================================================================================

Правила записи формул:
  • Переменные: заглавные буквы + цифры 1-9 (A, B, A1, B23)
  • Запрещено: цифра 0 в имени переменной (A0 - нельзя)
  • Отрицание: !A (должно быть в скобках: (!A))
  • Дизъюнкция: \\/ (ИЛИ)
  • Конъюнкция: /\\ (И)
  • Скобки: каждая операция должна быть в скобках
  • Количество пар скобок = количеству операторов

Примеры правильных формул:
  • A                    - простая переменная
  • (!A)                 - отрицание
  • (A\\/B)              - дизъюнкция
  • ((A\\/B)/\\(C\\/D))  - КНФ из двух дизъюнктов

Команды:
  • Введите формулу для проверки
  • 'help' - показать справку
  • 'exit' или 'quit' - выход
  • 'test' - запустить тесты
==========================================================================================
""")


def check_formula(formula):
    parser = CNFParser(formula)
    result = parser.check()
    
    print("\n" + "=" * 90)
    print(f"Формула: {formula}")
    print("-" * 90)
    
    if result:
        print("✅ Результат: ФОРМУЛА ЯВЛЯЕТСЯ КНФ")
    else:
        print("❌ Результат: ФОРМУЛА НЕ ЯВЛЯЕТСЯ КНФ")
        if parser.get_error():
            print(f"   Ошибка: {parser.get_error()}")
    
    # Статистика
    ops = formula.count('\\/') + formula.count('/\\') + formula.count('!')
    brackets = formula.count('(')
    print(f"   Операторов: {ops} (\\/: {formula.count('\\/')}, /\\: {formula.count('/\\')}, !: {formula.count('!')})")
    print(f"   Пар скобок: {brackets}")
    print(f"   Соответствие: {'✓' if ops == brackets else '✗'}")
    print("=" * 90 + "\n")
    
    return result


def main():
    print_help()
    
    while True:
        try:
            formula = input("\nВведите формулу (или 'help', 'exit', 'test'): ").strip()
            
            if not formula:
                print("⚠️  Введите формулу!")
                continue
            
            if formula.lower() in ['exit', 'quit', 'выход']:
                print("\n👋 До свидания!")
                break
            
            if formula.lower() == 'help':
                print_help()
                continue
            
            if formula.lower() == 'test':
                print("\n🧪 Запуск тестов...\n")
                import test_cnf
                test_cnf.run_tests()
                continue
            
            check_formula(formula)
            
        except KeyboardInterrupt:
            print("\n\n👋 До свидания!")
            break
        except Exception as e:
            print(f"\n❌ Ошибка: {e}\n")


if __name__ == "__main__":
    main()