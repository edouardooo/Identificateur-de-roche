"""Fausse photothèque en mémoire, qui se comporte comme base_photos.BaseSupabase."""
from datetime import datetime, timezone

from base_photos import A_VERIFIER, LICENCE, REJETEE, VALIDEE, PhotoEnDouble


class FausseBase:
    def __init__(self):
        self.photos = []
        self.fichiers = {}

    def photo(self, photo_id):
        return next(p for p in self.photos if p["id"] == photo_id)

    def enregistrer(self, jpeg, empreinte, roche=None, source="inconnue", contributeur=None):
        if any(p["empreinte_fichier"] == empreinte for p in self.photos):
            raise PhotoEnDouble
        photo_id = f"photo-{len(self.photos) + 1}"
        chemin = f"{photo_id}.jpg"
        self.fichiers[chemin] = jpeg
        self.photos.append({
            "id": photo_id, "cree_le": datetime.now(timezone.utc).isoformat(),
            "chemin_image": chemin, "empreinte_fichier": empreinte,
            "roche_proposee": roche, "source_etiquette": source, "statut": A_VERIFIER,
            "roche_validee": None, "contributeur": contributeur, "origine": "contribution",
            "auteur": None, "licence": LICENCE,
        })
        return photo_id

    def etiqueter(self, photo_id, roche, source):
        self.photo(photo_id).update(roche_proposee=roche, source_etiquette=source)

    def a_verifier(self, limite=10):
        return [p for p in self.photos if p["statut"] == A_VERIFIER][:limite]

    def decider(self, photo_id, statut, roche=None):
        photo = self.photo(photo_id)
        photo["statut"] = statut
        if statut == VALIDEE:
            photo["roche_validee"] = roche
        else:
            del self.fichiers[photo["chemin_image"]]

    def validees(self, roche, limite=60):
        return [p for p in self.photos if p["statut"] == VALIDEE and p["roche_validee"] == roche][:limite]

    def nombre_par_statut(self):
        return {s: sum(p["statut"] == s for p in self.photos) for s in (A_VERIFIER, VALIDEE, REJETEE)}

    def nombre_par_roche(self):
        nombres = {}
        for p in self.photos:
            if p["statut"] == VALIDEE:
                nombres[p["roche_validee"]] = nombres.get(p["roche_validee"], 0) + 1
        return nombres

    def urls_images(self, chemins):
        return {chemin: f"https://exemple.test/{chemin}" for chemin in chemins}
