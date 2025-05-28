import streamlit as st
from pyairtable import Table


def afficher_dico(table):
    st.title("📘 Dictionnaire des termes géologiques")

    table = Table(API_TOKEN, BASE_ID, TABLE_NAME)
    records = table.all(formula="IF({validé}, TRUE(), FALSE())")

    # Construction de la liste des entrées
    termes = []
    for rec in records:
        fields = rec["fields"]
        if "terme" in fields and "définition" in fields:
            termes.append({
                "terme": fields["terme"],
                "definition": fields["définition"]
            })

    # Tri alphabétique
    termes.sort(key=lambda x: x["terme"].lower())

    # Barre de recherche
    search = st.text_input("🔍 Rechercher un terme").strip().lower()

    # Navigation par lettre
    lettres = sorted({t["terme"][0].upper() for t in termes if t["terme"]})
    lettre_sel = st.selectbox("🔠 Filtrer par lettre", options=["Toutes"] + lettres)

    # Filtrage
    filtrés = [
        t for t in termes
        if (search in t["terme"].lower())
        and (lettre_sel == "Toutes" or t["terme"].upper().startswith(lettre_sel))
    ]

    # Affichage
    if not filtrés:
        st.info("Aucun terme trouvé.")
    else:
        for t in filtrés:
            st.markdown(f"### {t['terme']}")
            st.markdown(t["definition"])
            st.markdown("---")


def sugestions_dico(table):
    table = Table(API_TOKEN, BASE_ID, TABLE_NAME)
    
    st.title("✍️ Proposer un terme géologique")

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
                    "validé": False
                })
                st.success("✅ Proposition envoyée ! Elle sera ajoutée si elle est validée.")
            else:
                st.warning("⚠️ Merci de remplir au moins le terme et la définition.")


# Connexion Airtable globale
API_TOKEN = st.secrets["airtable_token"]
BASE_ID = st.secrets["base_id"]
TABLE_NAME = st.secrets["table_name"]
table = Table(API_TOKEN, BASE_ID, TABLE_NAME)

