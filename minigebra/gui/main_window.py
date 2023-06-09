from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PyQt5.QtGui import QIcon

from .canvas import Canvas 
from .sidebar import Sidebar

from ..interpreter import Interpreter


class MainWindow(QMainWindow):
    """
    Main widget of the gui.
    """
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("MiniGebra")
        self.setWindowIcon(QIcon('images/icon.png'))
        self.setGeometry(0,0, 500, 500)
        self.showMaximized()

        self.canvas = Canvas()
        self.sidebar = Sidebar()
        self.interpreter = Interpreter()
        self.sidebar.input.editingFinished(self.process_input)

        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(self.sidebar, 5)
        layout.addWidget(self.canvas, 20)
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self.show()

    def process_input(self, text: str) -> None:
        if text == "":
            self.canvas.reset_axes()
            self.canvas.create_grid_axes()
            self.canvas.clear_axes()
            self.canvas.canvas.draw()
        elif text:
            try:
                self.interpreter.interpret_text(text)
                self.interpreter.generate_data()
                self.canvas.montage(self.interpreter.database.plot_data)
                self.sidebar.board.rewrite(self.interpreter.database)
            except Exception as e:
                print(e)
