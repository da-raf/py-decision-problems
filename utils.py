#!/usr/bin/python3

from syntax import *

def to_NNF(formula, negated=False):
    if type(formula) == Literal:
        if not negated:
            return Literal(formula.name, formula.negated)
        else:
            return Literal(formula.name, not formula.negated)
    elif type(formula) == And:
        if not negated:
            return And([to_NNF(child, negated=False) for child in formula.children])
        else:
            return Or([to_NNF(child, negated=True) for child in formula.children])
    elif type(formula) == Or:
        if not negated:
            return Or([to_NNF(child, negated=False) for child in formula.children])
        else:
            return And([to_NNF(child, negated=True) for child in formula.children])
    elif type(formula) == Negation:
        return to_NNF(formula.child, negated=(not negated))
    elif type(formula) == Implication:
        temp_formula = Or([Negation(formula.lhs), formula.rhs])
        return to_NNF(temp_formula, negated=negated)
    elif type(formula) == Equivalence:
        temp_formula = Or([And([Negation(formula.lhs), Negation(formula.rhs)]), And([formula.lhs, formula.rhs])])
        return to_NNF(temp_formula, negated=negated)
    else:
        raise SyntaxError("unsupported formula type")

def pos(assignment, formula, is_nnf=False):
    if not is_nnf:
        formula = to_NNF(formula)
    
    if type(formula) == Literal:
        if assignment[formula.name] != formula.negated:
            return [formula]
        else:
            return []
    elif type(formula) == And:
        return [pos_lit for child in formula.children for pos_lit in pos(assignment, child)]
    elif type(formula) == Or:
        return [pos_lit for child in formula.children for pos_lit in pos(assignment, child)]
    else:
        raise SyntaxError("formula is not in NNF")

def eval_formula(assignment, formula):
    if type(formula) == Literal:
        return assignment[formula.name] != formula.negated
    elif type(formula) == And:
        return all(eval_formula(assignment, child) for child in formula.children)
    elif type(formula) == Or:
        return any(eval_formula(assignment, child) for child in formula.children)
    elif type(formula) == Negation:
        return not eval_formula(assignment, formula.child)
    elif type(formula) == Implication:
        if eval_formula(assignment, formula.lhs):
            return eval_formula(assignment, formula.rhs)
        else:
            return True
    elif type(formula) == Equivalence:
        return eval_formula(assignment, formula.lhs) == eval_formula(assignment, formula.rhs)
    else:
        raise SyntaxError("unknown formula type")

if __name__ == '__main__':
    from formula_formatter import *

    formatter = FormulaFormatter()

    formula = Implication(Literal('x_1'), Negation(And([Or([Literal('α', True), Literal('β')]), Or([Literal('α'), Literal('β', True)])])))
    print('formula: %s' % formatter.format(formula))

    nnf_formula = to_NNF(formula)
    print('NNF-form: %s' % formatter.format(nnf_formula))

    ass = {"α": True, "β": False, "x_1": True}
    print('assignment: %s' % str(ass))
    print('pos(assignment, formula): %s' % str([formatter.format(pos_lit) for pos_lit in pos(ass, nnf_formula)]))
    print('result: %s' % str(eval_formula(ass, formula)))

