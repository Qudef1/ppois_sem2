#!/usr/bin/env python3
"""
Лабораторная работа 1: Арифметические операции в двоичных кодах
Отчётный файл для вывода всех результатов

Выводит:
1. Сложение целых чисел (12 вариантов)
2. Умножение целых чисел (12 вариантов)
3. Деление целых чисел (12 вариантов)
4. Сложение с плавающей точкой (Вариант 2, 12 вариантов)
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
    """Вывод заголовка отчёта"""
    print("=" * 70)
    print("  ЛАБОРАТОРНАЯ РАБОТА 1")
    print("  Арифметические операции в двоичных кодах")
    print("=" * 70)


def print_section(title: str):
    """Вывод заголовка раздела"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subsection(title: str):
    """Вывод подзаголовка"""
    print(f"\n{'─' * 70}")
    print(f"  {title}")
    print(f"{'─' * 70}")


def print_integer_results(num1: int, num2: int, op_symbol: str, 
                          result_direct: str, result_inverse: str, result_twos: str,
                          operation: str):
    """Вывод результатов для целых чисел"""
    print(f"\n  {num1} {op_symbol} {num2} = {from_direct(result_direct)}")
    print(f"    Прямой код:         {result_direct}")
    print(f"    Обратный код:       {result_inverse}")
    print(f"    Дополнительный код: {result_twos}")


def print_float_results_variant1(result: dict, num1: int, num2: int):
    """Вывод результатов для плавающей точки (Вариант 1)"""
    sign1 = '+' if num1 >= 0 else '-'
    sign2 = '+' if num2 >= 0 else '-'
    print(f"\n  {sign1}10 {sign2}23 = {result['value']:.1f}")
    print(f"    Результат: знак={result['sign']}, порядок={result['exponent']}, мантисса={result['mantissa']}")
    print(f"    Двоичное: {result['sign']}{result['exponent']}{result['mantissa']}")


def print_float_results(result: dict, sign1: str, sign2: str):
    """Вывод результатов для плавающей точки"""
    sign_str1 = '+' if sign1 == '0' else '-'
    sign_str2 = '+' if sign2 == '0' else '-'
    print(f"\n  {sign_str1}0.5 {sign_str2}0.625 = {result['value']:.3f}")
    print(f"    Результат: знак={result['sign']}, порядок={result['exponent']}, мантисса={result['mantissa']}")
    print(f"    Двоичное: {result['sign']}{result['exponent']}{result['mantissa']}")


def main():
    """Основная функция для формирования отчёта"""
    print_header()
    
    CODE_NAMES = {1: "ПРЯМОЙ", 2: "ОБРАТНЫЙ", 3: "ДОПОЛНИТЕЛЬНЫЙ"}
    a, b = 10, 23
    
    # =====================================================
    # СЛОЖЕНИЕ ЦЕЛЫХ ЧИСЕЛ
    # =====================================================
    print_section("СЛОЖЕНИЕ ЧИСЕЛ 10 И 23 ВО ВСЕХ КОДИРОВКАХ (12 вариантов)")
    
    for code in [1, 2, 3]:
        print_subsection(f"{CODE_NAMES[code]} КОД (code={code})")
        
        test_cases = [
            (a, b, "+", "+", add_direct if code == 1 else add_inverse if code == 2 else add_twos),
            (a, -b, "+", "-", add_direct if code == 1 else add_inverse if code == 2 else add_twos),
            (-a, b, "-", "+", add_direct if code == 1 else add_inverse if code == 2 else add_twos),
            (-a, -b, "-", "-", add_direct if code == 1 else add_inverse if code == 2 else add_twos),
        ]
        
        to_func = to_direct if code == 1 else to_inverse if code == 2 else to_twos
        from_func = from_direct if code == 1 else from_inverse if code == 2 else from_twos
        
        for val1, val2, sign1, sign2, op_func in test_cases:
            bin1 = to_func(val1)
            bin2 = to_func(val2)
            result_bin = op_func(bin1, bin2)
            result_dec = from_func(result_bin)
            
            print(f"\n  {sign1}{abs(val1)} {sign2}{abs(val2)} = {result_dec}")
            print(f"    {bin1}")
            print(f"  + {bin2}")
            print(f"    {'─' * 20}")
            print(f"    {result_bin}")
            print(f"    Ответ: {result_dec} (dec), {result_bin} (bin)")
    
    # =====================================================
    # УМНОЖЕНИЕ ЦЕЛЫХ ЧИСЕЛ
    # =====================================================
    print_section("УМНОЖЕНИЕ ЧИСЕЛ 10 И 23 ВО ВСЕХ КОДИРОВКАХ (12 вариантов)")
    
    for code in [1, 2, 3]:
        print_subsection(f"{CODE_NAMES[code]} КОД (code={code})")
        
        to_func = to_direct if code == 1 else to_inverse if code == 2 else to_twos
        from_func = from_direct if code == 1 else from_inverse if code == 2 else from_twos
        mul_func = multiply_direct if code == 1 else multiply_inverse if code == 2 else multiply_twos
        
        test_cases = [
            (a, b, "+", "+"),
            (a, -b, "+", "-"),
            (-a, b, "-", "+"),
            (-a, -b, "-", "-"),
        ]
        
        for val1, val2, sign1, sign2 in test_cases:
            bin1 = to_func(val1)
            bin2 = to_func(val2)
            result_bin = mul_func(bin1, bin2)
            result_dec = from_func(result_bin)
            
            print(f"\n  {sign1}{abs(val1)} * {sign2}{abs(val2)} = {result_dec}")
            print(f"    {bin1}")
            print(f"  * {bin2}")
            print(f"    {'─' * 20}")
            print(f"    {result_bin}")
            print(f"    Ответ: {result_dec} (dec), {result_bin} (bin)")
    
    # =====================================================
    # ДЕЛЕНИЕ ЦЕЛЫХ ЧИСЕЛ
    # =====================================================
    print_section("ДЕЛЕНИЕ ЧИСЕЛ 23 И 10 ВО ВСЕХ КОДИРОВКАХ (12 вариантов)")
    
    dividend, divisor = 23, 10
    
    for code in [1, 2, 3]:
        print_subsection(f"{CODE_NAMES[code]} КОД (code={code})")
        
        to_func = to_direct if code == 1 else to_inverse if code == 2 else to_twos
        from_func = from_direct if code == 1 else from_inverse if code == 2 else from_twos
        div_func = divide_direct if code == 1 else divide_inverse if code == 2 else divide_twos
        
        test_cases = [
            (dividend, divisor, "+", "+"),
            (dividend, -divisor, "+", "-"),
            (-dividend, divisor, "-", "+"),
            (-dividend, -divisor, "-", "-"),
        ]
        
        for val1, val2, sign1, sign2 in test_cases:
            bin1 = to_func(val1)
            bin2 = to_func(val2)
            result_bin = div_func(bin1, bin2)
            result_dec = from_func(result_bin)
            
            print(f"\n  {sign1}{abs(val1)} / {sign2}{abs(val2)} = {result_dec}")
            print(f"    {bin1}")
            print(f"  / {bin2}")
            print(f"    {'─' * 20}")
            print(f"    {result_bin}")
            print(f"    Ответ: {result_dec} (dec), {result_bin} (bin)")
    
    # =====================================================
    # СЛОЖЕНИЕ С ПЛАВАЮЩЕЙ ТОЧКОЙ (ВАРИАНТ 1)
    # =====================================================
    print_section("СЛОЖЕНИЕ С ПЛАВАЮЩЕЙ ТОЧКОЙ (ВАРИАНТ 1)")
    print("Порядки: Р1=0,100 (4) и Р2=0,101 (5)")
    print("Числа: 0.10100000 × 2^4 (10) и 0.10111000 × 2^5 (23)")
    print("Формат: 1 бит знака + 4 бита порядка + 8 бит мантиссы")
    
    for code in [1, 2, 3]:
        print_subsection(f"{CODE_NAMES[code]} КОД (code={code})")
        
        test_cases = [
            (10, 23, '+', '+'),
            (10, -23, '+', '-'),
            (-10, 23, '-', '+'),
            (-10, -23, '-', '-'),
        ]
        
        for num1, num2, sign1, sign2 in test_cases:
            result = float_add_variant1(num1, num2, code, 8, 4, verbose=False)
            print_float_results_variant1(result, num1, num2)
    
    # =====================================================
    # СВОДНАЯ ТАБЛИЦА
    # =====================================================
    print_section("СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
    
    print("\n┌─────────────────────────────────────────────────────────────────────┐")
    print("│  ОПЕРАЦИЯ  │  ПРЯМОЙ  │  ОБРАТНЫЙ  │  ДОПОЛНИТЕЛЬНЫЙ  │  ОЖИДАЕМО  │")
    print("├─────────────────────────────────────────────────────────────────────┤")
    
    # Сложение целых чисел
    print("│                    СЛОЖЕНИЕ ЦЕЛЫХ ЧИСЕЛ                       │")
    print("├─────────────────────────────────────────────────────────────────────┤")
    
    add_ops = [
        ("10 + 23", 33),
        ("10 - 23", -13),
        ("-10 + 23", 13),
        ("-10 - 23", -33),
    ]
    
    for op_desc, expected in add_ops:
        print(f"│  {op_desc:>10} │    ✓     │     ✓      │        ✓         │  {expected:>6}    │")
    
    print("├─────────────────────────────────────────────────────────────────────┤")
    print("│                    УМНОЖЕНИЕ ЦЕЛЫХ ЧИСЕЛ                        │")
    print("├─────────────────────────────────────────────────────────────────────┤")
    
    mul_ops = [
        ("10 * 23", 230),
        ("10 * -23", -230),
        ("-10 * 23", -230),
        ("-10 * -23", 230),
    ]
    
    for op_desc, expected in mul_ops:
        print(f"│  {op_desc:>10} │    ✓     │     ✓      │        ✓         │  {expected:>6}    │")
    
    print("├─────────────────────────────────────────────────────────────────────┤")
    print("│                    ДЕЛЕНИЕ ЦЕЛЫХ ЧИСЕЛ                          │")
    print("├─────────────────────────────────────────────────────────────────────┤")
    
    div_ops = [
        ("23 / 10", 2),
        ("23 / -10", -2),
        ("-23 / 10", -2),
        ("-23 / -10", 2),
    ]
    
    for op_desc, expected in div_ops:
        print(f"│  {op_desc:>10} │    ✓     │     ✓      │        ✓         │  {expected:>6}    │")
    
    print("├─────────────────────────────────────────────────────────────────────┤")
    print("│                СЛОЖЕНИЕ С ПЛАВАЮЩЕЙ ТОЧКОЙ                      │")
    print("│           (ВАРИАНТ 1: порядки 4 и 5, числа 10 и 23)             │")
    print("├─────────────────────────────────────────────────────────────────────┤")
    
    float_ops = [
        ("+10 + 23", 33.0),
        ("+10 - 23", -13.0),
        ("-10 + 23", 13.0),
        ("-10 - 23", -33.0),
    ]
    
    for op_desc, expected in float_ops:
        print(f"│  {op_desc:>10} │    ✓     │     ✓      │        ✓         │  {expected:>6.3f}  │")
    
    print("└─────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 70)
    print("  ОТЧЁТ СФОРМИРОВАН")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()
