"""Tests de l'application. Pour les lancer, depuis le dossier du projet : pytest"""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from dictionnaire import definition_roche, termes_de_base
from fonction_d_identification import NON_IDENTIFIEE, RECHERCHES_LITHOTHEQUE

DOSSIER = Path(__file__).parent.parent
APP = str(DOSSIER / "identificateur_de_roche.py")

# Roches de la clé qui n'ont pas d'échantillon sur la lithothèque de l'ENS de Lyon
ROCHES_SANS_LIEN = {"pétrole", "lignite", "anthracite", "galets et graviers", "ardoise"}


def lancer(reponses=None, page="Identificateur"):
    at = AppTest.from_file(APP, default_timeout=30)
    for cle, valeur in (reponses or {}).items():
        at.session_state[cle] = valeur
    at.run()
    if page != "Identificateur":
        at.sidebar.selectbox[0].set_value(page).run()
    return at


def parcourir(reponses=None):
    """Essaie toutes les réponses possibles de la clé.

    Renvoie un dictionnaire {chemin de la roche: application affichant ce résultat}."""
    reponses = reponses or {}
    at = lancer(reponses)
    assert not at.exception, f"Erreur avec les réponses {reponses} : {at.exception}"
    sans_reponse = [radio for radio in at.radio if radio.value is None]
    if not sans_reponse:
        return {chemin_affiche(at): at}
    radio = sans_reponse[0]
    resultats = {}
    for option in radio.options:
        resultats.update(parcourir({**reponses, radio.key: option}))
    return resultats


def chemin_affiche(at):
    """Chemin de la roche identifiée, lu sur la page (ex. ("magmatique", "volcanique", "basalte"))."""
    if any("Aucune roche de la clé" in w.value for w in at.warning):
        return (at.session_state["type_roche"], NON_IDENTIFIEE)
    titres = [s.value for s in at.subheader if s.value.startswith("Roche identifiée : ")]
    assert len(titres) == 1, "La page n'affiche pas de résultat"
    nom = titres[0].removeprefix("Roche identifiée : ")
    classification = [c.value for c in at.caption if c.value.startswith("Classification : ")][0]
    return tuple(classification.removeprefix("Classification : ").split(" › ")) + (nom[0].lower() + nom[1:],)


@pytest.fixture(scope="module")
def resultats():
    return parcourir()


def test_rien_n_est_affiche_avant_la_premiere_reponse():
    at = lancer()
    assert not at.exception
    assert at.radio[0].value is None
    assert not [s for s in at.subheader if s.value.startswith("Roche identifiée")]


def test_toutes_les_roches_sont_atteignables(resultats):
    trouvees = {chemin[-1] for chemin in resultats}
    attendues = set(RECHERCHES_LITHOTHEQUE) | ROCHES_SANS_LIEN | {NON_IDENTIFIEE}
    assert trouvees == attendues


def test_chaque_roche_a_une_definition(resultats):
    for chemin in resultats:
        if chemin[-1] != NON_IDENTIFIEE:
            assert definition_roche(list(chemin)) is not None, chemin


def test_chaque_photo_correspond_a_une_roche(resultats):
    chemins = {" ".join(chemin) for chemin in resultats}
    for photo in (DOSSIER / "photos").glob("*.jpg"):
        assert photo.stem in chemins, f"Photo jamais affichée : {photo.name}"


def test_photo_et_lien_affiches():
    reponses = {"type_roche": "magmatique",
                "magmatique | La roche est-elle entièrement formée de cristaux jointifs, tous visibles à l'œil nu (structure grenue), sans pâte fine ni verre ?": "non",
                "magmatique > volcanique | La roche a-t-elle l'aspect d'un verre (brillante, cassure conchoïdale coupante) ?": "oui"}
    at = lancer(reponses)
    assert chemin_affiche(at) == ("magmatique", "volcanique", "obsidienne")
    assert len(at.image) == 1
    assert any("cindex.php?Type=obsidienne" in m.value for m in at.markdown)


def test_dictionnaire_de_base():
    termes = [t["terme"] for t in termes_de_base()]
    assert len(termes) >= 100
    assert len(termes) == len({t.lower() for t in termes}), "terme en double"
    assert all(t["definition"].strip() for t in termes_de_base())


def test_page_dictionnaire_sans_airtable():
    at = lancer(page="Dictionnaire")
    assert not at.exception
    assert any(m.value == "### Olivine" for m in at.markdown)
    at.text_input[0].set_value("éclog").run()
    titres = [m.value for m in at.markdown if m.value.startswith("### ")]
    assert titres == ["### Éclogite"]
    assert any("désactivées" in i.value for i in at.info)


def test_une_deuxieme_image_a_son_propre_lien(monkeypatch):
    """Avant la correction, une deuxième image affichait le lien de la première."""
    envois = []

    def faux_cloudinary(fichier):
        envois.append(fichier.name)
        return {"secure_url": f"https://exemple.test/{fichier.name}"}

    monkeypatch.setattr("cloudinary.uploader.upload", faux_cloudinary)
    image = next((DOSSIER / "photos").glob("*.jpg")).read_bytes()

    at = AppTest.from_file(APP, default_timeout=30)
    at.secrets.update(cloudinary_cloud_name="test", cloudinary_api_key="1", cloudinary_api_secret="x")
    at.run()
    at.sidebar.selectbox[0].set_value("La carte des kayous").run()
    at.file_uploader[0].upload("a.jpg", image, "image/jpeg").run()
    at.run()  # un autre clic sur la page ne renvoie pas l'image
    assert [c.value for c in at.code] == ["{{https://exemple.test/a.jpg}}"]
    at.file_uploader[0].upload("b.jpg", image, "image/jpeg").run()
    assert [c.value for c in at.code] == ["{{https://exemple.test/b.jpg}}"]
    assert envois == ["a.jpg", "b.jpg"]


@pytest.mark.parametrize("page", ["La carte des kayous", "Objectif"])
def test_autres_pages(page):
    at = lancer(page=page)
    assert not at.exception
