import streamlit as st
import cloudinary.uploader
import cloudinary.api
import requests


# Configure Cloudinary avec votre API Key et API Secret
cloudinary.config(
    cloud_name="dmyghvwnw",  # Remplacez par votre cloud_name
    api_key="432933417465676",        # Remplacez par votre api_key
    api_secret="ma9Y1jITjIZCxjOqtTVnzT3cg2s"   # Remplacez par votre api_secret
)

def uploader_image():
    uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        # Affichage de l'image en petit pendant le chargement
        st.image(uploaded_file, caption="Image en cours de chargement", width=150)
        
        # Envoi à Cloudinary
        st.write("Envoi en cours...")
        
        # Upload image à Cloudinary
        response = cloudinary.uploader.upload(uploaded_file)
        
        # Récupérer l'URL de l'image
        image_url = response['secure_url']
        
        # Affichage du lien direct de l'image sous le titre
        st.subheader("Voici le lien direct de votre image:")
        st.write(f"{{{{ {image_url} }}}}")  # Affichage dans le format demandé
        
        # Affichage de l'image dans son format original
        st.image(image_url, caption="Image uploadée", use_container_width=True)
        
        st.success("Image uploadée avec succès !")
    else:
        st.warning("Veuillez télécharger une image.")
