from streamlit_javascript import st_javascript
import streamlit as st
import cloudinary.uploader
import cloudinary.api

# Configure Cloudinary avec votre API Key et API Secret
cloudinary.config(
    cloud_name="dmyghvwnw",  # Remplacez par votre cloud_name
    api_key="432933417465676",  # Remplacez par votre api_key
    api_secret="ma9Y1jITjIZCxjOqtTVnzT3cg2s"  # Remplacez par votre api_secret
)

def uploader_image():
    # Utilisation de session_state pour éviter que l'URL change
    if 'image_url' not in st.session_state:
        st.session_state.image_url = None

    uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        # Upload de l'image à Cloudinary uniquement une fois
        if st.session_state.image_url is None:
            response = cloudinary.uploader.upload(uploaded_file)
            st.session_state.image_url = response['secure_url']
        
        # Création de 2 colonnes pour afficher l'image et le lien côte à côte
        col1, col2 = st.columns([2, 3])  # Ajuste la largeur des colonnes si nécessaire
        
        with col1:
            # Affichage de l'image en petit pendant le chargement
            st.image(uploaded_file, caption="Image en cours de chargement", width=150)
        
        with col2:
            # Affichage du lien direct sous le titre
            st.subheader("Voici le lien direct de votre image:")
            st.markdown(f"**Lien direct:** {{ {st.session_state.image_url} }}")
            
            # Bouton pour copier le lien dans le presse-papiers
            if st.button('Copier le lien'):
                # Envoi d'un message pour indiquer que le lien a été copié
                st.success("Lien copié dans le presse-papi
