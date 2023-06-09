from PyQt5.QtWidgets import QApplication
import sys

from .atoms import Atom
from .tokenizer import Tokenizer
from .parser import Parser
from .preprocessor import Preprocessor
from .database import Database
from .commands import Command

from ..gui.canvas import Canvas, PlotData

class Interpreter:
    """
    This class represents interpreter which accepts parsed math expressions and does operations on them.
    Simplifications, differentiations, evaluations and string representations of parsed expressions are also supported by this class.
    """

    def __init__(self):
        self.database = Database()
        self.database.expressions = self.database.expressions

    def print_expressions(self, padding: int = 1) -> None:
        """
        Prints currently held expressions to standard output.
        """
        print("Expressions:")
        pad = "\t" * padding
        expressions = self.database.expressions[0]
        for expr in expressions:
            print(pad+str(expr))

    def print_derivations(self, padding: int = 1) -> None:
        """
        Prints derivatives of currently held expressions to standard output.
        """
        derivations = self.database.expressions[1:]
        pad = "\t" * padding
        for rank, diffs in enumerate(derivations):
            print(f"Differentiations of order {rank+1}:")
            for diff in diffs:
                print(pad+str(diff))

    def print(self, padding=1) -> None:
        """
        Prints expressions and theirs derivatives to standard output.
        """
        self.print_expressions(padding=padding)
        self.print_derivations(padding=padding)

    def diff(self, diff_order: int = 1) -> None:
        """
        Produces derivatives of the original expressions (up to differentiation order, including).
        """
        expr = self.database.expressions[0]
        self.database.expressions=[expr]

        for _ in range(diff_order):
            expr = [i.diff() for i in expr]
            self.database.expressions.append(expr)

    def simplify(self) -> None:
        """
        Simplifies the original expressions.
        """
        self.database.expressions = [[self.__simplify_internal(expr) for expr in elem] for elem in self.database.expressions]

    def generate_data(self) -> None:
        """
        Generates plotting data for each expression and it's derivatives.
        """
        self.database.plot_data = [[PlotData(expr, self.database.variables, self.database.domain, self.database.precision) for expr in elem] for elem in self.database.expressions]

    def __simplify_internal(self, expr: Atom):
        """
        Keeps simplifying the expression recursively until no changes are made.
        """
        simplified = expr.simplify()
        while str(simplified) != str(expr):
           expr = simplified 
           simplified = expr.simplify()
        return simplified

    def compile(self, input):
        """
        Accepts input expressions and commands as strings and produces according commands and expressions from them.
        """
        try:
            commands, exprs = Preprocessor(input).preprocess()
            p = Parser(Tokenizer(), self.database.built_in_functions)
            commands = [p.parse_command(comm) for comm in commands]
            expressions = [p.parse_expr(expr) for expr in exprs]
            return commands, expressions

        except Exception as e:
            print(e)
            return None, None

    def print_commands(self, commands:list, padding: int = 1) -> None:
        """
        Print information about commands on the standart input.
        """
        print("Commands:")
        pad = "\t" * padding
        for command in commands:
            print(pad+str(command))
        print("")

    def interpret_exprs(self, exprs: list[Atom]) -> None:
        """
        Accepts list of expressions as input. Simplifies and differentiates this input. Saves it into the database.
        """
        self.database.expressions = [exprs]
        self.diff(self.database.diff_order)
        self.simplify()

    def interpret_commands(self, commands: list[Command]):
        """
        Interprets list of commands and saves information about them into the database.
        """
        for command in commands:
            name = command.name
            if name == "vars":
                self.database.variables = command.params
            elif name == "params":
                self.database.parameters = command.params
            elif name == "domain":
                left = command.params[0].lstrip("(")
                right = command.params[1].rstrip(")")

                self.database.domain = (float(left), float(right))
            elif name == "precision":
                self.database.precision = float(command.params[0])
            elif name == "diff_order":
                self.database.diff_order = int(command.params[0])
        
    def interpreter_loop(self, plot: bool =False, padding: int =1) -> None:
        """
        This functions provides the command line interface.
        """
        while True:
            text = input("MiniGebra> ")
            commands, expressions = self.compile(text)
            if commands:
                self.print_commands(commands, padding=padding)
                self.interpret_commands(commands)

            if expressions:
                try:
                    self.interpret_exprs(expressions)
                    self.print(padding=padding)
                    if plot:
                        self.generate_data()
                        app = QApplication(sys.argv)
                        canvas = Canvas()
                        canvas.montage(self.database.plot_data)
                        canvas.show()
                        app.exec_()
                        del canvas
                        del app

                except Exception as e:
                    print(e)
                print("")

    def interpret_text(self, input: str) -> None:
        """
        Interprets commands and expressions in the input string. 
        """
        commands, expressions = self.compile(input)
        self.interpret_exprs(expressions)
        self.interpret_commands(commands)