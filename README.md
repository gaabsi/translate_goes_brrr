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
│   ├── base_trad.py            #Script qui construit le squelette de la traduction par appel API
│   ├── batch_trad.py           #Script qui parallèlise la traduction et veille a ne pas dépaser le quota d'appel API
│   └── main.py                 #Script d'orchestration de la traduction
├── postprocessing              #Dossier relatif à la mise en forme de l'output final
│   ├── epub.css                #Contient les styles de mise en forme de l'output
│   └── mise_en_forme.py        #Script de mise en forme final pour un output aux petits oignons
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

On crée la clé API pour faire les traductions :   
Pour rappel : [portail API](https://platform.openai.com/account/api-keys) > **“Create new secret key”**  
On copie la clé obtenue et on éxecute ceci (crée un fichier texte "api_key.txt" et y met le contenu du presse-papier) : 
```bash
touch api_key.txt
pbpaste > api_key.txt #Get-Clipboard // wl-paste 
```

On crée un fichier texte pour donner le contexte à notre traduction (c'est un texte qui sera envoyé en meme temps que notre chapitre à traduire) : 
```bash 
touch context_prompt.txt
code context_prompt.txt
```

Une fois toutes ces configurations prêtes on peut ouvrir le translate.sh qui est le fichier qui orchestre la traduction : 
```bash 
code translate.sh 
#On change toutes les variables relatives à la traduction
#Une fois les variables changées 
chmod +x translate.sh 
./translate.sh 
```

Bonne lecture ! 

