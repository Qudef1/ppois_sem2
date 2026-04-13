# Лабораторная работа №1 по дисциплине ЛОИС
# Выполнена студентом группы 421702 БГУИР Сайковским Антоном Валерьевичем
# CLI для проверки формул на КНФ
#
# 31.03.2026 V1.1 (Добавлена обработка пробелов)
# 

from CnfChecker import CNFParser
import time
import sqlite3

conn = sqlite3.connect('tests.db')
cursor = conn.cursor()
def init_db():
    cursor.execute(""" CREATE TABLE IF NOT EXISTS tests (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   formula TEXT NOT NULL,
                   is_cnf BOOLEAN NOT NULL CHECK (is_cnf IN (0, 1))
                   )
""")
    conn.commit()

def print_help():
    print("""
==========================================================================================
ПРОВЕРКА ФОРМУЛЫ НА КНФ (Конъюнктивная Нормальная Форма)
==========================================================================================

Команды:
  - Введите формулу для проверки
  - 'help' - показать справку
  - 'exit' или 'quit' - выход
  - 'test' - пройти тест
==========================================================================================
""")
    
    
def print_syntax():
    print("""
==========================================================================================
ГРАММАТИКА СОКРАЩЕННОГО ЯЗЫКА ЛОГИКИ ВЫСКАЗЫВАНИЙ.
==========================================================================================
    • <латинская буква> ::= A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z
    • <конъюнкция> ::= /\
    • <дизъюнкция> ::= \/
    • <отрицание> ::= !
    • <открывающая скобка> ::= (
    • <закрывающая скобка> ::= )
    • <атомарная формула> ::= <латинская буква>
    • <унарная сложная формула> ::= <открывающая скобка><отрицание><формула><закрывающая скобка>
    • <литерал> ::= <атомарная формула>|<унарная сложная формула>
    • <бинарная сложная формула> :: = <открывающая скобка><формула><бинарная связка><формула><закрывающая скобка>
    • <сложная формула> ::= <унарная сложная формула>|<бинарная сложная формула>
    • <формула> ::= <логическая константа>|<атомарная формула>|<сложная формула>
          
КНФ - конъюнкция дизъюнктов. Пример: (<дизъюнкт><конъюнкция><дизъюнкт>)
""")


def check_formula(formula):
    start = time.perf_counter()
    
    parser = CNFParser(formula)
    result = parser.check()
    
    elapsed = time.perf_counter() - start
    cursor.execute("INSERT INTO tests (formula,is_cnf) VALUES (?,?)", (formula,int(result)))
    conn.commit()
    print("\n")
    print(f"Формула: {formula}")
    
    if result:
        print("1 ФОРМУЛА ЯВЛЯЕТСЯ КНФ")
    else:
        print("0 ФОРМУЛА НЕ ЯВЛЯЕТСЯ КНФ")
        if parser.get_error():
            print(f"    Ошибка: {parser.get_error()}")  
    
    print(f"Время проверки: {elapsed:.6f} сек.")
    return result


def make_test():
    cursor.execute("SELECT formula, is_cnf FROM tests ORDER BY RANDOM() LIMIT 7")
    random_tasks = cursor.fetchall()
    score = 0
    for task in random_tasks:
        print(f"Является ли формула {task[0]} КНФ?\n")
        if int(input("Введите 0, если не является, 1, если является.\n")) == task[1]:
            score += 1
    return round(score/7 * 10, 2)

def main():
    init_db()
    print_help()

    while True:
        try:
            formula_raw = input("\nВведите формулу (или 'help', 'exit', 'test'): ")
            formula = formula_raw.strip()

            if not formula:
                print("Введите формулу!")
                continue

            elif formula.lower().strip() in ['exit', 'quit', 'выход']:
                print("\nДо свидания!")
                break
            
            elif formula.lower() == 'help':
                print_help()
                print_syntax()
                continue

            elif formula.lower() == 'test':
                print( f"Ваша оценка за тест: {make_test()}")

            elif len(formula) != len(formula.replace(' ', '')) or formula_raw != formula:
                print('Некорректный вид ввода: слишком много пробелов.')
                continue
            else:
                check_formula(formula)
            
        except KeyboardInterrupt:
            print("\n\nДо свидания!")
            break
        except Exception as e:
            print(f"\nОшибка: {e}\n")


if __name__ == "__main__":
    main()
    conn.close()