"""Sauvegarde de la carte des kayous (uMap) dans le dossier backups/.

Lancé chaque nuit par GitHub Actions (.github/workflows/backup.yml), qui enregistre
ensuite le nouveau fichier dans le dépôt. Une sauvegarde n'est créée que si la carte
a changé depuis la dernière, pour ne pas remplir le dépôt de fichiers identiques."""
import json
import sys
from datetime import datetime
from pathlib import Path

import requests

# URL pour télécharger la carte en format .geojson
umap_url = "https://umap.openstreetmap.fr/map/1135136/download/"

# Dossier pour stocker les backups
backup_dir = Path(__file__).parent / "backups"
backup_dir.mkdir(exist_ok=True)

# Télécharger la carte
response = requests.get(umap_url, timeout=60)
if response.status_code != 200:
    print(f"❌ Erreur lors du téléchargement de la carte uMap (code {response.status_code}).")
    sys.exit(1)
carte = response.json()

# Comparer avec la dernière sauvegarde (les noms de fichiers datés se trient dans l'ordre chronologique)
sauvegardes = sorted(backup_dir.glob("*.geojson"))
if sauvegardes and json.loads(sauvegardes[-1].read_text(encoding="utf-8")) == carte:
    print(f"✔ Carte inchangée depuis {sauvegardes[-1].name}, pas de nouvelle sauvegarde.")
    sys.exit(0)

# Nom du fichier basé sur la date et l'heure
date_str = datetime.now().strftime("%Y-%m-%d-%Hh%M")
backup_path = backup_dir / f"{date_str}.geojson"
backup_path.write_text(response.text, encoding="utf-8")
print(f"✔ Backup enregistré dans : {backup_path}")
