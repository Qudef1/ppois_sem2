# Лабораторная работа №1 по дисциплине ЛОИС
# Выполнена студентом группы 421702 БГУИР Сайковским Антоном Валерьевичем
# CLI для проверки формул на КНФ и запуска тестов
#
# 31.03.2026 V1.1 (Добавлена обработка пробелов)
# 

from CnfChecker import CNFParser

def print_help():
    print("""
==========================================================================================
ПРОВЕРКА ФОРМУЛЫ НА КНФ (Конъюнктивная Нормальная Форма)
==========================================================================================

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
    
    print("\n")
    print(f"Формула: {formula}")
    
    if result:
        print("1 ФОРМУЛА ЯВЛЯЕТСЯ КНФ")
    else:
        print("0 ФОРМУЛА НЕ ЯВЛЯЕТСЯ КНФ")
        if parser.get_error():
            print(f"   Ошибка: {parser.get_error()}")  
    return result


def main():
    print_help()

    while True:
        try:
            formula_raw = input("\nВведите формулу (или 'help', 'exit', 'test'): ")
            formula = formula_raw.strip()

            if not formula:
                print("Введите формулу!")
                continue

            # Проверка на пробелы внутри формулы и в начале и в конце
            if len(formula) != len(formula.replace(' ', '')) or formula_raw != formula:
                print('Некорректный вид формулы: слишком много пробелов.')
                continue
                
            if formula.lower() in ['exit', 'quit', 'выход']:
                print("\nДо свидания!")
                break
            
            if formula.lower() == 'help':
                print_help()
                continue
            
            if formula.lower() == 'test':
                print("\nЗапуск тестов...\n")
                import test_cnf
                test_cnf.run_tests()
                continue
            
            check_formula(formula)
            
        except KeyboardInterrupt:
            print("\n\nДо свидания!")
            break
        except Exception as e:
            print(f"\nОшибка: {e}\n")

if __name__ == "__main__":
    main()