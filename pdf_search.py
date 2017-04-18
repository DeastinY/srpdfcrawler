import os
try:
    from cfuzzyset import cFuzzySet as FuzzySet
except ImportError:
    from fuzzyset import FuzzySet


class Searcher:
    def __init__(self, directory):
        self.pdf_folder = directory
        self.scope = 20
        self.fuzzySets = {}
        self.content = self.read(directory)

    def search(self, term):
        result = []
        for key, value in self.fuzzySets.items():
            result.append((key, value.get(term)))
        print(len(result))
        top_ten = sorted(result, key=lambda v: v[1][0], reverse=True)[10]
        print(top_ten)
        return top_ten

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
                        print("Building fuzzy dict for {}".format(f))
                        self.fuzzySets[f] = FuzzySet()
                        for i in range(len(lines) // self.scope + 1):
                            word_group = ' '.join(lines[i:i + self.scope])
                            print(word_group)
                            self.fuzzySets[f].add(word_group)
        return content



