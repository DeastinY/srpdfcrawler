"""Place pdf in pdf/* and parse them using this file."""
import os
import sys
import sqlite3
import nltk
from tqdm import tqdm
import logging
import textract
import configparser
from pathlib import Path

logging.basicConfig(level=logging.INFO)
# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    APPLICATION_PATH = os.path.dirname(sys.executable)
elif __file__:
    APPLICATION_PATH = os.path.dirname(__file__)
PATH = APPLICATION_PATH
PATH_DATA = Path(PATH) / 'data'
PATH_DATA.mkdir(exist_ok=True)
FILE_DB = PATH_DATA / "data.db"


def load_db(path_rulebooks):
    if not FILE_DB.exists():
        get_pdf(path_rulebooks)
        generate_db()
        for f in PATH_DATA.iterdir():
            if f != FILE_DB:
                f.unlink()


def extract_text(file_extraction, file_pdf):
    logging.info(f"Extracting text from {file_pdf} ... ( This may take a minute or two.)")
    with file_extraction.open("w", encoding="utf-8") as fout:
        fout.write(textract.process(str(file_pdf)).decode('utf-8'))
    logging.info(f"Saved extraction to {file_extraction}")


def generate_db():
    """Generates a sqlite database from the extracted txt files."""
    con = sqlite3.connect(str(FILE_DB))
    cur = con.cursor()
    logging.info("Creating Tables")
    cur.execute(r"CREATE TABLE IF NOT EXISTS TEXT("
                "ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
                "BOOK INTEGER NOT NULL,"
                "PAGE INTEGER NOT NULL,"
                "CONTENT STRING NOT NULL)")
    cur.execute(r"CREATE TABLE IF NOT EXISTS BOOKS("
                "ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
                "NAME STRING NOT NULL)")
    logging.info("Filling Database")
    books = []
    for f in tqdm(PATH_DATA.iterdir()):
        if 'txt' in f.name:
            name = f.name.split('.')[0]
            name_id = -1
            if not name in books:
                books.append(name)
                name_id = len(books)-1
            else:
                name_id = books.index(books)
            lines = f.read_text(encoding="utf-8")
            pages = lines.split('\f')
            for i, p in enumerate(pages):
                cur.execute("INSERT INTO TEXT (BOOK, PAGE, CONTENT) VALUES (?, ?, ?)", (name_id, i, p))
    for i, b in enumerate(books):
        cur.execute("INSERT INTO BOOKS (ID, NAME) VALUES (?, ?)", (i, b))
    con.commit()
    con.close()


def get_pdf(path_rulebooks):
    """
    Creates text files from PDF files and gathers them locally.
    """
    logging.info(f"Getting PDF files from {path_rulebooks}")
    for f in Path(path_rulebooks).iterdir():
        if '.pdf' in str(f).lower() and '.txt' not in str(f).lower():
            logging.debug(f"Checking whether an extraction for {f} exists ...")
            file_extraction = PATH_DATA / (f.name+'.txt')
            if file_extraction.exists():
                logging.debug("Extraction found !")
            else:
                logging.debug("No extraction found !")
                extract_text(file_extraction, f)


if __name__ == '__main__':
    logging.error("Execute this through gui.py")