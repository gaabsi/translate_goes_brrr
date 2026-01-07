import os
import sys

import openai

from base_trad import BookTranslator
from batch_trad import BatchTranslator

API_KEY = os.getenv("OPENAI_API_KEY")
PROMPT = os.getenv("PROMPT")
EPUB_ORIGINAL = sys.argv[1]
FROM = int(sys.argv[2])
TO = int(sys.argv[3])
CSS_PATH = os.path.join(os.path.dirname(__file__), "epub.css")
MD_SAVE_PATH = os.path.expanduser(f"~/translate_goes_brrr/trad/md/{sys.argv[4]}.md")


bt = BookTranslator(prompt=PROMPT, model="gpt-4o", api_key=API_KEY)
manager = BatchTranslator(bt, max_tpm=60000)

manager.translate_epub_range(
    input_epub=EPUB_ORIGINAL,
    output_md=MD_SAVE_PATH,
    start_chap=FROM,
    end_chap=TO,
)
