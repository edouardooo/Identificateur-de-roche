import streamlit as st
from streamlit_javascript import st_javascript
from fonction_d_identification import identificationsedimentaire,identificationmagmatique,identificationmetamorphique
    
def afficher_carte():
    st.header("La carte des kayous")
    st.write("Voici la carte des affleurements et des échantillons.")
    map_url = "https://umap.openstreetmap.fr/fr/map/la-carte-des-kayous_1119639"
    st.components.v1.iframe(map_url, width="90%", height="90%")
    st.write("By Edouard Azoulay")


def afficher_objectif():
    st.header("Objectif")
    st.write("Ce projet est un identificateur de roche et une carte géologique participative.")
    st.write("Le premier permet d'identifier l'ensemble des roches du programme de BCPST en suivant une clef d'identification. Cela a pour but d'aider les étudiants de cette filière à développer leurs capacité à reconnaitre les roches. L'ensemble de ce site est codé en python et le programme est en open source sur Github.")
    st.markdown("https://github.com/edouardooo/Identificateur-de-roche")
    st.write("La deuxième partie du projet est une carte participative qui permet de localiser des affleurements ou des structures d'intérêt géologique.")
    st.write("A un plus long terme, le but est de réaliser la reconnaissance de roche grâce à de la reconnaissance d'image via du deep learning.")
    st.write("By Edouard Azoulay")

def identificateur_de_rochee():
    st.title("Identificateur de roche")
    st.write("Répondez aux questions suivantes pour identifier la roche que vous étudiez.")
    
    type_roche = st.radio("La roche est-elle sédimentaire, magmatique ou métamorphique ?", 
                          ["sédimentaire", "magmatique", "métamorphique"])
    
    if type_roche == "sédimentaire":
        roche.append("sédimentaire")
        result = identificationsedimentaire()
    elif type_roche == "magmatique":
        roche.append("magmatique")
        result = identificationmagmatique()
    else:
        roche.append("métamorphique")
        result = identificationmetamorphique()
    
    st.write("**Roche Identifiée :**")
    st.write("La roche est",", ".join(result))
    
    image_url = "https://raw.githubusercontent.com/edouardooo/Identificateur-de-roche/main/" + "%20".join(roche) + ".jpg"
    st.image("https://raw.githubusercontent.com/edouardooo/Identificateur-de-roche/main/" + "%20".join(roche) + ".jpg", use_column_width=True)
    st.write("Toutes les images sont issues de la litothèque de l'ENS de Lyon:")
    st.markdown("https://lithotheque.ens-lyon.fr/index.php")
    st.write("By Edouard Azoulay")
def main():
    st.sidebar.title("Menu de Navigation")
    menu = st.sidebar.selectbox("Choisir une section", ["Identificateur", "La carte des kayous", "Objectif"])
    if menu == "Identificateur":
        identificateur_de_rochee()
    if menu == "La carte des kayous":
        afficher_carte()
    if menu == "Objectif":
        afficher_objectif()
    
    
if __name__ == "__main__":
    main()
