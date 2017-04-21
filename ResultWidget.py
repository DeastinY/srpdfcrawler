from PyQt5.QtWidgets import QWidget, QScrollArea, QSizePolicy, QVBoxLayout


class ResultWidget(QWidget):
    def __init__(self, parent=None):
        super(ResultWidget, self).__init__(parent=parent)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

    def add(self, widget):
        self.main_layout.addWidget(widget)

    def clear(self):
        layout = self.main_layout
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
