import os
import requests
from datetime import datetime, timedelta
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
        
        # Utiliser le token pour le push
        token = os.environ.get("GITHUB_TOKEN")
        if token is None:
            raise Exception("Le token GitHub n'est pas défini dans l'environnement.")
        
        repo_url = f"https://{token}@github.com/edouardooo/Identificateur-de-roche.git"
        subprocess.run(["git", "push", repo_url, "main"], check=True)
        
        print(f"✔ Backup envoyé sur GitHub avec le message : {commit_msg}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur Git : {e}")
else:
    print("❌ Erreur lors du téléchargement de la carte Umap.")

# Nettoyage des anciens backups : garder les 30 derniers jours
now = datetime.now()
for filename in os.listdir(backup_dir):
    file_path = os.path.join(backup_dir, filename)
    if os.path.isfile(file_path):
        try:
            file_date = datetime.strptime(filename.split('.')[0], "%Y-%m-%d-%Hh%M")
            if now - file_date > timedelta(days=30):
                os.remove(file_path)
                print(f"❌ Ancien fichier supprimé : {file_path}")
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier {filename}: {e}")
