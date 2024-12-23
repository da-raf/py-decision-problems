#!/usr/bin/python

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
    res = toks[0]
    for tok in toks[1:]:
        res = sx.Implication(res, tok)
    return res

def equiv_conv(toks):
    res = toks[0]
    for tok in toks[1:]:
        res = sx.Equivalence(res, tok)
    return res

def gen_conv(toks):
    return toks[0]

def to_operator(lits):
    return functools.reduce(pp.ParserElement.__or__, map(pp.Literal, lits))


class FormulaParser:
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

