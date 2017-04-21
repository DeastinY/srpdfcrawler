"""Place pdf in pdf/* and parse them using this file."""
import re
import io
import os
import json
import nltk
import logging
import textract

logging.basicConfig(level=logging.DEBUG)
nltk.data.path.append('.'+os.sep+'nltk_data')


def separate_sentences(tokenized_sentences):
    """Generates a list where every line is a sentence."""
    separated = []
    for t in tokenized_sentences:
        # expected amount of numbers for a text to be considered part of a table.
        numbers = re.findall(r'\d+', ' '.join(t))
        if len(numbers) > 5 and len(numbers) < 100:
            separated.append(' '.join(t))
    return separated


def find_tables(sentences):
    """Generates a list of potential table entries.
    INPUT : Output of separated_sentences
    OUTPUT : List of matched regex"""
    tables = []
    for count, sep in enumerate(sentences):
        #logging.debug("Searching %d/%d ...", count, len(sentences))
        if not 'preis' in sep.lower():
            continue
        pattern = re.compile(r'[^¥\s]+.*?¥')
        matches = pattern.findall(sep)
        if len(matches) > 0:
            tables.append(matches)
    return tables


def named_entity_extraction(chunked_sentences):
    """Performs NER on the passed txtfile."""
    def extract_entity_names(tree):
        """Extractes the NE tags from the tree."""
        entity_names = []
        if hasattr(tree, 'label') and tree.label:
            if tree.label() == 'NE':
                entity_names.append(' '.join([child[0] for child in tree]))
            else:
                for child in tree:
                    entity_names.extend(extract_entity_names(child))
        return entity_names

    entity_names = []
    logging.debug("Extracting entity names")
    for tree in chunked_sentences:
        entity_names.extend(extract_entity_names(tree))

    return set(entity_names)


def extract_weapons(txtfile, tokenized_sentences, write_temp=True):
    """Tries to extract weapon stats from tables."""
    logging.info("Extracting weapons")
    separated = separate_sentences(tokenized_sentences)
    tables = find_tables(separated)
    if write_temp:
        file_name = txtfile.split(".pdf.txt")[0] + "_weapons.txt"
        with io.open(file_name, 'w', encoding='utf-8') as fout:
            json.dump(tables, fout, sort_keys=False, indent=4, ensure_ascii=False)

def process(txtfile):
    """Processes a rulebook."""
    logging.info("Processing %s", txtfile)
    with open(txtfile, 'r', encoding='utf-8') as fin:
        lines = fin.readlines()
        lines = '\n'.join(lines)
        logging.debug("Tokenizing")
        sentences = nltk.sent_tokenize(lines)
        tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
        extract_weapons(txtfile, tokenized_sentences)
        #logging.debug("POS Tagging")
        #tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
        #chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)
        #named_entities = named_entity_extraction(chunked_sentences)


def extract_text(file_extraction, file_pdf):
    logging.info("Extracting text ... ( This may take a minute )")
    with open(file_extraction, 'w', encoding='utf-8') as fout:
        text = textract.process(file_pdf).decode('utf-8')
        fout.write(text)


def parse(directory):
    for root, dirs, files in os.walk(directory):
        for f in files:
            if '.pdf' in f.lower() and '.txt' not in f.lower():
                logging.info("Checking whether an extraction for %s exists ...", f)
                file_pdf = os.path.join(root, f)
                file_extraction = file_pdf+'.txt'
                if os.path.exists(file_extraction):
                    logging.info("Extraction found !")
                else:
                    logging.info("No extraction found !")
                    extract_text(file_extraction, file_pdf)
                process(file_extraction)


if __name__ == '__main__':
    parse('pdf')
