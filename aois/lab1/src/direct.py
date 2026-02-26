"""
Прямой код (Direct Code)
Формат: старший бит - знак (0=+, 1=-), остальные биты - модуль числа
Диапазон для 8 бит: -127 ... +127
"""

from .base import (
    add_binary_strings, subtract_binary_strings, compare_binary,
    multiply_magnitudes, divide_magnitudes
)


def to_direct(value: int, bits: int = 8) -> str:
    """Преобразование десятичного числа в прямой код"""
    if value == 0:
        return '0' * bits
    
    max_val = (1 << (bits - 1)) - 1
    if value < -max_val or value > max_val:
        raise ValueError(f"Число {value} вне диапазона прямого кода: [{-max_val}, {max_val}]")
    
    sign = 0 if value >= 0 else 1
    magnitude_bin = bin(abs(value))[2:].zfill(bits - 1)
    return str(sign) + magnitude_bin


def from_direct(bits_str: str) -> int:
    """Преобразование из прямого кода в десятичное число"""
    if not bits_str:
        return 0
    
    sign = bits_str[0]
    magnitude = bits_str[1:]
    value = int(magnitude, 2) if magnitude else 0
    return -value if sign == '1' else value


def add_direct(val1: str, val2: str) -> str:
    """Сложение двух чисел в прямом коде"""
    sign1, sign2 = val1[0], val2[0]
    mag1, mag2 = val1[1:], val2[1:]
    
    if sign1 == sign2:
        mag_result, _ = add_binary_strings(mag1, mag2)
        if len(mag_result) > len(mag1):
            mag_result = mag_result[-len(mag1):]
        return sign1 + mag_result
    else:
        cmp = compare_binary(mag1, mag2)
        if cmp >= 0:
            mag_result = subtract_binary_strings(mag1, mag2)
            return sign1 + mag_result.zfill(len(mag1))
        else:
            mag_result = subtract_binary_strings(mag2, mag1)
            return sign2 + mag_result.zfill(len(mag1))


def multiply_direct(val1: str, val2: str, bits: int = 16) -> str:
    """Умножение двух чисел в прямом коде"""
    result_sign = '1' if val1[0] != val2[0] else '0'
    mag_result = multiply_magnitudes(val1[1:], val2[1:])
    
    if len(mag_result) > bits - 1:
        mag_result = mag_result[-(bits - 1):]
    return result_sign + mag_result.zfill(bits - 1)


def divide_direct(val1: str, val2: str, bits: int = 16, precision: int = 5) -> str:
    """
    Деление двух чисел в прямом коде.
    Возвращает строку с десятичным представлением результата (дробное, меньшее/большее).
    """
    mag1, mag2 = val1[1:], val2[1:]
    float_result = divide_magnitudes(mag1, mag2, precision)
    # Определяем знак результата
    if val1[0] != val2[0]:
        # Отрицательный результат
        return f"-{float_result}"
    return float_result
