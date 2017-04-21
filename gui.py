import os
import sys
import configparser
from GroupWidget import GroupWidget
from ResultWidget import ResultWidget
from pdf_search import Searcher
from pdf_parser import parse
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox, \
    QHBoxLayout, QGroupBox, QVBoxLayout, QLineEdit, QLabel, QScrollArea


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
        window_layout.addWidget(self.horizontal_groupbox)
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
        self.content_area = ResultWidget(self)

    def search(self):
        results = []  # [ (term, [title, page, content], count ]
        for term, matches in self.searcher.search(self.line_edit.text()):
            hits = []
            count = 0
            search = [(match["title"], match["page"], match["content"].strip(' \t\n\r')) for match in matches]
            for title, page, content in search:
                hits.append((title, page, content))
                count += 1
            results.append((term, hits, count))
        self.content_area.clear()
        for term, hits, count in results:
            group_widget = GroupWidget(title="{} Matches : {}".format(count, term))
            content_layout = QVBoxLayout(group_widget)
            for title, page, content in hits:
                text = "############# {} [Page: {}]\n{}".format(title, page, content)
                content_layout.addWidget(QLabel(text))
            group_widget.set_content_layout(content_layout)
            self.content_area.add(group_widget)

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