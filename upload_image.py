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
    # Variable pour vérifier si une image a déjà été téléchargée
    if 'image_url' not in st.session_state:
        st.session_state.image_url = None

    uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        # Si une nouvelle image est téléchargée, upload à Cloudinary et récupère le lien
        response = cloudinary.uploader.upload(uploaded_file)
        st.session_state.image_url = response['secure_url']  # Enregistrer le lien dans le state de session
        
        # Création de 2 colonnes pour afficher l'image et le lien côte à côte
        col1, col2 = st.columns([2, 3])  # Ajuste la largeur des colonnes si nécessaire
        
        with col1:
            # Affichage de l'image en petit pendant le chargement
            st.image(uploaded_file, caption="Image en cours de chargement", width=150)
        
        with col2:
            # Affichage du lien direct sous le titre
            st.subheader("Voici le lien direct de votre image:")
            st.markdown(f"**Lien direct:** {{ {st.session_state.image_url} }}")
            
            # Ajout du bouton pour copier le lien
            if st.button('Copier le lien'):
                # JavaScript pour copier le texte dans le presse-papiers
                st_javascript(f"""
                const textToCopy = '{{ {st.session_state.image_url} }}';
                navigator.clipboard.writeText(textToCopy).then(function() {{
                    alert('Lien copié dans le presse-papiers !');
                }}).catch(function(err) {{
                    console.error('Erreur lors de la copie dans le presse-papiers: ', err);
                }});
                """)

        st.success("Image uploadée avec succès !")
    elif st.session_state.image_url:
        # Si une image a déjà été téléchargée précédemment, ne pas redemander à l'utilisateur
        st.image(st.session_state.image_url, caption="Image précédente", width=150)
        st.subheader("Voici le lien direct de votre image:")
        st.markdown(f"**Lien direct:** {{ {st.session_state.image_url} }}")

        # Ajout du bouton pour copier le lien
        if st.button('Copier le lien'):
            # JavaScript pour copier le texte dans le presse-papiers
            st_javascript(f"""
            const textToCopy = '{{ {st.session_state.image_url} }}';
            navigator.clipboard.writeText(textToCopy).then(function() {{
                alert('Lien copié dans le presse-papiers !');
            }}).catch(function(err) {{
                console.error('Erreur lors de la copie dans le presse-papiers: ', err);
            }});
            """)

    else:
        st.warning("Veuillez télécharger une image.")
