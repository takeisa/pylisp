from vm import Constant, Halt
from object import TSymbol


def compile(expr, next_expr=Halt()):
    if isinstance(expr, TSymbol):
        pass
    else:
        return Constant(expr, next_expr)
