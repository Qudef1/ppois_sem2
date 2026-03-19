import unittest
from CnfChecker import CNFParser


class TestCnf(unittest.TestCase):

    def test_simple_variable(self):
        parser = CNFParser("A")
        self.assertTrue(parser.check())

    def test_negation(self):
        parser = CNFParser("(!A)")
        self.assertTrue(parser.check())

    def test_disjunction(self):
        parser = CNFParser("(A\\/B)")
        self.assertTrue(parser.check())

    def test_conjunction(self):
        parser = CNFParser("(A/\\B)")
        self.assertTrue(parser.check())

    def test_negation_disjunction(self):
        parser = CNFParser("((!A)\\/B)")
        self.assertTrue(parser.check())

    def test_cnf_two_disjuncts(self):
        parser = CNFParser("((A\\/B)/\\(C\\/D))")
        self.assertTrue(parser.check())

    def test_variables_with_digits(self):
        parser = CNFParser("(A1\\/B2)")
        self.assertTrue(parser.check())

    def test_cnf_three_disjuncts(self):
        parser = CNFParser("(((A\\/B)/\\(C\\/D))/\\(E\\/F))")
        self.assertTrue(parser.check())

    def test_negation_variables_with_digits(self):
        parser = CNFParser("((!A1)\\/B2)")
        self.assertTrue(parser.check())

    def test_two_negations(self):
        parser = CNFParser("((!A)\\/(!B))")
        self.assertTrue(parser.check())

    def test_extra_parentheses(self):
        parser = CNFParser("(A)")
        self.assertFalse(parser.check())

    def test_double_parentheses(self):
        parser = CNFParser("((A))")
        self.assertFalse(parser.check())

    def test_extra_parentheses_around_variables(self):
        parser = CNFParser("((A1)\\/(B2))")
        self.assertFalse(parser.check())

    def test_no_parentheses_for_each_operation(self):
        parser = CNFParser("(A\\/B\\/C)")
        self.assertFalse(parser.check())

    def test_negation_without_parentheses(self):
        parser = CNFParser("(!A\\/B)")
        self.assertFalse(parser.check())

    def test_digit_zero(self):
        parser = CNFParser("(A0)")
        self.assertFalse(parser.check())

    def test_only_digit(self):
        parser = CNFParser("(1)")
        self.assertFalse(parser.check())

    def test_lowercase_letter(self):
        parser = CNFParser("(a)")
        self.assertFalse(parser.check())

    def test_negation_expression(self):
        parser = CNFParser("(!((A)\\/(B)))")
        self.assertFalse(parser.check())

    def test_no_parentheses_for_conjunction(self):
        parser = CNFParser("(A)/\\(B)")
        self.assertFalse(parser.check())

    def test_negation_parenthesis(self):
        parser = CNFParser("(!(A))")
        self.assertFalse(parser.check())

    def test_dnf(self):
        parser = CNFParser("((A/\\B)\\/(C/\\D))")
        self.assertFalse(parser.check())

    def test_disjunction_top_level(self):
        parser = CNFParser("(A/\\B)\\/C")
        self.assertFalse(parser.check())


if __name__ == "__main__":
    unittest.main()
