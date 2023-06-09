import dominate
from dominate.tags import script, link, style, div, h3, p
from PyQt5.QtWebEngineWidgets import QWebEngineView

# for type hinting
from ..interpreter.database import Database
from .canvas import PlotData

class Board(QWebEngineView):
    """
    This class provides a widget for rendering latex in the gui.
    This widget basically displays a html file with embedded MathJax.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc = self.new_doc()
        self.rewrite()
        self.setHtml(str(self.doc))

    def new_doc(self) -> dominate.document:
        """
        Creates new blank document that will be displayed in the gui.
        """
        doc = dominate.document()
        with doc.head:
            script(src="https://polyfill.io/v3/polyfill.min.js?features=es6")
            script(type="text/javascript", id="MathJax-script",src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js")
            link(rel="stylesheet", href="https://www.w3schools.com/w3css/4/w3.css")
            style(".MathJax {font-size: 1.5em !important;}")
        return doc

    def rewrite(self, database: Database = None) -> None:
        """
        Writes information about the program onto the widget. Information is stored in an instance of Database class.
        """
        if database:
            data = database.plot_data
            self.doc = self.new_doc()
            with self.doc:
                self.attribute("Variables:", "".join([i + ", " for i in database.variables])[:-2])
                self.attribute("Parameters:", "".join([i + ", " for i in database.parameters])[:-2])
                self.attribute("Order of differentiation:", database.diff_order)
                self.attribute("Domain:", database.domain)
                self.attribute("Precision:", database.precision)
                if len(data)> 0 and len(data[0]) > 0:
                    self.expressions(data[0])
                    if len(data) > 1:
                        for i in range(1,len(data)):
                            self.derivations(i, data[i])
            self.setHtml(str(self.doc))

    @div
    def attribute(self, name: str, text: str) -> None:
        """
        Creates a html element that displays a heading3 "name" and paragraph "text".
        """
        h3(name)
        p(f"$${text}$$", align="center")

    @div(h3("Expressions:"))
    def expressions(self, exprs: list[PlotData]) -> None:
        """
        Creates a html element that displays expressions in latex.
        """
        for expr in exprs:
            p(expr.expr.print("mathjax2"), align="center")

    @div
    def derivations(self, n: int, diffs: list[PlotData]) -> None:
        """
        Creates a html element that displays differentiations of expressions in latex.
        """
        h3(f"Derivative of {n}-th order")
        for diff in diffs:
            p(diff.expr.print("mathjax2"), align="center")

