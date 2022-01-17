from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QListWidget, QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt

class PreferencesDialog(QDialog):
    def __init__(self, parent, todolists):
        super().__init__(parent)
        self.parent = parent

        self.setFixedSize(500, 400)

        dialogLayout = QGridLayout(self)

        # dialogLayout.addWidget(QListWidget(), 0, 0)
        self.todolistsList = QListWidget()
        self.todolistsList.setMaximumWidth(400)
        self.todolistsList.addItems(todolists)
        dialogLayout.addWidget(self.todolistsList, 0, 0)

        buttonColumn = QWidget()
        buttonColumn.setMinimumWidth(200)
        buttonColumnLayout = QVBoxLayout(buttonColumn)
        buttonColumnLayout.setAlignment(Qt.AlignmentFlag.AlignTop) 
    
        button_names = ['move up', 'move down', 'clear', 'rename', 'delete']

        for name in button_names:
            button = QPushButton(name)
            # button.clicked.connect(lambda checked, list_widget=self.todolistsList, action=name: self.parent.preferences_dialog_clicked(list_widget, action))
            button.clicked.connect(lambda checked, action=name: self.button_clicked(action))
            buttonColumnLayout.addWidget(button)

        buttonColumnLayout.setContentsMargins(0, 0, 0, 0)

        dialogLayout.addWidget(buttonColumn, 0, 1)


        # dialogLayout.addWidget(QLabel('Hello'), 0, 1)

    def button_clicked(self, action):
        self.parent.preferences_dialog_clicked(self.todolistsList.currentItem().text(), action)

    def update_list_widget(self, new_list, selected_item):
        self.todolistsList.clear()
        self.todolistsList.addItems(new_list)

        if selected_item:
            for i in range(self.todolistsList.count()):
                item = self.todolistsList.item(i)
                if item.text() == selected_item:
                    focused_item = item
                    break

            self.todolistsList.setCurrentItem(focused_item)

