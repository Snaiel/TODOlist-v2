from PyQt5.QtGui import QColor, QMouseEvent, QPalette, QCloseEvent
from PyQt5.QtCore import QSize, Qt, pyqtSlot
from PyQt5.QtWidgets import QDialog, QMainWindow, QMessageBox, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QComboBox, QInputDialog, QAbstractButton
import view.widgetObjects as widgetObjects
from view.preferencesDialog import PreferencesDialog
from model.model import Model

class Window(QMainWindow):
    """Main Window."""
    def __init__(self, model):
        """Initializer."""
        super().__init__()

        self.model = model # type: Model

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

        self._createPreferencesDialog(self.model.get_list_names())

        self._darkMode()

        self.copied_element = None

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
        self.menu_file = self.menuBar().addMenu("&Menu")
        self.menu_file.addAction("&Preferences", lambda: self.show_preferences_dialog())
        self.menu_file.addAction('&Exit', self.close)

        self.menu_add = self.menuBar().addMenu("&Add")
        self.menu_add.addAction('&Task', lambda: self.create_element(type='Task'))
        self.menu_add.addAction('&Section', lambda: self.create_element(type='Section'))
        self.menu_add.addAction('&List', lambda: self.create_list())

        self.menu_edit = self.menuBar().addMenu("&Edit")
        self.menu_edit.addAction('Paste', lambda: self.paste())
        list_menu = self.menu_edit.addMenu('List')
        list_menu.addAction("&Rename", lambda: self.rename_list())
        list_menu.addAction("&Delete", lambda: self.delete_list())
        clear_menu = self.menu_edit.addMenu('Clear')
        clear_menu.addAction("Checked", lambda: self.clear_list(action='Checked'))
        clear_menu.addAction("All Checked", lambda: self.clear_list(action='All Checked'))
        clear_menu.addAction("All", lambda: self.clear_list(action='All'))

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

    def _createPreferencesDialog(self, todolists):
        self.preferencesDialog = PreferencesDialog(self, todolists)

    def show_preferences_dialog(self):
        self.preferencesDialog.exec()

    def preferences_dialog_clicked(self, **kwargs):
        FUNCS = {
            'move up': self.move_list,
            'move down': self.move_list,
            'clear': self.clear_list,
            'rename': self.rename_list,
            'delete': self.delete_list
        }
        FUNCS[kwargs['action']](**kwargs)

    @pyqtSlot(dict)
    def send_changed_data(self, kwargs):
        kwargs['list_name'] = self.focused_list.list_name
        print(kwargs)
        self.model.write_to_todolist_file(**kwargs)

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
        row_layout = self.scrollAreaRowLayout
        for i in range(row_layout.count()):
            the_list = row_layout.itemAt(i).widget()
            the_list.setVisible(i == index)
            if i == index:
                self.focused_list = the_list
                print('change!!', the_list.list_name)
                self.model.change_focus(the_list.list_name)

    def create_element(self, **kwargs):
        if self.focused_list:
            self.focused_list.create_element(type=kwargs['type'])
        else:
            return

    def get_list(self, list_name):
        '''
        given the name of the list, return the widget
        '''
        lists = self.scrollAreaRow.children()[1:]
        for list in lists:
            if list.list_name == list_name:
                return list
        else:
            return None

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
                self.add_list(value, list_name)
                self.change_focus(len(self.scrollAreaRow.children()[1:])-1)
                self.combo.addItem(list_name)
                self.combo.setCurrentText(list_name)
                self.preferencesDialog.update_list_widget(self.model.get_list_names(), None)

    def move_list(self, **kwargs):
        if 'the_list' not in kwargs and self.focused_list is None:
            return

        direction = kwargs['action'].split()[1]

        row_layout = self.scrollAreaRowLayout
        for i in range(row_layout.count()):
            the_list_widget = row_layout.itemAt(i).widget()
            new_index = i -1 if direction == 'up' else + 1
            if the_list_widget.list_name == kwargs['the_list']:
                self.scrollAreaRowLayout.insertWidget(new_index, row_layout.takeAt(i).widget())
                # if self.focused_list.list_name == kwargs['the_list']:
                #     self.change_focus(new_index)
                break

        self.model.move_list(kwargs['the_list'], -1 if direction == 'up' else 1) # descending order
        self.preferencesDialog.update_list_widget(self.model.get_list_names(), kwargs['the_list'])
        self.combo.clear()
        self.add_combo_items(self.model.get_list_names(), self.focused_list.list_name)

    def clear_list(self, **kwargs):
        '''
        deletes elements of the list given, depending on the action type, defaults to the focused list

            - Checked
            - All Checked
            - All
        '''
        if 'the_list' not in kwargs and self.focused_list is None:
            return
        if 'action' not in kwargs:
            kwargs['action'] == 'All'

        messages = {
            'Checked': "Do you want to clear the checked tasks in the base level of the list?",
            'All Checked': "Do you want to clear the checked tasks within the entire list?",
            'All': f"Do you want to clear the contents of the {'selected' if 'the_list' in kwargs else 'focused'} list?"
        }

        dialog = QMessageBox(self)
        dialog.setWindowTitle("clear content")
        dialog.setText(messages[kwargs['action']])
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dialog.setDefaultButton(QMessageBox.Yes)
        answer = dialog.exec()
        if answer == QMessageBox.Yes:
            if 'the_list' in kwargs:
                self.get_list(kwargs['the_list']).clear_list()
                self.model.clear(kwargs['the_list'], kwargs['action'])
                self.preferencesDialog.update_list_widget(self.model.get_list_names(), kwargs['the_list'])
            else:
                self.focused_list.clear_list(kwargs['action'])
                self.model.clear(self.focused_list.list_name, clear_type=kwargs['action'])

    def rename_list(self, **kwargs):
        '''
        renames a list given, defaults to the focused list
        '''
        if 'the_list' not in kwargs and self.focused_list is None:
            return

        new_name, ok = QInputDialog.getText(self, 'rename list', 'enter new name')
        if not ok or new_name == '':
            return

        if not self.model.check_if_todolist_exists(new_name):
            if 'the_list' in kwargs:
                self.model.rename_list(kwargs['the_list'], new_name)
                self.get_list(kwargs['the_list']).list_name = new_name
                self.preferencesDialog.update_list_widget(self.model.get_list_names(), new_name)
            else:
                self.model.rename_list(self.focused_list.list_name, new_name)
                self.focused_list.list_name = new_name
            self.combo.clear()
            self.add_combo_items(self.model.get_list_names(), self.focused_list.list_name if 'the_list' in kwargs else new_name)

    def delete_list(self, **kwargs):
        '''
        deletes the list given, defaults to the focused list
        '''
        print(self.focused_list)
        if 'the_list' not in kwargs and self.focused_list is None:
            return

        dialog = QMessageBox(self)
        dialog.setWindowTitle("delete list")
        dialog.setText("Do you want to delete the focused list?")
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dialog.setDefaultButton(QMessageBox.Yes)
        answer = dialog.exec()
        if answer == QMessageBox.Yes:
            if 'the_list' in kwargs:
                the_list = self.get_list(kwargs['the_list'])
                self.scrollAreaRowLayout.removeWidget(the_list)
                the_list.setParent(None)
                the_list.deleteLater()
                self.model.delete_list(kwargs['the_list'])
            else:
                self.scrollAreaRowLayout.removeWidget(self.focused_list)
                self.focused_list.deleteLater()
                self.model.delete_list(self.focused_list.list_name)

            self.combo.clear()
            self.add_combo_items(self.model.get_list_names(), self.focused_list.list_name if 'the_list' in kwargs else None)
            self.change_focus(0)
            self.preferencesDialog.update_list_widget(self.model.get_list_names(), None)

            if self.scrollAreaRowLayout.count() == 0:
                self.focused_list = None

    def paste(self):
        if self.focused_list:
            self.focused_list.paste()

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.model.close_event(self.focused_list.list_name if self.focused_list else None)
        return super().closeEvent(a0)

                