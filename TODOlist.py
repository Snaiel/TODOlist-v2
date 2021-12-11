# Filename: main_window.py
"""Main Window-Style application."""
import sys
from PyQt5.QtGui import QColor, QMouseEvent, QPalette
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import *
from widgetObjects import Section, Task

class Window(QMainWindow):
    """Main Window."""
    def __init__(self, controller):
        """Initializer."""
        super().__init__()

        self.controller = controller
        self._init_ui()
        

    def _init_ui(self):
        self.setWindowTitle('TODOlist')
        self.setFixedSize(400, 700)

        self.generalLayout = QVBoxLayout()

        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

        self._createMenu()
        self._createComboBox()
        self._createScrollArea()
        self._createAddButtons()

        self._darkMode()

    def _darkMode(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)

    def _createMenu(self):
        self.menu = self.menuBar().addMenu("&Menu")
        self.menu.addAction('&Exit', self.close)

    def _createComboBox(self):
        self.combo = QComboBox()
        self.combo.addItem('Organote')
        self.combo.addItem('Endless Exile')
        self.generalLayout.addWidget(self.combo)

    def _createScrollArea(self):
        self.scrollAreaBody = QWidget()
        self.scrollArea = QScrollArea()

        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.scrollAreaLayout = QVBoxLayout()
        self.scrollAreaLayout.setAlignment(Qt.AlignmentFlag.AlignTop) 

        self.scrollAreaBody.setLayout(self.scrollAreaLayout)
        self.scrollArea.setWidget(self.scrollAreaBody)

        self.generalLayout.addWidget(self.scrollArea)

    def _createAddButtons(self):
        self.addButtonsLayout = QHBoxLayout()

        self.addTaskButton = QPushButton('Add Task')
        self.addSectionButton = QPushButton('Add Section')

        self.addButtonsLayout.addWidget(self.addTaskButton)
        self.addButtonsLayout.addWidget(self.addSectionButton)

        self.addTaskButton.clicked.connect(lambda: self.create_element('Task'))
        self.addSectionButton.clicked.connect(lambda: self.create_element('Section'))

        self.generalLayout.addLayout(self.addButtonsLayout)

    def create_element(self, type):
        print('add element', type)
        element_name, ok = QInputDialog.getText(self, f'add {type.lower()}', f'enter name of {type.lower()}')
        if not ok or element_name == '':
            return

        element = eval(f'{type}(element_name)')
        self.scrollAreaLayout.addWidget(element)
        eval(f'element.{type.lower()}RightClick.triggered.connect(self.right_click_menu_clicked)')

    def delete_element(self, action):
        parent_widget = action.parentWidget().parentWidget()
        print(parent_widget)
        self.scrollAreaLayout.removeWidget(parent_widget)
        parent_widget.deleteLater()

    def right_click_menu_clicked(self, action):
        print(action.text())
        switch_case_dict = {
            'Delete': self.delete_element
        }

        if action.text() in switch_case_dict:
            switch_case_dict[action.text()](action)


class Model:
    def __init__(self, controller) -> None:
        self.data = []
        self.controller = controller

class Controller:
    pass

class TODOlistApplication():
    def __init__(self) -> None:
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")

        self.controller = Controller()

        self.model = Model(self.controller)
        self.view = Window(self.controller)
        self.view.show()

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == '__main__':
    TODOlistApp = TODOlistApplication()
    TODOlistApp.run()
