import os
import sys

import openai

from scripts.base_trad import BookTranslator
from scripts.batch_trad import BatchTranslator

openai.api_key = os.getenv("OPENAI_API_KEY")
EPUB_ORIGINAL = sys.argv[1]
FROM = int(sys.argv[2])
TO = int(sys.argv[3])
CSS_PATH = os.path.join(os.path.dirname(__file__), "epub.css")
MD_SAVE_PATH = os.path.expanduser(f"~/gpt_ebook_translator/trad/md/{sys.argv[4]}.md")


PROMPT = """
 You are a translator (English to French).
 Translate fluently and idiomatically, preserving tone and structure. 
 I want your translation to be easily readable. 
 This is a fantasy webnovel, you must keep a very narrative tone in your translation.
 Use Markdown syntax: *italics*, **bold**, ## for titles.
 Do not translate proper nouns. 
 Keep ellipses and punctuation. 
 Return clean, fluent, structured Markdown.
 Make sure that you don't repeat yourself in your translations.
 """

bt = BookTranslator(prompt=PROMPT, model="gpt-4o")
manager = BatchTranslator(bt, max_tpm=60000)

manager.translate_epub_range(
    input_epub=EPUB_ORIGINAL,
    output_md=MD_SAVE_PATH,
    start_chap=FROM,
    end_chap=TO,
)
