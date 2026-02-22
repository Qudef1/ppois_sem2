def to_unsigned(value, bits):
    """Обрезка числа до заданной разрядности (беззнаковое)"""
    return value & ((1 << bits) - 1)


def from_unsigned(value, bits):
    """Преобразование беззнакового числа в знаковое (для ДК)"""
    if value & (1 << (bits - 1)):  # Если установлен знаковый бит
        return value - (1 << bits)
    return value

def dec_to_direct(num, bits=8):
    """
    Перевод десятичного числа в прямой код.
    
    Формат: [знак][модуль]
            0/1  |n-1 бит|
    
    Примеры (8 бит):
        +10 → 00001010
        -10 → 10001010
        +0  → 00000000
        -0  → 10000000
    """
    if num >= 0:
        # Положительное: 0 + модуль
        return format(num, f'0{bits}b')
    else:
        # Отрицательное: 1 + модуль
        return '1' + format(abs(num), f'0{bits-1}b')

def direct_to_dec(code):
    bits = len(code)
    sign_bit = code[0]
    magnitude = int(code[1:],2)
    if magnitude == 0:
        return 0
    return -magnitude if sign_bit == '1' else magnitude

def dec_to_inverse(num,bits=8):
    if num>=0:
        return format(num,f'0{bits}b')
    else: 
        positive = format(abs(num),f'0{bits}b')
        inverted = ''.join('1'if b=='0' else '0' for b in positive)
        return inverted

def inverse_to_dec(code):
    bits = len(code)
    
    # Проверка на ноль
    if code == '0' * bits:
        return 0, 'положительный'
    if code == '1' * bits:
        return 0, 'отрицательный'
    
    # Обычное число
    if code[0] == '0':
        # Положительное
        return int(code, 2)
    else:
        # Отрицательное: инвертируем и берём отрицание
        inverted = ''.join('1' if b == '0' else '0' for b in code)
        return -int(inverted, 2)

def dec_to_additional(num,bits=8):
    if num>=0:
        if num > (1 << (bits - 1)) - 1:
            raise OverflowError(f"Число {num} выходит за пределы диапазона +0..+{(1 << (bits-1)) - 1} для {bits} бит")
        return format(num, f'0{bits}b')
    else:
        if num < -(1 << (bits - 1)):
            raise OverflowError(f"Число {num} выходит за пределы диапазона -{1 << (bits-1)}..-1 для {bits} бит")
        value = (1 << bits) + num  # 2^bits + num (num отрицательное)
        return format(value, f'0{bits}b')

def additional_to_dec(code):
    bits = len(code)
    value = int(code, 2)
    
    if code[0] == '1':  # Отрицательное число
        return value - (1 << bits) + 1
    else:  # Положительное число
        return value

# --- сложение
def bin_add_unsigned(a: str, b: str) -> tuple[str, int]:
    """
    Сложение двух беззнаковых двоичных чисел одинаковой длины.
    
    Возвращает: (результат, перенос_из_старшего_разряда)
    """
    if len(a) != len(b):
        raise ValueError("Операнды должны иметь одинаковую длину")
    
    bits = len(a)
    a_val = int(a, 2)
    b_val = int(b, 2)
    total = a_val + b_val
    
    carry = (total >> bits) & 1
    result = total & ((1 << bits) - 1)
    
    return format(result, f'0{bits}b'), carry


def bin_minus_unsigned(a: str, b: str) -> tuple[str, int]:
    """
    Вычитание двух беззнаковых двоичных чисел: a - b (a >= b).
    
    Возвращает: (результат, заём_из_старшего_разряда)
    Если a < b, возвращает отрицательный результат в ДК.
    """
    if len(a) != len(b):
        raise ValueError("Операнды должны иметь одинаковую длину")
    
    bits = len(a)
    a_val = int(a, 2)
    b_val = int(b, 2)
    
    # Вычитание как сложение с дополнением
    # a - b = a + (2^bits - b) = a + дополнение_до_2^bits(b)
    diff = a_val - b_val
    
    # Заём = 1 если результат отрицательный
    borrow = 1 if diff < 0 else 0
    
    # Обрезка до разрядности (представление в ДК для отрицательных)
    result = diff & ((1 << bits) - 1)
    
    return format(result, f'0{bits}b'), borrow


def add_direct(a: str, b: str) -> str:
    """
    Сложение в прямом коде.
    
    Алгоритм:
    1. Извлечь знаки и модули
    2. Если знаки одинаковые → сложить модули, присвоить общий знак
    3. Если знаки разные → вычесть меньший модуль из большего,
       присвоить знак числа с большим модулем
    4. Если модули равны → результат = +0
    
    Возвращает: результат в прямом коде
    """
    if len(a) != len(b):
        raise ValueError("Операнды должны иметь одинаковую длину")
    
    bits = len(a)
    sign_a, mag_a = a[0], a[1:]
    sign_b, mag_b = b[0], b[1:]
    
    mag_a_val = int(mag_a, 2)
    mag_b_val = int(mag_b, 2)
    
    # Случай 1: одинаковые знаки
    if sign_a == sign_b:
        # Сложить модули
        mag_sum, carry = bin_add_unsigned(mag_a, mag_b)
        
        # Проверка переполнения модуля (модуль должен быть < 2^(bits-1))
        if carry or int(mag_sum, 2) >= (1 << (bits - 1)):
            raise OverflowError(f"Переполнение в прямом коде: {mag_a_val} + {mag_b_val} не помещается в {bits-1} бит")
        
        return sign_a + mag_sum
    
    # Случай 2: разные знаки
    else:
        # Определить, какой модуль больше
        if mag_a_val > mag_b_val:
            # |a| > |b| → результат имеет знак a
            mag_diff, _ = bin_minus_unsigned(mag_a, mag_b)
            return sign_a + mag_diff
        
        elif mag_b_val > mag_a_val:
            # |b| > |a| → результат имеет знак b
            mag_diff, _ = bin_minus_unsigned(mag_b, mag_a)
            return sign_b + mag_diff
        
        else:  # Модули равны → результат = +0
            return '0' + '0' * (bits - 1)

def add_inverse_codes(a_code: str, b_code: str) -> dict:
    """
    Универсальное сложение в обратном коде с циклическим переносом.
    
    Алгоритм:
    1. Сложить как беззнаковые числа
    2. Если есть перенос из знакового разряда → добавить его к результату (циклический перенос)
    3. После коррекции может получиться -0 (111...111) → опционально нормализовать в +0
    
    Возвращает словарь с полной информацией.
    """
    if len(a_code) != len(b_code):
        raise ValueError("Операнды должны иметь одинаковую разрядность")
    
    bits = len(a_code)
    a_val = int(a_code, 2)
    b_val = int(b_code, 2)
    
    # Шаг 1: базовое сложение
    total = a_val + b_val
    carry_out = (total >> bits) & 1  # Перенос из знакового разряда
    raw_result = total & ((1 << bits) - 1)  # Обрезка до разрядности
    
    # Шаг 2: циклический перенос (только если был перенос)
    if carry_out:
        corrected = raw_result + 1
        second_carry = (corrected >> bits) & 1
        final_result = corrected & ((1 << bits) - 1)
        
        # Редкий случай: второй перенос (требует ещё одной коррекции)
        if second_carry:
            final_result = (final_result + 1) & ((1 << bits) - 1)
            correction_steps = 2
        else:
            correction_steps = 1
    else:
        final_result = raw_result
        correction_steps = 0
    
    # Шаг 3: нормализация -0 в +0 (по соглашению)
    zero_type = None
    if final_result == (1 << bits) - 1:  # 111...111 = -0 в ОК
        zero_type = 'отрицательный'
        # Опционально нормализуем в +0:
        # final_result = 0
        # zero_type = 'нормализован в положительный'
    
    return {
        'код': 'обратный',
        'операнды': (a_code, b_code),
        'промежуточный_результат': format(raw_result, f'0{bits}b'),
        'перенос_из_знакового': carry_out,
        'шагов_коррекции': correction_steps,
        'результат': format(final_result, f'0{bits}b'),
        'тип_нуля': zero_type,
        'статус': 'успех'
    }


def add_additional_codes(a_code: str, b_code: str) -> dict:
    """
    Универсальное сложение в дополнительном коде.
    
    Алгоритм:
    1. Сложить как беззнаковые числа
    2. Игнорировать перенос из знакового разряда (автоматическая обрезка)
    3. Проверить переполнение: знаки операндов одинаковы, а знак результата другой
    
    Возвращает словарь с полной информацией.
    """
    if len(a_code) != len(b_code):
        raise ValueError("Операнды должны иметь одинаковую разрядность")
    
    bits = len(a_code)
    a_val = int(a_code, 2)
    b_val = int(b_code, 2)
    
    # Шаг 1: сложение
    total = a_val + b_val
    result_val = total & ((1 << bits) - 1)  # Автоматическая обрезка переноса
    
    # Шаг 2: проверка переполнения
    # Переполнение = (знаки операндов равны) И (знак результата ≠ знак операндов)
    sign_a = (a_val >> (bits - 1)) & 1
    sign_b = (b_val >> (bits - 1)) & 1
    sign_result = (result_val >> (bits - 1)) & 1
    
    overflow = (sign_a == sign_b) and (sign_a != sign_result)
    
    # Диагностика переполнения
    if overflow:
        overflow_info = {
            'было': True,
            'пояснение': f"Знаки операндов одинаковы ({'+' if sign_a == 0 else '-'}), "
                        f"но знак результата другой ({'+' if sign_result == 0 else '-'})"
        }
    else:
        overflow_info = {'было': False, 'пояснение': 'нет'}
    
    return {
        'код': 'дополнительный',
        'операнды': (a_code, b_code),
        'результат': format(result_val, f'0{bits}b'),
        'переполнение': overflow_info,
        'статус': 'ПЕРЕПОЛНЕНИЕ' if overflow else 'успех'
    }


if __name__=="__main__":
    print(dec_to_direct(-10,8))
    print(direct_to_dec(add_direct(dec_to_direct(-13,8),dec_to_direct(5,8))))

    print()

    print(dec_to_inverse(-10))
    print(inverse_to_dec(dec_to_inverse(-10)))

    print()

    print(dec_to_additional(-10))
    print(additional_to_dec(dec_to_inverse(-20)))

