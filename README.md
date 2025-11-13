# gpt_ebook_translator

## Contexte
Ce projet a été inspiré par ma récente découverte d'un webnovel chinois.  
Après avoir regardé les premiers épisodes de l'animé **Lord Of The Mysteries**, j'ai eu envie de commencer à lire le webnovel.  
Cependant j'ai très vite vu que les tranductions fanmade s'arrêtaient tôt dans leurs parutions.  
J'ai donc cherché si le webnovel était disponible sur internet et j'ai trouvé sa version originale (en mandarin) et une seconde en anglais.  
Malheureusement je ne parle pas le mandarin et je ne me sentais pas de lire 1500+ chapitres dans la langue de Shakespeare alors j'ai eu l'idée de ce projet. 

Pour les curieux, voici le trailer de l'animé :  

<p align="center">
  <a href="https://youtu.be/cbdDMWAuHks?si=0Xe5hF28gJ_pu6Xc">
    <img src="https://img.youtube.com/vi/cbdDMWAuHks/0.jpg" alt="Trailer Crunchyroll">
  </a>
</p>

## Fonctionnement
J'ai donc développé une solution qui exploite l'API de ChatGPT d'OpenAI pour effectuer la traduction de l'anglais vers le français de manière automatique (et relativement qualitative par rapport à d'autres modèles disponibles sur Hugging Face).  
La solution prend en entrée un ebook au format .epub et ressort un ebook au format .epub également.  
Ceci afin de rendre l'objet fini lisible par l'application "Livres" native sur iPhone.  

### Modèle de base 
La pipeline s'articule ainsi : 
- le livre en .epub est transformé en .md 
- on spécifie quels chapitres on veut traduire
- on envoie chaque chapitre non traduit accompagnés d'un prompt au modèle 
- on récupère la réponse traduite qu'on stocke 
- ... on itère jusqu'a traduire tous les chapitres voulus ...
- on prend tous les chapitres traduis qu'on assemble selon un style défini et on retransforme le tout en .epub  
![schema](/images/schema/schema.png)

### Traduction séquentielle Vs parallèlisée
Pour éviter un traitement séquentiel — c’est-à-dire la traduction d’un chapitre après l’autre — et donc un temps de traduction total qui aurait cette forme :   
 
On peut donc généraliser notre temps de traduction unitaire en :  
$$
\text{Temps total} = \text{nombre de chapitres} \times \text{temps par chapitre}
$$
*Supposons qu'un appel API pour une traduction d'un chapitre prenne ≃ 1.5 minute.*   
Pour 10 chapitres on passe déjà 15 minutes de temps de traduction.  

Là où, en parallèlisant, on peut diviser ce temps de calcul et obtenir un temps total de traduction qui prend cette forme : 
$$
\text{Temps total} = \frac{\text{nombre de chapitres} \times \text{temps par chapitre}}{\text{nombre de workers}}
$$
Il est donc bien plus efficace de paralléliser les traductions - c'est-à-dire travailler en même temps plutôt qu'un après l'autre.  

## Contenu du projet 
```text
gpt_ebook_translator/ 
├── images/
│   ├── schema/
│   │   └── schema_glo.png      #Schéma expliquant la pipeline complète
│   └── covers/                 #Dossier pour stocker les couvertures d'ebooks (optionnel mais c'est vraiment joli)
├── .gitignore                  #Fichiers à ignorer par Git
├── README.md                   #Ce document
├── translation_scripts/        #Dossier qui contient les scripts python de traduction
    ├── base_trad.py            #Script qui construit le squelette de la traduction par appel API
    ├── batch_trad.py           #Script qui parallèlise la traduction et veille a ne pas dépaser le quota d'appel API
    └── main.py                 #Script d'orchestration de la traduction
├── postprocessing              #Dossier relatif à la mise en forme de l'output final
    ├── epub.css                #Contient les styles de mise en forme de l'output
    └── mise_en_forme.py        #Script de mise en forme final pour un output aux petits oignons
├── requirements.txt            #Pour répliquer l'env
└── translate.sh                #Script shell pour lancer l’ensemble de la pipeline
```

Il n'y a malheureusement aucun fichier d'input ou d'output dans ce repo afin de respecter les droits d'auteur.  
Je vous fait confiance pour trouver les bons fichiers d'input ;) 

## Prérequis
Pour fonctionner il faut obtenir une clé API sans quoi on ne pourra pas requêter le modèle.   
Pour ce faire voici la démarche : 
- créer un compte ou se connecter au [portail API](https://platform.openai.com/account/api-keys)
- cliquer sur **“Create new secret key”** pour générer une nouvelle clé (en haut à droite)
- copier la clé créée (gardez-la au chaud pour la partie suivante où je vous explique comment l'utiliser)
- recharger le compte de quelques dollars pour pouvoir requêter l'API sur ce [portail](https://platform.openai.com/settings/organization/billing/overview)
  >  *À titre indicatif, un volume de* **Lord of the Mysteries** *d’environ 200 chapitres m’a coûté un peu moins de 6 $ à traduire.*


## Réutilisation

Afin de pouvoir traduire aussi **LOTM** ou tout autre ebook au format .epub.  
Sur le terminal de votre machine physique : 

Copiez le projet dans votre machine et préparer le venv pour le projet  : 
```bash 
cd ~
git clone https://github.com/gaabsi/gpt_ebook_translator.git
cd gpt_ebook_translator 
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Ajouter au shell votre clé API et donnez lui les droits d'execution : 
```bash
code translate.sh #Changez la variable OPENAI_API_KEY et remplacez la par votre clé et sauvegardez le fichier
chmod +x translate.sh
```

Pour traduire un ebook pour pourrez ainsi procéder de la manière suivante : 
```bash 
./translate.sh {Chemin du .epub à traduire} {Chemin du .epub traduit} {Chapitre début trad} {Chapitre fin trad}
#Exemple de traduction du tome Undying de LOTM (chap 733 à 946)
./translate.sh LOTM_original.epub Undying.epub 733 946
```

Bonus : ajouter une couverture au livre créé : 
```bash
#Déplacer l'image dans le dossier images/covers/
mv {Chemin de votre image} {gpt_ebook_translator/images/covers/[votre_image.png]}
ebook-meta {Chemin du .epub traduit} --cover={gpt_ebook_translator/images/covers/[votre_image.png]}
```

Bonne lecture ! 

