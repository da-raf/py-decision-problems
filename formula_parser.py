#!/usr/bin/python

"""
Creates formulas (their syntax trees) from strings.
"""

import pyparsing as pp
import syntax as sx
import functools

def lit_conv(toks):
    return sx.Literal(toks[0])

def neg_conv(toks):
    res = toks[-1]
    for i in range(len(toks)-1):
        res = sx.Negation(res)
    return res

def or_conv(toks):
    return sx.Or(list(toks)) if len(toks) > 1 else toks[0]

def and_conv(toks):
    return sx.And(list(toks)) if len(toks) > 1 else toks[0]

def impl_conv(toks):
    return functools.reduce(sx.Implication, toks)

def equiv_conv(toks):
    return functools.reduce(sx.Equivalence, toks)

def to_operator(lits):
    return functools.reduce(pp.ParserElement.__or__, map(pp.Literal, lits))


class FormulaParser:
    """
    Converts a formula from a string into a syntax tree. Currently ASCII-symbols
    (-/+/*/=>/<=>) and unicode symbols (¬/∧/∨/=>/<=>) are supported as operators.

    >>> FormulaParser().parse("a∧b")
    And(Literal(a), Literal(b))
    >>> FormulaParser().parse("a*b")
    And(Literal(a), Literal(b))

    Operator precedence is negation > conjunction > disjunction > implication > equivalence
    >>> FormulaParser().parse("¬a∧b∨c=>d<=>e")
    Equivalence(Implication(Or(And(Negation(Literal(a)), Literal(b)), Literal(c)), Literal(d)), Literal(e))
    >>> FormulaParser().parse("a<=>b=>c∨d∧¬e")
    Equivalence(Literal(a), Implication(Literal(b), Or(Literal(c), And(Literal(d), Negation(Literal(e))))))

    Associativity is left-to-right:
    >>> FormulaParser().parse("a=>b=>c")
    Implication(Implication(Literal(a), Literal(b)), Literal(c))

    Operators can get freely re-defined:
    >>> FormulaParser().parse("a*b+c")
    Or(And(Literal(a), Literal(b)), Literal(c))
    >>> FormulaParser(or_ops=("*",), and_ops=("+",)).parse("a*b+c")
    Or(Literal(a), And(Literal(b), Literal(c)))
    """
    def __init__(self, neg_ops=("¬", "-"), or_ops=("+", "∨"), and_ops=("*", "∧"), impl_ops=("=>",), equiv_ops=("<=>",), open_bracket=("(",), close_bracket=(")",)):
        self.and_op = to_operator(and_ops)
        self.or_op = to_operator(or_ops)
        self.neg_op = to_operator(neg_ops)
        self.impl_op = to_operator(impl_ops)
        self.equiv_op = to_operator(equiv_ops)
        self.bracket_open = to_operator(open_bracket)
        self.bracket_close = to_operator(close_bracket)
        self.literal_chars = pp.alphas

        self.formula = pp.Forward()

        self.literal = pp.Word(self.literal_chars).set_parse_action(lit_conv)
        self.base_formula = self.literal | (self.bracket_open.suppress() + self.formula + self.bracket_close.suppress())
        self.neg_formula = (pp.ZeroOrMore(self.neg_op) + self.base_formula).set_parse_action(neg_conv)
        self.and_formula = pp.DelimitedList(self.neg_formula, self.and_op).set_parse_action(and_conv)
        self.or_formula = pp.DelimitedList(self.and_formula, self.or_op).set_parse_action(or_conv)
        self.impl_formula = pp.DelimitedList(self.or_formula, self.impl_op).set_parse_action(impl_conv)
        self.equiv_formula = pp.DelimitedList(self.impl_formula, self.equiv_op).set_parse_action(equiv_conv)
        self.formula << self.equiv_formula

    def parse(self, f):
        return self.formula.parse_string(f)[0]


if __name__ == '__main__':
    import doctest

    doctest.testmod()

