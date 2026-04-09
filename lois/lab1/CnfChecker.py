# Лабораторная работа №1 по дисциплине ЛОИС
# Выполнена студентом группы 421702 БГУИР Сайковским Антоном Валерьевичем
# Реализация обработчика логической формулы на Python для проверки является ли формула КНФ.
#
# 31.03.2026 V1.1 (исправлены источники)
# 
# Источники:
# Система для студентов на кафедре ИИТ
#
# Jackson P., Sheridan D. Clause Form Conversions for Boolean Circuits [Электронный ресурс]
# University of Edinburgh, School of Informatics. – Режим доступа: https://homepages.inf.ed.ac.uk/pbj/papers/sat04-bc-conv.pdf
# - Дата доступа: 02.04.2026.
#
# Колмогоров А.Н., Драгалин А.Г. Математическая логика. Введение в математическую логику. Ч. 1 
# Учебное пособие по математической логике.

class CNFParser:
    def __init__(self, formula: str):
        self.formula = formula
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
        if self.pos >= self.length:
            self.error = "Некорректная формула"
            return False

        ch = self.peek()
        if not (ch.isalpha() and ch.isupper()):
            self.error = (
                f"Некорректная формула"
            )
            return False
        self.consume()

        return True

    def parse_literal(self) -> bool:
        if self.peek() == '(':
            if self.peek(1) == '!':
                self.consume()
                self.consume()

                if self.peek() == '(':
                    self.error = "Отрицание в КНФ применяется только к переменной: (!A)"
                    return False

                if not self.parse_variable():
                    if not self.error:
                        self.error = "После '!' должна быть переменная"
                    return False

                if not self.expect(')'):
                    return False

                return True
            else:
                return False
        else:
            return self.parse_variable()

    def parse_atomic(self) -> bool:
        if self.peek() != '(':
            return self.parse_literal()

        if self.peek(1) == '!':
            return self.parse_literal()

        self.consume()  # '('

        if not self.parse_atomic():
            return False

        if self.peek2() != '\\/':
            self.error = (
                f"Внутри скобок ожидается '\\/' на позиции {self.pos}, "
                f"найдено '{self.peek2()}'"
            )
            return False
        self.consume(2)  # '\/'
        if not self.parse_literal():
            if not self.error:
                self.error = "После '\\/' ожидается литерал"
            return False

        if self.peek2() == '\\/' or self.peek2() == '/\\':
            self.error = (
                "Каждая операция должна быть в отдельных скобках. "
            )
            return False

        if not self.expect(')'):
            return False

        return True

    def _is_conjunction_bracket(self) -> bool:
        i = self.pos + 1   
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
                if op == '/\\': # если на первой глубине скобок конъюнкция, то возвращаем истину
                    return True
                if op == '\\/':
                    return False # если дизъюнкция, то это уже не КНФ
                i += 1
            else:
                i += 1

        return False

    def parse_cnf(self) -> bool:
        if self.peek() != '(':
            return self.parse_atomic()

        if self._is_conjunction_bracket():
            self.consume()  

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
                    self.error = "После '/\\' ожидается либо дизъюнкт либо атомарная формула"
                return False

            if self.peek2() in ('/\\', '\\/'):
                self.error = (
                    "Каждая операция должна быть в отдельных скобках. "
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
                self.error = f"Парсер не отработал до конца"
                return False

            return True

        except Exception as e:
            self.error = str(e)
            return False

    def get_error(self) -> str | None:
        return self.error
