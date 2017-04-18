import os
from fuzzywuzzy import process


class Searcher:
    def __init__(self, directory):
        self.pdf_folder = directory
        self.content = self.read(directory)

    def search(self, term):
        if len(term) < 10:
            return [(k, v) for k, v in self.content.items() if term.lower() in ' '.join(v).lower()]
        else:
            return [(k, process.extract(term, v)) for k, v in self.content.items()]

    def read(self, directory):
        content = {}
        for root, dirs, files in os.walk(directory):
            for f in files:
                if '.pdf' in f.lower() and '.txt' in f.lower():
                    with open(os.path.join(root, f), 'r', encoding='utf-8') as fin:
                        lines = fin.readlines()
                        content[f] = lines
        return content



