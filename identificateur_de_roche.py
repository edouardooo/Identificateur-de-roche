from pathlib import Path

import streamlit as st

from dictionnaire import afficher_dico, definition_roche, sugestions_dico, table_airtable
from fonction_d_identification import (NON_IDENTIFIEE, identificationmagmatique,
                                       identificationmetamorphique, identificationsedimentaire,
                                       lien_lithotheque)
from upload_image import uploader_image

DOSSIER_PHOTOS = Path(__file__).parent / "photos"


def afficher_carte():
    st.header("La carte des kayous")
    st.write("Voici la carte des affleurements et des échantillons.")
    st.write("Vous pouvez modifier la carte et rajouter des points ! Pour ajouter une photo dans la description d'un point, déposez-la en dessous de la carte et copiez le code obtenu dans la description.")

    map_url = "https://umap.openstreetmap.fr/fr/map/la-carte-des-kayous_1135136"
    st.iframe(map_url, height=650)
    st.subheader("Uploadez une photo et récupérez le lien direct")
    uploader_image()

    st.write("By Edouard Azoulay")


def afficher_objectif():
    st.header("Objectif")
    st.write("Ce projet est un identificateur de roche, une carte géologique participative et un dictionnaire des termes géologiques.")
    st.write("Le premier permet d'identifier les roches du programme de BCPST en suivant une clef d'identification. Cela a pour but d'aider les étudiants de cette filière à développer leurs capacités à reconnaître les roches. L'ensemble de ce site est codé en python et le programme est en open source sur Github.")
    st.markdown("https://github.com/edouardooo/Identificateur-de-roche")
    st.write("La deuxième partie du projet est une carte participative qui permet de localiser des affleurements ou des structures d'intérêt géologique.")
    st.write("La dernière partie du projet est un dictionnaire des termes géologiques. Il est participatif et les utilisateurs peuvent faire des suggestions de modifications qui seront validées ou non par les administrateurs.")
    st.write("À plus long terme, le but est de réaliser la reconnaissance de roche grâce à de la reconnaissance d'image via du deep learning.")
    st.write("By Edouard Azoulay")


def afficher_resultat(roche):
    nom = roche[-1]
    if nom == NON_IDENTIFIEE:
        st.warning("Aucune roche de la clé ne correspond à ces réponses. Vérifiez-les : "
                   "il s'agit peut-être aussi d'une roche que la clé ne connaît pas encore.")
        return

    st.subheader("Roche identifiée : " + nom[0].upper() + nom[1:])
    st.caption("Classification : " + " › ".join(roche[:-1]))

    entree = definition_roche(roche)
    if entree is not None:
        if entree["terme"].lower() == nom:
            st.write(entree["definition"])
        else:
            st.write(f"**{entree['terme']}** : {entree['definition']}")

    photo = DOSSIER_PHOTOS / (" ".join(roche) + ".jpg")
    if photo.exists():
        st.image(str(photo), width="stretch")
    else:
        st.info("Pas encore de photo pour cette roche sur ce site.")

    lien = lien_lithotheque(nom)
    if lien is not None:
        st.markdown(f"🔎 [Voir les échantillons de {nom} de la lithothèque de l'ENS de Lyon]({lien})")
    st.write("Toutes les images sont issues de la lithothèque de l'ENS de Lyon :")
    st.markdown("https://lithotheque.ens-lyon.fr/index.php")


def identificateur_de_rochee():
    st.title("Identificateur de roche")
    st.write("Répondez aux questions suivantes pour identifier la roche que vous étudiez.")

    type_roche = st.radio("La roche est-elle sédimentaire, magmatique ou métamorphique ?",
                          ["sédimentaire", "magmatique", "métamorphique"],
                          index=None, key="type_roche")
    if type_roche is None:
        return

    roche = [type_roche]
    if type_roche == "sédimentaire":
        identificationsedimentaire(roche)
    elif type_roche == "magmatique":
        identificationmagmatique(roche)
    else:
        identificationmetamorphique(roche)

    afficher_resultat(roche)
    st.write("By Edouard Azoulay")


def main():
    st.set_page_config(page_title="Identificateur de roche", page_icon="🪨")
    st.sidebar.title("Menu de Navigation")
    menu = st.sidebar.selectbox("Choisir une section", ["Identificateur", "La carte des kayous", "Dictionnaire", "Objectif"])
    if menu == "Identificateur":
        identificateur_de_rochee()
    if menu == "La carte des kayous":
        afficher_carte()
    if menu == "Objectif":
        afficher_objectif()
    if menu == "Dictionnaire":
        afficher_dico()
        sugestions_dico(table_airtable())


if __name__ == "__main__":
    main()
