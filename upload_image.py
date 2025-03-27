import streamlit as st
import cloudinary.uploader
import cloudinary.api
import streamlit.components.v1 as components

# Configure Cloudinary avec vos informations
cloudinary.config(
    cloud_name="dmyghvwnw",        # Remplacez par votre cloud_name
    api_key="432933417465676",      # Remplacez par votre api_key
    api_secret="ma9Y1jITjIZCxjOqtTVnzT3cg2s"  # Remplacez par votre api_secret
)

def uploader_image():
    # Utilisation de session_state pour stabiliser l'URL
    if 'image_url' not in st.session_state:
        st.session_state.image_url = None

    uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        # On charge l'image et on l'upload vers Cloudinary une seule fois
        if st.session_state.image_url is None:
            response = cloudinary.uploader.upload(uploaded_file)
            st.session_state.image_url = response['secure_url']
        
        # Création de 2 colonnes pour afficher l'image et le lien côte à côte
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.image(uploaded_file, caption="Image en cours de chargement", width=150)
        
        with col2:
            st.subheader("Voici le lien direct de votre image:")
            # Affichage du lien formaté avec accolades
            st.markdown(f"**Lien direct:** {{ {st.session_state.image_url} }}")
            
            # Création d'un composant HTML pour copier le lien dans le presse-papiers
            # Le champ de texte est en lecture seule et contient le lien avec les accolades
            html_code = f"""
            <input type="text" value="{{ {st.session_state.image_url} }}" id="myInput" style="width:80%; padding:5px;" readonly>
            <button onclick="copyText()" style="padding:5px;">Copier le lien</button>
            <script>
            function copyText() {{
                var copyText = document.getElementById("myInput");
                copyText.select();
                copyText.setSelectionRange(0, 99999); /* Pour mobile */
                document.execCommand("copy");
                alert("Lien copié: " + copyText.value);
            }}
            </script>
            """
            components.html(html_code, height=100)
        
        st.success("Image uploadée avec succès !")
    elif st.session_state.image_url:
        # Si une image a déjà été uploadée, on affiche son lien
        st.image(st.session_state.image_url, caption="Image précédente", width=150)
        st.subheader("Voici le lien direct de votre image:")
        st.markdown(f"**Lien direct:** {{ {st.session_state.image_url} }}")
        
        html_code = f"""
        <input type="text" value="{{ {st.session_state.image_url} }}" id="myInput" style="width:80%; padding:5px;" readonly>
        <button onclick="copyText()" style="padding:5px;">Copier le lien</button>
        <script>
        function copyText() {{
            var copyText = document.getElementById("myInput");
            copyText.select();
            copyText.setSelectionRange(0, 99999);
            document.execCommand("copy");
            alert("Lien copié: " + copyText.value);
        }}
        </script>
        """
        components.html(html_code, height=100)
    else:
        st.warning("Veuillez télécharger une image.")
