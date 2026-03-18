class CNFParser:
    def __init__(self, formula: str):
        self.formula = formula.replace(' ', '')
        self.pos = 0
        self.length = len(self.formula)
        self.error: str | None = None

    def peek(self, offset: int = 0) -> str | None:
        idx = self.pos + offset
        return self.formula[idx] if idx < self.length else None

    def peek2(self) -> str:
        return self.formula[self.pos:self.pos + 2]

    def consume(self, count: int = 1) -> str:
        result = self.formula[self.pos:self.pos + count]
        self.pos += count
        return result

    def expect(self, char: str) -> bool:
        if self.peek() != char:
            self.error = f"Ожидается '{char}', найдено '{self.peek()}' на позиции {self.pos}"
            return False
        self.consume()
        return True

    def parse_variable(self) -> bool:
        """
        Переменная: [A-Z][1-9]*
        Заглавная буква, за которой могут идти цифры 1-9 (не 0).
        """
        if self.pos >= self.length:
            self.error = "Неожиданный конец формулы, ожидается переменная"
            return False

        ch = self.peek()
        if not (ch.isalpha() and ch.isupper()):
            self.error = (
                f"Ожидается заглавная буква (переменная), "
                f"найдено '{ch}' на позиции {self.pos}"
            )
            return False
        self.consume()

        while self.pos < self.length and self.peek().isdigit():
            if self.peek() == '0':
                self.error = "Цифра 0 в имени переменной запрещена"
                return False
            self.consume()

        return True

    def parse_literal(self) -> bool:
        if self.peek() == '(':
            # Может быть (!переменная) — смотрим вперёд
            if self.peek(1) == '!':
                self.consume()          # '('
                self.consume()          # '!'

                if self.peek() == '(':
                    self.error = "Отрицание применяется только к переменной: (!A), а не (!(...))"
                    return False

                if not self.parse_variable():
                    if not self.error:
                        self.error = "После '!' должна быть переменная"
                    return False

                if not self.expect(')'):
                    return False

                return True
            else:
                # Это не литерал — откат: скобка принадлежит верхнему уровню
                return False
        else:
            return self.parse_variable()

    def parse_atomic(self) -> bool:
        """
        Клауза КНФ (дизъюнкт):
            literal                           — одиночный литерал
            ( literal \/ literal \/ ... )    — дизъюнкция литералов в скобках

        Внутри скобок разрешён ТОЛЬКО оператор \/.
        Внутри скобок должно быть РОВНО одно вхождение оператора
        (т.е. ровно два литерала) — за счёт вложенности:
            (A\/B) — OK
            ((A\/B)\/C) — OK (левый операнд сам является клаузой в скобках)
        Запрещено: (A\/B\/C) — два оператора в одних скобках.
        """
        if self.peek() != '(':
            # Одиночный литерал без скобок
            return self.parse_literal()

        # Смотрим, это скобка клаузы или литерал (!A)?
        if self.peek(1) == '!':
            # Это литерал (!A)
            return self.parse_literal()

        # Открываем скобку клаузы
        self.consume()  # '('

        # Левый операнд — клауза (рекурсия позволяет ((A\/B)\/C))
        if not self.parse_atomic():
            return False

        if self.peek2() != '\\/':
            self.error = (
                f"Внутри скобок клаузы ожидается '\\/' на позиции {self.pos}, "
                f"найдено '{self.peek2()}'"
            )
            return False
        self.consume(2)  # '\/'

        # Правый операнд — только литерал (не вложенная клауза),
        # чтобы запретить (A\/B\/C) в одних скобках
        if not self.parse_literal():
            if not self.error:
                self.error = "После '\\/' ожидается литерал"
            return False

        # Проверяем, нет ли лишнего оператора в этих же скобках
        if self.peek2() == '\\/' or self.peek2() == '/\\':
            self.error = (
                "Каждая операция должна быть в отдельных скобках. "
                "Вместо (A\\/B\\/C) пишите ((A\\/B)\\/C)"
            )
            return False

        if not self.expect(')'):
            return False

        return True

    def _is_conjunction_bracket(self) -> bool:
        """
        Смотрит вперёд (без изменения pos), чтобы понять:
        открывающая скобка на текущей позиции — это скобка конъюнкции КНФ
        вида (X /\\ Y), или скобка клаузы/литерала (X \\/ Y) / литерала (!X)?

        Алгоритм: заходим внутрь внешних скобок (depth=1) и ищем первый
        оператор на глубине 1. Если это /\\ — конъюнкция КНФ, если \\/ — клауза.
        """
        i = self.pos + 1   # сразу за открывающей '('
        depth = 1
        length = self.length
        formula = self.formula

        while i < length and depth > 0:
            ch = formula[i]
            if ch == '(':
                depth += 1
                i += 1
            elif ch == ')':
                depth -= 1
                i += 1
            elif depth == 1:
                op = formula[i:i+2]
                if op == '/\\':
                    return True
                if op == '\\/':
                    return False
                i += 1
            else:
                i += 1

        return False

    def parse_cnf(self) -> bool:
        if self.peek() != '(':
            # Нет скобки — одиночная переменная
            return self.parse_atomic()

        if self._is_conjunction_bracket():
            # Скобка конъюнкции: ( cnf /\ clause )
            self.consume()  # '('

            if not self.parse_cnf():
                return False

            if self.peek2() != '/\\':
                self.error = (
                    f"Внутри скобок КНФ ожидается '/\\' на позиции {self.pos}, "
                    f"найдено '{self.peek2()}'"
                )
                return False
            self.consume(2)  # '/\'

            if not self.parse_cnf():
                if not self.error:
                    self.error = "После '/\\' ожидается клауза"
                return False

            if self.peek2() in ('/\\', '\\/'):
                self.error = (
                    "Каждая операция должна быть в отдельных скобках. "
                    "Вместо (A/\\B/\\C) пишите ((A/\\B)/\\C)"
                )
                return False

            if not self.expect(')'):
                return False

            return True
        else:
            return self.parse_atomic()

    def check(self) -> bool:
        if not self.formula:
            self.error = "Пустая формула"
            return False

        try:
            if not self.parse_cnf():
                return False

            if self.pos != self.length:
                remaining = self.formula[self.pos:]
                self.error = f"Непарсенный остаток: '{remaining}' на позиции {self.pos}"
                return False

            return True

        except Exception as e:
            self.error = str(e)
            return False

    def get_error(self) -> str | None:
        return self.error
