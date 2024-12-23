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

    >>> ass = get_assignment_type(formula)(α=True, β=False, x_1=True)
    >>> sorted([formatter.format(pos_lit) for pos_lit in pos(ass, formula)])
    ['¬β', 'α']
    >>> doublelit_formula = And([Literal('x'), Literal('x')])
    >>> doublelit_ass = get_assignment_type(doublelit_formula)(x=True)
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

    >>> eval_formula(get_assignment_type(formula)(α=True, β=False, x_1=True), formula)
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
def get_assignment_type(obj):
    if type(obj) in {Literal, And, Or, Implication, Equivalence}:
        atoms = get_atoms(obj)
    else:
        atoms = obj

    return namedtuple('Assignment', atoms, defaults=(None,)*len(atoms))

# get all possible assignments of atoms in a formula
def get_all_assignments(formula):
    atoms = sorted(get_atoms(formula))

    # construct a namedtuple-based type for Assignments
    # dicts could not be used in sets
    Assignment = get_assignment_type(atoms)
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
    >>> is_satisfiable(And([Literal('x'), Literal('x', negated=True)]))
    False
    >>> is_satisfiable(And([equal_formula1, Negation(equal_formula2)]))
    False
    """

    return bool(get_satisfying_assignments(formula))

def is_valid(formula):
    """
    check if formula is satisfied by all possible assignments

    >>> is_valid(Literal('x'))
    False
    >>> is_valid(Or([Literal('x'), Literal('x', negated=True)]))
    True
    >>> is_valid(Equivalence(equal_formula1, equal_formula2))
    True
    >>> is_valid(Equivalence(Or([equal_formula1, Literal('a')]), equal_formula2))
    False
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

    >>> are_equivalent(simple_formula, simple_formula_equivalent)
    True
    """

    return get_satisfying_assignments(formula1) == get_satisfying_assignments(formula2)

def _tseitsin_substitute(formula, helper_name_format, helper_idx):
    if type(formula) == Literal:
        return Literal(formula.name, formula.negated)
    else:
        return Literal(helper_name_format % next(helper_idx))

def _tseitsin_child(connector, helper_name_format, formula, substituter, helper_idx, res):
    if type(formula) == Literal:
        res.children.append(connector(substituter, Literal(formula.name, formula.negated)))
    elif type(formula) == Or:
        children_substituters = [_tseitsin_substitute(child, helper_name_format, helper_idx) for child in formula.children]

        res.children.append(connector(substituter, Or(children_substituters)))
        for (child_substituter, child_formula) in zip(children_substituters, formula.children):
            if type(child_formula) != Literal:
                _tseitsin_child(connector, helper_name_format, child_formula, child_substituter, helper_idx, res)
    elif type(formula) == And:
        children_substituters = [_tseitsin_substitute(child, helper_name_format, helper_idx) for child in formula.children]

        res.children.append(connector(substituter, And(children_substituters)))
        for (child_substituter, child_formula) in zip(children_substituters, formula.children):
            if type(child_formula) != Literal:
                _tseitsin_child(connector, helper_name_format, child_formula, child_substituter, helper_idx, res)
    elif type(formula) == Negation:
        child_substituter = _tseitsin_substitute(formula.child, helper_name_format, helper_idx)

        res.children.append(connector(substituter, Literal(child_substituter.name, negated=True)))
        if type(formula.child) != Literal:
            _tseitsin_child(connector, helper_name_format, formula.child, child_substituter, helper_idx, res)
    elif type(formula) == Implication:
        lhs_substituter = _tseitsin_substitute(formula.lhs, helper_name_format, helper_idx)
        rhs_substituter = _tseitsin_substitute(formula.rhs, helper_name_format, helper_idx)

        res.children.append(connector(substituter, Implication(lhs_substituter, rhs_substituter)))
        if type(formula.lhs) != Literal:
            _tseitsin_child(connector, helper_name_format, formula.lhs, lhs_substituter, helper_idx, res)
        if type(formula.rhs) != Literal:
            _tseitsin_child(connector, helper_name_format, formula.rhs, rhs_substituter, helper_idx, res)
    elif type(formula) == Equivalence:
        lhs_substituter = _tseitsin_substitute(formula.lhs, helper_name_format, helper_idx)
        rhs_substituter = _tseitsin_substitute(formula.rhs, helper_name_format, helper_idx)

        res.children.append(connector(substituter, Equivalence(lhs_substituter, rhs_substituter)))
        if type(formula.lhs) != Literal:
            _tseitsin_child(connector, helper_name_format, formula.lhs, lhs_substituter, helper_idx, res)
        if type(formula.rhs) != Literal:
            _tseitsin_child(connector, helper_name_format, formula.rhs, rhs_substituter, helper_idx, res)

    return res

def _tseitsin_toplevel(connector, helper_name_format, formula):
    res = And([])

    import itertools
    helper_idx = itertools.count()
    substituter = _tseitsin_substitute(formula, helper_name_format, helper_idx)
    res.children.append(substituter)

    if type(formula) != Literal:
        _tseitsin_child(connector, helper_name_format, formula, substituter, helper_idx, res)

    return res

def onesided_tseitsin(formula, helper_name_format='x_%d'):
    """
    convert formula to onesided Tseitsin encoding

    >>> formatter.format(onesided_tseitsin(Literal('a')))
    'a'
    >>> formatter.format(onesided_tseitsin(formula, helper_name_format='t_%d'))
    't_0∧(t_0=>(x_1=>t_1))∧(t_1=>¬t_2)∧(t_2=>(t_3∧t_4))∧(t_3=>(¬α∨β))∧(t_4=>(α∨¬β))'
    """
    return _tseitsin_toplevel(Implication, helper_name_format, formula)

def tseitsin(formula, helper_name_format='x_%d'):
    """
    convert formula to Tseitsin encoding

    >>> formatter.format(tseitsin(formula, helper_name_format='t_%d'))
    't_0∧(t_0<=>(x_1=>t_1))∧(t_1<=>¬t_2)∧(t_2<=>(t_3∧t_4))∧(t_3<=>(¬α∨β))∧(t_4<=>(α∨¬β))'
    """
    return _tseitsin_toplevel(Equivalence, helper_name_format, formula)

def convert_assignments(asss, new_ass_type):
    """
    map assignments of variables with the same name from one assignment type to another

    If not all values of the destination type will get assigned, the namedtuple-type needs to define defaults.

    >>> convert_assignments({namedtuple('Assignment', ['x', 'y'])(True, False)}, namedtuple('Assignment', ['x', 'z'], defaults=(None,)*2))
    {Assignment(x=True, z=None)}
    """

    if not asss:
        return set()

    old_ass_type = type(next(iter(asss)))
    fields_to_copy = set(old_ass_type._fields).intersection(new_ass_type._fields)

    return {new_ass_type(**{field_name:getattr(ass, field_name) for field_name in fields_to_copy}) for ass in asss}

def filter_assignments(asss, constrs):
    """
    return only those assignments, which have identical values for all assigned values in an element of 'constrs'. Elements with value 'None' count as unassigned.

    >>> Assg = namedtuple('Assignment', ['x', 'z'], defaults=(None,)*2)
    >>> filter_assignments({Assg(x=True, z=False), Assg(x=False, z=True), Assg(x=True, z=True)}, [Assg(x=True)])
    {Assignment(x=True, z=False), Assignment(x=True, z=True)}
    """

    if not asss or not constrs:
        return set()

    target_type = type(next(iter(constrs)))

    if target_type != type(next(iter(constrs))):
        constrs = convert_assignments(constrs, target_type)

    res = set()

    for constr in constrs:
        for ass in asss:
            if all(getattr(constr, field_name) == getattr(ass, field_name) for field_name in constr._fields if getattr(constr, field_name) is not None):
                res.add(ass)

    return res


if __name__ == '__main__':
    import doctest
    from formula_formatter import *
    formatter = FormulaFormatter()

    # make formulas available to doctests
    formula = Implication(Literal('x_1'), Negation(And([Or([Literal('α', True), Literal('β')]), Or([Literal('α'), Literal('β', True)])])))
    simple_formula = Implication(Literal('x'), Negation(Literal('x')))
    simple_formula_equivalent = Negation(Literal('x'))

    equal_formula1 = Or([And([Literal('a', negated=True), Literal('b', negated=True), Literal('h')]), And([Negation(And([Literal('a', negated=True), Literal('b', negated=True)])), Or([And([Literal('a', negated=True), Literal('g')]), And([Literal('a'), Literal('f')])])])])
    equal_formula2 = Or([And([Literal('a'), Literal('f')]), And([Literal('a', negated=True), Or([And([Literal('b'), Literal('g')]), And([Literal('b', negated=True), Literal('h')])])])])

    doctest.testmod()

