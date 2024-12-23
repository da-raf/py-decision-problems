class Literal:
    def __init__(self, name, negated=False):
        self.name = name
        self.negated = negated

    def __hash__(self):
        return hash((self.name, self.negated))

    def __eq__(self, other):
        return self.name == other.name and self.negated == other.negated and isinstance(other, Literal)

    def __repr__(self):
        return f"Literal({"!" if self.negated else ""}{self.name})"

class And:
    def __init__(self, children):
        self.children = tuple(children)

    def __eq__(self, other):
        return self.children == other.children and isinstance(other, And)

    def __repr__(self):
        return f"And({", ".join(map(repr, self.children))})"

class Or:
    def __init__(self, children):
        self.children = tuple(children)

    def __eq__(self, other):
        return self.children == other.children and isinstance(other, Or)

    def __repr__(self):
        return f"Or({", ".join(map(repr, self.children))})"

class Negation:
    def __init__(self, child):
        self.child = child

    def __eq__(self, other):
        return self.child == other.child and isinstance(other, Negation)

    def __repr__(self):
        return f"Negation({repr(self.child)})"

class Implication:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __eq__(self, other):
        return self.rhs == other.rhs and self.lhs == other.lhs and isinstance(other, Implication)

    def __repr__(self):
        return f"Implication({repr(self.lhs)}, {repr(self.rhs)})"

class Equivalence:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __eq__(self, other):
        return self.rhs == other.rhs and self.lhs == other.lhs and isinstance(other, Equivalence)

    def __repr__(self):
        return f"Equivalence({repr(self.lhs)}, {repr(self.rhs)})"

