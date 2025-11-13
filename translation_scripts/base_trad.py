import os
import re
import time

import ebooklib
import pypandoc
from bs4 import BeautifulSoup, NavigableString, Tag
from ebooklib import epub
from openai import OpenAI


class BookTranslator:
    def __init__(
        self, prompt, model="gpt-4o", css_path=None, temp_md_path=None, delay=2
    ):
        self.prompt = prompt
        self.model = model
        self.css_path = css_path
        self.temp_md_path = temp_md_path or os.path.join(os.getcwd(), "temp.md")
        self.delay = delay
        self.client = OpenAI()

    def extract_epub_to_markdown(self, epub_path, output_md_path):
        """
        Prend un livre au format epub (lisible sur l'application livres).
        Retourne le même livre mais en markdown.
        """
        markdown_content = []
        book = epub.read_epub(epub_path)

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), features="xml")
                for tag in soup.find_all(["h1", "h2", "h3", "h4", "p"]):
                    if tag.name.startswith("h"):
                        level = int(tag.name[1])
                        markdown_content.append(
                            f"\n{'#' * level} {tag.get_text().strip()}\n"
                        )
                    elif tag.name == "p":
                        text = ""
                        for child in tag.children:
                            if isinstance(child, Tag):
                                if child.name in ("b", "strong"):
                                    text += f"**{child.get_text()}**"
                                elif child.name in ("i", "em"):
                                    text += f"*{child.get_text()}*"
                                else:
                                    text += child.get_text()
                            elif isinstance(child, NavigableString):
                                text += str(child)
                        markdown_content.append(text.strip() + "\n")

        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_content))

    def extract_chapter_by_index(self, md_path, chapter_number, level=2):
        """
        Prend un fichier markdown (un livre dans notre cas) et extrait un chapitre en particulier.
        Selon la mise en page du markdown en question le niveau peut changer.
        Ici on avait des titres de niveau 2 (##).
        """
        with open(md_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        heading_prefix = "#" * level + " "
        chapter_idx = 0
        in_chapter = False
        content = []

        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith(heading_prefix):
                chapter_idx += 1
                if chapter_idx == chapter_number:
                    in_chapter = True
                    content.append(line)
                    continue
                elif in_chapter and chapter_idx > chapter_number:
                    break
            elif in_chapter:
                content.append(line)

        return "".join(content)

    def translate_chapter(self, text):
        """
        Prend du texte en entrée, un prompt additionnel.
        Envoie la requête ainsi composée via appel API.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": text},
            ],
        )
        traduction = response.choices[0].message.content

        return traduction
