import sys
from PyQt5.QtWidgets import QApplication
from model.model import Model
from view.view import Window

class TODOlistApplication():
    def __init__(self) -> None:
        self.app = QApplication(sys.argv)
        # self.app.setStyle("Fusion")

        self.model = Model()
        self.view = Window(self.model)

        self.view.show()

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == '__main__':
    TODOlistApp = TODOlistApplication()
    TODOlistApp.run()
