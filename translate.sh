#!/bin/bash 

# Pour que le script tourne aussi bien en local que dans son conteneur 
if [ -d "/app" ]; then
    BASE_DIR="/app"
    PYTHON="python"
else
    BASE_DIR="$HOME/translation_goes_brrr"
    PYTHON="$BASE_DIR/venv/bin/python"
fi

OPENAI_API_KEY="$(cat "$BASE_DIR/api_key.txt")"  # Mettre la clé personnelle (obtenue comme indiqué dans le README)
PROMPT="$(cat "$BASE_DIR/context_prompt.txt")" # Context prompt qu'on veut donner à notre traduction (pas trop long sinon ça prend plus de tokens)
export OPENAI_API_KEY PROMPT

SRC_DIR="$BASE_DIR/src"

EPUB_NAME="Quoicoubeh" # Nom du livre qu'on veut écrire
INPUT_EPUB="$BASE_DIR/COI_original.epub" # Path du .epub en input (non-traduit)
OUTPUT_EPUB="$BASE_DIR/trad/epub/$EPUB_NAME.epub" # Path du .epub de sortie (traduit)
CHAP_START="1" # Premier chapitre à traduire
CHAP_END="2" # Dernier chapitre à traduire
COVER_PATH="$BASE_DIR/images/covers/COI_vol_1.png" # Cover qu'on veut donner au livre (.png)


$PYTHON "$SRC_DIR/main.py" "$INPUT_EPUB" "$CHAP_START" "$CHAP_END" "$EPUB_NAME"
$PYTHON "$SRC_DIR/mise_en_forme.py" "$EPUB_NAME" "$OUTPUT_EPUB" "$COVER_PATH"