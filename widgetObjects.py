from PyQt5 import QtGui
from PyQt5.QtGui import QColor, QMouseEvent, QPalette
from PyQt5.QtCore import QEvent, QSize, Qt
from PyQt5.QtWidgets import *

class Task(QCheckBox):
    def __init__(self, task_name):
        super().__init__(task_name)

        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

        self.taskRightClick = QMenu()
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

        # Header
        self.sectionHeader = self.SectionHeader(section_name)

        # Body
        self.sectionBody = QWidget()
        self.sectionBodyLayout = QVBoxLayout()
        self.sectionBodyLayout.setContentsMargins(20, 5, 20, 5)

        self.sectionBodyLayout.addWidget(QCheckBox('Quest'))
        self.sectionBody.setLayout(self.sectionBodyLayout)

        self.sectionRightClick = QMenu()
        self.sectionRightClick.addAction('Rename')
        self.sectionRightClick.addAction('Delete')

        # self.sectionHeader.mouseReleaseEvent = lambda event, section_right_click=sectionRightClick, toggle_icon=toggleIcon, section_body=sectionBody: self.sectionClicked(event=event, section_right_click=section_right_click, toggle_icon=toggle_icon, section_body=section_body, pos=event.globalPos())

        self.sectionLayout.addWidget(self.sectionHeader)
        self.sectionLayout.addWidget(self.sectionBody)
        self.setLayout(self.sectionLayout)

        self.sectionHeader.installEventFilter(self)

    def _toggle_section(self, toggle_icon, section_body):
        if section_body.isVisible():
            section_body.hide()
            toggle_icon.setText('▶')
            toggle_icon.setStyleSheet("color: white; padding-bottom: 5px")
        else:
            section_body.show()
            toggle_icon.setText('▼')

    def eventFilter(self, object, event):
        if event.type() == QMouseEvent.MouseButtonRelease:
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
        else:
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

        # def mouseReleaseEvent(self, e: QtGui.QMouseEvent) -> None:
        #     if e.button() == 1:
        #         self._toggle_section(kwargs['toggle_icon'], kwargs['section_body'])
        #     elif e.button() == 2:
        #         kwargs['section_right_click'].popup(kwargs['pos'])