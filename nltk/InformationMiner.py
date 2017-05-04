import os
import json
import nltk
import numpy
import pickle
import logging
import textract
import pos_tagger
import time

logging.basicConfig(level=logging.DEBUG)


class InformationMiner():
    def __init__(self, text, outdir="output", outfile="output", force_create=False):
        self.outdir = outdir
        self.outfile = outfile
        self.force_create = force_create
        self.tokens = None
        self.pos = None
        self.chunk = None
        self.text = text
        self.process()

    def process(self, text=None):
        logging.info("Start processing text")
        start = time.time()
        self.text = text if text else self.text
        self.tokens = self.tokenize()
        self.pos = self.tag_pos()
        self.chunk = self.ne_chunk()
        self.ne = self.extract_entity_names()
        stop = time.time()
        logging.info("Processing finished in {:.2f} s".format(stop-start))

    def tokenize(self):
        return self.exec_cached_func("Tokenizing text",
                                     "Creating new tokens",
                                     self.text,
                                     '01_token_',
                                     lambda d: nltk.word_tokenize(d, 'german'),
                                     False)

    def ne_chunk(self):
        return self.exec_cached_func("Chunking POS",
                                "Creating new chunks. This can take some time ...",
                                self.pos,
                                '03_chunk_',
                                lambda d: nltk.ne_chunk(self.pos),
                                True)

    def tag_pos(self):
        return self.exec_cached_func("POS tagging tokens",
                         "Creating new POS tags. This can take some time ...",
                         self.tokens,
                         '02_pos_',
                         lambda d: pos_tagger.tag(d),
                         False)

    def extract_entity_names(self):
        return self.exec_cached_func("Extracting entity names",
                                     "Searching for named entities",
                                     self.chunk,
                                     '04_ne_',
                                     self.extract_recurse,
                                     False)

    def extract_recurse(self, tree):
        entity_names = []
        if hasattr(tree, 'label') and tree.label():
            for child in tree:
                entity_names.extend(self.extract_recurse(child))
        else:
            if 'NE' in tree[1]:
                entity_names.append(tree[0])

        return entity_names

    #######################################Util Functions Down Here #######################################

    def get_file(self, prefix, binary=False):
        outfile = os.path.join(self.outdir, prefix+self.outfile)
        outfile += '.pickle' if binary else '.json'
        return outfile

    def save(self, data, prefix='', binary=False):
        file = self.get_file(prefix, binary)
        if os.path.exists(file) and not self.force_create:
            logging.warning("Did not write {}. Already exists and overwrite is disabled.".format(file))
        else:
            logging.info("Writing {}".format(file))
            if binary:
                with open(file, 'wb') as fout:
                    pickle.dump(data, fout, protocol=3)
            else:
                with open(file, 'w') as fout:
                    json.dump(data, fout)

    def get_cached(self, prefix, binary):
        file = self.get_file(prefix, binary)
        if os.path.exists(file) and not self.force_create:
            if binary:
                with open(file, 'rb') as fin:
                    return pickle.load(fin)
            else:
                with open(file, 'r') as fin:
                    return json.load(fin)

    def exec_cached_func(self, log_msg, log_msg_create, data, prefix, func, binary):
        logging.info(log_msg)
        cached = self.get_cached(prefix, binary)
        if not cached:
            logging.info(log_msg_create)
            res = func(data)
            self.save(res, prefix, binary)
        return cached if cached else res


if __name__ == '__main__':
    def get_text():
        infile = 'input.txt'
        if os.path.exists(infile):
            logging.info("Reading file from disk.")
            with open(infile, 'r') as fin:
                text = fin.readlines()
        else:
            logging.info("Creating new file from PDF.")
            text = textract.process('/home/ric/Nextcloud/rpg/shadowrun/rulebooks/Shadowrun_5_Grundregelwerk.pdf').decode('utf-8')
            with open(infile, 'w') as fout:
                fout.writelines(text)
        return text


    #Annotator("\n".join(get_text()))
    Annotator("Peter ist ein großer Junge. Er kauft bei dem großen Supermarkt Tedi schon ganz alleine eine Frisbee.", outfile='short_test', force_create=True)
