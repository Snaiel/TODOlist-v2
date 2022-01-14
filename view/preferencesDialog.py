from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QListWidget, QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt

class PreferenceDialog(QDialog):
    def __init__(self, parent, todolists):
        super().__init__(parent)

        self.setFixedSize(500, 400)

        dialogLayout = QGridLayout(self)

        # dialogLayout.addWidget(QListWidget(), 0, 0)
        todolistsList = QListWidget()
        todolistsList.setMaximumWidth(400)
        todolistsList.addItems(todolists)
        dialogLayout.addWidget(todolistsList, 0, 0)

        buttonColumn = QWidget()
        buttonColumn.setMinimumWidth(200)
        buttonColumnLayout = QVBoxLayout(buttonColumn)
        buttonColumnLayout.setAlignment(Qt.AlignmentFlag.AlignTop) 
    
        button_names = ['move up', 'move down', 'rename', 'delete']

        for name in button_names:
            button = QPushButton(name)
            buttonColumnLayout.addWidget(button)

        buttonColumnLayout.setContentsMargins(0, 0, 0, 0)

        dialogLayout.addWidget(buttonColumn, 0, 1)


        # dialogLayout.addWidget(QLabel('Hello'), 0, 1)

