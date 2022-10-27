from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QInputDialog, QMenu, QSizePolicy, QAction, QActionGroup, QLabel, QHBoxLayout, QLineEdit
import view.widgets.list as list
import view.widgets.task as task

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

        self.sectionRightClick = self.SectionRightClick(self)

        self.sectionLayout.addWidget(self.sectionHeader)
        self.sectionLayout.addWidget(self.sectionBody)
        self.setLayout(self.sectionLayout)

        self.sectionRightClick.insert_menu.installEventFilter(self)
        self.sectionRightClick.triggered.connect(self.right_click_menu_clicked)

        self.change_visibility.connect(root.send_changed_data)
        self.sectionHeader.installEventFilter(self)

        if open != self.sectionBody.isVisible():
            self._toggle_section(self.sectionHeader.toggleIcon, self.sectionBody, True)
        self.sectionBody.setVisible(open)

    def _get_index_location(self):
        indices = []
        widget = []
        widget.append(self.parentWidget())
        indices.append(widget[0].layout().indexOf(self))
        print(widget, indices)
        while not isinstance(widget[-1].parentWidget().parentWidget(), list.List):
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
                'indices': self._get_index_location(),
                'value': section_body.isVisible(),
                'action': 'toggle_section'
            }
            self.change_visibility.emit(kwargs)

    def _create_element(self, **kwargs):
        if 'imported' not in kwargs:
            kwargs['imported'] = False

        if 'state' not in kwargs:
            print(kwargs['action'].parentWidget().parentWidget().parentWidget())
            ## preventing double creation
            if kwargs['action'].parentWidget().title() == 'Insert' and isinstance(kwargs['action'].parentWidget().parentWidget().parentWidget(), QScrollArea):
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

        element = eval(f"{element_type.lower() + '.' if element_type == 'Task' else ''}{element_type}(element_name, self.root, state)")

        if creation_type == 'Insert':
            index = self.sectionBody.sectionBodyLayout.indexOf(eval(f"kwargs['action']{'.parentWidget()'*3}"))
            insert_position = 0 if kwargs['action'].parentWidget().parentWidget().insert_menu.actions()[3].isChecked() is True else 1
            self.sectionBody.sectionBodyLayout.insertWidget(index + insert_position, element)
        else:
            self.sectionBody.sectionBodyLayout.addWidget(element)

        if kwargs['imported'] == False:
            print('hello')
            sending_data = {
                'indices': element._get_index_location(),
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
                element._create_element(**creation_data)

        return element

    def insert(self, action):
        print(action.parentWidget().title())
        parent_widget = self.parentWidget() # type: list.List
        while True:
            if type(parent_widget) in (list.List, Section):
                break
            else:
                parent_widget = parent_widget.parentWidget()

        print(parent_widget)
        parent_widget._create_element(action=action)

    def rename(self, action):
        new_name, ok = QInputDialog.getText(self, 'rename section', 'enter new name', QLineEdit.EchoMode.Normal, self.sectionHeader.sectionName.text())
        if not ok or new_name == '':
            return

        sending_data = {
            'indices': self._get_index_location(),
            'value': new_name,
            'action': 'rename_section'
        }
        
        self.root.send_changed_data(sending_data)
        self.sectionHeader.sectionName.setText(new_name)

    def clear_contents(self, action, triggered_from_parent=False):
        if isinstance(action, QAction):
            action = action.text()
        for widget in self.sectionBody.children()[1:]:
            if action == 'Checked':
                if isinstance(widget, task.Task) and widget.isChecked():
                    self.sectionLayout.removeWidget(widget)
                    widget.deleteLater()
            elif action == 'All Checked':
                if isinstance(widget, task.Task) and widget.isChecked():
                    self.sectionLayout.removeWidget(widget)
                    widget.deleteLater()
                elif isinstance(widget, Section):
                    widget.clear_contents('All Checked', True)
            elif action == 'All':
                self.sectionLayout.removeWidget(widget)
                widget.deleteLater()

        ACTION = {
            'Checked': 'clear_checked',
            'All Checked': 'clear_all_checked',
            'All': 'clear_all'
        }

        if not triggered_from_parent:
            sending_data = {
            'indices': self._get_index_location(),
            'action': ACTION[action]
            }
            self.root.send_changed_data(sending_data)

    def delete(self, action):
        parent_widget = self.parentWidget().parentWidget().parentWidget()
        while True:
            if type(parent_widget) in (list.List, Section):
                break
            else:
                parent_widget = parent_widget.parentWidget()
        parent_widget.delete_child(self)

    def delete_child(self, element):

        kwargs = {
            'indices': element._get_index_location(),
            'action': 'delete_element'
        }

        self.root.send_changed_data(kwargs)

        self.sectionBody.sectionBodyLayout.removeWidget(element)
        element.deleteLater()

    def copy(self, action):
        if isinstance(action.parentWidget().parentWidget(), task.Task):
            return
        self.root.copied_element = self._get_section_data()
        print(self._get_section_data())

    def _get_section_data(self, section=None):
        data = []
        if not section:
            section = self
        data.append([section.sectionHeader.sectionName.text(), section.sectionBody.isVisible()])
        section_data = []
        for element in section.sectionBody.children()[1:]:
            if isinstance(element, task.Task):
                section_data.append([element.text(), element.isChecked()])
            else:
                section_data.append(self._get_section_data(element))
        data.append(section_data)
        return(data)

    def paste(self, action):
        element_data = self.root.copied_element
        kwargs = { }

        kwargs['type'] = 'Task' if isinstance(element_data[1], bool) else 'Section'
        kwargs['name'] = element_data[0] if kwargs['type'] == 'Task' else element_data[0][0]
        kwargs['state'] = element_data[1] if kwargs['type'] == 'Task' else element_data[0][1]
        if kwargs['type'] == 'Section':
            kwargs['section_data'] = element_data[1]

        self._create_element(**kwargs)

    @pyqtSlot(QAction)
    def right_click_menu_clicked(self, action):
        if action.parentWidget() is not None and action.parentWidget().title() == 'Insert':
            self.insert(action)
            return

        switch_case_dict = {
            'Task': self._create_element,
            'Section': self._create_element,
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

        ## Toggle visibility of section body when the header is clicked
        if isinstance(object, self.SectionHeader) and event.type() == QMouseEvent.MouseButtonRelease:
            if event.button() == 1:
                self._toggle_section(self.sectionHeader.toggleIcon, self.sectionBody)

            elif event.button() == 2:
                self.sectionRightClick.popup(event.globalPos())
            return True

        if object == self.sectionRightClick.insert_menu and event.type() == QMouseEvent.MouseButtonRelease:
            action = object.actionAt(event.pos())
            if action is not None and action.text() in ('Before', 'After'):
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

