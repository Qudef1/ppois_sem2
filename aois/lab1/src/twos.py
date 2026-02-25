"""
Дополнительный код (Two's Complement)
Формат: для положительных = прямой код, для отрицательных = обратный код + 1
Диапазон для 8 бит: -128 ... +127
"""

from .base import (
    add_binary_strings, invert_bits, add_one, get_magnitude,
    multiply_magnitudes, divide_magnitudes
)


def to_twos(value: int, bits: int = 8) -> str:
    """Преобразование десятичного числа в дополнительный код"""
    max_val = (1 << (bits - 1)) - 1
    min_val = -(1 << (bits - 1))
    
    if value < min_val or value > max_val:
        raise ValueError(f"Число {value} вне диапазона дополнительного кода: [{min_val}, {max_val}]")
    
    if value == min_val:
        return '1' + '0' * (bits - 1)
    
    if value >= 0:
        magnitude_bin = bin(value)[2:].zfill(bits - 1)
        return '0' + magnitude_bin
    else:
        magnitude_bin = bin(abs(value))[2:].zfill(bits - 1)
        inverted = invert_bits(magnitude_bin)
        result, _ = add_one(inverted)
        return '1' + result


def from_twos(bits_str: str) -> int:
    """Преобразование из дополнительного кода в десятичное число"""
    if not bits_str:
        return 0
    
    sign = bits_str[0]
    magnitude = bits_str[1:]
    
    if sign == '0':
        return int(magnitude, 2) if magnitude else 0
    else:
        inverted = invert_bits(magnitude)
        result, _ = add_one(inverted)
        return -(int(result, 2) if result else 0)


def add_twos(val1: str, val2: str) -> str:
    """Сложение двух чисел в дополнительном коде (перенос отбрасывается)"""
    result, _ = add_binary_strings(val1, val2)
    return result


def multiply_twos(val1: str, val2: str, bits: int = 16) -> str:
    """Умножение двух чисел в дополнительном коде"""
    result_sign = '1' if val1[0] != val2[0] else '0'
    mag1 = get_magnitude(val1, 3)
    mag2 = get_magnitude(val2, 3)
    mag_result = multiply_magnitudes(mag1, mag2)
    
    if len(mag_result) > bits - 1:
        mag_result = mag_result[-(bits - 1):]
    mag_result = mag_result.zfill(bits - 1)
    
    if result_sign == '0':
        return '0' + mag_result
    else:
        inverted = invert_bits(mag_result)
        result, _ = add_one(inverted)
        return '1' + result


def divide_twos(val1: str, val2: str, bits: int = 16) -> str:
    """Деление двух чисел в дополнительном коде"""
    mag1 = get_magnitude(val1, 3)
    mag2 = get_magnitude(val2, 3)
    
    if mag2 == '0' * len(mag2):
        raise ValueError("Деление на ноль!")
    
    mag_result = divide_magnitudes(mag1, mag2)
    result_sign = '0' if mag_result == '0' or mag_result == '0' * len(mag_result) else ('1' if val1[0] != val2[0] else '0')
    
    if len(mag_result) > bits - 1:
        mag_result = mag_result[-(bits - 1):]
    mag_result = mag_result.zfill(bits - 1)
    
    if result_sign == '0':
        return '0' + mag_result
    else:
        inverted = invert_bits(mag_result)
        result, _ = add_one(inverted)
        return '1' + result
