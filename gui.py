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
        self.readConfig()
        self.searcher = Searcher(self.config['GENERAL']['RulebookLocation'])
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.createLayout()
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox, 1)
        windowLayout.addWidget(self.contentArea, 100)
        windowLayout.setAlignment(self.contentArea, Qt.AlignTop)
        self.setLayout(windowLayout)

        self.show()

    
    def createLayout(self):
        self.horizontalGroupBox = QGroupBox("Enter the search query")
        layout = QHBoxLayout()
 
        self.lineEdit = QLineEdit(self)
        layout.addWidget(self.lineEdit)

        self.lineEdit.editingFinished.connect(self.search)
 
        self.horizontalGroupBox.setLayout(layout)
        self.contentArea = QLabel(self)


    def search(self):
        print('Search started')
        results = self.searcher.search(self.lineEdit.text())
        text = ["Found {} results\n------------------------\n".format(len(results))]
        #text.extend([s[0]+" : \t"+' '.join(s[1]) for s in results])
        self.contentArea.setText('\n'.join(text))
        print('Search done')

    def readConfig(self):
        if not os.path.exists(self.config_file):
            self.config['GENERAL'] = {}
            self.config['GENERAL']['RulebookLocation'] = self.openPdfDialog()
            with open(self.config_file, 'w') as confout:
                self.config.write(confout)
        self.config.read(self.config_file)

    def openPdfDialog(self):    
        QMessageBox.question(self, "Process rulebooks", "Not set up yet. Select directory containing PDF files to process. This may take up to 5 minutes", QMessageBox.Ok)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        directoryName = QFileDialog.getExistingDirectory(self, options=options)
        if directoryName:
            parse(directoryName)
            return directoryName

 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())