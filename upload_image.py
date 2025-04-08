import streamlit as st
import cloudinary
import cloudinary.uploader
import cloudinary.api
import streamlit.components.v1 as components
from PIL import Image, ImageDraw, ImageFont
import io

# Configuration Cloudinary
cloudinary.config(
    cloud_name="dmyghvwnw",
    api_key="432933417465676",
    api_secret="ma9Y1jITjIZCxjOqtTVnzT3cg2s"
)

def ajouter_filigrane(image_bytes, texte_filigrane):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    filigrane = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(filigrane)

    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()

    x = 10
    y = image.height - font.getsize(texte_filigrane)[1] - 10
    draw.text((x, y), texte_filigrane, font=font, fill=(255, 255, 255, 180))

    image_finale = Image.alpha_composite(image, filigrane)
    output = io.BytesIO()
    image_finale.convert("RGB").save(output, format="JPEG")
    output.seek(0)
    return output

def uploader_image():
    if 'image_url' not in st.session_state:
        st.session_state.image_url = None

    st.title("Uploader une image avec ou sans signature")
    texte_filigrane = st.text_input("Entrez votre nom ou signature (optionnel)")

    uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image_bytes = uploaded_file.read()

        # Ajout du filigrane seulement si texte fourni
        if texte_filigrane.strip():
            image_a_uploader = ajouter_filigrane(image_bytes, texte_filigrane.strip())
        else:
            image_a_uploader = io.BytesIO(image_bytes)
            image_a_uploader.seek(0)

        if st.session_state.image_url is None:
            response = cloudinary.uploader.upload(image_a_uploader, resource_type="image")
            st.session_state.image_url = response['secure_url']

        col1, col2 = st.columns([2, 3])
        with col1:
            st.image(image_bytes, caption="Image affichée", width=150)
        with col2:
            st.subheader("Lien direct de votre image :")
            st.markdown(f"**Lien direct :** `{st.session_state.image_url}`")

            html_code = f"""
            <style>
            .copy-btn {{
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                font-size: 14px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 4px;
            }}
            </style>
            <button class="copy-btn" onclick="copyText()">Copier le lien</button>
            <script>
            function copyText() {{
                var copyText = "{st.session_state.image_url}";
                navigator.clipboard.writeText(copyText);
                alert("Lien copié : " + copyText);
            }}
            </script>
            """
            components.html(html_code, height=100)

        st.success("Image uploadée avec succès !")

    elif st.session_state.image_url:
        st.image(st.session_state.image_url, caption="Image précédente", width=150)
        st.markdown(f"**Lien direct :** `{st.session_state.image_url}`")

    else:
        st.warning("Veuillez télécharger une image.")
