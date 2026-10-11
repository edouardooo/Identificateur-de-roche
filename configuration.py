import streamlit as st


def secret(nom):
    """Valeur d'un secret, ou None s'il n'est pas configuré.

    Les secrets (clés Airtable et Cloudinary) ne doivent jamais être écrits dans le code :
    en local ils vont dans .streamlit/secrets.toml (ignoré par git), en ligne dans les
    réglages « Secrets » de l'application sur Streamlit Cloud."""
    try:
        return st.secrets[nom]
    except (KeyError, FileNotFoundError):
        return None
