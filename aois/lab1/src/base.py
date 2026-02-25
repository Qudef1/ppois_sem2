"""
Базовые операции для работы с двоичными числами
Общие вспомогательные функции для всех кодировок
"""


def add_binary_strings(a: str, b: str) -> tuple:
    """Сложение двух двоичных строк, возвращает (сумма, перенос)"""
    max_len = max(len(a), len(b))
    a = a.zfill(max_len)
    b = b.zfill(max_len)
    result = ''
    carry = 0
    for i in range(max_len - 1, -1, -1):
        bit_a = 1 if a[i] == '1' else 0
        bit_b = 1 if b[i] == '1' else 0
        sum_bit = bit_a ^ bit_b ^ carry
        carry = (bit_a & bit_b) | (carry & (bit_a ^ bit_b))
        result = ('1' if sum_bit else '0') + result
    return (result, carry)


def subtract_binary_strings(a: str, b: str) -> str:
    """Вычитание двоичных строк (a - b), предполагается a >= b"""
    result = ''
    borrow = 0
    for i in range(len(a) - 1, -1, -1):
        bit_a = (1 if a[i] == '1' else 0) - borrow
        bit_b = 1 if b[i] == '1' else 0
        if bit_a < bit_b:
            bit_a += 2
            borrow = 1
        else:
            borrow = 0
        result = ('1' if (bit_a - bit_b) else '0') + result
    return result.lstrip('0') or '0'


def compare_binary(a: str, b: str) -> int:
    """Сравнение двоичных строк: 1 если a > b, -1 если a < b, 0 если равны"""
    a = a.zfill(max(len(a), len(b)))
    b = b.zfill(max(len(a), len(b)))
    if a > b:
        return 1
    elif a < b:
        return -1
    return 0


def add_one(bits: str) -> tuple:
    """Прибавление 1 к двоичному числу, возвращает (результат, перенос)"""
    result = ''
    carry = 1
    for i in range(len(bits) - 1, -1, -1):
        bit = 1 if bits[i] == '1' else 0
        sum_bit = bit ^ carry
        carry = bit & carry
        result = ('1' if sum_bit else '0') + result
    return (result, carry)


def invert_bits(bits: str) -> str:
    """Инверсия битов"""
    return ''.join('1' if bit == '0' else '0' for bit in bits)


def get_magnitude(bits: str, code: int) -> str:
    """
    Извлечение модуля из кодировки.
    code: 1=прямой, 2=обратный, 3=дополнительный
    """
    sign = bits[0]
    mag = bits[1:]
    
    if sign == '0':
        return mag.lstrip('0') or '0'
    
    if code == 1:  # Прямой
        return mag.lstrip('0') or '0'
    elif code == 2:  # Обратный
        return invert_bits(mag).lstrip('0') or '0'
    elif code == 3:  # Дополнительный
        inverted = invert_bits(mag)
        result, _ = add_one(inverted)
        return result.lstrip('0') or '0'
    return mag


def multiply_magnitudes(mag1: str, mag2: str) -> str:
    """Умножение двух модулей"""
    result = '0'
    for i, bit in enumerate(reversed(mag2)):
        if bit == '1':
            shifted = mag1 + '0' * i
            sum_result, carry = add_binary_strings(result.zfill(len(shifted)), shifted)
            result = ('1' + sum_result) if carry else sum_result
    return result.lstrip('0') or '0'


def divide_magnitudes(dividend: str, divisor: str) -> str:
    """Деление модулей. Возвращает частное."""
    dividend = dividend.lstrip('0') or '0'
    divisor = divisor.lstrip('0') or '0'
    
    if divisor == '0':
        raise ValueError("Деление на ноль!")
    if dividend == '0':
        return '0'
    if compare_binary(dividend, divisor) < 0:
        return '0'
    
    quotient = '0'
    remainder = '0'
    
    for bit in dividend:
        remainder = (remainder + bit).lstrip('0') or '0'
        quotient = quotient + '0'
        if compare_binary(remainder, divisor) >= 0:
            remainder = subtract_binary_strings(remainder, divisor)
            quotient = quotient[:-1] + '1'
    
    return quotient.lstrip('0') or '0'
