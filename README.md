Ce projet a pour but d'arriver à une application permettant l'identification de roche par photo de manière gratuite, fiable et scientifiquement correcte.
N'hésitez pas à faire des retours à identificateur.de.roche@gmail.com
Merci d'avance et bonne visite
Azoulay Edouard

## Contenu du site

- **Identificateur** : une clé de détermination (questions oui/non) pour les roches sédimentaires, magmatiques et métamorphiques du programme de BCPST. Le code de la clé est dans `fonction_d_identification.py`.
- **La carte des kayous** : une carte uMap participative des affleurements, sauvegardée chaque nuit dans `backups/` par GitHub Actions (seulement si elle a changé).
- **Dictionnaire** : les termes de base sont dans `dictionnaire_base.csv` (modifiable avec un tableur ou un éditeur de texte). Les propositions des visiteurs arrivent dans Airtable et s'affichent une fois la case « validé » cochée.
- **Objectif** : la présentation du projet.

## Lancer le site sur son ordinateur

```
pip install -r requirements.txt
streamlit run identificateur_de_roche.py
```

## Secrets (Airtable et Cloudinary)

Les clés ne doivent **jamais** être écrites dans le code ni envoyées sur GitHub. Le modèle `.streamlit/secrets.toml.exemple` explique où les mettre : en local dans `.streamlit/secrets.toml` (ignoré par git), en ligne dans les réglages « Secrets » de Streamlit Cloud. Sans secrets, le site fonctionne mais l'envoi de photos et les propositions du dictionnaire sont désactivés.

## Tests

```
pip install pytest
pytest
```

Les tests parcourent automatiquement toutes les branches de la clé d'identification et vérifient que chaque roche trouvée a une définition dans le dictionnaire.

## Photos

Les photos du dossier `photos/` proviennent de la lithothèque de l'ENS de Lyon. Le nom d'un fichier est le chemin de la roche dans la clé (exemple : `magmatique volcanique basalte.jpg`). Pour chaque roche, le site donne aussi un lien vers les échantillons de la lithothèque : https://lithotheque.ens-lyon.fr/index.php
