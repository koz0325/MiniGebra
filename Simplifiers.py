import Atoms as Atoms
from numpy import gcd

# some of the applied simplifications
# sin^2 + cos^2 = 1
# sin/cos = tan
# cos/sin = 1/tan
# expr ^ -a = 1 / (expr ^ a)
# 1 / (expr ^ -a) = (expr ^ a)
# ln a^b = b * ln a
# ln a - ln b = ln (a/b)
# ln a + ln b = ln (a*b)
# a * (b * x) = (a*b)*x
# a ^ b = a^b
# ((x ^ a) ^ b) ^ c = x ^ (a*b*c)
# expr ^ a * expr ^ b = expr ^ (a+b)
# expr ^ 0 = 1
# expr ^ 1 = expr
# reduce fraction
# a/b * c/d = (a*c)/(b*d)
# a*var + b*var = (a+b) * var
# 0 / expr = 0
# expr / 1 = expr
# const / const = const/const
# const * const = const*const
# expr * constant = constant * expr
# expr * 1 = expr
# 1 * expr = expr
# expr * 0 = 0
# 0 * expr = 0
# const + const = const+const
# expr + 0 = expr
# 0 + expr = expr
# const - const = const-const
# expr - 0 = expr
# 0 - expr = expr
# func(expr) = func(expr.simplify_expr())

class Binary:
    def __init__(self, left, right, parent):
        self.left = left
        self.right = right
        self.parent = parent

    def _simplify_list(self, list_, operation):
        if len(list_) > 1:
            elem = list_[0]
            rest = list_[1:]
            for index, atom in enumerate(rest):
                simplification = operation(elem, atom).simplify_expr()
                if type(simplification) != operation:
                    list_[index+1] = simplification
                    list_ = self._simplify_list(list_[1:], operation)
                    return list_
            return [elem] + self._simplify_list(rest, operation)
        else:
            return list_

    def simplify_list(self):
        return self.parent.to_ast(self._simplify_list(self.parent.to_list(), type(self.parent)))

class Div(Binary):
    def __init__(self, left, right, parent):
        super().__init__(left, right, parent)
    
    def simplify_expr(self):
        left = self.left
        right = self.right
        # 0 / expr = 0
        if left == 0:
            return Atoms.Number(0)

        # expr / 1 = expr
        elif right == 1:
            return left.simplify_expr()

        # # const / const = const/const
        # elif type(left) == Atoms.Number and type(right) == Atoms.Number:
        #     return Atoms.Number(left.num / right.num)

        # reduce fraction
        elif type(left) == Atoms.Number and type(right) == Atoms.Number:
            a = left.num
            b = right.num
            if type(a) == int and type(b) == int:
                div = gcd(a,b)
                a = Atoms.Number(int(a/div))
                b = Atoms.Number(int(b/div))
                return Atoms.Div(a,b)

        else:
            return Atoms.Div(left.simplify_expr(), right.simplify_expr())

class Mul(Binary):
    def __init__(self, left, right, parent):
        super().__init__(left, right, parent)

    def _isNumMul(self, left, right):
        if type(left) == Atoms.Number and type(right) == Atoms.Number:
            return True
        else:
            return False

    def isNumMul(self):
        return self._isNumMul(self.left, self.right)
    
    def simplify_expr(self):
        left = self.left
        right = self.right
        # 0 * expr = 0
        if left == 0:
            return Atoms.Number(0)

        # expr * 0 = 0
        elif right == 0:
            return Atoms.Number(0)

        # 1 * expr = expr
        elif left == 1:
            return right.simplify_expr()

        # expr * 1 = expr
        elif right == 1:
            return left.simplify_expr()

        # expr * constant = constant * expr
        elif type(right) == Atoms.Number and type(left) != Atoms.Number:
            return right * left.simplify_expr()

        # const * const = const*const
        elif type(left) == Atoms.Number and type(right) == Atoms.Number:
            return Atoms.Number(left.num * right.num)

        # a/b * c/d = (a*c)/(b*d)
        elif type(left) == Atoms.Div and type(right) == Atoms.Div:
            return Atoms.Div(left.left.simplify_expr() * right.left.simplify_expr(), left.right.simplify_expr() * right.right.simplify_expr())

        # expr ^ a * expr ^ b = expr ^ (a+b)
        elif type(left) == Atoms.Expon and type(right) == Atoms.Expon:
            if type(left.right) == Atoms.Number and type(right.right) == Atoms.Number and str(left.left) == str(right.left):
                return Atoms.Expon(left.left.simplify_expr(), Atoms.Number(left.right.num * right.right.num))
            else:
                return self.parent

        # a * (b * x) = (a*b)*x
        elif type(left) == Atoms.Number and type(right) == Atoms.Mul and type(right.left) == Atoms.Number:
            return Atoms.Mul(Atoms.Number(left.num * right.left.num), right.right.simplify_expr())

        # a * (b/c) = (a*b)/c
        elif type(left) == Atoms.Number and type(right) == Atoms.Div and type(right.left) == Atoms.Number:
            return Atoms.Div(left*right.left, right.right.simplify_expr())

        # (b/c)*a = (a*b)/c
        elif type(right) == Atoms.Number and type(left) == Atoms.Div and type(left.left) == Atoms.Number:
            return Atoms.Div(right*left.left, left.right.simplify_expr())

        # (a^b) * (c*/d) = (c*/d) * (a^b)
        elif type(left) == Atoms.Expon and (type(right) == Atoms.Mul or type(right) == Atoms.Div):
            return Atoms.Mul(right, left)
        
        # a * ((b*c)*expr) = (a*b*c)*expr
        elif type(left) == Atoms.Number and type(right) == Atoms.Mul and type(right.left) == Atoms.Mul and self._isNumMul(right.left.left, right.left.right):
            return Atoms.Mul(left * right.left.left * right.left.right, right.right.simplify_expr())

        # a * (expr*(b*c)) = (a*b*c)*expr
        elif type(left) == Atoms.Number and type(right) == Atoms.Mul and type(right.right) == Atoms.Mul and self._isNumMul(right.right.left, right.right.right):
            return Atoms.Mul(left * right.right.left * right.right.right, right.left.simplify_expr())

        # (expr*(b*c))*a = (a*b*c)*expr
        elif type(right) == Atoms.Number and type(left) == Atoms.Mul and type(left.right) == Atoms.Mul and self._isNumMul(left.right.left, left.right.right):
            return Atoms.Mul(right * left.right.left * left.right.right, left.left.simplify_expr())

        # ((b*c)*expr)*a = (a*b*c)*expr
        elif type(right) == Atoms.Number and type(left) == Atoms.Mul and type(left.left) == Atoms.Mul and self._isNumMul(left.left.left, left.left.right):
            return Atoms.Mul(right * left.left.left * left.left.right, left.right.simplify_expr())

        # expr * expr
        elif str(left) == str(right):
            return Atoms.Expon(left, Atoms.Number(2))

        # expr * expr ^ a
        elif type(right) == Atoms.Expon and str(left) == str(right.left):
            return Atoms.Expon(left, Atoms.Number(2+1))

        else:
            return Atoms.Mul(left.simplify_expr(), right.simplify_expr())
            

    
class Plus(Binary):
    def __init__(self, left, right, parent):
        super().__init__(left, right, parent)

    def simplify_expr(self):
        left = self.left
        right = self.right
        # 0 + expr = expr
        if left == 0:
            return right.simplify_expr()
        # expr + 0 = expr
        elif right == 0:
            return left.simplify_expr()
        # const + const = const+const
        elif type(left) == Atoms.Number and type(right) == Atoms.Number:
            return Atoms.Number(left.num + right.num)

        # ln a + ln b = ln (a*b)
        elif type(left) == Atoms.Ln and type(right) == Atoms.Ln and len(left.args) == 1 and len(right.args) == 1:
            return Atoms.Ln(left.args[0].simplify_expr() * right.args[0].simplify_expr())

        # a * x + x = (a+1) * x
        elif type(left) == Atoms.Mul and type(left.left) == Atoms.Number and str(left.right) == str(right):
            return Atoms.Mul(Atoms.Number(left.left.num + 1), left.right)

        # expr + expr = 2*expr
        elif str(left) == str(right):
            return Atoms.Number(2) * left

        # a*expr + b*expr = (a+b) * expr
        elif type(left) == Atoms.Mul and type(right) == Atoms.Mul:
            if type(left.left) == Atoms.Number and type(right.left) == Atoms.Number and str(left.right) == str(right.right):
                return Atoms.Number(left.left.num + right.left.num) * left.right.simplify_expr()
            else:
                return Atoms.Plus(left.simplify_expr(), right.simplify_expr())

        else:
            return Atoms.Plus(left.simplify_expr(), right.simplify_expr())

    
class Minus(Binary):
    def __init__(self, left, right, parent):
        super().__init__(left, right, parent)

    def simplify_expr(self):
        left = self.left
        right = self.right
        # 0 - expr = expr
        if left == 0:
            return Atoms.Number(-1) * right.simplify_expr()

        # expr - 0 = expr
        elif right == 0:
            return left.simplify_expr()

        # const - const = const-const
        elif type(left) == Atoms.Number and type(right) == Atoms.Number:
            return Atoms.Number(left.num + right.num)

        # ln a - ln b = ln (a/b)
        elif type(left) == Atoms.Ln and type(right) == Atoms.Ln and len(left.args) == 1 and len(right.args) == 1:
            return Atoms.Ln(left.args[0].simplify_expr() / right.args[0].simplify_expr())

        # var - var = 0
        elif type(left) == Atoms.Variable and type(right) == Atoms.Variable and left.value == right.value:
                return Atoms.Number(0)

        # a*var - b*var = (a-b) * var
        elif type(left) == Atoms.Mul and type(right) == Atoms.Mul:
            if type(left.left) == Atoms.Number and type(right.left) == Atoms.Number and str(left.right) == str(right.right):
                return (left.left - left.right) * left.right.simplify_expr()
            else:
                return Atoms.Minus(left.simplify_expr(), right.simplify_expr())

        else:
            return Atoms.Minus(left.simplify_expr(), right.simplify_expr())

class Expon(Binary):
    def __init__(self, left, right, parent):
        super().__init__(left, right, parent)

    def simplify_expr(self):
        left = self.left
        right = self.right

        # expr ^ 1 = expr
        if type(right) == Atoms.Number and right == 1:
            return left.simplify_expr()

        # expr ^ 0 = 1
        elif type(right) == Atoms.Number and right == 0:
            return Atoms.Number(1)

        # ((x ^ a) ^ b) = x ^ (a*b)
        elif type(left) == Atoms.Expon and type(right) == Atoms.Number:
            if type(left.right) == Atoms.Number:
                return Atoms.Expon(left.left.simplify_expr(), left.right * right)
            else:
                return self.parent

        # a ^ b = a^b
        elif type(left) == Atoms.Number and type(right) == Atoms.Number:
            return Atoms.Number(left.num ** right.num)

        else:
            return self.parent

class Function:
    def __init__(self, name, args, parent):
        self.name = name
        self.args = args
        self.parent = parent

    def simplify_expr(self):
        # func(expr) = func(expr.simplify_expr())
        class_ = type(self.parent)
        if class_ in Atoms.built_in_functions:
            return class_([a.simplify_expr() for a in self.args])
        else:
            return class_(self.name, [a.simplify_expr() for a in self.args])

class Exp(Function):
    def __init__(self, name, args, parent):
        super().__init__(name, args, parent)
    
    def simplify_expr(self):
        if len(self.args) == 1:
            arg = self.args[0]
            if type(arg) == Atoms.Mul and type(arg.right) == Atoms.Ln and len(arg.right.args) == 1:
                return Atoms.Expon(arg.right.args[0].simplify_expr(), arg.left.simplify_expr())
            else:
                return self.parent
        else:
            return self.parent

class Ln(Function):
    def __init__(self, name, args, parent):
        super().__init__(name, args, parent)

    def simplify_expr(self):
        args = self.args
        # ln a^b = b * ln a
        if len(args) == 1 and type(args[0]) == Atoms.Expon:
            return args[0].right.simplify_expr() * Atoms.Ln([args[0].left.simplify_expr()])
        else:
            return self.parent
