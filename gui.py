import os
import sys
import configparser
from pdf_search import Searcher
from pdf_parser import parse
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox, QHBoxLayout, QGroupBox, QVBoxLayout, QLineEdit, QLabel


class App(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'SR PDF Searcher'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        self.config = configparser.ConfigParser()
        self.config_file = 'config.ini'
        self.read_config()
        self.searcher = Searcher(self.config['GENERAL']['RulebookLocation'])
        self.horizontal_groupbox = None
        self.content_area = None
        self.line_edit = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.create_layout()
        window_layout = QVBoxLayout()
        window_layout.addWidget(self.horizontal_groupbox, 1)
        window_layout.addWidget(self.content_area, 100)
        window_layout.setAlignment(self.content_area, Qt.AlignTop)
        self.setLayout(window_layout)

        self.show()

    def create_layout(self):
        self.horizontal_groupbox = QGroupBox("Enter the search query")
        layout = QHBoxLayout()
 
        self.line_edit = QLineEdit(self)
        layout.addWidget(self.line_edit)

        self.line_edit.editingFinished.connect(self.search)
 
        self.horizontal_groupbox .setLayout(layout)
        self.content_area = QLabel(self)

    def search(self):
        results = self.searcher.search(self.line_edit.text())
        text = ["Found {} results\n------------------------\n".format(len(results))]
        for term, result in results:
            content = []
            for t, p, c in [(r["title"], r["page"], r["content"].strip(' \t\n\r')) for r in result]:
                content.append("{} [{}] : {}".format(t, p, c))
            text.append("Word : {}\t Matches : {}\n#######\n{}\n#######".format(term, len(result), '\n'.join(content)))
        self.content_area.setText('\n'.join(text))

    def read_config(self):
        if not os.path.exists(self.config_file):
            self.config['GENERAL'] = {}
            self.config['GENERAL']['RulebookLocation'] = self.open_pdfdialog()
            with open(self.config_file, 'w') as confout:
                self.config.write(confout)
        self.config.read(self.config_file)

    def open_pdfdialog(self):
        message = "Not set up yet. Select directory containing PDF files to process. This may take up to 5 minutes"
        QMessageBox.question(self, "Process rulebooks", message, QMessageBox.Ok)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        directory_name = QFileDialog.getExistingDirectory(self, options=options)
        if directory_name:
            parse(directory_name)
            return directory_name

 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())