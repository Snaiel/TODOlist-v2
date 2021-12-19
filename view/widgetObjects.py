from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QInputDialog, QMenu, QCheckBox, QSizePolicy, QAction, QActionGroup, QLabel, QHBoxLayout

class List(QScrollArea):
    '''
    A QScrollArea that will hold the Tasks and Sections of a given 'list' or 'project'
    '''

    def __init__(self, name, focused, data, root):
        super().__init__()

        self.list_name = name
        self.focused = focused
        self.root = root

        if not focused:
            self.hide()

        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.scrollAreaLayout = QVBoxLayout()
        self.scrollAreaLayout.setAlignment(Qt.AlignmentFlag.AlignTop) 

        self.setLayout(self.scrollAreaLayout)

        self.create_imported_data(data)

    def create_section_from_data(self, data, parent=None):
        if parent is None:
            section = self.create_element(type='Section', name=data[0][0], state=data[0][1])
        else:
            section = parent.create_element(type='Section', name=data[0][0], state=data[0][1])

        for element in data[1]:
            if isinstance(element[0], str):
                print(element)
                section.create_element(type='Task', name=element[0], state=element[1])
            else:
                self.create_section_from_data(element, section)


    def create_imported_data(self, data):
        for element in data:
            if isinstance(element[0], str):
                self.create_element(type='Task', name=element[0], state=element[1])
            else:
                self.create_section_from_data(element)

    def create_element(self, **kwargs):
        if 'state' not in kwargs:
            type_of_element = kwargs['type'] if 'type' in kwargs else kwargs['action'].text()
            element_name, ok = QInputDialog.getText(self, f"create {type_of_element.lower()}", f"enter name of {type_of_element.lower()}")
            state=False
            
            if not ok or element_name == '':
                return
        else:
            type_of_element = kwargs['type']
            element_name = kwargs['name']
            state = kwargs['state']

        element = eval(f"{type_of_element}(element_name, self.root, state)")
        if 'action' in kwargs:
            action = kwargs['action']
            # index = self.scrollAreaLayout.indexOf(action.parentWidget().parentWidget().parentWidget())
            index = self.scrollAreaLayout.indexOf(eval(f"action{'.parentWidget()'*3}"))

            # print(action.parentWidget().parentWidget().add_menu.actions()[3].isChecked())
            insert_position = 0 if action.parentWidget().parentWidget().insert_menu.actions()[3].isChecked() is True else 1

            self.scrollAreaLayout.insertWidget(index + insert_position, element)
        else:
            self.scrollAreaLayout.addWidget(element)

        ## Listen for when an action in the element's menu is triggered
        eval(f"element.{type_of_element.lower()}RightClick.triggered.connect(self.right_click_menu_clicked)")

        # If element is created by the user, write to file
        if 'state' not in kwargs:
            self.root.send_changed_data(element.get_index_location(), element_name, f'create_{type_of_element.lower()}')

        return element

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

        if action is not None and action.text() in switch_case_dict:
            if isinstance(action.parentWidget(), QMenu) and action.parentWidget().title() == 'Add':
                return
            print(action.text())
            switch_case_dict[action.text()](action=action)

class Task(QCheckBox):
    '''
    A QCheckBox that signifies a single task
    '''

    changed_state = pyqtSignal(list, bool, str)

    def __init__(self, task_name, root, checked=False):
        super().__init__(task_name)
        self.root = root

        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.setChecked(checked)

        self.taskRightClick = self.TaskRightClick(self)
        self.taskRightClick.insert_menu.installEventFilter(self)
        self.taskRightClick.triggered.connect(self.right_click_menu_clicked)
        self.changed_state.connect(root.send_changed_data)
        self.installEventFilter(self)

    def get_index_location(self):
        indices = []
        widget = []
        widget.append(self.parentWidget())
        indices.append(widget[0].layout().indexOf(self))
        print(widget, indices)
        while not isinstance(widget[-1], List):
            widget.append(widget[-1].parentWidget())
            widget.append(widget[-1].parentWidget())
            indices.append(widget[-1].layout().indexOf(widget[-2]))
            widget.pop(0)
        print(indices)
        return indices

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        if e.button() == 1:
            self.click()
        if e.button() == 2:
            self.taskRightClick.popup(e.globalPos())

    def rename(self, action):
        new_name, ok = QInputDialog.getText(self, 'rename task', 'enter new name')
        if not ok or new_name == '':
            return
        self.setText(new_name)

    @pyqtSlot(QAction)
    def right_click_menu_clicked(self, action):
        switch_case_dict = {
            'Rename': self.rename
        }
        
        if action.text() in switch_case_dict:
            print(action.text(), action.parentWidget().title())
            switch_case_dict[action.text()](action)

    def eventFilter(self, object, event):
        # print(object, event.type())

        if event is not None :
            # Prevent menu closing when selecting 'Before'/ 'After'
            if isinstance(object, QMenu) and event.type() == QMouseEvent.MouseButtonPress:
                action = object.actionAt(event.pos())
                if isinstance(action, QAction):
                    action.trigger()
                return True

            # When the task is clicked
            if isinstance(object, Task) and event.type() == QMouseEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                print(event)
                self.changed_state.emit(self.get_index_location(), not object.isChecked(), 'toggle_task')
        return False


    class TaskRightClick(QMenu):
        def __init__(self, parent):
            super().__init__(parent)
            
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

        class AddMenu(QMenu):
            def __init__(self):
                super().__init__()

                

class Section(QWidget):
    '''
    A Custom widget that holds tasks or sections. The visibility of the body can be toggled by clicking on the section header.
    '''

    change_visibility = pyqtSignal(list, bool, str)

    def __init__(self, section_name, root, open=False):
        super().__init__()
        self.root = root

        self.sectionLayout = QVBoxLayout()
        self.sectionLayout.setContentsMargins(0, 0, 0, 0)

        self.sectionHeader = self.SectionHeader(section_name)
        self.sectionBody = self.SectionBody()
        self.sectionBody.setVisible(open)

        self.sectionRightClick = self.SectionRightClick(self)

        self.sectionLayout.addWidget(self.sectionHeader)
        self.sectionLayout.addWidget(self.sectionBody)
        self.setLayout(self.sectionLayout)

        self.sectionRightClick.insert_menu.installEventFilter(self)
        self.sectionRightClick.triggered.connect(self.right_click_menu_clicked)

        # self.sectionRightClick.installEventFilter(self)
        self.change_visibility.connect(root.send_changed_data)
        self.sectionHeader.installEventFilter(self)

    def get_index_location(self):
        indices = []
        widget = []
        widget.append(self.parentWidget())
        indices.append(widget[0].layout().indexOf(self))
        print(widget, indices)
        while not isinstance(widget[-1], List):
            widget.append(widget[-1].parentWidget())
            widget.append(widget[-1].parentWidget())
            indices.append(widget[-1].layout().indexOf(widget[-2]))
            widget.pop(0)
        print(indices)
        return indices

    def _toggle_section(self, toggle_icon, section_body):
        if section_body.isVisible():
            section_body.hide()
            toggle_icon.setText('▶')
            toggle_icon.setStyleSheet("color: white; padding-bottom: 5px")
            # self.change_visibility.emit(False)
        else:
            section_body.show()
            toggle_icon.setText('▼')
            # self.change_visibility.emit(True)
        
        self.change_visibility.emit(self.get_index_location(), section_body.isVisible(), 'toggle_section')

    def create_element(self, **kwargs):
        if 'state' not in kwargs:
            print(kwargs['action'].parentWidget().parentWidget().parentWidget())
            ## preventing double creation
            if kwargs['action'].parentWidget().title() == 'Insert' and isinstance(kwargs['action'].parentWidget().parentWidget().parentWidget(), QScrollArea):
                return
            elif kwargs['action'].parentWidget().title() == 'Insert' and kwargs['action'].parentWidget().parentWidget().parentWidget() is self:
                return
            elif kwargs['action'].parentWidget().title() == 'Add' and kwargs['action'].parentWidget().parentWidget().parentWidget() is not self:
                return

            creation_type = kwargs['action'].parentWidget().title()
            element_type = kwargs['action'].text()
            print(creation_type, element_type)

            element_name, ok = QInputDialog.getText(self, f'{creation_type.lower()} {element_type.lower()}', f'enter name of {element_type.lower()}')
            if not ok or element_name == '':
                return
            state=False
        else:
            element_type = kwargs['type']
            creation_type = 'Add'
            element_name = kwargs['name']
            state = kwargs['state']

        element = eval(f"{element_type}(element_name, self.root, state)")

        # parent_element = eval(f"action{'.parentWidget()'*4}")
        # print(parent_element.sectionHeader.sectionName.getText())

        if creation_type == 'Insert':
            index = self.sectionBody.sectionBodyLayout.indexOf(eval(f"kwargs['action']{'.parentWidget()'*3}"))

            insert_position = 0 if kwargs['action'].parentWidget().parentWidget().insert_menu.actions()[3].isChecked() is True else 1

            self.sectionBody.sectionBodyLayout.insertWidget(index + insert_position, element)
        else:
            self.sectionBody.sectionBodyLayout.addWidget(element)

        # Listen for when an action in the element's menu is triggered
        eval(f'element.{element_type.lower()}RightClick.triggered.connect(self.right_click_menu_clicked)')

        # If element is created by the user, write to file
        if 'state' not in kwargs:
            self.root.send_changed_data(element.get_index_location(), element_name, f'create_{element_type.lower()}')

        return element


    def rename(self, action):
        new_name, ok = QInputDialog.getText(self, 'rename section', 'enter new name')
        if not ok or new_name == '':
            return
        self.sectionHeader.sectionName.setText(new_name)

    def delete_child_element(self, action):
        parent_widget = action.parentWidget().parentWidget()
        print(parent_widget)
        self.sectionBody.sectionBodyLayout.removeWidget(parent_widget)
        parent_widget.deleteLater()

    @pyqtSlot(QAction)
    def right_click_menu_clicked(self, action):
        # print(action.text(), 'hi')

        switch_case_dict = {
            'Task': self.create_element,
            'Section': self.create_element,
            'Rename': self.rename,
            'Delete': self.delete_child_element
        }

        if action.text() in switch_case_dict:
            switch_case_dict[action.text()](action=action)

    def eventFilter(self, object, event):
        # print(object, event, event.type())

        ## Toggle visibility of section body when the header is clicked
        if isinstance(object, self.SectionHeader) and event.type() == QMouseEvent.MouseButtonRelease:
            if event.button() == 1:
                self._toggle_section(self.sectionHeader.toggleIcon, self.sectionBody)

            elif event.button() == 2:
                self.sectionRightClick.popup(event.globalPos())
            return True

        # if isinstance(object, self.SectionRightClick):
        #     print(object.menuAction().text())

        # Prevent menu from closing when changing 'Placement' option
        if isinstance(object, QMenu):
            if event.type() == QMouseEvent.MouseButtonPress:
                action = object.actionAt(event.pos())
                if isinstance(action, QAction):
                    action.trigger()
                return True

        return False

    class SectionHeader(QWidget):
        def __init__(self, section_name):
            super().__init__()

            self.sectionHeaderLayout = QHBoxLayout()
            self.sectionHeaderLayout.setContentsMargins(2, 0, 0, 0)

            self.toggleIcon = QLabel('▶')
            self.toggleIcon.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
            self.toggleIcon.setStyleSheet("color: white; padding-bottom: 5px")
            self.toggleIcon.setIndent(0)
            self.sectionHeaderLayout.addWidget(self.toggleIcon, stretch=1)

            self.sectionName = QLabel(section_name)
            self.sectionName.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
            self.sectionHeaderLayout.addWidget(self.sectionName, stretch=10)

            self.setLayout(self.sectionHeaderLayout)

    class SectionBody(QWidget):
        def __init__(self):
            super().__init__()

            self.sectionBodyLayout = QVBoxLayout()
            self.sectionBodyLayout.setContentsMargins(20, 5, 20, 5)

            # self.sectionBodyLayout.addWidget(QCheckBox('Quest'))
            self.setLayout(self.sectionBodyLayout)

    class SectionRightClick(QMenu):
        def __init__(self, parent):
            super().__init__(parent)

            self.add_menu = self.addMenu('Add')
            
            self.add_menu.addAction('Task')
            self.add_menu.addAction('Section')

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

