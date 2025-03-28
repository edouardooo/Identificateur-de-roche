import requests
from datetime import datetime
import os
import subprocess

# URL de ta carte en JSON (change bien l'id)
umap_url = "https://umap.openstreetmap.fr/fr/map/1135136.geojson"

# Dossier backup
backup_dir = "backups"
os.makedirs(backup_dir, exist_ok=True)

# Nom du fichier
date_str = datetime.now().strftime("%Y-%m-%d-%Hh%M")
backup_path = f"{backup_dir}/{date_str}.geojson"

# Télécharger la carte
response = requests.get(umap_url)
if response.status_code == 200:
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    print("✔ Backup enregistré :", backup_path)

    # Commit git auto (optionnel)
    subprocess.run(["git", "add", backup_path])
    subprocess.run(["git", "commit", "-m", f"Backup automatique {date_str}"])
    subprocess.run(["git", "push"])
else:
    print("❌ Erreur lors du téléchargement")
