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
        self.horizontal_recommendations = None
        self.recommendations = None
        self.content_area = None
        self.scroll_area = None
        self.utility_label = None
        self.line_edit = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.create_layout()
        window_layout = QVBoxLayout()
        window_layout.addWidget(self.horizontal_groupbox, 1)
        window_layout.addWidget(self.scroll_area, 100)
        window_layout.setAlignment(self.scroll_area, Qt.AlignTop)
        self.setLayout(window_layout)

        self.show()

    def create_layout(self):
        self.horizontal_groupbox = QGroupBox("Enter the search query")
        layout = QVBoxLayout()
        self.line_edit = QLineEdit(self)
        layout.addWidget(self.line_edit)
        self.line_edit.editingFinished.connect(self.search)
        self.recommendations = QLabel("Other recommendations: [Currently in development]")
        layout.addWidget(self.recommendations)
        self.horizontal_groupbox.setLayout(layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setMinimumSize(600, 400)  # TODO: Replace by proper scaling

        self.content_area = ResultWidget(self.scroll_area)

        self.scroll_area.setWidget(self.content_area)


    def search(self):
        results = []  # [ (term, [title, page, content], count ]
        extended_matches = self.searcher.search(self.line_edit.text())
        if len(extended_matches) == 0:
            return
        terms = [m[0] for m in extended_matches]
        self.recommendations.setText(" ".join(terms[1:]))
        term, matches = extended_matches[0]
        hits = []
        search = [(match["title"], match["page"], match.highlights("content")) for match in matches]
        for title, page, content in search:
            hits.append((title, page, content))
        self.update_results(hits)

    def update_results(self, hits):
        self.content_area.clear()
        books = {}
        for title, page, content in hits:
            if not title in books:
                books[title] = []
            books[title].append((page, content))
        for b in books.keys():
            group_widget = GroupWidget(title="{}\t{} Matches".format(b, len(books[b])))
            content_layout = QVBoxLayout(group_widget)
            for t in sorted(books[b]):
                label = QLabel("Page: {}\n{} ".format(*t))
                label.setWordWrap(True)
                content_layout.addWidget(label)
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
    print("Loading language processing toolkit ...")
    import nltk
    for dl in ["averaged_perceptron_tagger", "maxent_ne_chunker", "punkt"]:
        nltk.download(dl, download_dir='nltk_data')
    print("Done")
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())