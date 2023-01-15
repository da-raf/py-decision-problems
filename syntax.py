class Literal:
    def __init__(self, name, negated=False):
        self.name = name
        self.negated = negated

class And:
    def __init__(self, children):
        self.children = children

class Or:
    def __init__(self, children):
        self.children = children

class Negation:
    def __init__(self, child):
        self.child = child

class Implication:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

class Equivalence:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

