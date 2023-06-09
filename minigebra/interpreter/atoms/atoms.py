import ast
import numpy as np

from . import simplifiers as simplifiers
from . import formatters as formatters
from . import differentiators as differentiators

class Atom:
    """
    Provides representation of atomic expressions in python code. Each expression is of type Atom or one of it's children.
    Each Atom provides functionality such as pretty printing, simplification, differentiation and evaluation.
    """
    def __init__(self):
        self.init_args = ()

    def __add__(self, other):
        return self.__work_with_numbers(Plus, other)
    
    def __sub__(self, other):
        return self.__work_with_numbers(Minus, other)
    
    def __mul__(self, other):
        return self.__work_with_numbers(Mul, other)

    def __truediv__(self, other):
        return self.__work_with_numbers(Div, other)

    def __pow__(self, other):
        return self.__work_with_numbers(Expon, other)

    def get_simplifier(self):
        name = self.__class__.__name__
        func = eval(f"simplifiers.{name}")
        return func(*self.init_args)

    def simplify(self):
        return self.get_simplifier().simplify()

    def simplify_expr(self):
        return self.get_simplifier().simplify_expr()

    def simplify_list(self):
        return self.get_simplifier().simplify_list()

    def get_differentiator(self):
        name = self.__class__.__name__
        func = eval(f"differentiators.{name}")
        return func(*self.init_args)

    def diff(self):
        return self.get_differentiator().diff()

    def get_formatter(self):
        name = self.__class__.__name__
        func =  eval(f"formatters.{name}")
        return func(*self.init_args)

    def __repr__(self):
        return self.get_formatter().string_format()

    def to_ast(self, list_):
        return list_[0]

    def to_list(self):
        return [self]

    def eval(dict: dict) -> float:
        pass

    def __call__(self, *args):
        return self.eval(*args)

    def __work_with_numbers(self, operation, other):
        if type(other) == int or type(other) == float:
            return operation(self, Num(other))
        else:
            return operation(self, other)

    def print(self, option:str):
        if option == "mathjax1":
            return self.get_formatter().mathjax_format1()
        elif option == "mathjax2":
            return self.get_formatter().mathjax_format2()
        elif option == "latex":
            return self.get_formatter().latex_format()
        else:
            return str(self)


class BinaryOperator(Atom):
    def __init__(self, left, right):
        super().__init__()
        self.left = left
        self.right = right
        self.init_args = (self.left, self.right, self)

    def _to_list(self, operation):
        a=[]; b=[]
        left=self.left; right=self.right

        if type(left) == operation:
            a = left.to_list()
        else:
            a.append(left)
        
        if type(right) == operation:
            b = right.to_list()
        else:
            b.append(right)
        
        return a+b

    def _to_ast(self, list_, operation):
        if len(list_) == 1:
            return list_[0]
        else:
            return operation(list_[0], self._to_ast(list_[1:], operation))

    def to_list(self):
        return self._to_list(type(self))

    def to_ast(self, list_):
        return self._to_ast(list_, type(self))

class Div(BinaryOperator):
    def eval(self, dict: dict):
        return self.left.eval(dict) / self.right.eval(dict)

class Mul(BinaryOperator):
    def eval(self, dict: dict):
        return self.left.eval(dict) * self.right.eval(dict)

class Plus(BinaryOperator):
    def eval(self, dict: dict):
        return self.left.eval(dict) + self.right.eval(dict)

class Minus(BinaryOperator):
    def eval(self, dict: dict):
        return self.left.eval(dict) - self.right.eval(dict)

class Expon(BinaryOperator):
    def eval(self, dict: dict):
        return self.left.eval(dict) ** self.right.eval(dict)

class Num(Atom):
    def __init__(self, value):
        self.value = str(value)
        self.num = self.convert()
        self.init_args = (self.value, self)

    def convert(self):
        return ast.literal_eval(self.value)

    def __eq__(self, other):
        if isinstance(other, Num):
            return self.value == other.value
        elif isinstance(other, int) or isinstance(other, float):
            return self.num == other
        else:
            return False

    def __add__(self, other):
        if type(other) == Num:
            return Num(self.num+other.num)
        else:
            return super().__add__(other)
    
    def __sub__(self, other):
        if type(other) == Num:
            return Num(self.num-other.num)
        else:
            return super().__sub__(other)
    
    def __mul__(self, other):
        if type(other) == Num:
            return Num(self.num*other.num)
        else:
            return super().__mul__(other)

    def __pow__(self, other):
        if type(other) == Num:
            return Num(self.num**other.num)
        else:
            return super().__pow__(other)

    def eval(self, dict: dict):
        return self.num

class Var(Atom):
    def __init__(self, value):
        self.value = value
        self.init_args = (self.value, self)

    def eval(self, dict: dict):
        try:
            return dict[self.value]
        except:
            raise Exception(f"Var {self.value} has no specified value.")

class Function(Atom):
    def __init__(self, name, args, func = None):
        self.name = name
        if type(args) != list:
            self.args = [args]
        else:
            self.args = args
        self.func = func
        self.init_args = (self.name, self.args, self)

    def eval(self, dict: dict):
        args = tuple([a.eval(dict) for a in self.args])
        return self.func(*args)

class Sin(Function):
    name = "sin"
    def __init__(self, args):
        super().__init__(self.name, args, np.sin)

class Cos(Function):
    name = "cos"
    def __init__(self, args):
        super().__init__(self.name, args, np.cos)

class Tan(Function):
    name = "tan"
    def __init__(self, args):
        super().__init__(self.name, args, np.tan)

class Exp(Function):
    name = "exp"
    def __init__(self, args):
        super().__init__(self.name, args, np.exp)

class Ln(Function):
    name = "ln"
    def __init__(self, args):
        super().__init__(self.name, args, np.log)

BUILT_IN_FUNCTIONS = [Sin, Cos, Tan, Exp, Ln]