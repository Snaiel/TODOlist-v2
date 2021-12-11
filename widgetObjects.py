from PyQt5 import QtGui
from PyQt5.QtGui import QColor, QMouseEvent, QPalette
from PyQt5.QtCore import QEvent, QSize, Qt, pyqtSlot
from PyQt5.QtWidgets import *


class Task(QCheckBox):
    def __init__(self, task_name):
        super().__init__(task_name)

        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

        self.taskRightClick = QMenu(self)
        self.taskRightClick.addAction('Rename')
        self.taskRightClick.addAction('Delete')

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        if e.button() == 1:
            self.click()
        if e.button() == 2:
            self.taskRightClick.popup(e.globalPos())

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
        type = action.text()
        print('add element', type)
        element_name, ok = QInputDialog.getText(self, f'add {type.lower()}', f'enter name of {type.lower()}')
        if not ok or element_name == '':
            return
        # self.sectionBody.sectionBodyLayout.addWidget(eval(f'{type}(element_name)'))

        element = eval(f'{type}(element_name)')
        self.sectionBody.sectionBodyLayout.addWidget(element)
        eval(f'element.{type.lower()}RightClick.triggered.connect(self.right_click_menu_clicked)')

    def delete_element(self, action):
        parent_widget = action.parentWidget().parentWidget()
        print(parent_widget)
        self.sectionBody.sectionBodyLayout.removeWidget(parent_widget)
        parent_widget.deleteLater()

    @pyqtSlot(QAction)
    def right_click_menu_clicked(self, action):
        print(action.text())

        switch_case_dict = {
            'Task': self.create_element,
            'Section': self.create_element,
            'Delete': self.delete_element
        }

        switch_case_dict[action.text()](action)


    def eventFilter(self, object, event):
        # print(object, event, event.type())
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

        if isinstance(object, self.SectionRightClick):
            print(object.menuAction().text())

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

            addMenu = self.addMenu('Add',)
            addMenu.addAction('Task')
            addMenu.addAction('Section')
            self.addAction('Rename')
            self.addAction('Delete')

