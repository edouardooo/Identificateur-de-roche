import requests
from datetime import datetime, timedelta
import os
import subprocess

# URL de ta carte en JSON
umap_url = "https://umap.openstreetmap.fr/map/1135136/download/"

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

    # Nettoyer les backups plus vieux que 30 jours
    now = datetime.now()
    for filename in os.listdir(backup_dir):
        file_path = os.path.join(backup_dir, filename)
        if os.path.isfile(file_path):
            file_time = datetime.strptime(filename.split('.')[0], "%Y-%m-%d-%Hh%M")
            if now - file_time > timedelta(days=30):  # Supprimer les fichiers plus vieux que 30 jours
                os.remove(file_path)
                print(f"✔ Fichier supprimé : {file_path}")

    # Commit git auto
    subprocess.run(["git", "add", backup_path])
    subprocess.run(["git", "commit", "-m", f"Backup automatique {date_str}"])
    subprocess.run(["git", "push"])
else:
    print("❌ Erreur lors du téléchargement")
