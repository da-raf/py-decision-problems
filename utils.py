#!/usr/bin/python3

from syntax import *

# transfrom formula to negative normal form
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

# return all literals that are positive in a formula wrt to the given assignment
def pos(assignment, formula, is_nnf=False):
    if not is_nnf:
        formula = to_NNF(formula)

    if type(formula) == Literal:
        if getattr(assignment, formula.name) != formula.negated:
            return {formula}
        else:
            return {}
    elif type(formula) == And:
        return {pos_lit for child in formula.children for pos_lit in pos(assignment, child)}
    elif type(formula) == Or:
        return {pos_lit for child in formula.children for pos_lit in pos(assignment, child)}
    else:
        raise SyntaxError("formula is not in NNF")

# evaluate formula on a specific assignment
def eval_formula(assignment, formula):
    if type(formula) == Literal:
        return getattr(assignment, formula.name) != formula.negated
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

# get all atoms of a formula
def get_atoms(formula, res=None):
    if res is None:
        res = set()

    if type(formula) == Literal:
        res.add(formula.name)
        return res
    elif type(formula) == And or type(formula) == Or:
        for child in formula.children:
            get_atoms(child, res)
        return res
    elif type(formula) == Negation:
        return get_atoms(formula.child, res)
    elif type(formula) == Implication or type(formula) == Equivalence:
        get_atoms(formula.lhs, res)
        return get_atoms(formula.rhs, res)
    else:
        raise SyntaxError("unknown formula type")

from collections import namedtuple

# immutable (and hashable) type to represent assignments
def get_assignment(atoms):
    return namedtuple('Assignment', atoms, defaults=(None,)*len(atoms))

# get all possible assignments of atoms in a formula
def get_all_assignments(formula):
    atoms = get_atoms(formula)

    # construct a namedtuple-based type for Assignments
    # dicts could not be used in sets
    Assignment = get_assignment(atoms)
    res = {Assignment()}

    for atom in atoms:
        new_res = set()
        for ass in res:
            new_res.add(ass._replace(**{atom: False}))
            new_res.add(ass._replace(**{atom: True}))
        res = new_res

    return res

import copy

# get all assignments to atoms of a formula, which evaluate it to true
def get_satisfying_assignments(formula, is_nnf=False, all_assignments=None):
    if all_assignments is None:
        all_assignments = get_all_assignments(formula)
    if not is_nnf:
        formula = to_NNF(formula)

    if type(formula) == Literal:
        return {ass for ass in all_assignments if getattr(ass, formula.name) != formula.negated}
    elif type(formula) == Or:
        res = set()
        for child in formula.children:
            res |= get_satisfying_assignments(child, True, all_assignments)
        return res
    elif type(formula) == And:
        res = copy.copy(all_assignments)
        for child in formula.children:
            res &= get_satisfying_assignments(child, True, res)
        return res
    else:
        raise SyntaxError("formula is not in NNF")

# check, if a formula is satisfiable
def is_satisfiable(formula):
    return bool(get_satisfying_assignments(formula))

# transform a formula to disjunctive normal form
def to_DNF(formula):
    satisfying_assignments = get_satisfying_assignments(formula)

    return Or([And([Literal(name, negated=(not getattr(assignment, name)))
                    for name in assignment._fields])
               for assignment in satisfying_assignments])

# check equivalence of two formulas
def are_equivalent(formula1, formula2):
    return get_satisfying_assignments(formula1) == get_satisfying_assignments(formula2)

if __name__ == '__main__':
    from formula_formatter import *

    formatter = FormulaFormatter()

    formula = Implication(Literal('x_1'), Negation(And([Or([Literal('α', True), Literal('β')]), Or([Literal('α'), Literal('β', True)])])))
    print('formula: %s' % formatter.format(formula))

    nnf_formula = to_NNF(formula)
    print('NNF-form: %s' % formatter.format(nnf_formula))

    Assignment = get_assignment(get_atoms(formula))
    ass = Assignment(α=True, β=False, x_1=True)
    print('assignment: %s' % str(ass))
    print('pos(assignment, formula): %s' % str([formatter.format(pos_lit) for pos_lit in pos(ass, nnf_formula)]))
    print('result: %s' % str(eval_formula(ass, formula)))

    print('atoms: %s' % str(get_atoms(formula)))

    dnf_formula = to_DNF(formula)
    print('DNF-form: %s' % formatter.format(dnf_formula))

    simple_formula = Implication(Literal('x'), Negation(Literal('x')))
    print('formula %s is satisfiable: %s' % (formatter.format(simple_formula), str(is_satisfiable(simple_formula))))
    print('satisfying assignments: %s' % str(get_satisfying_assignments(simple_formula)))
    print('equivalent to ¬x? %s' % str(are_equivalent(Negation(Literal('x')), simple_formula)))

    double_check_formula = And([Literal('x'), Literal('x')])
    DCFAssignment = get_assignment(get_atoms(double_check_formula))
    ass = DCFAssignment(x=True)
    print('double reporting of positive literals? α=%s ∧ φ=%s => pos(φ)=%s' % (str(ass), formatter.format(double_check_formula), {formatter.format(literal) for literal in pos(ass, double_check_formula)}))

