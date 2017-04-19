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

    def search(self, term):
        result = []
        matches = self.fuzzySet.get(term)
        matches.extend([(1, term)])
        for t in sorted(matches, key=lambda v: v[0], reverse=True):
            for key, value in self.content.items():
                if t.lower() in value.lower():
                    result.append((key, value))
        top_ten = sorted(result, reverse=True)[10]
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
                        for l in lines:
                            self.fuzzySet.add(l)
                        content[f] = []
                        for i in range(len(lines) // self.scope + 1):
                            word_group = ' '.join(lines[i:i + self.scope])
                            content[f].append(word_group)
        return content



