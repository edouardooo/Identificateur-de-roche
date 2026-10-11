import csv
import unicodedata
from pathlib import Path

import requests
import streamlit as st
from pyairtable import Api

from configuration import secret

# Termes de base du dictionnaire, livrés avec le site (modifiable avec un tableur)
FICHIER_BASE = Path(__file__).parent / "dictionnaire_base.csv"


def sans_accents(texte):
    """« Éclogite » -> « Eclogite », pour trier et rechercher sans se soucier des accents."""
    decompose = unicodedata.normalize("NFD", texte)
    return "".join(c for c in decompose if not unicodedata.combining(c))


@st.cache_data
def termes_de_base():
    with open(FICHIER_BASE, encoding="utf-8-sig", newline="") as f:
        return [{"terme": ligne["terme"], "definition": ligne["définition"]}
                for ligne in csv.DictReader(f)]


def table_airtable():
    """Table Airtable des propositions, ou None si les secrets Airtable ne sont pas configurés."""
    token, base_id, nom_table = secret("airtable_token"), secret("base_id"), secret("table_name")
    if not (token and base_id and nom_table):
        return None
    return Api(token).table(base_id, nom_table)


@st.cache_data(ttl=600, show_spinner=False)
def termes_valides_airtable():
    """Propositions des visiteurs validées par un administrateur (rechargées toutes les 10 minutes)."""
    table = table_airtable()
    if table is None:
        return []
    termes = []
    for rec in table.all(formula="{validé}"):
        fields = rec["fields"]
        if "terme" in fields and "définition" in fields:
            termes.append({"terme": fields["terme"].strip(), "definition": fields["définition"]})
    return termes


def definition_roche(roche):
    """Entrée du dictionnaire de base pour le terme le plus précis du chemin d'identification.

    Ex. : pour ["sédimentaire", "détritique", "rudite", "galets et graviers"], si
    « galets et graviers » n'est pas dans le dictionnaire, on renvoie « Rudite »."""
    index = {sans_accents(t["terme"]).lower(): t for t in termes_de_base()}
    for nom in reversed(roche):
        for cle in (nom, "roche " + nom):
            terme = index.get(sans_accents(cle).lower())
            if terme:
                return terme
    return None


def afficher_dico():
    st.title("📘 Dictionnaire des termes géologiques")

    # Une proposition validée remplace la définition de base du même terme
    termes = {sans_accents(t["terme"]).lower(): t for t in termes_de_base()}
    try:
        for t in termes_valides_airtable():
            termes[sans_accents(t["terme"]).lower()] = t
    except requests.RequestException:
        st.warning("Les termes proposés par les visiteurs n'ont pas pu être chargés (Airtable injoignable).")

    # Tri alphabétique
    termes = sorted(termes.values(), key=lambda t: sans_accents(t["terme"]).lower())

    # Barre de recherche
    search = sans_accents(st.text_input("🔍 Rechercher un terme").strip().lower())

    # Navigation par lettre
    lettres = sorted({sans_accents(t["terme"][0]).upper() for t in termes if t["terme"]})
    lettre_sel = st.selectbox("🔠 Filtrer par lettre", options=["Toutes"] + lettres)

    # Filtrage
    filtrés = [
        t for t in termes
        if (search in sans_accents(t["terme"]).lower())
        and (lettre_sel == "Toutes" or sans_accents(t["terme"]).upper().startswith(lettre_sel))
    ]

    # Affichage
    st.caption(f"{len(filtrés)} terme(s) sur {len(termes)}")
    if not filtrés:
        st.info("Aucun terme trouvé.")
    else:
        for t in filtrés:
            st.markdown(f"### {t['terme']}")
            st.markdown(t["definition"])
            st.markdown("---")


def sugestions_dico(table):
    st.title("✍️ Proposer un terme géologique")

    if table is None:
        st.info("Les propositions de termes sont momentanément désactivées.")
        return

    with st.form("proposition_terme", clear_on_submit=True):
        terme = st.text_input("Terme")
        definition = st.text_area("Définition")
        image_url = st.text_input("Lien vers une image (optionnel)").strip()
        propose_par = st.text_input("Ton nom ou email")

        submitted = st.form_submit_button("Envoyer la proposition")

        if submitted:
            if not (terme and definition):
                st.warning("⚠️ Merci de remplir au moins le terme et la définition.")
            elif image_url and not image_url.startswith(("http://", "https://")):
                st.warning("⚠️ Le lien de l'image doit commencer par http:// ou https://")
            else:
                try:
                    table.create({
                        "terme": terme.strip(),
                        "définition": definition.strip(),
                        "proposé_par": propose_par.strip(),
                        "image": [{"url": image_url}] if image_url else [],
                        "validé": False
                    })
                    st.success("✅ Proposition envoyée ! Elle sera ajoutée si elle est validée.")
                except requests.RequestException:
                    st.error("❌ La proposition n'a pas pu être envoyée. Réessayez plus tard.")
