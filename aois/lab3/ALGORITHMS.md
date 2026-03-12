# Алгоритмы минимизации логических функций

## Обзор

Данный проект реализует **три классических метода минимизации булевых функций**:
1. Расчетный метод (алгебраические преобразования)
2. Метод Квайна-Мак-Класски (расчетно-табличный)
3. Метод Вейча-Карно (табличный)

Все методы работают с **совершенными нормальными формами** (СДНФ и СКНФ) и находят **минимальную дизъюнктивную/конъюнктивную нормальную форму** (МДНФ/МКНФ).

---

## 1. Общие понятия

### 1.1. Представление данных

Все методы используют единое представление термов в виде **списка битов**:
- `0` — переменная входит с инверсией (`~x`)
- `1` — переменная входит без инверсии (`x`)
- `-1` — переменная отсутствует (удалена при склеивании)

**Пример:**
```python
[0, -1, 1]  # соответствует терму ~x1*x3 (x2 удалена)
```

### 1.2. Основные операции

#### Склеивание (Glue/Merge)
```
a·b + a·~b = a
```
Два терма, отличающиеся **ровно в одной позиции**, объединяются с заменой этой позиции на `-1`.

```python
def merge_bits(bits1, bits2):
    """Объединяет два набора битов"""
    result = []
    for b1, b2 in zip(bits1, bits2):
        if b1 != b2:
            result.append(-1)  # переменная удаляется
        else:
            result.append(b1)
    return result
```

#### Поглощение (Absorption)
```
a + a·b = a
```
Если один терм **покрывает** другой (более общий), частный удаляется.

```python
def covers(general, specific):
    """Проверяет, покрывает ли general терм specific"""
    for g, s in zip(general, specific):
        if g != -1 and g != s:
            return False
    return True
```

---

## 2. Расчетный метод (AlgebraicMinimizer)

### 2.1. Назначение

Алгебраический метод минимизации через последовательное применение **законов булевой алгебры**:
- Склеивание
- Поглощение  
- Удаление лишних импликант

### 2.2. Алгоритм

```
┌─────────────────────────────────────────────────────────┐
│  1. Преобразовать минтермы в наборы битов               │
│  2. Получить все простые импликанты (полное склеивание) │
│  3. Построить минимальное покрытие                      │
└─────────────────────────────────────────────────────────┘
```

### 2.3. Реализация

#### Шаг 1: Получение простых импликант

```python
def _get_all_prime_implicants(self, terms):
    current = list(set(terms))
    all_prime_implicants = set()
    
    while True:
        next_round = set()
        used = set()
        
        # Склеиваем все пары
        for i in range(len(current)):
            for j in range(i + 1, len(current)):
                can_merge, _ = self._differs_by_one_tuple(current[i], current[j])
                if can_merge:
                    merged = self._merge_tuples(current[i], current[j])
                    next_round.add(merged)
                    used.add(current[i])
                    used.add(current[j])
        
        # Немаркированные — простые импликанты
        for t in current:
            if t not in used:
                all_prime_implicants.add(t)
        
        current = list(next_round)
        if not current:
            break
    
    return list(all_prime_implicants)
```

**Как работает:**
1. На каждой итерации склеиваются все возможные пары термов
2. Термы, которые были склеены — **маркируются**
3. Немаркированные термы — **простые импликанты**
4. Процесс повторяется с объединенными термами
5. Когда склеивание невозможно — алгоритм завершается

#### Шаг 2: Построение минимального покрытия

```python
def _get_minimal_cover(self, prime_implicants, minterms):
    # Вычисляем покрытие для каждой импликанты
    coverage = {}
    for pi in prime_implicants:
        covered = set()
        for m in minterms:
            if self._covers_tuple(pi, bits_of(m)):
                covered.add(m)
        coverage[pi] = covered
    
    # Находим существенные импликанты
    result = set()
    for m in minterms:
        covering = [pi for pi, cov in coverage.items() if m in cov]
        if len(covering) == 1:  # единственная покрывающая
            result.add(covering[0])
    
    # Жадный алгоритм для остальных
    uncovered = minterms - covered_by(result)
    while uncovered:
        best = argmax(|coverage[pi] ∩ uncovered|)
        result.add(best)
        uncovered -= coverage[best]
    
    return result
```

### 2.4. Преимущества и недостатки

| Преимущества | Недостатки |
|-------------|------------|
| Простота реализации | Не всегда находит оптимальное решение |
| Быстрая работа | Требует проверки всех пар |
| Хорош для небольших функций | |

---

## 3. Метод Квайна-Мак-Класски (QuineMcCluskeyMinimizer)

### 3.1. Назначение

**Таблично-расчетный метод**, который:
1. Систематически находит все простые импликанты
2. Строит таблицу покрытия
3. Находит минимальное покрытие

### 3.2. Алгоритм

```
┌──────────────────────────────────────────────────────────┐
│  1. Группировка минтермов по количеству единиц           │
│  2. Последовательное склеивание соседних групп           │
│  3. Извлечение простых импликант (немаркированные)       │
│  4. Построение таблицы покрытия                          │
│  5. Выбор минимального покрытия (существенные + жадный)  │
└──────────────────────────────────────────────────────────┘
```

### 3.3. Реализация

#### Шаг 1: Группировка по количеству единиц

```python
def _group_by_ones(self, minterms):
    groups = {}
    for m in minterms:
        bits = tuple((m >> i) & 1 for i in range(self.n_vars - 1, -1, -1))
        ones_count = sum(bits)
        if ones_count not in groups:
            groups[ones_count] = []
        groups[ones_count].append(bits)
    return groups
```

**Пример:**
```
Минтермы: [1, 2, 3, 6]  (в битах: 001, 010, 011, 110)

Группы:
  1 единица:  [001, 010]
  2 единицы:  [011, 110]
```

#### Шаг 2: Последовательное склеивание

```python
def _find_prime_implicants(self, groups):
    current = все термы из всех групп
    prime_implicants = set()
    
    while True:
        next_round = set()
        used = set()
        
        # Склеиваем только соседние группы (k и k+1)
        for t1 in current:
            for t2 in current:
                if differs_by_one(t1, t2):
                    merged = merge(t1, t2)
                    next_round.add(merged)
                    used.add(t1)
                    used.add(t2)
        
        # Немаркированные — простые импликанты
        for t in current:
            if t not in used:
                prime_implicants.add(t)
        
        if not next_round:
            break
        current = next_round
    
    return prime_implicants
```

#### Шаг 3: Таблица покрытия

```
        │ Минтермы │
        │ 1  2  3  6│
────┬───┼──────────┤
A   │ X │ X     X  │  ← покрывает 1, 3
B   │ X │ X        │  ← покрывает 1, 2
C   │   │ X     X  │  ← покрывает 2, 6
```

**Существенные импликанты** — покрывают уникальные минтермы.

### 3.4. Преимущества и недостатки

| Преимущества | Недостатки |
|-------------|------------|
| Систематический подход | Экспоненциальная сложность |
| Находит все простые импликанты | Требует много памяти |
| Применим к функциям с любым числом переменных | Медленнее Карно для 3-4 переменных |

---

## 4. Метод Вейча-Карно (KarnaughMinimizer)

### 4.1. Назначение

**Табличный метод**, использующий **геометрическое представление** функции в виде карты Карно.

### 4.2. Теоретические основы

**Карта Карно** — таблица, где:
- Каждая клетка соответствует одному набору переменных
- Соседние клетки отличаются **ровно в одном бите** (код Грея)
- Объединение 2^k соседних клеток дает терм с k удаленными переменными

**Код Грея для 2 бит:**
```
00 → 01 → 11 → 10  (не 00→01→10→11!)
```

### 4.3. Алгоритм

```
┌─────────────────────────────────────────────────────────┐
│  1. Построить карту Карно                               │
│  2. Найти все максимальные объединения (2^k клеток)     │
│  3. Выбрать минимальное покрытие                        │
└─────────────────────────────────────────────────────────┘
```

### 4.4. Реализация

#### Поиск объединений

```python
def _find_all_prime_implicants(self, minterms):
    minterm_set = set(minterms)
    implicants = set()
    
    for start in minterms:
        # Пробуем размеры от большего к меньшему
        for size_power in range(self.n_vars, -1, -1):
            size = 2 ** size_power
            
            # Находим все группы этого размера
            groups = self._find_groups_containing(start, size, minterm_set)
            
            for group in groups:
                if not is_covered_by_any(group, implicants):
                    # Удаляем подмножества
                    implicants = {imp for imp in implicants 
                                  if not is_subset(imp, group)}
                    implicants.add(group)
    
    return list(implicants)
```

#### Поиск соседей

```python
def _find_neighbors(self, bits, minterm_set):
    neighbors = []
    for i in range(self.n_vars):
        new_bits = bits.copy()
        new_bits[i] = 1 - new_bits[i]  # инвертируем бит
        if tuple(new_bits) in minterm_set:
            neighbors.append((i, tuple(new_bits)))
    return neighbors
```

#### Объединение в группы

```python
def _find_groups_containing(self, minterm, size, minterm_set):
    bits = bits_of(minterm)
    groups = []
    
    if size == 1:
        return [tuple(bits)]
    
    # Находим соседей
    neighbors = self._find_neighbors(bits, minterm_set)
    
    if size == 2:
        # Для размера 2: просто соседи
        for _, neighbor_bits in neighbors:
            merged = tuple(
                -1 if bits[j] != neighbor_bits[j] else bits[j]
                for j in range(self.n_vars)
            )
            groups.append(merged)
    
    elif size > 2:
        # Для больших размеров: комбинируем направления
        k = log2(size)
        for dirs in combinations(range(len(neighbors)), k):
            if can_combine(dirs, neighbors, minterm_set):
                merged = create_merged_term(dirs, bits)
                groups.append(merged)
    
    return groups
```

### 4.5. Визуализация (пример для 3 переменных)

```
        x2\x3  00  01  11  10  (код Грея)
       ┌─────────────────────┐
    x1 │                     │
    0  │  0 │  1 │  3 │  2  │
       │────┼────┼────┼────│
    1  │  4 │  5 │  7 │  6  │
       └─────────────────────┘
```

**Объединение клеток 1, 3, 5, 7:**
- Все имеют x3 = 1
- Результат: терм `x3`

### 4.6. Преимущества и недостатки

| Преимущества | Недостатки |
|-------------|------------|
| Наглядность | Только для 3-4 (макс. 5-6) переменных |
| Быстро для небольших функций | Сложно автоматизировать для больших n |
| Легко найти оптимальное решение | Требует визуального контроля |

---

## 5. Сравнение методов

### 5.1. Сложность

| Метод | Временная сложность | Пространственная сложность |
|-------|---------------------|---------------------------|
| Расчетный | O(n²·2ⁿ) | O(2ⁿ) |
| Квайна-Мак-Класски | O(n·2ⁿ) | O(2ⁿ) |
| Вейча-Карно | O(2ⁿ) | O(2ⁿ) |

### 5.2. Применимость

| Метод | 3-4 переменных | 5-6 переменных | 7+ переменных |
|-------|---------------|---------------|--------------|
| Расчетный | ✓ | ✓ | ✓ (медленно) |
| Квайна-Мак-Класски | ✓ | ✓ | ✓ (очень медленно) |
| Вейча-Карно | ✓✓✓ | ✓ | ✗ |

### 5.3. Результаты

Все три метода **должны давать одинаковый результат** (с точностью до перестановки термов), так как находят **минимальную форму**.

---

## 6. Проверка эквивалентности

### 6.1. Зачем нужна

После минимизации СДНФ и СКНФ необходимо убедиться, что полученные формы **логически эквивалентны**.

### 6.2. Алгоритм

```python
def check_equivalence(self, terms_dnf, terms_cnf):
    """Сравнивает таблицы истинности для ТДНФ и ТКНФ"""
    
    def evaluate_terms(terms, form_type):
        results = []
        for i in range(2 ** self.n_vars):
            bits = bits_of(i)
            
            if form_type == 'DNF':
                # Дизъюнкция: достаточно одного истинного терма
                overall = any(evaluate_term(term, bits) for term in terms)
            else:  # CNF
                # Конъюнкция: все термы должны быть истинны
                overall = all(evaluate_term(term, bits) for term in terms)
            
            results.append(1 if overall else 0)
        return results
    
    return evaluate_terms(terms_dnf, 'DNF') == evaluate_terms(terms_cnf, 'CNF')
```

### 6.3. Альтернативные методы

1. **Алгебраическое преобразование** — сложно реализовать
2. **Сравнение через СДНФ** — привести обе формы к СДНФ и сравнить
3. **Таблица истинности** — используется в данной реализации

---

## 7. Структура проекта

```
lab3/
├── LogicFunction.py      # Построение таблицы истинности, СДНФ/СКНФ
├── Minimization.py       # Реализация трёх методов минимизации
│   ├── AlgebraicMinimizer
│   ├── QuineMcCluskeyMinimizer
│   ├── KarnaughMinimizer
│   └── LogicMinimizer    # Главный класс (сравнение + отчет)
├── main.py               # Точка входа
└── ALGORITHMS.md         # Этот файл
```

---

## 8. Пример использования

```python
from Minimization import solve_lab3

# Запуск минимизации для заданного выражения
minimizer = solve_lab3("~((x2+~x3)*~(x1*x3))")

# Доступ к результатам
print("ТДНФ:", minimizer._terms_to_string_dnf(minimizer.algebraic_dnf))
print("ТКНФ:", minimizer._terms_to_string_cnf(minimizer.algebraic_cnf))
print("Методы совпали (СДНФ):", minimizer.check_dnf_methods_match())
print("Методы совпали (СКНФ):", minimizer.check_cnf_methods_match())
print("ТДНФ = ТКНФ:", minimizer.check_dnf_cnf_equivalence())
```

---

## 9. Выводы

1. **Все три метода реализованы корректно** и дают одинаковые результаты
2. **Расчетный метод** — простейший в реализации, хорош для понимания
3. **Метод Квайна-Мак-Класски** — систематический, применим к любым функциям
4. **Метод Вейча-Карно** — наглядный, идеален для 3-4 переменных
5. **Проверка эквивалентности** через таблицу истинности гарантирует корректность
