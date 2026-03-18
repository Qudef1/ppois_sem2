class CNFParser:
    def __init__(self, formula):
        self.formula = formula.replace(' ', '')
        self.pos = 0
        self.length = len(self.formula)
        self.error = None
        self.operator_count = 0
        self.bracket_count = 0
    
    def peek(self, offset=0):
        idx = self.pos + offset
        if idx < self.length:
            return self.formula[idx]
        return None
    
    def peek_string(self, length):
        return self.formula[self.pos:self.pos + length]
    
    def consume(self, count=1):
        result = self.formula[self.pos:self.pos + count]
        self.pos += count
        return result
    
    def is_variable_start(self, char):
        return char.isalpha() and char.isupper()
    
    def parse_variable(self):
        """Переменная: заглавная буква + цифры 1-9 (не 0)"""
        if self.pos >= self.length:
            return False
        
        char = self.peek()
        if not self.is_variable_start(char):
            return False
        
        self.consume()
        
        while self.pos < self.length and self.peek().isdigit():
            if self.peek() == '0':
                self.error = "Цифра 0 в имени переменной запрещена"
                return False
            self.consume()
        
        return True
    
    def parse_literal(self):
        """
        Литерал: переменная или !переменная
        ! считается оператором
        """
        if self.pos >= self.length:
            return False
        
        if self.peek() == '!':
            self.consume()
            self.operator_count += 1
            
            if self.peek() == '(':
                self.error = "Отрицание применяется только к переменной: !A"
                return False
            
            if not self.parse_variable():
                self.error = "После ! должна быть переменная"
                return False
        else:
            if not self.parse_variable():
                return False
        
        return True
    
    def parse_atom(self):
        """
        Атом: литерал или (выражение)
        """
        if self.pos >= self.length:
            return False
        
        if self.peek() == '(':
            self.consume()
            self.bracket_count += 1
            
            if not self.parse_expression():
                return False
            
            if self.peek() != ')':
                self.error = "Ожидается ')'"
                return False
            
            self.consume()
            return True
        else:
            return self.parse_literal()
    
    def parse_expression(self):
        """
        Выражение: атом [оператор атом]
        Операторы: \/ (дизъюнкция), /\ (конъюнкция)
        """
        if not self.parse_atom():
            return False
        
        while True:
            if self.peek_string(2) == '/\\':
                self.consume(2)
                self.operator_count += 1
                if not self.parse_atom():
                    return False
            elif self.peek_string(2) == '\\/':
                self.consume(2)
                self.operator_count += 1
                if not self.parse_atom():
                    return False
            else:
                break
        
        return True
    
    def check(self):
        """Основной метод проверки"""
        try:
            if not self.formula:
                self.error = "Пустая формула"
                return False
            
            if not self.parse_expression():
                return False
            
            if self.pos != self.length:
                self.error = f"Непропарсенный остаток: {self.formula[self.pos:]}"
                return False
            
            if self.bracket_count != self.operator_count:
                self.error = f"Несоответствие скобок и операторов: {self.bracket_count} скобок, {self.operator_count} операторов"
                return False
            
            return True
        except Exception as e:
            self.error = str(e)
            return False
    
    def get_error(self):
        return self.error