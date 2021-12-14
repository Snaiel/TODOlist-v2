from PyQt5 import QtGui
from PyQt5.QtGui import QColor, QMouseEvent, QPalette
from PyQt5.QtCore import QEvent, QObject, QSize, Qt, pyqtSlot
from PyQt5.QtWidgets import *


class Task(QCheckBox):
    def __init__(self, task_name):
        super().__init__(task_name)

        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

        self.taskRightClick = self.TaskRightClick(self)
        self.taskRightClick.insert_menu.installEventFilter(self)
        self.taskRightClick.triggered.connect(self.right_click_menu_clicked)
        # self.taskRightClick.mouseReleaseEvent = lambda event: print(event)

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

        # Prevent menu closing when selecting 'Before'/ 'After'
        if event is not None and event.type() == QMouseEvent.MouseButtonPress:
            # print(object, event)
            # print('hello')
            object.actionAt(event.pos()).trigger()
            return True
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
    def __init__(self, section_name):
        super().__init__()

        self.sectionLayout = QVBoxLayout()
        self.sectionLayout.setContentsMargins(0, 0, 0, 0)

        self.sectionHeader = self.SectionHeader(section_name)
        self.sectionBody = self.SectionBody()

        self.sectionRightClick = self.SectionRightClick(self)

        self.sectionLayout.addWidget(self.sectionHeader)
        self.sectionLayout.addWidget(self.sectionBody)
        self.setLayout(self.sectionLayout)

        self.sectionBody.hide()

        self.sectionRightClick.insert_menu.installEventFilter(self)
        self.sectionRightClick.triggered.connect(self.right_click_menu_clicked)

        # self.sectionRightClick.installEventFilter(self)
        self.sectionHeader.installEventFilter(self)

    def _toggle_section(self, toggle_icon, section_body):
        if section_body.isVisible():
            section_body.hide()
            toggle_icon.setText('▶')
            toggle_icon.setStyleSheet("color: white; padding-bottom: 5px")
        else:
            section_body.show()
            toggle_icon.setText('▼')

    def create_element(self, action):
        print(action.parentWidget().parentWidget().parentWidget())
        ## preventing double creation
        if action.parentWidget().title() == 'Insert' and isinstance(action.parentWidget().parentWidget().parentWidget(), QScrollArea):
            return
        elif action.parentWidget().title() == 'Insert' and action.parentWidget().parentWidget().parentWidget() is self:
            return
        elif action.parentWidget().title() == 'Add' and action.parentWidget().parentWidget().parentWidget() is not self:
            return

        creation_type = action.parentWidget().title()
        element_type = action.text()
        print(creation_type, element_type)

        element_name, ok = QInputDialog.getText(self, f'{creation_type.lower()} {element_type.lower()}', f'enter name of {element_type.lower()}')
        if not ok or element_name == '':
            return

        element = eval(f'{element_type}(element_name)')

        # parent_element = eval(f"action{'.parentWidget()'*4}")
        # print(parent_element.sectionHeader.sectionName.getText())

        if creation_type == 'Insert':
            index = self.sectionBody.sectionBodyLayout.indexOf(eval(f"action{'.parentWidget()'*3}"))

            insert_position = 0 if action.parentWidget().parentWidget().insert_menu.actions()[3].isChecked() is True else 1

            self.sectionBody.sectionBodyLayout.insertWidget(index + insert_position, element)
        else:
            self.sectionBody.sectionBodyLayout.addWidget(element)

        # Listen for when an action in the element's menu is triggered
        eval(f'element.{element_type.lower()}RightClick.triggered.connect(self.right_click_menu_clicked)')





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
            switch_case_dict[action.text()](action)

    def eventFilter(self, object, event):
        # print(object, event, event.type())

        ## Toggle visibility of section body when the header is clicked
        if isinstance(object, self.SectionHeader) and event.type() == QMouseEvent.MouseButtonRelease:
            if event.button() == 1:
                if self.sectionBody.isVisible():
                    self.sectionBody.hide()
                    self.sectionHeader.toggleIcon.setText('▶')
                    self.sectionHeader.toggleIcon.setStyleSheet("color: white; padding-bottom: 5px")
                else:
                    self.sectionBody.show()
                    self.sectionHeader.toggleIcon.setText('▼')

            elif event.button() == 2:
                self.sectionRightClick.popup(event.globalPos())
            return True

        # if isinstance(object, self.SectionRightClick):
        #     print(object.menuAction().text())

        # Prevent menu from closing when changing 'Placement' option
        if isinstance(object, QMenu):
            if event.type() == QMouseEvent.MouseButtonPress:
                object.actionAt(event.pos()).trigger()
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

