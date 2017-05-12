import os
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, NUMERIC
from whoosh.qparser import QueryParser
from whoosh.spelling import ListCorrector
from whoosh.highlight import UppercaseFormatter


class Searcher:
    def __init__(self, directory):
        self.pdf_folder = directory
        self.scope = 20
        self.terms = set()
        self.index_path = "index"
        self.common_terms = set()
        self.schema = Schema(
            title=TEXT(stored=True),
            path=TEXT(stored=True),
            page=NUMERIC(stored=True),
            content=TEXT(stored=True))
        self.ix = None
        self.index_files = False
        if not os.path.exists(self.index_path):
            os.mkdir(self.index_path)
            self.ix = create_in(self.index_path, self.schema)
            self.index_files = True
        else:
            self.ix = open_dir(self.index_path)
        self.writer = self.ix.writer()
        self.read()
        self.writer.commit()
        self.searcher = self.ix.searcher()
        self.corrector = ListCorrector(sorted(list(self.common_terms)))
        self.parser = QueryParser("content", self.ix.schema)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.searcher.close()

    def search(self, term):
        results = []
        suggestions = [term]+(self.corrector.suggest(term, limit=5))
        for t in suggestions:
            query = self.parser.parse(t)
            query_res = self.searcher.search(query, limit=100)
            query_res.fragmenter.maxchars = 3000
            query_res.fragmenter.surround = 1000
            query_res.formatter = UppercaseFormatter()
            results.append((t, query_res))
        return results

    def read(self):
        for root, dirs, files in os.walk(self.pdf_folder):
            for f in files:
                if '.pdf' in f.lower() and '.txt' in f.lower():
                    wf = os.path.join(root, f)
                    with open(wf, 'r', encoding='utf-8') as fin:
                        page = 1
                        print("Building index for {}".format(f))
                        lines = fin.readlines()
                        for l in lines:
                            [self.common_terms.add(i) for i in l.split(' ')]
                            if self.index_files:
                                if '\f' in l:
                                    page+=1
                                self.writer.add_document(title=f, content=l, path=wf, page=page)




