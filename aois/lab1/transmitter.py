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
        return value - (1 << bits)
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


# ============================================================
# ПУНКТ 1: Сложение/вычитание в прямом, обратном, дополнительном кодах
# ============================================================

def inverse_to_dec(code):
    bits = len(code)

    # Проверка на ноль
    if code == '0' * bits:
        return 0
    if code == '1' * bits:
        return 0  # -0 = 0

    # Обычное число
    if code[0] == '0':
        # Положительное
        return int(code, 2)
    else:
        # Отрицательное: инвертируем и берём отрицание
        inverted = ''.join('1' if b == '0' else '0' for b in code)
        return -int(inverted, 2)


def add_inverse(a: str, b: str) -> tuple[str, int]:
    """
    Сложение в обратном коде с циклическим переносом.
    Возвращает (результат, перенос)
    """
    if len(a) != len(b):
        raise ValueError("Операнды должны иметь одинаковую длину")

    bits = len(a)
    a_val = int(a, 2)
    b_val = int(b, 2)
    total = a_val + b_val

    # Перенос из знакового разряда
    carry = (total >> bits) & 1
    result = total & ((1 << bits) - 1)

    # Циклический перенос: добавить единицу к результату
    if carry:
        result = (result + 1) & ((1 << bits) - 1)

    return format(result, f'0{bits}b'), carry


def subtract_inverse(a: str, b: str) -> str:
    """
    Вычитание в обратном коде: a - b = a + (-b)
    """
    if len(a) != len(b):
        raise ValueError("Операнды должны иметь одинаковую длину")

    bits = len(a)
    # Инвертируем знак второго операнда (получаем -b в обратном коде)
    if b[0] == '0':
        # b положительное, делаем отрицательным
        mag = b[1:]
        neg_b = '1' + ''.join('1' if bit == '0' else '0' for bit in mag)
    else:
        # b отрицательное, делаем положительным
        mag = b[1:]
        neg_b = '0' + ''.join('1' if bit == '0' else '0' for bit in mag)

    result, _ = add_inverse(a, neg_b)
    return result


def add_additional(a: str, b: str) -> str:
    """
    Сложение в дополнительном коде.
    """
    if len(a) != len(b):
        raise ValueError("Операнды должны иметь одинаковую длину")

    bits = len(a)
    a_val = int(a, 2)
    b_val = int(b, 2)
    total = a_val + b_val

    # Обрезка до разрядности (перенос игнорируется)
    result = total & ((1 << bits) - 1)
    return format(result, f'0{bits}b')


def subtract_additional(a: str, b: str) -> str:
    """
    Вычитание в дополнительном коде: a - b = a + (~b + 1)
    """
    if len(a) != len(b):
        raise ValueError("Операнды должны иметь одинаковую длину")

    bits = len(a)
    # Получаем дополнительный код для -b (инверсия + 1)
    b_inverted = ''.join('1' if bit == '0' else '0' for bit in b)
    neg_b = (int(b_inverted, 2) + 1) & ((1 << bits) - 1)

    result = add_additional(a, format(neg_b, f'0{bits}b'))
    return result


def run_arithmetic_demo(x1=10, x2=23, bits=8):
    """
    Демонстрация сложения/вычитания для всех вариантов знаков.
    """
    print("=" * 70)
    print("ПУНКТ 1: Арифметические операции в прямом, обратном, дополнительном кодах")
    print(f"X1 = {x1}, X2 = {x2}, разрядность = {bits} бит")
    print("=" * 70)

    variants = [
        (x1, x2, "+/+",),
        (x1, -x2, "+/-"),
        (-x1, x2, "-/+"),
        (-x1, -x2, "-/-"),
    ]

    for a, b, sign_variant in variants:
        print(f"\n--- Вариант {sign_variant}: ({a}) + ({b}) и ({a}) - ({b}) ---")

        # Прямой код
        a_direct = dec_to_direct(a, bits)
        b_direct = dec_to_direct(b, bits)
        print(f"  Прямой код: A={a_direct}, B={b_direct}")

        # Сложение в прямом коде
        try:
            sum_direct = add_direct(a_direct, b_direct)
            print(f"    Сложение: {sum_direct} = {direct_to_dec(sum_direct)}")
        except OverflowError as e:
            print(f"    Сложение: ПЕРЕПОЛНЕНИЕ ({e})")

        # Вычитание в прямом коде (A - B = A + (-B))
        neg_b_direct = dec_to_direct(-b, bits)
        try:
            diff_direct = add_direct(a_direct, neg_b_direct)
            print(f"    Вычитание: {diff_direct} = {direct_to_dec(diff_direct)}")
        except OverflowError as e:
            print(f"    Вычитание: ПЕРЕПОЛНЕНИЕ ({e})")

        # Обратный код
        a_inverse = dec_to_inverse(a, bits)
        b_inverse = dec_to_inverse(b, bits)
        print(f"  Обратный код: A={a_inverse}, B={b_inverse}")

        sum_inverse, carry = add_inverse(a_inverse, b_inverse)
        print(f"    Сложение: {sum_inverse} = {inverse_to_dec(sum_inverse)} (перенос={carry})")

        diff_inverse = subtract_inverse(a_inverse, b_inverse)
        print(f"    Вычитание: {diff_inverse} = {inverse_to_dec(diff_inverse)}")

        # Дополнительный код
        a_additional = dec_to_additional(a, bits)
        b_additional = dec_to_additional(b, bits)
        print(f"  Дополнительный код: A={a_additional}, B={b_additional}")

        sum_additional = add_additional(a_additional, b_additional)
        print(f"    Сложение: {sum_additional} = {additional_to_dec(sum_additional)}")

        diff_additional = subtract_additional(a_additional, b_additional)
        print(f"    Вычитание: {diff_additional} = {additional_to_dec(diff_additional)}")


# ============================================================
# ПУНКТ 2: Умножение модулей чисел
# ============================================================

def multiply_unsigned(a: str, b: str) -> str:
    """
    Умножение двух беззнаковых двоичных чисел.
    Возвращает результат удвоенной разрядности.
    """
    a_val = int(a, 2)
    b_val = int(b, 2)
    product = a_val * b_val
    # Результат может занимать до 2*bits
    return format(product, 'b')


def multiply_with_sign(x1: int, x2: int, bits=8):
    """
    Умножение с определением знака произведения.
    """
    print("\n" + "=" * 70)
    print("ПУНКТ 2: Умножение модулей чисел")
    print(f"X1 = {x1}, X2 = {x2}")
    print("=" * 70)

    # Модули
    mod_x1 = abs(x1)
    mod_x2 = abs(x2)

    print(f"\nМодули: |X1| = {mod_x1}, |X2| = {mod_x2}")
    print(f"|X1| в двоичной: {format(mod_x1, f'0{bits}b')}")
    print(f"|X2| в двоичной: {format(mod_x2, f'0{bits}b')}")

    # Умножение модулей
    product_binary = multiply_unsigned(format(mod_x1, f'0{bits}b'), format(mod_x2, f'0{bits}b'))
    product_decimal = mod_x1 * mod_x2

    print(f"\nПроизведение модулей: {product_binary}_2 = {product_decimal}_10")

    # Знаки произведения для всех вариантов
    print("\nЗнаки произведения для всех вариантов:")
    variants = [
        (x1, x2, "+/+"),
        (x1, -x2, "+/-"),
        (-x1, x2, "-/+"),
        (-x1, -x2, "-/-"),
    ]

    for a, b, sign_variant in variants:
        sign_result = '+' if (a >= 0) == (b >= 0) else '-'
        print(f"  {sign_variant}: ({a}) × ({b}) = {sign_result}{product_decimal}")


# ============================================================
# ПУНКТ 3: Деление модулей чисел
# ============================================================

def divide_unsigned_with_precision(dividend: int, divisor: int, precision=5):
    """
    Деление двух чисел с заданной точностью (до precision разрядов после запятой).
    Возвращает (целая_часть, дробная_часть_строка).
    """
    if divisor == 0:
        raise ZeroDivisionError("Деление на ноль")

    # Целая часть
    integer_part = dividend // divisor
    remainder = dividend % divisor

    # Дробная часть
    fractional_bits = []
    for _ in range(precision):
        remainder *= 2
        bit = remainder // divisor
        fractional_bits.append(str(bit))
        remainder %= divisor

    return integer_part, ''.join(fractional_bits), remainder


def divide_with_sign(x1: int, x2: int, precision=5, bits=8):
    """
    Деление с определением знака частного.
    """
    print("\n" + "=" * 70)
    print("ПУНКТ 3: Деление модулей чисел")
    print(f"X1 = {x1}, X2 = {x2}, точность = {precision} разрядов")
    print("=" * 70)

    # Модули
    mod_x1 = abs(x1)
    mod_x2 = abs(x2)

    print(f"\nМодули: |X1| = {mod_x1}, |X2| = {mod_x2}")
    print(f"|X1| в двоичной: {format(mod_x1, f'0{bits}b')}")
    print(f"|X2| в двоичной: {format(mod_x2, f'0{bits}b')}")

    # Деление модулей
    integer_part, fractional_part, remainder = divide_unsigned_with_precision(mod_x1, mod_x2, precision)

    print(f"\nЧастное модулей: {integer_part}.{fractional_part}_2")

    # Перевод дробной части в десятичную для проверки
    fractional_decimal = sum(int(b) * 2**(-(i+1)) for i, b in enumerate(fractional_part))
    result_decimal = integer_part + fractional_decimal
    print(f"Частное модулей (десятичное): {result_decimal:.5f}")
    print(f"Остаток после {precision} разрядов: {remainder}")

    # Знаки частного для всех вариантов
    print("\nЗнаки частного для всех вариантов:")
    variants = [
        (x1, x2, "+/+"),
        (x1, -x2, "+/-"),
        (-x1, x2, "-/+"),
        (-x1, -x2, "-/-"),
    ]

    for a, b, sign_variant in variants:
        sign_result = '+' if (a >= 0) == (b >= 0) else '-'
        print(f"  {sign_variant}: ({a}) / ({b}) = {sign_result}{result_decimal:.5f}")


# ============================================================
# ПУНКТ 4: Сложение чисел с плавающей точкой
# ============================================================

def float_add(m1: int, m2: int, p1_bin: str, p2_bin: str, bits=8):
    """
    Сложение чисел с плавающей точкой.
    M1, M2 - мантиссы (десятичные)
    P1_bin, P2_bin - порядки в двоичной форме (например, "0.100")
    """
    print("\n" + "=" * 70)
    print("ПУНКТ 4: Сложение чисел с плавающей точкой")
    print(f"M1 = {m1}, M2 = {m2}")
    print(f"P1 = {p1_bin}, P2 = {p2_bin}")
    print("=" * 70)

    # Извлечение порядков (дробная часть после запятой)
    p1_frac = p1_bin.split('.')[1] if '.' in p1_bin else p1_bin
    p2_frac = p2_bin.split('.')[1] if '.' in p2_bin else p2_bin

    # Преобразование порядков в десятичные (как дробные двоичные числа)
    p1_val = sum(int(b) * 2**(-(i+1)) for i, b in enumerate(p1_frac))
    p2_val = sum(int(b) * 2**(-(i+1)) for i, b in enumerate(p2_frac))

    print(f"\nПорядки в десятичной форме: P1 = {p1_val}, P2 = {p2_val}")

    # Выравнивание порядков (сдвигаем меньшую мантиссу)
    if p1_val > p2_val:
        larger_p, smaller_p = p1_val, p2_val
        larger_m, smaller_m = m1, m2
        larger_name, smaller_name = "M1", "M2"
    else:
        larger_p, smaller_p = p2_val, p1_val
        larger_m, smaller_m = m2, m1
        larger_name, smaller_name = "M2", "M1"

    # Разница порядков
    p_diff = larger_p - smaller_p
    print(f"\nРазница порядков: {p_diff}")

    # Выравнивание: сдвиг меньшей мантиссы вправо на разницу порядков
    # Для простоты: сдвиг в двоичной форме
    shift_bits = int(p_diff * (2 ** len(p1_frac)))  # Приблизительное количество бит для сдвига

    # Более точный способ: представить мантиссы как дроби
    # M1 × 2^P1 + M2 × 2^P2
    # Выравниваем к большему порядку

    # Представим мантиссы в нормализованной форме (как дробь)
    m1_bits = format(abs(m1), f'0{bits}b')
    m2_bits = format(abs(m2), f'0{bits}b')

    print(f"\nМантиссы в двоичной форме: M1 = {m1_bits}, M2 = {m2_bits}")

    # Для сложения с плавающей точкой:
    # 1. Выровнять порядки (сдвиг мантиссы меньшего числа)
    # 2. Сложить мантиссы
    # 3. Нормализовать результат

    # Упрощённый расчёт:
    # Число1 = M1 × 2^P1, Число2 = M2 × 2^P2
    # Сумма = M1 × 2^P1 + M2 × 2^P2

    # Для P1 = 0.100 (это 2^0.5 ≈ 1.414) и P2 = 0.101 (это 2^0.625 ≈ 1.545)
    # Но в лабораторных обычно порядок трактуется как степень двойки

    # Интерпретация: порядок записан как двоичная дробь
    # P1 = 0.100_2 = 0.5_10, значит 2^0.5
    # P2 = 0.101_2 = 0.625_10, значит 2^0.625

    # Вычисляем значения
    import math
    value1 = m1 * (2 ** p1_val)
    value2 = m2 * (2 ** p2_val)

    print(f"\nЗначения чисел:")
    print(f"  Число1 = M1 × 2^P1 = {m1} × 2^{p1_val} = {m1} × {2**p1_val:.4f} = {value1:.4f}")
    print(f"  Число2 = M2 × 2^P2 = {m2} × 2^{p2_val} = {m2} × {2**p2_val:.4f} = {value2:.4f}")

    sum_value = value1 + value2
    print(f"\nСумма: {value1:.4f} + {value2:.4f} = {sum_value:.4f}")

    # Представление результата в форме с плавающей точкой
    # Нормализация: найти порядок результата
    if sum_value != 0:
        # Находим порядок результата (логарифм по основанию 2)
        p_result = math.log2(abs(sum_value))
        # Нормализованная мантисса: M_result = sum_value / 2^p_result
        # Но нам нужно представить в той же форме

        # Для упрощения: выразим как M_result × 2^P_result
        # где P_result - ближайший из исходных порядков или их среднее

        print(f"\nРезультат в нормализованной форме:")
        print(f"  Сумма = {sum_value:.4f}")
        print(f"  Порядок результата (log2): {p_result:.4f}")

        # Округлим порядок до представимого в 3 битах после запятой
        p_result_rounded = round(p_result * 8) / 8  # 3 бита = точность до 1/8
        p_result_bits = format(int(p_result_rounded * 8), '03b')
        print(f"  Порядок результата (округлённый): {p_result_rounded} = 0.{p_result_bits}_2")

        m_result = sum_value / (2 ** p_result_rounded)
        print(f"  Мантисса результата: {m_result:.4f}")
        print(f"  Мантисса в двоичной: {format(int(abs(m_result)), f'0{bits}b')}")

    return sum_value


def run_full_demo(x1=10, x2=23):
    """
    Запуск всех пунктов лабораторной работы.
    """
    print("\n" + "#" * 70)
    print(f"ЛАБОРАТОРНАЯ РАБОТА: Арифметические операции с числами X1={x1}, X2={x2}")
    print("#" * 70)

    # Пункт 1
    run_arithmetic_demo(x1, x2, bits=8)

    # Пункт 2
    multiply_with_sign(x1, x2, bits=8)

    # Пункт 3
    divide_with_sign(x1, x2, precision=5, bits=8)

    # Пункт 4
    # P1=0,100 , P2=0,101 (двоичные дроби)
    float_add(x1, x2, "0.100", "0.101", bits=8)

    print("\n" + "#" * 70)
    print("РАБОТА ЗАВЕРШЕНА")
    print("#" * 70)


if __name__ == "__main__":
    # Тесты базовых функций
    print("=== Тесты базовых функций ===")
    print(f"dec_to_direct(-10, 8) = {dec_to_direct(-10, 8)}")
    print(f"direct_to_dec('10001010') = {direct_to_dec('10001010')}")
    print()
    print(f"dec_to_inverse(-10, 8) = {dec_to_inverse(-10, 8)}")
    print(f"inverse_to_dec('11110101') = {inverse_to_dec('11110101')}")
    print()
    print(f"dec_to_additional(-10, 8) = {dec_to_additional(-10, 8)}")
    print(f"additional_to_dec('11110110') = {additional_to_dec('11110110')}")
    print()

    # Запуск полной демонстрации
    run_full_demo(10, 23)

