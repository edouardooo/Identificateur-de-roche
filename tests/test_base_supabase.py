"""Teste la vraie classe BaseSupabase contre un mini-serveur qui imite l'API de Supabase
(base de données PostgREST et stockage). Vérifie que les requêtes envoyées et la lecture
des réponses sont correctes, sans avoir besoin d'un vrai projet Supabase."""
import json
import re
import uuid
from urllib.parse import parse_qsl, unquote, urlsplit

import httpx
import pytest
from supabase import create_client
from supabase.lib.client_options import SyncClientOptions

import base_photos
from base_photos import A_VERIFIER, REJETEE, VALIDEE, BaseSupabase, ErreurBase, PhotoEnDouble

URL = "https://projet-test.supabase.co"


class MiniSupabase:
    def __init__(self):
        self.lignes = []
        self.fichiers = {}
        self.en_panne = False

    def __call__(self, requete):
        if self.en_panne:
            return httpx.Response(503, json={"message": "service indisponible", "code": "503"})
        chemin = unquote(urlsplit(str(requete.url)).path)
        if chemin.startswith("/storage/v1/"):
            return self.stockage(requete, chemin.removeprefix("/storage/v1/"))
        return self.base(requete, chemin.removeprefix("/rest/v1/"))

    def stockage(self, requete, chemin):
        if requete.method == "POST" and chemin == "object/sign/photos":
            corps = json.loads(requete.content)
            return httpx.Response(200, json=[
                {"error": None, "path": p, "signedURL": f"/object/sign/photos/{p}?token=jeton"}
                for p in corps["paths"]])
        if requete.method == "POST" and chemin.startswith("object/photos/"):
            nom = chemin.removeprefix("object/photos/")
            self.fichiers[nom] = requete.content
            return httpx.Response(200, json={"Key": f"photos/{nom}", "Id": str(uuid.uuid4())})
        if requete.method == "DELETE" and chemin == "object/photos":
            for nom in json.loads(requete.content)["prefixes"]:
                del self.fichiers[nom]
            return httpx.Response(200, json=[])
        return httpx.Response(404, json={"message": "inconnu", "error": "not_found", "statusCode": "404"})

    def filtrer(self, requete):
        lignes = self.lignes
        limite = None
        for cle, valeur in parse_qsl(urlsplit(str(requete.url)).query):
            if valeur.startswith("eq."):
                lignes = [l for l in lignes if str(l.get(cle)) == valeur[3:]]
            elif cle == "limit":
                limite = int(valeur)
        return lignes, limite

    def base(self, requete, chemin):
        if chemin == "rpc/nombre_photos_validees":
            nombres = {}
            for l in self.lignes:
                if l["statut"] == VALIDEE:
                    nombres[l["roche_validee"]] = nombres.get(l["roche_validee"], 0) + 1
            return httpx.Response(200, json=[{"roche": r, "nombre": n} for r, n in nombres.items()])
        assert chemin == "photos", chemin
        lignes, limite = self.filtrer(requete)
        if requete.method == "POST":
            ligne = {"id": str(uuid.uuid4()), "cree_le": "2026-10-11T12:00:00+00:00", "statut": A_VERIFIER,
                     "roche_validee": None, "origine": "contribution", "auteur": None,
                     **json.loads(requete.content)}
            self.lignes.append(ligne)
            return httpx.Response(201, json=[ligne])
        if requete.method == "PATCH":
            for ligne in lignes:
                ligne.update(json.loads(requete.content))
            return httpx.Response(200, json=lignes)
        total = len(lignes)
        lignes = lignes[:limite] if limite is not None else lignes
        entetes = {"Content-Range": f"0-{max(len(lignes) - 1, 0)}/{total}"}
        if "vnd.pgrst.object" in requete.headers.get("accept", ""):
            return httpx.Response(200, json=lignes[0], headers=entetes)
        return httpx.Response(200, json=lignes, headers=entetes)


@pytest.fixture
def serveur(monkeypatch):
    serveur = MiniSupabase()
    client_http = httpx.Client(transport=httpx.MockTransport(serveur))

    def create_client_de_test(url, cle):
        return create_client(url, cle, SyncClientOptions(httpx_client=client_http))

    monkeypatch.setattr(base_photos, "create_client", create_client_de_test)
    return serveur


def test_cycle_complet_d_une_photo(serveur):
    photos = BaseSupabase(URL, "sb_secret_test")

    photo_id = photos.enregistrer(b"jpeg-1", "empreinte-1", contributeur="Edouard")
    (chemin,) = serveur.fichiers
    assert re.fullmatch(r"\d{4}/\d{2}/[0-9a-f-]{36}\.jpg", chemin)
    # Le fichier part dans un envoi « multipart », comme depuis un formulaire web
    assert b"jpeg-1" in serveur.fichiers[chemin] and b"image/jpeg" in serveur.fichiers[chemin]
    assert serveur.lignes[0]["consentement"] is True
    assert serveur.lignes[0]["licence"] == "CC BY 4.0"

    with pytest.raises(PhotoEnDouble):
        photos.enregistrer(b"jpeg-1", "empreinte-1")

    photos.etiqueter(photo_id, "granite", "liste")
    assert serveur.lignes[0]["roche_proposee"] == "granite"
    assert [p["id"] for p in photos.a_verifier()] == [photo_id]
    assert photos.nombre_par_statut() == {A_VERIFIER: 1, VALIDEE: 0, REJETEE: 0}

    urls = photos.urls_images([chemin])
    assert urls[chemin].startswith(URL) and "token=jeton" in urls[chemin]

    photos.decider(photo_id, VALIDEE, "gabbro")
    assert serveur.lignes[0]["statut"] == VALIDEE
    assert serveur.lignes[0]["roche_validee"] == "gabbro"
    assert photos.nombre_par_roche() == {"gabbro": 1}
    assert [p["id"] for p in photos.validees("gabbro")] == [photo_id]


def test_une_photo_rejetee_est_supprimee_du_stockage(serveur):
    photos = BaseSupabase(URL, "sb_secret_test")
    photo_id = photos.enregistrer(b"jpeg-2", "empreinte-2")
    photos.decider(photo_id, REJETEE)
    assert serveur.lignes[0]["statut"] == REJETEE
    assert serveur.fichiers == {}


def test_une_panne_de_supabase_devient_erreur_base(serveur):
    photos = BaseSupabase(URL, "sb_secret_test")
    serveur.en_panne = True
    with pytest.raises(ErreurBase):
        photos.a_verifier()
    with pytest.raises(ErreurBase):
        photos.enregistrer(b"jpeg-3", "empreinte-3")
