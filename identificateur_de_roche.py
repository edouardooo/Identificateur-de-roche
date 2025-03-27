import streamlit as st
from streamlit_javascript import st_javascript
from fonction_d_identification import identificationsedimentaire,identificationmagmatique,identificationmetamorphique
from dictionnaire import afficher_dico
global roche
roche = []

def afficher_carte():
    st.header("La carte des kayous")
    st.write("Voici la carte des affleurements et des échantillons.")
    map_url = "https://umap.openstreetmap.fr/fr/map/la-carte-des-kayous_1135136"
    st.components.v1.html(f"""
        <style>
            .iframe-container {{
                width: 100%;
                height: 80vh; /* 80% de la hauteur de la fenêtre */
            }}
            .iframe {{
                width: 100%;
                height: 100%;
                border: none;
            }}
        </style>
        <div class="iframe-container">
            <iframe src="{map_url}" class="iframe"></iframe>
        </div>
    """, height=650)
    st.write("By Edouard Azoulay")

    import streamlit as st
    import requests

    # Clé API Imgur (remplace par ta clé)
    CLIENT_ID = "TON_CLIENT_ID"

    st.title("Uploader une photo sur Imgur")

    # Deux options : caméra ou fichier
    uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])
    camera_photo = st.camera_input("Ou prenez une photo")

    # Sélection de l'image (priorité à l'upload)
    image = uploaded_file if uploaded_file else camera_photo

    if image:
        st.image(image, caption="Image sélectionnée", use_container_width=True)

        # Envoi de l'image à Imgur
        st.write("Envoi en cours...")
        headers = {"Authorization": f"Client-ID {CLIENT_ID}"}
        files = {"image": image.getvalue()}

        response = requests.post("https://api.imgur.com/3/upload", headers=headers, files=files)

        if response.status_code == 200:
            image_url = response.json()["data"]["link"]
            st.success(f"Image uploadée ! [Voir l'image]({image_url})")
        else:
            st.error("Échec de l'upload")
            st.write(response.json())  # Debugging




def afficher_objectif():
    st.header("Objectif")
    st.write("Ce projet est un identificateur de roche, une carte géologique participative et un dictionnaire des termes géologiques.")
    st.write("Le premier permet d'identifier l'ensemble des roches du programme de BCPST en suivant une clef d'identification. Cela a pour but d'aider les étudiants de cette filière à développer leurs capacité à reconnaitre les roches. L'ensemble de ce site est codé en python et le programme est en open source sur Github.")
    st.markdown("https://github.com/edouardooo/Identificateur-de-roche")
    st.write("La deuxième partie du projet est une carte participative qui permet de localiser des affleurements ou des structures d'intérêt géologique.")
    st.write("La dernière partie du projet est un dictionnaire des termes géologiques. Il est participatif et les utilisateurs peuvent faire des sugestions de modifications qui seront validées ou non par les administrateurs.")
    st.write("A un plus long terme, le but est de réaliser la reconnaissance de roche grâce à de la reconnaissance d'image via du deep learning.")
    st.write("By Edouard Azoulay")

def identificateur_de_rochee():
    st.title("Identificateur de roche")
    st.write("Répondez aux questions suivantes pour identifier la roche que vous étudiez.")
    
    type_roche = st.radio("La roche est-elle sédimentaire, magmatique ou métamorphique ?", 
                          ["sédimentaire", "magmatique", "métamorphique"])
    roche.clear()
    if type_roche == "sédimentaire":
        roche.append("sédimentaire")
        result = identificationsedimentaire(roche)
    elif type_roche == "magmatique":
        roche.append("magmatique")
        result = identificationmagmatique(roche)
    else:
        roche.append("métamorphique")
        result = identificationmetamorphique(roche)
    
    st.write("**Roche Identifiée :**")
    st.write("La roche est",", ".join(result))
    
    image_url = "https://raw.githubusercontent.com/edouardooo/Identificateur-de-roche/refs/heads/main/photos/" + "%20".join(roche) + ".jpg"
    st.image(image_url, use_container_width=True)
    st.write("Toutes les images sont issues de la litothèque de l'ENS de Lyon:")
    st.markdown("https://lithotheque.ens-lyon.fr/index.php")
    st.write("By Edouard Azoulay")


    
def main():
    st.sidebar.title("Menu de Navigation")
    menu = st.sidebar.selectbox("Choisir une section", ["Identificateur", "La carte des kayous","Dictionnaire","Objectif"])
    if menu == "Identificateur":
        identificateur_de_rochee()
    if menu == "La carte des kayous":
        afficher_carte()
    if menu == "Objectif":
        afficher_objectif()
    if menu=="Dictionnaire":
       afficher_dico()
    
    
if __name__ == "__main__":
    main()
