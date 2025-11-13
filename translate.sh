export OPENAI_API_KEY="ma clé personnelle" #Mettre la clé personnelle (obtenue comme indiqué dans le README)

PYTHON_PATH="$HOME/gpt_ebook_translator/.venv/bin/python" 
MAIN_PATH="$HOME/gpt_ebook_translator/translation_scripts/main.py"
MISE_EN_FORME_PATH="$HOME/gpt_ebook_translator/translation_scripts/mise_en_forme.py"

EPUB_NAME="The Hanged Man" #Nom du livre qu'on veut écrire
INPUT_EPUB="$HOME/gpt_ebook_translator/original.epub" #Path du .epub en input (non-traduit)
OUTPUT_EPUB="$HOME/gpt_ebook_translator/trad/epub/$EPUB_NAME.epub" #Path du .epub de sortie (traduit)
CHAP_START="1" #Premier chapitre à traduire
CHAP_END="1000" #Dernier chapitre à traduire
COVER_PATH="$HOME/gpt_ebook_translator/images/covers/quoicoubeh.png" #Cover qu'on veut donner au livre (.png)


$PYTHON_PATH $MAIN_PATH "$INPUT_EPUB" "$CHAP_START" "$CHAP_END" "$EPUB_NAME"
$PYTHON_PATH $MISE_EN_FORME_PATH "$EPUB_NAME" "$OUTPUT_EPUB" "$COVER_PATH"