from xml.etree.ElementTree import SubElement
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

        self.setVisible(focused)

        self.theWidget = QWidget()
        self.setWidget(self.theWidget)
            
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.scrollAreaLayout = QVBoxLayout()
        self.scrollAreaLayout.setAlignment(Qt.AlignmentFlag.AlignTop) 

        self.theWidget.setLayout(self.scrollAreaLayout)

        self.create_imported_data(data)
        # print(self.isVisible())

    def create_section_from_data(self, data, parent=None):
        if parent is None:
            section = self.create_element(type='Section', name=data[0][0], state=data[0][1], imported=True)
        else:
            section = parent.create_element(type='Section', name=data[0][0], state=data[0][1], imported=True)

        for element in data[1]:
            if isinstance(element[0], str):
                # print(element)
                section.create_element(type='Task', name=element[0], state=element[1], imported=True)
            else:
                self.create_section_from_data(element, section)

    def create_imported_data(self, data):
        for element in data:
            if isinstance(element[0], str):
                self.create_element(type='Task', name=element[0], state=element[1], imported=True)
            else:
                self.create_section_from_data(element)

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

    def create_element(self, **kwargs):
        '''
            creates an element, placing it somewhere lol idk

            - type: task or section
            - action: whether an element is created by a right click event, the right click action
            - name: the text shown on the task or section
            - state: whether a task is checked or a section is opened
        '''
        if 'imported' not in kwargs:
            kwargs['imported'] = False

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
        # eval(f"element.{type_of_element.lower()}RightClick.triggered.connect(self.right_click_menu_clicked)")

        # If element is created by the user, write to file
        if kwargs['imported'] == False:
            sending_data = {
                'indices': element.get_index_location(),
                'value': element_name,
                'state': state,
                'action': f'create_{type_of_element.lower()}'
            }
            self.root.send_changed_data(sending_data)

        if 'section_data' in kwargs:
            for sub_element in kwargs['section_data']:
                print(sub_element)
                creation_data = {}
                creation_data['type'] = 'Task' if isinstance(sub_element[1], bool) else 'Section'
                creation_data['name'] = sub_element[0] if creation_data['type'] == 'Task' else sub_element[0][0]
                creation_data['state'] = sub_element[1] if creation_data['type'] == 'Task' else sub_element[0][1]
                creation_data['pasted'] = True
                if creation_data['type'] == 'Section':
                    creation_data['section_data'] = sub_element[1]
                element.create_element(**creation_data)

        return element

    def delete_child(self, element):

        kwargs = {
            'indices': element.get_index_location(),
            'action': 'delete_element'
        }
        self.root.send_changed_data(kwargs)

        self.scrollAreaLayout.removeWidget(element)
        element.deleteLater()

    def clear_list(self, action):
        layout = self.scrollAreaLayout
        print(action)

        print(self.theWidget.children())

        for element in self.theWidget.children()[1:]:
            if action == 'Checked':
                if isinstance(element, Task) and element.isChecked():
                    layout.removeWidget(element)
                    element.deleteLater()
            elif action == 'All Checked':
                if isinstance(element, Task) and element.isChecked():
                    layout.removeWidget(element)
                    element.deleteLater()
                elif isinstance(element, Section):
                    element.clear_contents('All Checked')
            elif action == 'All' and element:
                layout.removeWidget(element)
                element.deleteLater()

    def paste(self):
        element_data = self.root.copied_element
        kwargs = { }

        kwargs['type'] = 'Task' if isinstance(element_data[1], bool) else 'Section'
        kwargs['name'] = element_data[0] if kwargs['type'] == 'Task' else element_data[0][0]
        kwargs['state'] = element_data[1] if kwargs['type'] == 'Task' else element_data[0][1]
        if kwargs['type'] == 'Section':
            kwargs['section_data'] = element_data[1]

        self.create_element(**kwargs)

class Task(QCheckBox):
    '''
    A QCheckBox that signifies a single task
    '''

    changed_state = pyqtSignal(dict)

    def __init__(self, task_name, root, checked=False):
        super().__init__(task_name)
        self.root = root

        # self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
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
        while not isinstance(widget[-1].parentWidget().parentWidget(), List):
            widget.append(widget[-1].parentWidget())
            widget.append(widget[-1].parentWidget())
            indices.append(widget[-1].layout().indexOf(widget[-2]))
            widget.pop(0)
        print(indices)
        return indices

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
    def right_click_menu_clicked(self, action):
        switch_case_dict = {
            'Rename': self.rename,
            'Copy': self.copy,
            'Delete': self.delete
        }
        
        if action.text() in switch_case_dict:
            print(action.text(), action.parentWidget().title())
            switch_case_dict[action.text()](action)


    def rename(self, action):
        new_name, ok = QInputDialog.getText(self, 'rename task', 'enter new name')
        if not ok or new_name == '':
            return

        sending_data = {
            'indices': self.get_index_location(),
            'value': new_name,
            'action': 'rename_task'
        }
        
        self.root.send_changed_data(sending_data)
        self.setText(new_name)

    def copy(self, action):
        self.root.copied_element = [self.text(), self.isChecked()]
        print(self.root.copied_element)

    def delete(self, action):
        parent_widget = self.parentWidget()
        print(self, parent_widget)
        while True:
            print(parent_widget)
            if type(parent_widget) in (List, Section):
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
                

class Section(QWidget):
    '''
    A Custom widget that holds tasks or sections. The visibility of the body can be toggled by clicking on the section header.
    '''

    change_visibility = pyqtSignal(dict)

    def __init__(self, section_name, root, open=False):
        super().__init__()
        self.root = root

        self.sectionLayout = QVBoxLayout()
        self.sectionLayout.setContentsMargins(0, 0, 0, 0)

        self.sectionHeader = self.SectionHeader(section_name)
        self.sectionBody = self.SectionBody()
        # self.sectionBody.setVisible(open)

        self.sectionRightClick = self.SectionRightClick(self)

        self.sectionLayout.addWidget(self.sectionHeader)
        self.sectionLayout.addWidget(self.sectionBody)
        self.setLayout(self.sectionLayout)

        self.sectionRightClick.insert_menu.installEventFilter(self)
        self.sectionRightClick.triggered.connect(self.right_click_menu_clicked)

        # self.sectionRightClick.installEventFilter(self)
        self.change_visibility.connect(root.send_changed_data)
        self.sectionHeader.installEventFilter(self)

        print(section_name, open, self.sectionBody.isVisible())
        if open != self.sectionBody.isVisible():
            self._toggle_section(self.sectionHeader.toggleIcon, self.sectionBody, True)
        self.sectionBody.setVisible(open)

    def get_index_location(self):
        indices = []
        widget = []
        widget.append(self.parentWidget())
        indices.append(widget[0].layout().indexOf(self))
        print(widget, indices)
        while not isinstance(widget[-1].parentWidget().parentWidget(), List):
            widget.append(widget[-1].parentWidget())
            widget.append(widget[-1].parentWidget())
            indices.append(widget[-1].layout().indexOf(widget[-2]))
            widget.pop(0)
        print(indices)
        return indices

    def _toggle_section(self, toggle_icon, section_body, imported=False):
        if section_body.isVisible():
            section_body.hide()
            toggle_icon.setText('▶')
            toggle_icon.setStyleSheet("color: white; padding-bottom: 5px")
        else:
            section_body.show()
            toggle_icon.setText('▼')
        
        if not imported:
            kwargs = {
                'indices': self.get_index_location(),
                'value': section_body.isVisible(),
                'action': 'toggle_section'
            }
            self.change_visibility.emit(kwargs)

    def create_element(self, **kwargs):
        if 'imported' not in kwargs:
            kwargs['imported'] = False

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
        # eval(f'element.{element_type.lower()}RightClick.triggered.connect(self.right_click_menu_clicked)')

        # If element is created by the user, write to file
        if kwargs['imported'] == False:
            print('hello')
            sending_data = {
                'indices': element.get_index_location(),
                'value': element_name,
                'state': state,
                'action': f'create_{element_type.lower()}'
            }
            self.root.send_changed_data(sending_data)

        if 'section_data' in kwargs:
            for sub_element in kwargs['section_data']:
                print(sub_element)
                creation_data = {}
                creation_data['type'] = 'Task' if isinstance(sub_element[1], bool) else 'Section'
                creation_data['name'] = sub_element[0] if creation_data['type'] == 'Task' else sub_element[0][0]
                creation_data['state'] = sub_element[1] if creation_data['type'] == 'Task' else sub_element[0][1]
                creation_data['pasted'] = True
                if creation_data['type'] == 'Section':
                    creation_data['section_data'] = sub_element[1]
                element.create_element(**creation_data)

        return element

    def rename(self, action):
        new_name, ok = QInputDialog.getText(self, 'rename section', 'enter new name')
        if not ok or new_name == '':
            return

        sending_data = {
            'indices': self.get_index_location(),
            'value': new_name,
            'action': 'rename_section'
        }
        
        self.root.send_changed_data(sending_data)
        self.sectionHeader.sectionName.setText(new_name)

    def clear_contents(self, action):
        if isinstance(action, QAction):
            action = action.text()
        for widget in self.sectionBody.children()[1:]:
            if action == 'Checked':
                if isinstance(widget, Task) and widget.isChecked():
                    self.sectionLayout.removeWidget(widget)
                    widget.deleteLater()
            elif action == 'All Checked':
                if isinstance(widget, Task) and widget.isChecked():
                    self.sectionLayout.removeWidget(widget)
                    widget.deleteLater()
                elif isinstance(widget, Section):
                    widget.clear_contents('All Checked')
            elif action == 'All':
                self.sectionLayout.removeWidget(widget)
                widget.deleteLater()

        ACTION = {
            'Checked': 'clear_checked',
            'All Checked': 'clear_all_checked',
            'All': 'clear_all'
        }

        sending_data = {
            'indices': self.get_index_location(),
            'action': ACTION[action]
        }

        self.root.send_changed_data(sending_data)

    def delete(self, action):
        parent_widget = self.parentWidget().parentWidget().parentWidget()
        while True:
            if type(parent_widget) in (List, Section):
                break
            else:
                parent_widget = parent_widget.parentWidget()
        parent_widget.delete_child(self)

    def delete_child(self, element):

        kwargs = {
            'indices': element.get_index_location(),
            'action': 'delete_element'
        }

        self.root.send_changed_data(kwargs)

        self.sectionBody.sectionBodyLayout.removeWidget(element)
        element.deleteLater()

    def get_section_data(self, section=None):
        data = []
        if not section:
            section = self
        data.append([section.sectionHeader.sectionName.text(), section.sectionBody.isVisible()])
        # print(self.sectionBody.children())
        section_data = []
        for element in section.sectionBody.children()[1:]:
            if isinstance(element, Task):
                section_data.append([element.text(), element.isChecked()])
            else:
                section_data.append(self.get_section_data(element))
        data.append(section_data)
        return(data)

    def copy(self, action):
        if isinstance(action.parentWidget().parentWidget(), Task):
            return
        self.root.copied_element = self.get_section_data()
        print(self.get_section_data())

    def paste(self, action):
        element_data = self.root.copied_element
        kwargs = { }

        kwargs['type'] = 'Task' if isinstance(element_data[1], bool) else 'Section'
        kwargs['name'] = element_data[0] if kwargs['type'] == 'Task' else element_data[0][0]
        kwargs['state'] = element_data[1] if kwargs['type'] == 'Task' else element_data[0][1]
        if kwargs['type'] == 'Section':
            kwargs['section_data'] = element_data[1]

        self.create_element(**kwargs)

    @pyqtSlot(QAction)
    def right_click_menu_clicked(self, action):
        # print(action.text(), 'hi')

        switch_case_dict = {
            'Task': self.create_element,
            'Section': self.create_element,
            'Rename': self.rename,
            'Checked': self.clear_contents,
            'All Checked': self.clear_contents,
            'All': self.clear_contents,
            'Delete': self.delete,
            'Copy': self.copy,
            'Paste': self.paste
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
            self.sectionHeaderLayout.addWidget(self.toggleIcon)

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
            
            self.addAction('Copy')
            self.addSeparator()

            self.add_menu = self.addMenu('Add')
            
            self.add_menu.addAction('Task')
            self.add_menu.addAction('Section')
            self.add_menu.addAction('Paste')

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

            clear_menu = self.addMenu('Clear')
            clear_menu.addAction("Checked")
            clear_menu.addAction("All Checked")
            clear_menu.addAction("All")
            
            self.addAction('Delete')

