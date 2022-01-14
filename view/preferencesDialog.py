from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QListWidget

class PreferenceDialog(QDialog):
    def __init__(self, parent, todolists):
        super().__init__(parent)

        dialogLayout = QGridLayout(self)

        # dialogLayout.addWidget(QListWidget(), 0, 0)
        todolistsList = QListWidget()
        todolistsList.addItems(todolists)
        dialogLayout.addWidget(todolistsList, 0, 0)

        dialogLayout.addWidget(QLabel('Hello'), 0, 1)

