import streamlit as st
import sqlite3
from pyairtable import Table


def afficher_dico():
   st.title("Dictionnaire des termes géologiques")
   

   # Config Airtable
   API_KEY = "ta_api_key"
   BASE_ID = "ta_base_id"
   TABLE_NAME = "Termes"
   table = Table(API_KEY, BASE_ID, TABLE_NAME)

   st.title("Proposer un terme géologique")

   with st.form("proposition_terme"):
       terme = st.text_input("Terme")
       definition = st.text_area("Définition")
       image_url = st.text_input("Lien vers une image (optionnel)")
       propose_par = st.text_input("Ton nom ou email")

       submitted = st.form_submit_button("Envoyer la proposition")

       if submitted:
           if terme and definition:
               table.create({
                   "terme": terme,
                   "définition": definition,
                   "proposé_par": propose_par,
                   "image": [{"url": image_url}] if image_url else [],
                   "validé": False  # par défaut non validé
               })
               st.success("Proposition envoyée ! Elle sera ajoutée si elle est validée.")
           else:
               st.warning("Merci de remplir au moins le terme et la définition.")

   
