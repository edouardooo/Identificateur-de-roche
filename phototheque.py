"""Onglet « Photothèque » : les photos validées, roche par roche."""
import streamlit as st

import base_photos
from base_photos import ErreurBase
from dictionnaire import sans_accents
from fonction_d_identification import ROCHES
from reconnaissance import INJOIGNABLE

# Nombre de photos validées par roche visé avant d'ouvrir la reconnaissance automatique
OBJECTIF_PAR_ROCHE = 15


def afficher_avancement(nombres):
    lignes = [{"Roche": roche, "Famille": famille, "Photos validées": nombres.get(roche, 0)}
              for famille, roches in ROCHES.items() for roche in roches]
    lignes.sort(key=lambda ligne: (-ligne["Photos validées"], sans_accents(ligne["Roche"])))
    st.dataframe(lignes, hide_index=True, width="stretch", column_config={
        "Photos validées": st.column_config.ProgressColumn(
            f"Photos validées (objectif {OBJECTIF_PAR_ROCHE})", min_value=0,
            max_value=OBJECTIF_PAR_ROCHE, format="%d"),
    })


def onglet_phototheque():
    st.title("🖼️ Photothèque")
    st.write("Les photos de roches envoyées par les visiteurs et vérifiées. Elles serviront "
             "de références à la reconnaissance automatique. Envoyez les vôtres depuis "
             "l'onglet « Reconnaissance par photo » !")
    photos = base_photos.base()
    if photos is None:
        st.info("La photothèque est momentanément désactivée.")
        return

    try:
        nombres = photos.nombre_par_roche()
        st.caption(f"{sum(nombres.values())} photo(s) validée(s) pour {len(nombres)} roche(s).")
        with st.expander("Avancement de la photothèque"):
            afficher_avancement(nombres)

        if not nombres:
            st.info("Pas encore de photo validée : soyez le premier à en envoyer une !")
            return
        roche = st.selectbox("Roche", sorted(nombres, key=sans_accents),
                             format_func=lambda r: f"{r} ({nombres[r]})")
        validees = photos.validees(roche)
        urls = photos.urls_images([photo["chemin_image"] for photo in validees])
        colonnes = st.columns(3)
        for i, photo in enumerate(validees):
            auteur = photo["auteur"] or photo["contributeur"] or "Anonyme"
            colonnes[i % 3].image(urls[photo["chemin_image"]], width="stretch",
                                  caption=f"© {auteur} · {photo['licence']}")
    except ErreurBase:
        st.error(INJOIGNABLE)
