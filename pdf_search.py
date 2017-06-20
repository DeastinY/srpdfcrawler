import os
import sys
import sqlite3
import logging
from tqdm import tqdm
from pathlib import Path
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, NUMERIC
from whoosh.qparser import QueryParser
from whoosh.spelling import ListCorrector
from whoosh.highlight import UppercaseFormatter

logging.basicConfig(level=logging.INFO)
if getattr(sys, 'frozen', False):
    APPLICATION_PATH = os.path.dirname(sys.executable)
elif __file__:
    APPLICATION_PATH = os.path.dirname(__file__)
PATH = APPLICATION_PATH
PATH_DATA = Path(PATH) / 'data'
FILE_DB = PATH_DATA / "data.db"


class Searcher:
    def __init__(self):
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
            query_res.fragmenter.maxchars = 300
            query_res.fragmenter.surround = 100
            query_res.formatter = UppercaseFormatter()
            results.append((t, query_res))
        return results

    def read(self):
        logging.info("Indexing")
        con = sqlite3.connect(str(FILE_DB))
        cur = con.cursor()
        cur.execute(r"SELECT BOOKS.NAME, PAGE, CONTENT "
                    r"FROM TEXT, BOOKS "
                    r"WHERE BOOK = BOOKS.ID "
                    r"ORDER BY BOOKS.NAME, PAGE")
        for row in tqdm(cur):
            book, page, content = row
            book, page, content = str(book), str(page), str(content)
            for i in content.split(' '):
                self.common_terms.add(i)
            if self.index_files:
                self.writer.add_document(title=book, content=content, path=book, page=page)




