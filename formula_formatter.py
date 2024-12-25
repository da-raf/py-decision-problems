#!/usr/bin/python3

"""
provides printing functionality for formulas
"""

from syntax import *
import enum

class OperatorSet:
    def __init__(self, true_sym, false_sym, neg_op, conj_op, disj_op, impl_op, equv_op):
        self.true = true_sym
        self.false = false_sym
        self.negation = neg_op
        self.conjunction = conj_op
        self.disjunction = disj_op
        self.implication = impl_op
        self.equivalence = equv_op

unicode_ops = OperatorSet('⊤', '⊥', '¬', '∧', '∨', '=>', '<=>')
ascii_ops = OperatorSet('T', 'F', '~', '*', '+', '=>', '<=>')

class FormulaFormatter:
    def __init__(self, operators=unicode_ops):
        self.operators = operators

    def format(self, formula, top_level=True):
        if isinstance(formula, bool):
            return (self.operators.true if formula else self.operators.false)
        elif isinstance(formula, Literal):
            return (self.operators.negation if formula.negated else '') + formula.name
        elif isinstance(formula, And):
            if len(formula.children) == 0:
                content = self.operators.true
            else:
                content = self.operators.conjunction.join(self.format(child, False) for child in formula.children)
            return content if top_level or len(formula.children) <= 1 else '(%s)' % content
        elif isinstance(formula, Or):
            if len(formula.children) == 0:
                content = self.operators.false
            else:
                content = self.operators.disjunction.join(self.format(child, False) for child in formula.children)
            return content if top_level or len(formula.children) <= 1 else '(%s)' % content
        elif isinstance(formula, Negation):
            return self.operators.negation + self.format(formula.child, False)
        elif isinstance(formula, Implication):
            content = self.format(formula.lhs, False) + self.operators.implication + self.format(formula.rhs, False)
            return content if top_level else '(%s)' % content 
        elif isinstance(formula, Equivalence):
            content = self.format(formula.lhs, False) + self.operators.equivalence + self.format(formula.rhs, False)
            return content if top_level else '(%s)' % content
        else:
            raise SyntaxError("unknown formula type")


def get_formatter(unicode=False):
    """
    >>> import curses.ascii
    >>> all(curses.ascii.isascii(c) for c in get_formatter(unicode=False).format(all_ops))
    True
    """

    if unicode:
        return FormulaFormatter(unicode_ops)
    else:
        return FormulaFormatter(ascii_ops)

if __name__ == '__main__':
    import doctest

    # formula that will be tested
    all_ops = Equivalence(Literal('a'), Implication(Literal('b'), And([Literal('c'), Or([Literal('d'), Negation(Literal('e'))])])))

    doctest.testmod()

