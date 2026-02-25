#!/usr/bin/env python3
"""
Лабораторная работа 1: Арифметические операции в двоичных кодах
Интерактивное меню для выполнения операций над числами
"""

import sys
import os

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(__file__))

from src.direct import to_direct, from_direct, add_direct, multiply_direct, divide_direct
from src.inverse import to_inverse, from_inverse, add_inverse, multiply_inverse, divide_inverse
from src.twos import to_twos, from_twos, add_twos, multiply_twos, divide_twos
from src.float_arith import float_add_variant1


def print_header():
    """Вывод заголовка программы"""
    print("\n" + "=" * 60)
    print("  АРИФМЕТИЧЕСКИЕ ОПЕРАЦИИ В ДВОИЧНЫХ КОДАХ")
    print("=" * 60)


def get_number(prompt: str) -> int:
    """Получение числа от пользователя"""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Ошибка: введите целое число!")


def get_operation() -> str:
    """Получение операции от пользователя"""
    print("\nДоступные операции:")
    print("  1 - Сложение (+)")
    print("  2 - Вычитание (-)")
    print("  3 - Умножение (*)")
    print("  4 - Деление (/)")
    print("  5 - Сложение с плавающей точкой")
    print("  0 - Выход")
    
    while True:
        op = input("\nВыберите операцию (0-5): ").strip()
        if op in ['0', '1', '2', '3', '4', '5']:
            return op
        print("Ошибка: введите число от 0 до 5!")


def print_result_table(num1: int, num2: int, operation: str, 
                       result_direct: str, result_inverse: str, result_twos: str):
    """Вывод таблицы результатов"""
    print("\n" + "=" * 70)
    print(f"  РЕЗУЛЬТАТ: {num1} {operation} {num2}")
    print("=" * 70)
    
    print("\n┌────────────────────┬──────────────────────┬─────────────────────────────┐")
    print("│ Кодировка          │ Двоичный результат │ Десятичный результат        │")
    print("├────────────────────┼──────────────────────┼─────────────────────────────┤")
    print(f"│ Прямой код         │ {result_direct:>20} │ {from_direct(result_direct):>27} │")
    print(f"│ Обратный код       │ {result_inverse:>20} │ {from_inverse(result_inverse):>27} │")
    print(f"│ Дополнительный код │ {result_twos:>20} │ {from_twos(result_twos):>27} │")
    print("└────────────────────┴──────────────────────┴─────────────────────────────┘")


def perform_integer_operation(num1: int, num2: int, op: str):
    """Выполнение целочисленной операции"""
    op_map = {'1': '+', '2': '-', '3': '*', '4': '/'}
    op_symbol = op_map.get(op, '?')
    
    try:
        if op == '1':  # Сложение
            r_direct = add_direct(to_direct(num1), to_direct(num2))
            r_inverse = add_inverse(to_inverse(num1), to_inverse(num2))
            r_twos = add_twos(to_twos(num1), to_twos(num2))
        elif op == '2':  # Вычитание
            r_direct = add_direct(to_direct(num1), to_direct(-num2))
            r_inverse = add_inverse(to_inverse(num1), to_inverse(-num2))
            r_twos = add_twos(to_twos(num1), to_twos(-num2))
        elif op == '3':  # Умножение
            r_direct = multiply_direct(to_direct(num1), to_direct(num2))
            r_inverse = multiply_inverse(to_inverse(num1), to_inverse(num2))
            r_twos = multiply_twos(to_twos(num1), to_twos(num2))
        elif op == '4':  # Деление
            r_direct = divide_direct(to_direct(num1), to_direct(num2))
            r_inverse = divide_inverse(to_inverse(num1), to_inverse(num2))
            r_twos = divide_twos(to_twos(num1), to_twos(num2))
        
        print_result_table(num1, num2, op_symbol, r_direct, r_inverse, r_twos)
        
    except ValueError as e:
        print(f"\nОшибка: {e}")


def perform_float_operation():
    """Выполнение сложения с плавающей точкой (ВАРИАНТ 1)"""
    print("\n" + "=" * 60)
    print("  СЛОЖЕНИЕ С ПЛАВАЮЩЕЙ ТОЧКОЙ (ВАРИАНТ 1)")
    print("  Порядки: Р1=0,100 (4) и Р2=0,101 (5)")
    print("  Числа: 10 и 23")
    print("=" * 60)
    
    num1 = get_number("\nВведите первое число (для знака): ")
    num2 = get_number("Введите второе число (для знака): ")
    
    CODE_NAMES = {1: "Прямой код", 2: "Обратный код", 3: "Дополнительный код"}
    
    print("\n" + "=" * 70)
    print(f"  РЕЗУЛЬТАТ: {abs(num1)} + {abs(num2)} с учётом знаков ({num1}, {num2})")
    print("=" * 70)
    
    print("\n┌────────────────────┬──────────────────────┬─────────────────────────────┐")
    print("│ Кодировка          │ Двоичный результат │ Десятичный результат        │")
    print("├────────────────────┼──────────────────────┼─────────────────────────────┤")
    
    for code in [1, 2, 3]:
        result = float_add_variant1(num1, num2, code, 8, 4, verbose=False)
        
        # Формируем двоичное представление
        binary_result = result['sign'] + result['exponent'] + result['mantissa']
        
        print(f"│ {CODE_NAMES[code]:<18} │ {binary_result:>20} │ {result['value']:>27.1f} │")
    
    print("└────────────────────┴──────────────────────┴─────────────────────────────┘")
    print(f"\nОжидаемые значения:")
    print(f"  10 + 23 = 33")
    print(f"  10 - 23 = -13")
    print(f"  -10 + 23 = 13")
    print(f"  -10 - 23 = -33")


def main():
    """Основная функция"""
    print_header()
    
    while True:
        op = get_operation()
        
        if op == '0':
            print("\nВыход из программы. До свидания!")
            break
        
        if op == '5':
            perform_float_operation()
        else:
            print("\nВведите два целых числа:")
            num1 = get_number("  Первое число: ")
            num2 = get_number("  Второе число: ")
            perform_integer_operation(num1, num2, op)
        
        # Предложение продолжить
        cont = input("\nПродолжить? (y/n): ").strip().lower()
        if cont != 'y':
            print("\nВыход из программы. До свидания!")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")
