#!/usr/bin/python

if __name__ == '__main__':
    import argparse
    import formula_parser
    import formula_formatter
    import utils

    arg_parser = argparse.ArgumentParser(description="Query properties of a formula in propositional logic, provided as parameter")
    arg_parser.add_argument('formula', metavar="FORMULA", help="formula in propositional logic")
    arg_parser.add_argument('--all', '-a', action='store_true', help="perform all checks and conversions")
    arg_parser.add_argument('--equivalent-to', metavar="OTHER_FORMULA", help="check if the formula is equivalent to the other formula")
    arg_parser.add_argument('--is-satisfiable', action='store_true', help="check if there exists any satisfying assignment to the formula")
    arg_parser.add_argument('--is-valid', action='store_true', help="check if the formula is valid")
    arg_parser.add_argument('--to-dnf', action='store_true', help="convert the formula to disjunctive normal form")
    arg_parser.add_argument('--to-nnf', action='store_true', help="convert the formula to negative normal form")
    arg_parser.add_argument('--to-cnf', action='store_true', help="convert the formula to conjunctive normal form")
    args = arg_parser.parse_args()

    fparser = formula_parser.FormulaParser()
    fformatter = formula_formatter.FormulaFormatter()

    f = fparser.parse(args.formula)

    print(f"formula: {fformatter.format(f)}")

    if args.is_satisfiable or args.all:
        print(f"satisfiable: {utils.is_satisfiable(f)}")

    if args.is_valid or args.all:
        print(f"valid: {utils.is_valid(f)}")

    if args.to_nnf or args.all:
        print(f"NNF: {fformatter.format(utils.to_NNF(f))}")

    if args.to_dnf or args.all:
        print(f"DNF: {fformatter.format(utils.to_DNF(f))}")

    if args.to_cnf or args.all:
        print(f"CNF: {fformatter.format(utils.to_CNF(f))}")

    if args.equivalent_to:
        other_f = fparser.parse(args.equivalent_to)
        print(f"formula {fformatter.format(f)} is {"" if utils.are_equivalent(f, other_f) else "not "}equivalent to {fformatter.format(other_f)}")

