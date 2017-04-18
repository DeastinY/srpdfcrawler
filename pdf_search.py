import os
try:
    from cfuzzyset import cFuzzySet as FuzzySet
except ImportError:
    from fuzzyset import FuzzySet


class Searcher:
    def __init__(self, directory):
        self.pdf_folder = directory
        self.scope = 20
        self.fuzzySet = FuzzySet()
        self.content = self.read(directory)

    def search(self, term, fuzzy=True):
        result = []
        for key, value in self.content.items():
            for word_group in value:
                if fuzzy:
                    result.append(self.fuzzySet.get(term))
                elif term.lower() in word_group.lower():
                    result.append((key, word_group))
                else:
                    pass  #no result found
        return result

    def search_fuzzy(self, term):
        pass

    def read(self, directory):
        content = {}
        for root, dirs, files in os.walk(directory):
            for f in files:
                if '.pdf' in f.lower() and '.txt' in f.lower():
                    with open(os.path.join(root, f), 'r', encoding='utf-8') as fin:
                        lines = fin.readlines()
                        lines = ' '.join(lines)
                        lines = lines.split(' ')
                        for i in range(len(lines)//self.scope+1):
                            word_group = ' '.join(lines[i:i+self.scope])
                            self.fuzzySet.add(word_group)
                            content[f] = word_group
        return content



