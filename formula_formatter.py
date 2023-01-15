#!/usr/bin/python3

from syntax import *

class FormulaFormatter:
    def format(self, formula):
        if type(formula) == Literal:
            return self.format_literal(formula)
        elif type(formula) == And:
            return self.format_and(formula)
        elif type(formula) == Or:
            return self.format_or(formula)
        elif type(formula) == Negation:
            return self.format_negation(formula)
        elif type(formula) == Implication:
            return self.format_implication(formula)
        elif type(formula) == Equivalence:
            return self.format_equivalence(formula)
        else:
            raise SyntaxError("unknown formula type")

    def format_literal(self, literal):
        return ('¬' if literal.negated else '') + literal.name

    def format_and(self, and_formula):
        return '(' + '∧'.join(self.format(child) for child in and_formula.children) + ')'

    def format_or(self, or_formula):
        return '(' + '∨'.join(self.format(child) for child in or_formula.children) + ')'
    
    def format_negation(self, negation_formula):
        return '¬' + self.format(negation_formula.child)

    def format_implication(self, implication):
        return '(' + self.format(implication.lhs) + '=>' + self.format(implication.rhs)

    def format_equivalence(self, equivalence):
        return '(' + self.format(implication.lhs) + '<=>' + self.format(implication.rhs) + ')'


if __name__ == '__main__':
    # test formatter
    formula = Implication(Literal('x_1'), Negation(And([Or([Literal('α', True), Literal('β')]), Or([Literal('α'), Literal('β', True)])])))
    print(FormulaFormatter().format(formula))

