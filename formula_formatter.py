#!/usr/bin/python3

from syntax import *

class FormulaFormatter:
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


if __name__ == '__main__':
    # test formatter
    formula = Implication(Literal('x_1'), Negation(And([Or([Literal('α', True), Literal('β')]), Or([Literal('α'), Literal('β', True)])])))
    print(FormulaFormatter().format(formula))

