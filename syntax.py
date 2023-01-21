class Literal:
    def __init__(self, name, negated=False):
        self.name = name
        self.negated = negated

    def __hash__(self):
        return hash((self.name, self.negated))

    def __eq__(self, other):
        return self.name == other.name and self.negated == other.negated

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

