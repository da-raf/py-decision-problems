#!/usr/bin/python

from syntax import *

# transfrom formula to negative normal form
def to_NNF(formula, negated=False):
    """
    get corresponding formula in negative-normal-form

    >>> formatter.format(to_NNF(formula))
    '¬x_1∨((α∧¬β)∨(¬α∧β))'
    """
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
    """
    get a set of literals, which is positive wrt. to the given assignment in the given formula

    >>> ass = get_assignment(get_atoms(formula))(α=True, β=False, x_1=True)
    >>> sorted([formatter.format(pos_lit) for pos_lit in pos(ass, formula)])
    ['¬β', 'α']
    >>> doublelit_formula = And([Literal('x'), Literal('x')])
    >>> doublelit_ass = get_assignment(get_atoms(doublelit_formula))(x=True)
    >>> [formatter.format(pos_lit) for pos_lit in pos(doublelit_ass, doublelit_formula)]
    ['x']
    """

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
    """
    evaluate a given formula wrt. the given assignment

    >>> eval_formula(get_assignment(get_atoms(formula))(α=True, β=False, x_1=True), formula)
    True
    """

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
    """
    get a set of the atoms in the given formula

    >>> get_atoms(formula) == {'α', 'β', 'x_1'}
    True
    """
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
    atoms = sorted(get_atoms(formula))

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
    """
    get a set of all assignments, which satisfy the given formula

    >>> get_satisfying_assignments(simple_formula)
    {Assignment(x=False)}
    """

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
    """
    check if there exists a satisfying assignment for the given formula

    >>> is_satisfiable(simple_formula)
    True
    """

    return bool(get_satisfying_assignments(formula))

def is_valid(formula):
    """
    check if formula is satisfied by all possible assignments

    >>> is_valid(Or([Literal('x'), Literal('x', negated=True)]))
    True
    >>> is_valid(Equivalence(Or([And([Literal('a', negated=True), Literal('b', negated=True), Literal('h')]), And([Negation(And([Literal('a', negated=True), Literal('b', negated=True)])), Or([And([Literal('a', negated=True), Literal('g')]), And([Literal('a'), Literal('f')])])])]), Or([And([Literal('a'), Literal('f')]), And([Literal('a', negated=True), Or([And([Literal('b'), Literal('g')]), And([Literal('b', negated=True), Literal('h')])])])])))
    True
    """
    return not is_satisfiable(Negation(formula))

# transform a formula to disjunctive normal form
def to_DNF(formula):
    """
    convert given formula to disjunctive normal form

    >>> formatter.format(to_DNF(formula))
    '(x_1∧¬α∧β)∨(x_1∧α∧¬β)∨(¬x_1∧α∧¬β)∨(¬x_1∧¬α∧¬β)∨(¬x_1∧¬α∧β)∨(¬x_1∧α∧β)'
    """

    satisfying_assignments = get_satisfying_assignments(formula)

    return Or([And([Literal(name, negated=(not getattr(assignment, name)))
                    for name in assignment._fields])
               for assignment in satisfying_assignments])

# check equivalence of two formulas
def are_equivalent(formula1, formula2):
    """
    check if the given formulas are equivalent

    >>> are_equivalent(Negation(Literal('x')), simple_formula)
    True
    """

    return get_satisfying_assignments(formula1) == get_satisfying_assignments(formula2)

def _onesided_tseitsin_int(formula, helper_var_name, helper_idx, res, cur_helper):
    if type(formula) == Literal:
        res.children.append(Implication(cur_helper, Literal(formula.name, formula.negated)))
        return helper_idx
    elif type(formula) == Or:
        children = []
        for child in formula.children:
            if type(child) == Literal:
                children.append(Literal(child.name, child.negated))
            else:
                children.append(Literal(helper_var_name % helper_idx))
                helper_idx += 1

        res.children.append(Implication(cur_helper, Or(children)))
        for (child, child_formula) in zip(children, formula.children):
            if type(child_formula) != Literal:
                helper_idx = _onesided_tseitsin_int(child_formula, helper_var_name, helper_idx, res, child)
        return helper_idx
    elif type(formula) == And:
        children = []
        for child in formula.children:
            if type(child) == Literal:
                children.append(Literal(child.name, child.negated))
            else:
                children.append(Literal(helper_var_name % helper_idx))
                helper_idx += 1

        res.children.append(Implication(cur_helper, And(children)))
        for (child, child_formula) in zip(children, formula.children):
            if type(child_formula) != Literal:
                helper_idx = _onesided_tseitsin_int(child_formula, helper_var_name, helper_idx, res, child)
        return helper_idx
    elif type(formula) == Negation:
        if type(formula.child) == Literal:
            child = Literal(child.name, child.negated)
        else:
            child = Literal(helper_var_name % helper_idx)
            helper_idx += 1

        res.children.append(Implication(cur_helper, Literal(child.name, negated=True)))
        if type(formula.child) != Literal:
            helper_idx = _onesided_tseitsin_int(formula.child, helper_var_name, helper_idx, res, child)
        return helper_idx
    elif type(formula) == Implication:
        if type(formula.lhs) == Literal:
            lhs_child = Literal(formula.lhs.name, formula.lhs.negated)
        else:
            lhs_child = Literal(helper_var_name % helper_idx)
            helper_idx += 1

        if type(formula.rhs) == Literal:
            rhs_child = Literal(formula.rhs.name, formula.rhs.negated)
        else:
            rhs_child = Literal(helper_var_name % helper_idx)
            helper_idx += 1

        res.children.append(Implication(cur_helper, Implication(lhs_child, rhs_child)))
        if type(formula.lhs) != Literal:
            helper_idx = _onesided_tseitsin_int(formula.lhs, helper_var_name, helper_idx, res, lhs_child)
        if type(formula.rhs) != Literal:
            helper_idx = _onesided_tseitsin_int(formula.rhs, helper_var_name, helper_idx, res, rhs_child)
        return helper_idx
    elif type(formula) == Equivalence:
        if type(formula.lhs) == Literal:
            lhs_child = Literal(formula.lhs.name, formula.lhs.negated)
        else:
            lhs_child = Literal(helper_var_name % helper_idx)
            helper_idx += 1

        if type(formula.rhs) == Literal:
            rhs_child = Literal(formula.rhs.name, formula.rhs.negated)
        else:
            rhs_child = Literal(helper_var_name % helper_idx)
            helper_idx += 1

        res.children.append(Implication(cur_helper, Equivalence(lhs_child, rhs_child)))
        if type(formula.lhs) != Literal:
            helper_idx = _onesided_tseitsin_int(formula.lhs, helper_var_name, helper_idx, res, lhs_child)
        if type(formula.rhs) != Literal:
            helper_idx = _onesided_tseitsin_int(formula.rhs, helper_var_name, helper_idx, res, rhs_child)
        return helper_idx

    return helper_idx
    
def onesided_tseitsin(formula, helper_var_name='x_%d'):
    """
    convert formula to onesided Tseitsin encoding
    """

    res = And([])

    child = Literal(helper_var_name % 0)
    res.children.append(child)
    _onesided_tseitsin_int(formula, helper_var_name, 1, res, child)

    return res

if __name__ == '__main__':
    import doctest
    from formula_formatter import *
    formatter = FormulaFormatter()

    # make formulas available to doctests
    formula = Implication(Literal('x_1'), Negation(And([Or([Literal('α', True), Literal('β')]), Or([Literal('α'), Literal('β', True)])])))
    simple_formula = Implication(Literal('x'), Negation(Literal('x')))

    doctest.testmod()
    tte = onesided_tseitsin(formula, 't_%d')
    print(formatter.format(tte))
    print(get_satisfying_assignments(formula))
    print(get_satisfying_assignments(tte))

