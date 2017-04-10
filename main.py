"""Place pdf in pdf/* and parse them using this file."""
import os
import shutil
import logging
from tempdir import tempfile
from PyPDF2 import PdfFileReader

logging.basicConfig(level=logging.DEBUG)

def remove_encryption(filename):
    """Tries to remove pdf-encryption using qpdf."""
    logging.warning("The PDF is encrypted ! Trying to remove encryption ...")
    # Things from the subprocess module don't rely on the shell unless you
    # explicitly ask for it and can accept a pre-split list of arguments,
    # making calling subprocesses much safer.
    # (If you really do need to split quoted stuff, use shlex.split() instead)
    from subprocess import check_call
    # Use try/finally to ensure our cleanup code gets run
    try:
        # There are a lot of ways to mess up creating temporary files in a way
        # that's free of race conditions, so just use mkdtemp() to safely
        # create a temporary folder that only we have permission to work inside
        # (We ask for it to be made in the same folder as filename because /tmp
        #  might be on a different drive, which would make the final overwrite
        #  into a slow "copy and delete" rather than a fast os.rename())
        tempdir = tempfile.mkdtemp(dir=os.path.dirname(filename))

        # I'm not sure if a qpdf failure could leave the file in a halfway
        # state, so have it write to a temporary file instead of reading from one
        temp_out = os.path.join(tempdir, 'qpdf_out.pdf')

        # Avoid the shell when possible and integrate with Python errors
        # (check_call() raises subprocess.CalledProcessError on nonzero exit)
        check_call(['qpdf', "--password=", '--decrypt', filename, temp_out])

        # I'm not sure if a qpdf failure could leave the file in a halfway
        # state, so write to a temporary file and then use os.rename to
        # overwrite the original atomically.
        # (We use shutil.move instead of os.rename so it'll fall back to a copy
        #  operation if the dir= argument to mkdtemp() gets removed)
        shutil.move(temp_out, filename)
        logging.warning('File Decrypted (qpdf)')
    finally:
        # Delete all temporary files
        shutil.rmtree(tempdir)

def parse_gundregelwerk(path):
    """Parses the Grundregelwerk"""
    logging.info("Parsing Grundregelwerk from %s", path)
    pdf = PdfFileReader(path)
    if pdf.isEncrypted:
        remove_encryption(path)
        pdf = PdfFileReader(path)
    for page_number in PAGES['grundregelwerk']:
        logging.debug("Extracting page %d", page_number)
        text = pdf.pages[page_number].extractText()

MAPPING = {
    'grundregelwerk' : parse_gundregelwerk
}

PAGES = {
    'grundregelwerk' : range(418, 424)
}

if __name__ == '__main__':
    for root, dirs, files in os.walk('pdf'):
        for f in files:
            logging.info("Found %s. Checking whether it's parseable ...", f)
            for s, m in MAPPING.items():
                if s in f.lower():
                    m(os.path.join(root, f))
