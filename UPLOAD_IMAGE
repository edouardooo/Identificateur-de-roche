import streamlit as st
import requests

CLIENT_ID = "00c6d0342204835"  # Remplace par ta vraie clé Imgur

def uploader_image():
    uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])
    camera_photo = st.camera_input("Ou prenez une photo")

    image = uploaded_file if uploaded_file else camera_photo

    if image:
        st.image(image, caption="Image sélectionnée", use_container_width=True)

        # Envoi à Imgur
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
