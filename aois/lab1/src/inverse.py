"""
Обратный код (Inverse Code / Ones' Complement)
Формат: для положительных = прямой код, для отрицательных = инверсия всех битов модуля
Диапазон для 8 бит: -127 ... +127 (существование -0 и +0)
"""

from .base import (
    add_binary_strings, compare_binary, invert_bits, add_one,
    get_magnitude, multiply_magnitudes, divide_magnitudes
)


def to_inverse(value: int, bits: int = 8) -> str:
    """Преобразование десятичного числа в обратный код"""
    if value == 0:
        return '0' * bits
    
    max_val = (1 << (bits - 1)) - 1
    if value < -max_val or value > max_val:
        raise ValueError(f"Число {value} вне диапазона обратного кода: [{-max_val}, {max_val}]")
    
    if value >= 0:
        magnitude_bin = bin(value)[2:].zfill(bits - 1)
        return '0' + magnitude_bin
    else:
        magnitude_bin = bin(abs(value))[2:].zfill(bits - 1)
        return '1' + invert_bits(magnitude_bin)


def from_inverse(bits_str: str) -> int:
    """Преобразование из обратного кода в десятичное число"""
    if not bits_str:
        return 0
    
    sign = bits_str[0]
    magnitude = bits_str[1:]
    
    if sign == '0':
        return int(magnitude, 2) if magnitude else 0
    else:
        inverted = invert_bits(magnitude)
        return -(int(inverted, 2) if inverted else 0)


def add_inverse(val1: str, val2: str) -> str:
    """Сложение двух чисел в обратном коде с циклическим переносом"""
    bits = len(val1)
    result, carry = add_binary_strings(val1, val2)
    
    if carry:
        result, _ = add_one(result)
    return result


def multiply_inverse(val1: str, val2: str, bits: int = 16) -> str:
    """Умножение двух чисел в обратном коде"""
    result_sign = '1' if val1[0] != val2[0] else '0'
    mag1 = get_magnitude(val1, 2)
    mag2 = get_magnitude(val2, 2)
    mag_result = multiply_magnitudes(mag1, mag2)
    
    if len(mag_result) > bits - 1:
        mag_result = mag_result[-(bits - 1):]
    mag_result = mag_result.zfill(bits - 1)
    
    if result_sign == '0':
        return '0' + mag_result
    else:
        return '1' + invert_bits(mag_result)


def divide_inverse(val1: str, val2: str, bits: int = 16, precision: int = 5) -> str:
    """
    Деление двух чисел в обратном коде.
    Возвращает строку с десятичным представлением результата (дробное, меньшее/большее).
    """
    mag1 = get_magnitude(val1, 2)
    mag2 = get_magnitude(val2, 2)

    if mag2 == '0' * len(mag2):
        raise ValueError("Деление на ноль!")

    float_result = divide_magnitudes(mag1, mag2, precision)
    # Определяем знак результата
    if val1[0] != val2[0]:
        return f"-{float_result}"
    return float_result
