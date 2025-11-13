import os
import subprocess
import sys

import pypandoc

CSS_PATH = os.path.join(os.path.dirname(__file__), "epub.css")
TITLE = sys.argv[1]
OUTPUT_FILE = sys.argv[2]
COVER = sys.argv[3]

convert_args = [
    "--standalone",
    "--toc",
    f"--metadata=title:{TITLE}",
    f"--css={CSS_PATH}",
]

pypandoc.convert_file(
    os.path.expanduser(f"~/gpt_ebook_translator/trad/md/{TITLE}.md"),
    to="epub",
    format="markdown",
    outputfile=OUTPUT_FILE,
    extra_args=convert_args,
)

subprocess.run(
    f"ebook-meta '{OUTPUT_FILE}' --cover={COVER}",
    shell=True,
)
