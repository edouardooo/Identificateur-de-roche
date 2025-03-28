import os
import requests
from datetime import datetime
import subprocess
import shutil

# URL pour télécharger la carte en format .geojson
umap_url = "https://umap.openstreetmap.fr/map/1135136/download/"

# Dossier pour stocker les backups
backup_dir = "backups"
os.makedirs(backup_dir, exist_ok=True)

# Nom du fichier basé sur la date et l'heure
date_str = datetime.now().strftime("%Y-%m-%d-%Hh%M")
backup_path = f"{backup_dir}/{date_str}.geojson"

# Télécharger le fichier .geojson
response = requests.get(umap_url)
if response.status_code == 200:
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"✔ Backup enregistré dans : {backup_path}")

    # Ajouter et commit dans GitHub
    try:
        # Ajouter les fichiers à Git
        subprocess.run(["git", "add", backup_path], check=True)
        
        # Commit avec message
        commit_msg = f"Backup automatique {date_str}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        
        # Push vers GitHub
        subprocess.run(["git", "push", "origin", "main"], check=True)  # Assure-toi que "main" est ton branche par défaut
        
        print(f"✔ Backup envoyé sur GitHub avec le message : {commit_msg}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur Git : {e}")
else:
    print("❌ Erreur lors du téléchargement de la carte Umap.")

# Nettoyage des anciens backups : garder les 30 derniers jours
# On va vérifier et supprimer les fichiers de plus de 30 jours dans le dossier backups

# Obtenir la liste des fichiers dans backups/
backup_files = [f for f in os.listdir(backup_dir) if os.path.isfile(os.path.join(backup_dir, f))]
backup_files.sort(reverse=True)  # Trier les fichiers par date (du plus récent au plus ancien)

# Supprimer les fichiers plus anciens que 30 jours
for file in backup_files[30:]:  # Garder seulement les 30 plus récents
    file_path = os.path.join(backup_dir, file)
    os.remove(file_path)
    print(f"❌ Ancien fichier supprimé : {file_path}")
