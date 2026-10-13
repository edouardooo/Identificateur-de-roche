"""Tests de la photothèque (étape 1 du plan), avec une fausse base Supabase en mémoire."""
import io

import pytest
from PIL import Image
from streamlit.testing.v1 import AppTest

import base_photos
from base_photos import A_VERIFIER, REJETEE, VALIDEE, ImageInvalide, preparer_image
from fausse_base import FausseBase
from test_app import APP

OBSIDIENNE = {
    "type_roche": "magmatique",
    "magmatique | La roche est-elle entièrement formée de cristaux jointifs, tous visibles à l'œil nu (structure grenue), sans pâte fine ni verre ?": "non",
    "magmatique > volcanique | La roche a-t-elle l'aspect d'un verre (brillante, cassure conchoïdale coupante) ?": "oui",
}


def photo_jpeg(largeur=2000, hauteur=1500, couleur=(120, 110, 100), orientation=None):
    """Une photo de test, avec des métadonnées EXIF comme celles d'un téléphone."""
    exif = Image.Exif()
    exif[0x010F] = "Fabricant du téléphone"
    if orientation:
        exif[0x0112] = orientation
    sortie = io.BytesIO()
    Image.new("RGB", (largeur, hauteur), couleur).save(sortie, "JPEG", exif=exif)
    return sortie.getvalue()


@pytest.fixture
def fausse_base(monkeypatch):
    base = FausseBase()
    monkeypatch.setattr(base_photos, "base", lambda: base)
    return base


def ouvrir(page, reponses=None, secrets=None):
    at = AppTest.from_file(APP, default_timeout=30)
    at.secrets.update(secrets or {})
    for cle, valeur in (reponses or {}).items():
        at.session_state[cle] = valeur
    at.session_state["menu"] = page
    return at.run()


def envoyer(at, contenu, nom="roche.jpg", cle="onglet"):
    at.checkbox(key=f"accord_{cle}").check().run()
    at.file_uploader(key=f"fichier_{cle}").upload(nom, contenu, "image/jpeg").run()
    assert not at.exception, at.exception
    return at


def test_preparer_image_redresse_reduit_et_supprime_les_metadonnees():
    # Orientation 6 : le téléphone était tenu debout, la photo doit être tournée
    jpeg, empreinte = preparer_image(photo_jpeg(orientation=6))
    image = Image.open(io.BytesIO(jpeg))
    assert image.size == (768, 1024)
    assert len(image.getexif()) == 0
    assert len(empreinte) == 64


def test_preparer_image_refuse_un_fichier_qui_n_est_pas_une_image():
    with pytest.raises(ImageInvalide):
        preparer_image(b"ceci n'est pas une photo")


def test_onglets_desactives_sans_supabase():
    for page in ["Reconnaissance par photo", "Photothèque", "Administration"]:
        at = ouvrir(page)
        assert not at.exception
        assert any("désactivé" in i.value or "pas configurée" in i.value for i in at.info)


def test_rien_n_est_envoye_sans_accord(fausse_base):
    at = ouvrir("Reconnaissance par photo")
    assert len(at.file_uploader) == 0
    at.checkbox(key="accord_onglet").check().run()
    assert len(at.file_uploader) == 1
    assert fausse_base.photos == []


def test_chaque_photo_envoyee_est_enregistree(fausse_base):
    at = envoyer(ouvrir("Reconnaissance par photo"), photo_jpeg())
    assert [p["statut"] for p in fausse_base.photos] == [A_VERIFIER]
    assert fausse_base.photos[0]["roche_proposee"] is None

    at.run()  # un autre clic sur la page n'enregistre pas la photo une deuxième fois
    assert len(fausse_base.photos) == 1

    photo_id = fausse_base.photos[0]["id"]
    at.selectbox(key=f"roche_{photo_id}").set_value("granite").run()
    at.button(key=f"envoyer_{photo_id}").click().run()
    assert fausse_base.photos[0]["roche_proposee"] == "granite"
    assert fausse_base.photos[0]["source_etiquette"] == "liste"
    assert any("granite" in m.value for m in at.markdown)


def test_la_meme_photo_n_est_pas_enregistree_deux_fois(fausse_base):
    envoyer(ouvrir("Reconnaissance par photo"), photo_jpeg())
    at = envoyer(ouvrir("Reconnaissance par photo"), photo_jpeg())
    assert len(fausse_base.photos) == 1
    assert any("déjà dans la photothèque" in w.value for w in at.warning)


def test_un_fichier_illisible_est_refuse(fausse_base):
    at = envoyer(ouvrir("Reconnaissance par photo"), b"pas une image", nom="faux.jpg")
    assert fausse_base.photos == []
    assert any("pas une image" in e.value for e in at.error)


def test_identifier_sa_photo_avec_la_cle(fausse_base):
    at = envoyer(ouvrir("Reconnaissance par photo"), photo_jpeg())
    photo_id = fausse_base.photos[0]["id"]
    at.button(key=f"vers_cle_{photo_id}").click().run()
    assert at.session_state["menu"] == "Identificateur"

    for cle, valeur in OBSIDIENNE.items():
        at.session_state[cle] = valeur
    at.run()
    at.button[0].click().run()  # « Indiquer « obsidienne » pour ma photo »
    assert fausse_base.photos[0]["roche_proposee"] == "obsidienne"
    assert fausse_base.photos[0]["source_etiquette"] == "cle"
    assert any("rattachée" in s.value for s in at.success)
    assert not any("pour ma photo" in b.label for b in at.button)


def test_ajouter_une_photo_depuis_le_resultat_de_la_cle(fausse_base):
    at = ouvrir("Identificateur", reponses=OBSIDIENNE)
    envoyer(at, photo_jpeg(), cle="cle_obsidienne")
    assert fausse_base.photos[0]["roche_proposee"] == "obsidienne"
    assert fausse_base.photos[0]["source_etiquette"] == "cle"


def test_administration_demande_le_bon_mot_de_passe(fausse_base):
    at = ouvrir("Administration", secrets={"admin_password": "mot de passe de test"})
    at.text_input(key="mot_de_passe_admin").input("mauvais").run()
    assert any("incorrect" in e.value for e in at.error)
    assert len(at.metric) == 0
    at.text_input(key="mot_de_passe_admin").input("mot de passe de test").run()
    assert len(at.metric) == 3


def test_administration_valide_et_rejette(fausse_base):
    for couleur in [(10, 10, 10), (200, 200, 200)]:
        jpeg, empreinte = preparer_image(photo_jpeg(couleur=couleur))
        fausse_base.enregistrer(jpeg, empreinte, roche="basalte", source="liste")
    premiere, seconde = (p["id"] for p in fausse_base.photos)

    at = ouvrir("Administration", secrets={"admin_password": "mot de passe de test"})
    at.text_input(key="mot_de_passe_admin").input("mot de passe de test").run()
    at.selectbox(key=f"admin_roche_{premiere}").set_value("gabbro").run()  # correction de l'étiquette
    at.button(key=f"valider_{premiere}").click().run()
    at.button(key=f"rejeter_{seconde}").click().run()
    assert not at.exception

    assert fausse_base.photo(premiere)["statut"] == VALIDEE
    assert fausse_base.photo(premiere)["roche_validee"] == "gabbro"
    assert fausse_base.photo(seconde)["statut"] == REJETEE
    assert fausse_base.photo(seconde)["chemin_image"] not in fausse_base.fichiers
    assert any("Aucune photo en attente" in s.value for s in at.success)


def test_la_phototheque_n_affiche_que_les_photos_validees(fausse_base):
    for couleur in [(10, 10, 10), (90, 90, 90), (200, 200, 200)]:
        jpeg, empreinte = preparer_image(photo_jpeg(couleur=couleur))
        fausse_base.enregistrer(jpeg, empreinte, roche="granite", source="liste", contributeur="Edouard")
    fausse_base.decider("photo-1", VALIDEE, "granite")
    fausse_base.decider("photo-2", REJETEE)

    at = ouvrir("Photothèque")
    assert not at.exception
    assert len(at.image) == 1
    assert any("1 photo(s) validée(s)" in c.value for c in at.caption)
