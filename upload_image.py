import streamlit as st
from streamlit_javascript import st_javascript
import cloudinary.uploader
import cloudinary.api

# Configure Cloudinary avec vos informations
cloudinary.config(
    cloud_name="dmyghvwnw",        # Remplacez par votre cloud_name
    api_key="432933417465676",      # Remplacez par votre api_key
    api_secret="ma9Y1jITjIZCxjOqtTVnzT3cg2s"  # Remplacez par votre api_secret
)

def uploader_image():
    uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        # Upload de l'image sur Cloudinary
        response = cloudinary.uploader.upload(uploaded_file)
        image_url = response['secure_url']

        # Préparez le lien avec des accolades
        display_link = f"{{ {image_url} }}"

        # Création de 2 colonnes pour afficher l'image et le lien côte à côte
        col1, col2 = st.columns([2, 3])

        with col1:
            # Affichage de l'image en petit pendant le chargement
            st.image(uploaded_file, caption="Image en cours de chargement", width=150)

        with col2:
            # Affichage du lien direct sous le titre
            st.subheader("Voici le lien direct de votre image:")
            # Affichage du lien directement avec Streamlit (avec st.code)
            st.code(display_link)

            # Bouton en HTML pour copier le lien
            st.markdown(f"""
            <button onclick="navigator.clipboard.writeText('{display_link}'); alert('Lien copié !');">
                Copier le lien
            </button>
            """, unsafe_allow_html=True)

    else:
        st.warning("Veuillez télécharger une image.")


