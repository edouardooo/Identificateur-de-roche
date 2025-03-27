import streamlit as st
import cloudinary
import cloudinary.uploader

import streamlit as st
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Configure Cloudinary avec votre API Key et API Secret
cloudinary.config(
    cloud_name="dmyghvwnw",  # Remplacez par votre cloud_name
    api_key="432933417465676",        # Remplacez par votre api_key
    api_secret="ma9Y1jITjIZCxjOqtTVnzT3cg2s"   # Remplacez par votre api_secret
)

def uploader_image():
    uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Image sélectionnée", use_container_width=True)

        # Envoi à Cloudinary
        st.write("Envoi en cours...")

        # Upload de l'image sur Cloudinary
        try:
            response = cloudinary.uploader.upload(uploaded_file)
            image_url = response['secure_url']
            st.success(f"Image uploadée ! Le lien direct de l'image est : {{ {image_url} }}")
        except Exception as e:
            st.error(f"Échec de l'upload : {e}")

# Fonction d'appel
uploader_image()
