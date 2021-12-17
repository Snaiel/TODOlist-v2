from PyQt5.QtGui import QColor, QMouseEvent, QPalette
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import *
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
        self.menu.addAction('&Task', lambda: self.create_element('Task'))
        self.menu.addAction('&Section', lambda: self.create_element('Section'))
        self.menu.addAction('&List')

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

    def add_combo_items(self, items, focused):
        self.combo.addItems(items)
        self.combo.setCurrentText(focused)

    def add_lists(self, data, focused):
        for todolist in data:
            # self.scrollAreaRowLayout.addWidget(widgetObjects.List(str(todolist), True if str(todolist) == focused else False))
            self.scrollAreaRowLayout.addWidget(widgetObjects.List(todolist['name'], True if todolist['name'] == focused else False, todolist['data']))

    def import_data(self):
        self.add_combo_items(self.model.get_list_names(), self.model.app_data['focused'])
        self.add_lists(self.model.test_data, self.model.app_data['focused'])
        self.set_focused_list(self.model.app_data['focused'])
        

    def set_focused_list(self, focused):
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
        

    def create_element(self, **kwargs):
        type_of_element = kwargs['type'] if 'type' in kwargs else kwargs['action'].text()
        element_name, ok = QInputDialog.getText(self, f"create {type_of_element.lower()}", f"enter name of {type_of_element.lower()}")
        
        if not ok or element_name == '':
            return

        element = eval(f"widgetObjects.{type_of_element}(element_name)")
        if 'action' in kwargs:
            action = kwargs['action']
            # index = self.scrollAreaLayout.indexOf(action.parentWidget().parentWidget().parentWidget())
            index = self.focused_list.scrollAreaLayout.indexOf(eval(f"action{'.parentWidget()'*3}"))

            # print(action.parentWidget().parentWidget().add_menu.actions()[3].isChecked())
            insert_position = 0 if action.parentWidget().parentWidget().insert_menu.actions()[3].isChecked() is True else 1

            self.focused_list.scrollAreaLayout.insertWidget(index + insert_position, element)
        else:
            self.focused_list.scrollAreaLayout.addWidget(element)

        ## Listen for when an action in the element's menu is triggered
        eval(f"element.{type_of_element.lower()}RightClick.triggered.connect(self.right_click_menu_clicked)")

    def delete_element(self, action):
        parent_widget = action.parentWidget().parentWidget()
        print(parent_widget)
        self.scrollAreaLayout.removeWidget(parent_widget)
        parent_widget.deleteLater()

    def right_click_menu_clicked(self, action):
        switch_case_dict = {
            'Delete': self.delete_element,
            'Task': self.create_element,
            'Section': self.create_element
        }

        if action is not None and action.text() in switch_case_dict and action.parentWidget().title() == 'Insert':
            print(action.text())
            switch_case_dict[action.text()](action=action)