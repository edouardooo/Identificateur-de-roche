"""Onglet « Administration » : vérification des photos envoyées par les visiteurs."""
import hmac

import streamlit as st

import base_photos
from base_photos import A_VERIFIER, REJETEE, SOURCES, VALIDEE, ErreurBase
from configuration import secret
from reconnaissance import INJOIGNABLE, toutes_les_roches


def connecte():
    """Demande le mot de passe d'administration (une fois par visite)."""
    if st.session_state.get("admin_connecte"):
        return True
    saisi = st.text_input("Mot de passe", type="password", key="mot_de_passe_admin")
    if saisi:
        if hmac.compare_digest(saisi.encode(), secret("admin_password").encode()):
            st.session_state["admin_connecte"] = True
            st.rerun()
        st.error("Mot de passe incorrect.")
    return False


def verifier_une_photo(photos, photo, url):
    with st.container(border=True):
        col_image, col_decision = st.columns([3, 2])
        col_image.image(url, width="stretch")
        with col_decision:
            proposee = photo["roche_proposee"]
            st.write(f"**Proposée :** {proposee or 'inconnue'}")
            st.caption(f"Source : {SOURCES.get(photo['source_etiquette'], photo['source_etiquette'])}"
                       f" · envoyée le {photo['cree_le'][:10]}"
                       f" · par {photo['contributeur'] or 'anonyme'}")
            roches = toutes_les_roches()
            roche = st.selectbox("Roche", roches, key=f"admin_roche_{photo['id']}",
                                 index=roches.index(proposee) if proposee in roches else None,
                                 placeholder="Choisissez la roche…")
            col1, col2 = st.columns(2)
            if col1.button("✅ Valider", key=f"valider_{photo['id']}", disabled=roche is None):
                photos.decider(photo["id"], VALIDEE, roche)
                st.rerun()
            if col2.button("🗑️ Rejeter", key=f"rejeter_{photo['id']}"):
                photos.decider(photo["id"], REJETEE)
                st.rerun()


def onglet_administration():
    st.title("🛠️ Administration")
    photos = base_photos.base()
    if photos is None or not secret("admin_password"):
        st.info("L'administration n'est pas configurée.")
        return
    if not connecte():
        return

    try:
        nombres = photos.nombre_par_statut()
        col1, col2, col3 = st.columns(3)
        col1.metric("À vérifier", nombres[A_VERIFIER])
        col2.metric("Validées", nombres[VALIDEE])
        col3.metric("Rejetées", nombres[REJETEE])

        st.subheader("Photos à vérifier")
        st.caption("Une photo validée apparaît dans la photothèque. Une photo rejetée "
                   "(floue, hors sujet, inappropriée) est supprimée.")
        a_verifier = photos.a_verifier(limite=10)
        if not a_verifier:
            st.success("Aucune photo en attente. 🎉")
            return
        urls = photos.urls_images([photo["chemin_image"] for photo in a_verifier])
        for photo in a_verifier:
            verifier_une_photo(photos, photo, urls[photo["chemin_image"]])
    except ErreurBase:
        st.error(INJOIGNABLE)
