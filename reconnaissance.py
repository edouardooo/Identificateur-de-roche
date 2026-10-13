"""Onglet « Reconnaissance par photo ».

Étape 1 du plan (docs/plan-reconnaissance-par-photo.md) : pas encore de reconnaissance
automatique. Chaque photo envoyée est enregistrée dans la photothèque, avec le nom de
la roche si le visiteur le connaît (liste ou clé d'identification)."""
import streamlit as st

import base_photos
from base_photos import LICENCE, ErreurBase, ImageInvalide, PhotoEnDouble
from dictionnaire import sans_accents
from fonction_d_identification import ROCHES

ACCORD = (f"J'accepte que ma photo soit conservée et publiée sous licence {LICENCE} "
          "(réutilisation libre en citant l'auteur) pour construire la photothèque "
          "et la reconnaissance automatique. Les données de localisation de la photo sont supprimées.")

CONSEILS = """**Pour une photo utile :**
- une **cassure fraîche** de la roche (pas une surface altérée ou couverte de lichens) ;
- en **gros plan**, la roche remplissant l'image ;
- à la **lumière du jour**, sans flash ;
- si possible avec une **pièce de monnaie** à côté pour l'échelle."""

INJOIGNABLE = "La photothèque est momentanément injoignable. Réessayez plus tard."


def toutes_les_roches():
    return sorted((roche for roches in ROCHES.values() for roche in roches), key=sans_accents)


def recevoir_photo(photos, cle, roche=None, source="inconnue"):
    """Accord + envoi d'une photo. Chaque nouvelle photo est enregistrée aussitôt.

    `cle` distingue les différents formulaires de la page. Renvoie l'identifiant
    de la photo enregistrée, ou None tant qu'aucune photo n'a été envoyée."""
    if not st.checkbox(ACCORD, key=f"accord_{cle}"):
        return None
    contributeur = st.text_input("Votre nom ou pseudo (facultatif, affiché avec la photo)",
                                 key=f"pseudo_{cle}", max_chars=60).strip()
    if st.toggle("Prendre la photo avec l'appareil photo", key=f"camera_{cle}"):
        fichier = st.camera_input("Photo de la roche", key=f"prise_{cle}")
    else:
        fichier = st.file_uploader("Photo de la roche", type=["jpg", "jpeg", "png", "webp"],
                                   key=f"fichier_{cle}")
    if fichier is None:
        return None

    # Streamlit relance la page à chaque clic : on n'enregistre qu'une fois chaque fichier
    deja = st.session_state.get(f"photo_{cle}")
    if deja is not None and deja["fichier"] == fichier.file_id:
        return deja["id"]
    try:
        jpeg, empreinte = base_photos.preparer_image(fichier.getvalue())
        photo_id = photos.enregistrer(jpeg, empreinte, roche, source, contributeur or None)
    except ImageInvalide:
        st.error("Ce fichier n'est pas une image lisible.")
        return None
    except PhotoEnDouble:
        st.warning("Cette photo est déjà dans la photothèque. Merci quand même !")
        return None
    st.session_state[f"photo_{cle}"] = {"fichier": fichier.file_id, "id": photo_id}
    return photo_id


def identifier_avec_la_cle(photo_id):
    """Ouvre l'onglet Identificateur ; son résultat pourra être rattaché à la photo."""
    st.session_state["menu"] = "Identificateur"
    st.session_state["photo_a_identifier"] = photo_id


def demander_la_roche(photos, photo_id):
    st.success("Photo enregistrée, merci ! Elle sera vérifiée avant d'apparaître dans la photothèque.")
    st.subheader("Quelle est cette roche ?")
    reponse = st.session_state.get(f"reponse_{photo_id}")
    if reponse is not None:
        st.write(f"Vous avez indiqué : **{reponse}**. Merci !")
        return

    roche = st.selectbox("Roche", toutes_les_roches(), index=None,
                         placeholder="Choisissez dans la liste…", key=f"roche_{photo_id}")
    col1, col2 = st.columns(2)
    if col1.button("Envoyer ma réponse", disabled=roche is None, key=f"envoyer_{photo_id}"):
        photos.etiqueter(photo_id, roche, "liste")
        st.session_state[f"reponse_{photo_id}"] = roche
        st.rerun()
    col2.button("🔑 Je ne sais pas : l'identifier avec la clé", key=f"vers_cle_{photo_id}",
                on_click=identifier_avec_la_cle, args=(photo_id,))


def onglet_reconnaissance():
    st.title("📷 Reconnaissance par photo")
    st.info("La reconnaissance automatique arrive bientôt ! Pour apprendre, elle a d'abord besoin "
            "de photos de référence : chaque photo envoyée ici enrichit la photothèque.")
    photos = base_photos.base()
    if photos is None:
        st.info("L'envoi de photos est momentanément désactivé.")
        return
    st.markdown(CONSEILS)
    try:
        photo_id = recevoir_photo(photos, cle="onglet")
        if photo_id is not None:
            demander_la_roche(photos, photo_id)
    except ErreurBase:
        st.error(INJOIGNABLE)


def proposer_photo(nom_roche):
    """Sous le résultat de la clé : rattacher ce résultat à la photo du visiteur,
    ou proposer d'ajouter une photo de cette roche à la photothèque."""
    photos = base_photos.base()
    if photos is None:
        return
    try:
        if st.session_state.pop("photo_rattachee", False):
            st.success("Merci ! Votre photo a été rattachée à ce résultat.")
        photo_id = st.session_state.get("photo_a_identifier")
        if photo_id is not None:
            if st.button(f"📷 Indiquer « {nom_roche} » pour ma photo", type="primary"):
                photos.etiqueter(photo_id, nom_roche, "cle")
                del st.session_state["photo_a_identifier"]
                st.session_state["photo_rattachee"] = True
                st.rerun()  # pour que le bouton disparaisse
            return
        with st.expander("📷 Ajouter une photo de cette roche à la photothèque"):
            if recevoir_photo(photos, cle=f"cle_{nom_roche}", roche=nom_roche, source="cle") is not None:
                st.success("Photo enregistrée, merci ! Elle sera vérifiée avant d'apparaître dans la photothèque.")
    except ErreurBase:
        st.error(INJOIGNABLE)
