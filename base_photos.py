"""Photothèque participative : les photos de roches envoyées par les visiteurs.

Les photos et leurs informations sont stockées dans Supabase (voir supabase/schema.sql).
Tout l'accès à Supabase passe par la classe BaseSupabase ; les tests la remplacent
par une fausse base en mémoire (tests/fausse_base.py)."""
import functools
import hashlib
import io
import uuid
from datetime import datetime, timezone

import httpx
import streamlit as st
from PIL import Image, ImageOps, UnidentifiedImageError
from postgrest.exceptions import APIError
from storage3.exceptions import StorageApiError
from supabase import create_client

from configuration import secret

TAILLE_MAX = 1024  # côté le plus long des photos enregistrées, en pixels
BUCKET = "photos"
LICENCE = "CC BY 4.0"
DUREE_LIENS = 3600  # durée de validité des liens vers les photos, en secondes

# Statuts d'une photo, tels qu'ils sont stockés dans la base
A_VERIFIER, VALIDEE, REJETEE = "a_verifier", "validee", "rejetee"

# D'où vient le nom de roche proposé pour une photo
SOURCES = {
    "inconnue": "inconnue",
    "liste": "choisie dans la liste",
    "cle": "clé d'identification",
    "suggestion": "suggestion acceptée",
}

# Colonnes lues pour afficher une photo (sans l'empreinte DINOv2, trop volumineuse)
COLONNES = ("id, cree_le, chemin_image, roche_proposee, source_etiquette, statut, "
            "roche_validee, contributeur, origine, auteur, licence")


class ImageInvalide(Exception):
    """Le fichier envoyé n'est pas une image lisible."""


class PhotoEnDouble(Exception):
    """Cette photo exacte est déjà dans la photothèque."""


class ErreurBase(Exception):
    """La photothèque (Supabase) ne répond pas ou a refusé la demande."""


def preparer_image(contenu):
    """Redresse la photo, la réduit à TAILLE_MAX pixels et la réenregistre en JPEG.

    Le réenregistrement supprime les métadonnées EXIF, dont la position GPS.
    Renvoie (jpeg, empreinte du fichier envoyé) ; l'empreinte sert à refuser les doublons."""
    try:
        image = Image.open(io.BytesIO(contenu))
        image = ImageOps.exif_transpose(image).convert("RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as erreur:
        raise ImageInvalide from erreur
    image.thumbnail((TAILLE_MAX, TAILLE_MAX))
    sortie = io.BytesIO()
    image.save(sortie, "JPEG", quality=85)
    return sortie.getvalue(), hashlib.sha256(contenu).hexdigest()


def _traduire_erreurs(methode):
    """Transforme les erreurs de Supabase et du réseau en ErreurBase."""
    @functools.wraps(methode)
    def enveloppe(*args, **kwargs):
        try:
            return methode(*args, **kwargs)
        except (APIError, StorageApiError, httpx.HTTPError) as erreur:
            raise ErreurBase(str(erreur)) from erreur
    return enveloppe


class BaseSupabase:
    def __init__(self, url, cle_secrete):
        self.client = create_client(url, cle_secrete)

    def _photos(self):
        return self.client.table("photos")

    @_traduire_erreurs
    def enregistrer(self, jpeg, empreinte, roche=None, source="inconnue", contributeur=None):
        """Enregistre une nouvelle photo (statut « à vérifier ») et renvoie son identifiant."""
        if self._photos().select("id").eq("empreinte_fichier", empreinte).limit(1).execute().data:
            raise PhotoEnDouble
        chemin = f"{datetime.now(timezone.utc):%Y/%m}/{uuid.uuid4()}.jpg"
        self.client.storage.from_(BUCKET).upload(chemin, jpeg, {"content-type": "image/jpeg"})
        ligne = self._photos().insert({
            "chemin_image": chemin,
            "empreinte_fichier": empreinte,
            "roche_proposee": roche,
            "source_etiquette": source,
            "contributeur": contributeur,
            "licence": LICENCE,
            "consentement": True,
        }).execute()
        return ligne.data[0]["id"]

    @_traduire_erreurs
    def etiqueter(self, photo_id, roche, source):
        """Enregistre le nom de roche proposé par le visiteur."""
        self._photos().update({"roche_proposee": roche, "source_etiquette": source}).eq("id", photo_id).execute()

    @_traduire_erreurs
    def a_verifier(self, limite=10):
        """Les photos les plus anciennes en attente de vérification."""
        return (self._photos().select(COLONNES).eq("statut", A_VERIFIER)
                .order("cree_le").limit(limite).execute().data)

    @_traduire_erreurs
    def decider(self, photo_id, statut, roche=None):
        """Valide (avec le nom de roche retenu) ou rejette une photo.

        Le fichier d'une photo rejetée est supprimé ; sa ligne est gardée pour
        refuser la même photo si elle est renvoyée."""
        if statut == VALIDEE:
            self._photos().update({
                "statut": VALIDEE,
                "roche_validee": roche,
                "validee_le": datetime.now(timezone.utc).isoformat(),
            }).eq("id", photo_id).execute()
        else:
            ligne = self._photos().select("chemin_image").eq("id", photo_id).single().execute()
            self._photos().update({"statut": REJETEE}).eq("id", photo_id).execute()
            self.client.storage.from_(BUCKET).remove([ligne.data["chemin_image"]])

    @_traduire_erreurs
    def validees(self, roche, limite=60):
        """Les photos validées d'une roche, des plus récentes aux plus anciennes."""
        return (self._photos().select(COLONNES).eq("statut", VALIDEE).eq("roche_validee", roche)
                .order("validee_le", desc=True).limit(limite).execute().data)

    @_traduire_erreurs
    def nombre_par_statut(self):
        return {statut: self._photos().select("id", count="exact").eq("statut", statut).limit(1).execute().count
                for statut in (A_VERIFIER, VALIDEE, REJETEE)}

    @_traduire_erreurs
    def nombre_par_roche(self):
        """Nombre de photos validées pour chaque roche."""
        return {ligne["roche"]: ligne["nombre"]
                for ligne in self.client.rpc("nombre_photos_validees").execute().data}

    @_traduire_erreurs
    def urls_images(self, chemins):
        """Liens temporaires pour afficher des photos du stockage privé : {chemin: lien}."""
        if not chemins:
            return {}
        reponses = self.client.storage.from_(BUCKET).create_signed_urls(list(chemins), DUREE_LIENS)
        return {reponse["path"]: reponse["signedURL"] for reponse in reponses}


@st.cache_resource(show_spinner=False)
def _connexion(url, cle_secrete):
    return BaseSupabase(url, cle_secrete)


def base():
    """La photothèque, ou None si Supabase n'est pas configuré dans les secrets."""
    url, cle_secrete = secret("supabase_url"), secret("supabase_secret_key")
    if not (url and cle_secrete):
        return None
    return _connexion(url, cle_secrete)
