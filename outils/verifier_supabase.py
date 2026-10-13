"""Vérifie que le projet Supabase de la photothèque est bien configuré.

À lancer une fois, après avoir exécuté supabase/schema.sql et rempli .streamlit/secrets.toml :

    python outils/verifier_supabase.py

Le script envoie une photo de test, la relit, la rejette, puis efface toute trace du test."""
import io
import sys
import tomllib
import uuid
from pathlib import Path

import httpx
from PIL import Image

DOSSIER = Path(__file__).parent.parent
sys.path.insert(0, str(DOSSIER))

from base_photos import REJETEE, BaseSupabase, ErreurBase, preparer_image  # noqa: E402


def etape(texte):
    print(f"✔ {texte}")


def main():
    fichier_secrets = DOSSIER / ".streamlit" / "secrets.toml"
    if not fichier_secrets.exists():
        sys.exit(f"❌ Fichier introuvable : {fichier_secrets}\n"
                 "   Copie .streamlit/secrets.toml.exemple en secrets.toml et remplis les clés Supabase.")
    secrets = tomllib.loads(fichier_secrets.read_text(encoding="utf-8"))
    if not (secrets.get("supabase_url") and secrets.get("supabase_secret_key")):
        sys.exit("❌ supabase_url ou supabase_secret_key manquant dans .streamlit/secrets.toml")
    if "xxxx" in secrets["supabase_url"].lower() or "XXXX" in secrets["supabase_secret_key"]:
        sys.exit("❌ .streamlit/secrets.toml contient encore les valeurs d'exemple :\n"
                 "   remplace-les par l'URL et la clé secrète de ton projet Supabase.")

    photos = BaseSupabase(secrets["supabase_url"], secrets["supabase_secret_key"])
    photo_id = None
    try:
        nombres = photos.nombre_par_statut()
        etape(f"Connexion à la base : {nombres}")
        photos.nombre_par_roche()
        etape("Fonction nombre_photos_validees disponible")

        image = io.BytesIO()
        Image.new("RGB", (64, 64), (128, 100, 80)).save(image, "JPEG")
        jpeg, _ = preparer_image(image.getvalue())
        photo_id = photos.enregistrer(jpeg, f"test-{uuid.uuid4()}", contributeur="test automatique")
        etape("Photo de test enregistrée (stockage + table)")

        (chemin,) = [p["chemin_image"] for p in photos.a_verifier(limite=1000) if p["id"] == photo_id]
        lien = photos.urls_images([chemin])[chemin]
        reponse = httpx.get(lien, timeout=30)
        reponse.raise_for_status()
        etape(f"Photo relue par un lien temporaire ({len(reponse.content)} octets)")

        photos.decider(photo_id, REJETEE)
        etape("Photo rejetée et fichier supprimé")
    except (ErreurBase, httpx.HTTPError) as erreur:
        sys.exit(f"❌ {erreur}\n   As-tu bien exécuté supabase/schema.sql dans le SQL Editor de Supabase ?")
    finally:
        if photo_id is not None:
            photos.client.table("photos").delete().eq("id", photo_id).execute()
    print("\n🎉 Supabase est prêt pour la photothèque.")


if __name__ == "__main__":
    main()
