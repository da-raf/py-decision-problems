#!/usr/bin/python3

"""
provides printing functionality for formulas
"""

from syntax import *
import enum

class FormulaFormatter:
    """
    formats formula with scientific symbols (requires unicode) ¬/∨/∧/=>/<=>

    >>> FormulaFormatter().format(formula)
    'x_1=>¬((¬a∨b)∧(a∨¬b))'
    """

    def format(self, formula, top_level=True):
        if type(formula) == Literal:
            return ('¬' if formula.negated else '') + formula.name
        elif type(formula) == And:
            content = '∧'.join(self.format(child, False) for child in formula.children)
            return content if top_level else '(%s)' % content
        elif type(formula) == Or:
            content = '∨'.join(self.format(child, False) for child in formula.children)
            return content if top_level else '(%s)' % content
        elif type(formula) == Negation:
            return '¬' + self.format(formula.child, False)
        elif type(formula) == Implication:
            content = self.format(formula.lhs, False) + '=>' + self.format(formula.rhs, False)
            return content if top_level else '(%s)' % content 
        elif type(formula) == Equivalence:
            content = self.format(formula.lhs, False) + '<=>' + self.format(formula.rhs, False)
            return content if top_level else '(%s)' % content
        else:
            raise SyntaxError("unknown formula type")

class AsciiFormulaFormatter:
    """
    formats formula using ascii characters +/-/*/=>/<=>

    >>> AsciiFormulaFormatter().format(formula)
    'x_1=>(-(((-a)+b)*(a+(-b))))'
    """

    def format(self, formula, top_level=True):
        if type(formula) == Literal:
            content = ('-' if formula.negated else '') + formula.name
            return content if top_level or not formula.negated else '(%s)' % content
        elif type(formula) == And:
            content = '*'.join(self.format(child, False) for child in formula.children)
            return content if top_level else '(%s)' % content
        elif type(formula) == Or:
            content = '+'.join(self.format(child, False) for child in formula.children)
            return content if top_level else '(%s)' % content
        elif type(formula) == Negation:
            content = '-' + self.format(formula.child, False)
            return content if top_level else '(%s)' % content
        elif type(formula) == Implication:
            content = self.format(formula.lhs, False) + '=>' + self.format(formula.rhs, False)
            return content if top_level else '(%s)' % content 
        elif type(formula) == Equivalence:
            content = self.format(formula.lhs, False) + '<=>' + self.format(formula.rhs, False)
            return content if top_level else '(%s)' % content
        else:
            raise SyntaxError("unknown formula type")
    
def get_formatter(unicode=False):
    """
    >>> import curses.ascii
    >>> all(curses.ascii.isascii(c) for c in get_formatter(unicode=False).format(formula))
    True
    """

    if unicode:
        return FormulaFormatter()
    else:
        return AsciiFormulaFormatter()

if __name__ == '__main__':
    import doctest

    # formula that will be tested
    formula = Implication(Literal('x_1'), Negation(And([Or([Literal('a', True), Literal('b')]), Or([Literal('a'), Literal('b', True)])])))

    doctest.testmod()

