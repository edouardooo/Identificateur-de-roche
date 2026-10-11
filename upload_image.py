import cloudinary
import cloudinary.exceptions
import cloudinary.uploader
import streamlit as st

from configuration import secret


def configurer_cloudinary():
    """Configure Cloudinary avec les secrets. Renvoie False s'ils ne sont pas configurés."""
    cloud_name = secret("cloudinary_cloud_name")
    api_key = secret("cloudinary_api_key")
    api_secret = secret("cloudinary_api_secret")
    if not (cloud_name and api_key and api_secret):
        return False
    cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret, secure=True)
    return True


def uploader_image():
    if not configurer_cloudinary():
        st.info("L'envoi de photos est momentanément désactivé.")
        return

    uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])
    if uploaded_file is None:
        return

    # On n'envoie l'image à Cloudinary qu'une fois par fichier : sans ce test, chaque clic
    # sur la page la renverrait, et avec un simple « déjà envoyé ? » une deuxième image
    # afficherait le lien de la première.
    deja_envoyee = st.session_state.get("image_envoyee")
    if deja_envoyee is None or deja_envoyee["fichier"] != uploaded_file.file_id:
        try:
            with st.spinner("Envoi de l'image…"):
                response = cloudinary.uploader.upload(uploaded_file)
        except cloudinary.exceptions.Error:
            st.error("❌ L'image n'a pas pu être envoyée. Réessayez plus tard.")
            return
        st.session_state.image_envoyee = {"fichier": uploaded_file.file_id,
                                          "url": response["secure_url"]}

    image_url = st.session_state.image_envoyee["url"]
    col1, col2 = st.columns([2, 3])
    with col1:
        st.image(uploaded_file, width=150)
    with col2:
        st.success("Image envoyée !")
        st.write("Copiez ce code (bouton à droite) et collez-le dans la description du point :")
        st.code("{{" + image_url + "}}", language=None)
