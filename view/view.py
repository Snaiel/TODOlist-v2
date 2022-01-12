from PyQt5.QtGui import QColor, QMouseEvent, QPalette
from PyQt5.QtCore import QSize, Qt, pyqtSlot
from PyQt5.QtWidgets import QDialog, QMainWindow, QMessageBox, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QComboBox, QInputDialog
import view.widgetObjects as widgetObjects

class Window(QMainWindow):
    """Main Window."""
    def __init__(self, model):
        """Initializer."""
        super().__init__()

        self.model = model

        self._init_ui()
        self.import_data()
        

    def _init_ui(self):
        self.setWindowTitle('TODOlist')
        self.setFixedSize(400, 700)

        self.generalLayout = QVBoxLayout()

        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

        self._createMenu()
        self._createComboBox()
        self._createScrollAreaRow()
        self._createAddButtons()

        self._darkMode()

    def import_data(self):
        focused_list = self.model.app_data['focused']
        self.add_combo_items(self.model.get_list_names(), focused_list)

        for todolist in self.model.data:
            self.add_list(todolist, focused_list)

        self.set_focused_list(focused_list)

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

        self.menu = self.menuBar().addMenu("&Add")
        self.menu.addAction('&Task', lambda: self.create_element(type='Task'))
        self.menu.addAction('&Section', lambda: self.create_element(type='Section'))
        self.menu.addAction('&List', lambda: self.create_list())

    def _createComboBox(self):
        self.combo = QComboBox()
        self.combo.activated.connect(lambda index: self.change_focus(index))
        self.generalLayout.addWidget(self.combo)

    def _createScrollAreaRow(self):
        self.scrollAreaRow = QWidget()
        self.scrollAreaRowLayout = QHBoxLayout(self.scrollAreaRow)
        self.scrollAreaRowLayout.setContentsMargins(0,0,0,0)

        self.generalLayout.addWidget(self.scrollAreaRow)

    def _createAddButtons(self):
        self.addButtonsLayout = QHBoxLayout()

        self.addTaskButton = QPushButton('Add Task')
        self.addSectionButton = QPushButton('Add Section')

        self.addButtonsLayout.addWidget(self.addTaskButton)
        self.addButtonsLayout.addWidget(self.addSectionButton)

        self.addTaskButton.clicked.connect(lambda: self.create_element(type='Task'))
        self.addSectionButton.clicked.connect(lambda: self.create_element(type='Section'))

        self.generalLayout.addLayout(self.addButtonsLayout)

    @pyqtSlot(list, bool, str)
    def send_changed_data(self, indices, value, action):
        print(indices, value, action)
        self.model.write_to_todolist_file(self.focused_list.list_name, indices, value, action)

    def add_combo_items(self, items, focused):
        self.combo.addItems(items)
        self.combo.setCurrentText(focused)

    def add_list(self, todolist, focused):
        self.scrollAreaRowLayout.addWidget(widgetObjects.List(todolist['name'], True if todolist['name'] == focused else False, todolist['data'], self))

    def set_focused_list(self, focused):
        '''
        the focus parameter indicates the name of the list
        '''
        lists = self.scrollAreaRow.children()[1:]
        for list in lists:
            if list.list_name == focused:
                self.focused_list = list
                return
        else:
            self.focused_list = None

    def change_focus(self, index):
        lists = self.scrollAreaRow.children()[1:]
        for list in lists:
            list.setVisible(lists.index(list) == index)
            if lists.index(list) == index:
                self.focused_list = list
                print(list.list_name)
                self.model.change_focus(list.list_name)

    def create_element(self, **kwargs):
        self.focused_list.create_element(type=kwargs['type'])

    def create_list(self):
        print('create list')
        list_name, ok = QInputDialog.getText(self, "create list", f"enter name of list")
        if ok:
            value = self.model.create_list(list_name)
            if value is False:
                message = QMessageBox(self)
                message.setText('List with name already exists')
                message.exec()
            else:
                print(value)
                self.add_list(value, list_name)
                self.change_focus(len(self.scrollAreaRow.children()[1:])-1)
                self.combo.addItem(list_name)
                self.combo.setCurrentText(list_name)

                