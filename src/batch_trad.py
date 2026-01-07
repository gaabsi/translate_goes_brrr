import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import tiktoken
from tqdm import tqdm


class BatchTranslator:
    def __init__(self, book_translator, max_tpm=30000, safety_margin=0.9):
        """
        Gère la traduction par lots en parallèle.

        Parametres :
        - book_translator : instance de BookTranslator
        - max_tpm (int): limite de tokens/minute (pour découpage)
        - safety_margin (float): % de marge pour ne pas saturer le quota
        """

        self.bt = book_translator
        self.max_tpm = max_tpm
        self.safety_margin = safety_margin

    def count_tokens(self, text):
        """
        Compte le nombre de token d'un chapitre.
        On les compte afin de ne pas envoyer trop de chapitres par batch.

        Parametres :
        - text (str) : test qu'on veut traduire

        Output :
        Nombre de token consommé par la requete.
        """

        enc = tiktoken.encoding_for_model(self.bt.model)
        return len(enc.encode(text))

    def batch_chapters(self, chap_texts):
        """
        Découpe les chapitres par batchs afin de ne pas dépasser la limite qu'on a fixé précédemment.
        Pour rappel on a max_tpm*safety_margin tokens max par minute.
        Donc pour notre model gpt-4o dans la doc on a un max de 60.000 tokens par minute.
        On aura donc des batchs qui seront >= 54.000 tokens.
        Cette marge de sécurité permet également d'inclure le context prompt qu'on injecte à chaque appel.

        Parametres :
        - chap_texts (dict) : dict sous forme {numéro du chapitre : contenu du chapitre}

        Output :
        - batches (liste de liste) : chaque liste est un batch, chaque batch contient n tuples (numero chapitre, contenu chapitre) avec n tq somme des tokens < max_tpm*safety_margin
        """

        batches, current_batch, current_tokens = [], [], 0

        for chap_num, text in chap_texts.items():
            tokens = self.count_tokens(text)

            if current_tokens + tokens > self.max_tpm * self.safety_margin:
                batches.append(current_batch)
                current_batch, current_tokens = [], 0
            current_batch.append((chap_num, text))
            current_tokens += tokens

        if current_batch:
            batches.append(current_batch)

        return batches

    def translate_in_batches(self, chap_texts, max_workers=os.cpu_count() - 1):
        """
        Traduit un dictionnaire de chapitres {chap_num: texte} par batchs parallèles.
        Retourne un dict {chap_num: traduction}.
        On met une barre de progression pour voir un peu où on en est dans la traduction.
        À la fin de chaque batch on met un sleep de 60s pour éviter les ratelimit.

        Parametres :
        - chap_texts (dict) : dictionnaire {numéro chapitre : contenu a traduire}
        - max_workers (int) : nombre de workers qui enverront des requêtes en même temps (ici le nombre de coeurs cpu -1 car tâche absolument pas gourmande en ressources)

        Output :
        - translations (dict) : dictionnaire {numéro chapitre : chapitre traduit}
        """

        batches = self.batch_chapters(chap_texts)
        translations = {}

        with tqdm(
            total=len(chap_texts), desc="Progression globale", unit="chap"
        ) as global_pbar:
            for batch_idx, batch in enumerate(batches, start=1):
                with ThreadPoolExecutor(
                    max_workers=min(max_workers, len(batch))
                ) as executor:
                    futures = {
                        executor.submit(self.bt.translate_chapter, text): chap_num
                        for chap_num, text in batch
                    }
                    for future in as_completed(futures):
                        chap_num = futures[future]
                        try:
                            translated = future.result()
                            translations[chap_num] = translated.strip()
                        except Exception as e:
                            print(e)
                        global_pbar.update(1)

                if batch_idx < len(batches):
                    time.sleep(60)

        return translations

    def translate_epub_range(
        self, input_epub, output_md, start_chap, end_chap, level=2
    ):
        """
        Pipeline complete de traduction par batch

        Parametres :
        - input_epub (str) : chemin du epub a traduire.
        - output_md (str) : chemin de là où on veut écrire le md temporaire (pas None par défaut car
          franchement vaut mieux supprimer un fichier après qu'avoir à repayer pour une traduction qu'on a déjà faite mdrrr)
        - start_chap (int) : chapitre par lequel on commence la traduction.
        - end_chap (int) : chapitre après lequel on arrête de traduire.
        - level (int) : niveau des titres dans le .md (ici tjr ##)

        Output :
        Ne retourne rien, écrit un markdown.
        Le markdown écrit est la traduction du epub qu'on a donné en input.
        """

        self.bt.extract_epub_to_markdown(input_epub, output_md)

        chap_texts = {}
        for chap_num in range(start_chap, end_chap + 1):
            chap_texts[chap_num] = self.bt.extract_chapter_by_index(
                output_md, chap_num, level=level
            )

        translations = self.translate_in_batches(chap_texts)

        with open(output_md, "w", encoding="utf-8") as f:
            for chap_num in sorted(translations.keys()):
                f.write(f"\n\n\\newpage\n\n{translations[chap_num]}\n")
