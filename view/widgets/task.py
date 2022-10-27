from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QInputDialog, QMenu, QCheckBox, QAction, QActionGroup, QLineEdit, QWidget
import view.widgets.list as list
import view.widgets.section as section
import view.view as view

class Task(QCheckBox):
    '''
    A QCheckBox that signifies a single task
    '''

    changed_state = pyqtSignal(dict)

    def __init__(self, task_name, root, checked=False):
        super().__init__(task_name)
        root: view.Window
        self.root = root

        self.setChecked(checked)

        self.taskRightClick = self.TaskRightClick(self)
        self.taskRightClick.insert_menu.installEventFilter(self)
        self.taskRightClick.triggered.connect(self.right_click_menu_clicked)

        self.changed_state.connect(root.send_changed_data)

        self.installEventFilter(self)

    def get_index_location(self):
        indices = []
        widgets = []
        widgets.append(self.parentWidget())
        indices.append(widgets[0].layout().indexOf(self))
        print(widgets, indices)
        while not isinstance(widgets[-1].parentWidget().parentWidget(), list.List):
            widgets.append(widgets[-1].parentWidget())
            widgets.append(widgets[-1].parentWidget())
            indices.append(widgets[-1].layout().indexOf(widgets[-2]))
            widgets.pop(0)
        indices.reverse()
        print(indices)
        return indices

    def eventFilter(self, object, event):
        # print(object, event.type())

        if event is not None :
            # Prevent menu closing when selecting 'Before'/ 'After'
            if isinstance(object, QMenu) and event.type() == QMouseEvent.MouseButtonPress:
                action = object.actionAt(event.pos())
                if action is not None and action.text() in ('Before', 'After'):
                    action.trigger()
                    return True

            # When the task is clicked
            if isinstance(object, Task) and event.type() == QMouseEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                kwargs = {
                    'indices': self.get_index_location(),
                    'value': not object.isChecked(),
                    'action': 'toggle_task'
                }
                self.changed_state.emit(kwargs)
        return False

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        if e.button() == 1:
            self.click()
        if e.button() == 2:
            self.taskRightClick.popup(e.globalPos())

    @pyqtSlot(QAction)
    def right_click_menu_clicked(self, action: QAction):
        # print(action.text())
        switch_case_dict = {
            'Task': self.insert,
            'Section': self.insert,
            'Rename': self.rename,
            'Copy': self.copy,
            'Delete': self.delete
        }
        
        if action.text() in switch_case_dict:
            print(action.text(), action.parentWidget().title())
            switch_case_dict[action.text()](action)

    def insert(self, action):
        print(action.parentWidget().title())
        parent_widget = self.parentWidget()
        while True:
            if type(parent_widget) in (list.List, section.Section):
                break
            else:
                parent_widget = parent_widget.parentWidget()

        print(parent_widget)
        parent_widget.create_element(action=action)

    def rename(self, action):
        new_name, ok = QInputDialog.getText(self, 'rename task', 'enter new name', QLineEdit.EchoMode.Normal, self.text())
        if not ok or new_name == '':
            return

        model_data = {
            'indices': self.get_index_location(),
            'value': new_name,
            'action': 'rename_task'
        }
        
        self.root.send_changed_data(model_data)
        self.setText(new_name)

    def copy(self, action):
        self.root.copied_element = [self.text(), self.isChecked()]
        print(self.root.copied_element)

    def delete(self, action):
        parent_widget = self.parentWidget()
        print(self, parent_widget)
        while True:
            print(parent_widget)
            if type(parent_widget) in (list.List, section.Section):
                break
            else:
                parent_widget = parent_widget.parentWidget()
        parent_widget.delete_child(self)

    class TaskRightClick(QMenu):
        def __init__(self, parent):
            super().__init__(parent)

            self.copy_action = self.addAction('Copy')
            self.addSeparator()
            
            self.insert_menu = self.addMenu('Insert')

            self.insert_menu.addAction('Task')
            self.insert_menu.addAction('Section')

            self.insert_menu.addSection('Placement')

            insert_before = QAction('Before')
            insert_after = QAction('After')

            insert_before.setCheckable(True)
            insert_after.setCheckable(True)

            self.insert_menu.addAction(insert_before)
            self.insert_menu.addAction(insert_after)

            placementGroup = QActionGroup(self.insert_menu)
            placementGroup.addAction(insert_before)
            placementGroup.addAction(insert_after)
            insert_after.setChecked(True)

            self.addAction('Rename')
            self.addAction('Delete')
                