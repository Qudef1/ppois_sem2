"""
Модуль для работы с двоичными кодировками
"""

from .base import (
    add_binary_strings, subtract_binary_strings, compare_binary,
    add_one, invert_bits, get_magnitude, multiply_magnitudes, divide_magnitudes
)
from .direct import to_direct, from_direct, add_direct, multiply_direct, divide_direct
from .inverse import to_inverse, from_inverse, add_inverse, multiply_inverse, divide_inverse
from .twos import to_twos, from_twos, add_twos, multiply_twos, divide_twos
from .float_arith import float_add, float_add_variant1

__all__ = [
    # Базовые операции
    'add_binary_strings', 'subtract_binary_strings', 'compare_binary',
    'add_one', 'invert_bits', 'get_magnitude', 'multiply_magnitudes', 'divide_magnitudes',
    # Прямой код
    'to_direct', 'from_direct', 'add_direct', 'multiply_direct', 'divide_direct',
    # Обратный код
    'to_inverse', 'from_inverse', 'add_inverse', 'multiply_inverse', 'divide_inverse',
    # Дополнительный код
    'to_twos', 'from_twos', 'add_twos', 'multiply_twos', 'divide_twos',
    # Плавающая точка
    'float_add', 'float_add_variant1',
]
