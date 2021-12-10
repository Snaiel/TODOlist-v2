# Filename: main_window.py
"""Main Window-Style application."""
import sys
from PyQt5.QtGui import QColor, QMouseEvent, QPalette
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import *

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

        self.addTaskButton.clicked.connect(self.create_task)
        self.addSectionButton.clicked.connect(self.create_section)

        self.generalLayout.addLayout(self.addButtonsLayout)

    def taskClicked(self, **kwargs):
        if kwargs['event'].button() == 1:
            kwargs['task'].click()
        if kwargs['event'].button() == 2:
            kwargs['task_right_click'].popup(kwargs['pos'])

    def sectionClicked(self, **kwargs):
        if kwargs['event'].button() == 1:
            self._toggle_section(kwargs['toggle_icon'], kwargs['section_body'])
        elif kwargs['event'].button() == 2:
            kwargs['section_right_click'].popup(kwargs['pos'])

    def create_task(self):
        task_name, ok = QInputDialog.getText(self, 'add task', 'enter name of task')
        if ok and task_name != '':
            task = QCheckBox(task_name)

            taskRightClick = QMenu()
            taskRightClick.addAction('Rename')
            taskRightClick.addAction('Delete')

            task.mouseReleaseEvent = lambda event, task_right_click=taskRightClick: self.taskClicked(event=event, task=task, task_right_click=task_right_click, pos=event.globalPos())
            task.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
            self.scrollAreaLayout.addWidget(task)

    def create_section(self):
        section_name, ok = QInputDialog.getText(self, 'add section', 'enter name of section')
        if not ok or section_name == '':
            return

        section = QWidget()
        sectionLayout = QVBoxLayout()
        sectionLayout.setContentsMargins(0, 0, 0, 0)

        # Header
        sectionHeader = QWidget()
        # sectionHeader.mouseReleaseEvent = self._toggle_section
        sectionHeaderLayout = QHBoxLayout()
        sectionHeaderLayout.setContentsMargins(2, 0, 0, 0)

        toggleIcon = QLabel('▶')
        toggleIcon.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        toggleIcon.setStyleSheet("color: white; padding-bottom: 5px")
        toggleIcon.setIndent(0)
        sectionHeaderLayout.addWidget(toggleIcon, stretch=1)

        sectionName = QLabel(section_name)
        sectionName.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sectionHeaderLayout.addWidget(sectionName, stretch=10)

        sectionHeader.setLayout(sectionHeaderLayout)

        # Body
        sectionBody = QWidget()
        sectionBodyLayout = QVBoxLayout()
        sectionBodyLayout.setContentsMargins(20, 5, 20, 5)

        sectionBodyLayout.addWidget(QCheckBox('Quest'))
        sectionBody.setLayout(sectionBodyLayout)

        sectionRightClick = QMenu()
        sectionRightClick.addAction('Rename')
        sectionRightClick.addAction('Delete')

        sectionHeader.mouseReleaseEvent = lambda event, section_right_click=sectionRightClick, toggle_icon=toggleIcon, section_body=sectionBody: self.sectionClicked(event=event, section_right_click=section_right_click, toggle_icon=toggle_icon, section_body=section_body, pos=event.globalPos())

        sectionLayout.addWidget(sectionHeader)
        sectionLayout.addWidget(sectionBody)
        section.setLayout(sectionLayout)

        self.scrollAreaLayout.addWidget(section)

    def _toggle_section(self, toggle_icon, section_body):
        # print('toggle', event.button(), section_body.hide())
        if section_body.isVisible():
            section_body.hide()
            toggle_icon.setText('▶')
            toggle_icon.setStyleSheet("color: white; padding-bottom: 5px")
        else:
            section_body.show()
            toggle_icon.setText('▼')

    def rename_task(self, task, new_name):
        pass


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
