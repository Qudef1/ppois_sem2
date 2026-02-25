"""
Арифметика с плавающей точкой
Формат: знак (1 бит) + порядок (4 бита) + мантисса (8 бит)

ВАРИАНТ 1: Порядки интерпретируются как целые числа
Р1 = 0,100 = 4, Р2 = 0,101 = 5
"""

from .base import add_binary_strings, subtract_binary_strings, compare_binary
from .direct import to_direct, from_direct
from .inverse import to_inverse, from_inverse
from .twos import to_twos, from_twos


def float_add(mant_a: str, exp_a: str, sign_a: str,
              mant_b: str, exp_b: str, sign_b: str,
              code: int, mantissa_bits: int = 8, exponent_bits: int = 4,
              verbose: bool = True) -> dict:
    """Сложение двух чисел с плавающей точкой"""
    exp_a_val = _from_exp(exp_a, code)
    exp_b_val = _from_exp(exp_b, code)
    
    if verbose:
        print(f"  Порядок A: {exp_a} ({exp_a_val}), Порядок B: {exp_b} ({exp_b_val})")
    
    # Выравнивание порядков
    if exp_a_val > exp_b_val:
        exp_diff = exp_a_val - exp_b_val
        if verbose:
            print(f"  Выравнивание: сдвиг мантиссы B вправо на {exp_diff}")
        mant_b_aligned = ('0' * exp_diff + mant_b)[:mantissa_bits].zfill(mantissa_bits)
        mant_a_aligned = mant_a
        result_exp_val = exp_a_val
    else:
        exp_diff = exp_b_val - exp_a_val
        if verbose:
            print(f"  Выравнивание: сдвиг мантиссы A вправо на {exp_diff}")
        mant_a_aligned = ('0' * exp_diff + mant_a)[:mantissa_bits].zfill(mantissa_bits)
        mant_b_aligned = mant_b
        result_exp_val = exp_b_val
    
    if verbose:
        print(f"  Мантисса A: {mant_a_aligned}, Мантисса B: {mant_b_aligned}")
    
    # Сложение/вычитание мантисс
    if sign_a == '0' and sign_b == '0':
        mant_sum, carry = add_binary_strings(mant_a_aligned, mant_b_aligned)
        result_sign = '0'
        if verbose:
            print(f"  Сложение мантисс: {mant_sum} (перенос: {carry})")
        if carry:
            mant_sum = '1' + mant_sum[:-1]
            result_exp_val += 1
    elif sign_a == '1' and sign_b == '1':
        mant_sum, carry = add_binary_strings(mant_a_aligned, mant_b_aligned)
        result_sign = '1'
        if verbose:
            print(f"  Сложение мантисс: {mant_sum} (перенос: {carry})")
        if carry:
            mant_sum = '1' + mant_sum[:-1]
            result_exp_val += 1
    else:
        cmp = compare_binary(mant_a_aligned, mant_b_aligned)
        if sign_a == '0':
            if cmp >= 0:
                mant_sum = subtract_binary_strings(mant_a_aligned, mant_b_aligned)
                result_sign = '0'
            else:
                mant_sum = subtract_binary_strings(mant_b_aligned, mant_a_aligned)
                result_sign = '1'
        else:
            if cmp >= 0:
                mant_sum = subtract_binary_strings(mant_a_aligned, mant_b_aligned)
                result_sign = '1'
            else:
                mant_sum = subtract_binary_strings(mant_b_aligned, mant_a_aligned)
                result_sign = '0'
        if verbose:
            print(f"  Вычитание мантисс: {mant_sum}")
    
    # Нормализация
    mant_sum = mant_sum.zfill(mantissa_bits)
    if mant_sum == '0' * mantissa_bits:
        return {'sign': '0', 'mantissa': '0' * mantissa_bits, 'exponent': '0' * exponent_bits, 'value': 0}
    
    shift_count = 0
    while mant_sum and mant_sum[0] == '0':
        mant_sum = mant_sum[1:] + '0'
        shift_count += 1
    
    if shift_count > 0:
        result_exp_val -= shift_count
    
    result_exp = _to_exp(result_exp_val, code, exponent_bits)
    
    if verbose:
        print(f"  Нормализация: сдвиг влево на {shift_count}, порядок: {result_exp} ({result_exp_val})")
    
    # Десятичное значение
    mant_val = sum(1 / (2 ** (i + 1)) for i, bit in enumerate(mant_sum[:mantissa_bits]) if bit == '1')
    result_value = (-1 if result_sign == '1' else 1) * mant_val * (2 ** result_exp_val)
    
    return {'sign': result_sign, 'mantissa': mant_sum[:mantissa_bits], 'exponent': result_exp, 'value': result_value}


def float_add_variant1(num1: int, num2: int, code: int, 
                       mantissa_bits: int = 8, exponent_bits: int = 4,
                       verbose: bool = True) -> dict:
    """
    Сложение чисел с плавающей точкой - ВАРИАНТ 1.
    Р1=0,100 (4) и Р2=0,101 (5), числа 10 и 23.
    """
    mant_v1_1 = '10100000'  # 0.625
    mant_v1_2 = '10111000'  # 0.71875
    exp_4 = '0100'
    exp_5 = '0101'
    
    sign1 = '1' if num1 < 0 else '0'
    sign2 = '1' if num2 < 0 else '0'
    
    if verbose:
        print(f"\nВАРИАНТ 1: Порядки как целые числа")
        print(f"  Число 1: знак={sign1}, мантисса={mant_v1_1}, порядок={exp_4} → 10")
        print(f"  Число 2: знак={sign2}, мантисса={mant_v1_2}, порядок={exp_5} → 23")
    
    return float_add(mant_v1_1, exp_4, sign1, mant_v1_2, exp_5, sign2,
                     code, mantissa_bits, exponent_bits, verbose)


def _to_exp(value: int, code: int, bits: int) -> str:
    if code == 1:
        return to_direct(value, bits)
    elif code == 2:
        return to_inverse(value, bits)
    elif code == 3:
        return to_twos(value, bits)
    return bin(value)[2:].zfill(bits)


def _from_exp(bits_str: str, code: int) -> int:
    if code == 1:
        return from_direct(bits_str)
    elif code == 2:
        return from_inverse(bits_str)
    elif code == 3:
        return from_twos(bits_str)
    return int(bits_str, 2)
