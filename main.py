"""Place pdf in pdf/* and parse them using this file."""
import re
import os
import nltk
import shutil
import logging
import textract
from tempdir import tempfile

logging.basicConfig(level=logging.DEBUG)

def separate_sentences(txtfile):
    """Generates a list where every line is a sentence."""
    with open(txtfile, 'r') as fin:
        lines = fin.readlines()
        lines = '\n'.join(lines)
        sentences = nltk.sent_tokenize(lines)
        tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
        separated = []
        for t in tokenized_sentences:
            # expected amount of numbers for a text to be considered part of a table.
            numbers = re.findall(r'\d+', ' '.join(t))
            if len(numbers) > 5 and len(numbers) < 100:
                separated.append(' '.join(t))
        for count, sep in enumerate(separated):
            logging.debug("Matching %d ...", count)
            p = re.compile(r'[^¥\s]+.*?¥')
            matches = p.findall(sep)
            if len(matches) > 0:
                print(sep)
                print(matches)
        return '\n'.join(separated)


def named_entity_extraction(txtfile):
    """Performs NER on the passed txtfile."""
    with open(txtfile, 'r') as fin:
        lines = fin.readlines()
        lines = '\n'.join(lines)
        logging.debug("Tokenizing")
        sentences = nltk.sent_tokenize(lines)
        tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
        logging.debug("POS Tagging")
        tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
        chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)

        def extract_entity_names(t):
            entity_names = []
            if hasattr(t, 'label') and t.label:
                if t.label() == 'NE':
                    entity_names.append(' '.join([child[0] for child in t]))
                else:
                    for child in t:
                        entity_names.extend(extract_entity_names(child))
            return entity_names

        entity_names = []
        logging.debug("Extracting entity names")
        for tree in chunked_sentences:
            entity_names.extend(extract_entity_names(tree))

        return set(entity_names)


def parse_gundregelwerk(txtfile):
    """Parses the Grundregelwerk"""
    logging.info("Parsing Grundregelwerk from %s", txtfile)
    separate_sentences(txtfile)
    with open(txtfile, 'r') as fin:
        pass
        #lines = fin.readlines()
        #p = re.compile('*', re.IGNORECASE)
        #p.match(lines)

MAPPING = {
    'grundregelwerk' : parse_gundregelwerk
}

PAGES = {  # remember to substract 1 due to indexing starting at 0 !
    'grundregelwerk' : range(426, 474)
}

if __name__ == '__main__':
    for root, dirs, files in os.walk('pdf'):
        for f in files:
            logging.info("Found %s. Checking whether it's parseable ...", f)
            for s, m in MAPPING.items():
                if s in f.lower() and not '.txt' in f.lower():
                    logging.info("It is ! Looking for existing extractions ...")
                    file_pdf = os.path.join(root, f)
                    file_extraction = file_pdf+'.txt'
                    if os.path.exists(file_extraction):
                        logging.info("Extracted text found !")
                    else:
                        logging.info("No extraction found !")
                        logging.info("Starting extraction ... ( This may take a minute )")
                        with open(file_extraction, 'w') as fout:
                            text = textract.process(file_pdf).decode('utf-8')
                            fout.write(text)
                    m(file_extraction)
