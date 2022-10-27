from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QInputDialog, QMenu
import view.widgets.task as task
import view.widgets.section as section

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

        element = eval(f"{type_of_element.lower()}.{type_of_element}(element_name, self.root, state)")
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
                if isinstance(element, task.Task) and element.isChecked():
                    layout.removeWidget(element)
                    element.deleteLater()
            elif action == 'All Checked':
                if isinstance(element, task.Task) and element.isChecked():
                    layout.removeWidget(element)
                    element.deleteLater()
                elif isinstance(element, section.Section):
                    element.clear_contents('All Checked', True)
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
