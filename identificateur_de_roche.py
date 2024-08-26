import streamlit as st

def identificationsedimentaire():
    if st.radio("La roche est-elle marron foncé ou noire ?", ["oui", "non"]) == "oui":
        roche.append("Carbonée")
        if st.radio("La roche présente-t-elle des fragments de végétaux ?", ["oui", "non"]) == "oui":
            roche.append("tourbe")
        elif st.radio("La roche est-elle liquide ?", ["oui", "non"]) == "oui":
            roche.append("pétrole")
        elif st.radio("La roche tache-t-elle les doigts ?", ["oui", "non"]) == "oui":
            roche.append("Houille")
        else:
            roche.append("lignite")
    elif st.radio("La roche ne présente pas d'éléments figurés ou ils sont issus d'êtres vivants ?", ["oui", "non"]) == "oui":
        if st.radio("La roche fait-elle effervescence à l'acide ?", ["oui", "non"]) == "oui":
            roche.append("Calcaire")
        elif st.radio("La roche raye-t-elle le verre ?", ["oui", "non"]) == "oui":
            roche.append("biogène siliceuse")
            if st.radio("La roche est-elle couleur lie de vin ?", ["oui", "non"]) == "oui":
                roche.append("radiolarite")
            else:
                roche.append("diatomite")
        else:
            roche.append("évaporitique")
            if st.radio("La roche est-elle rayable à l'ongle ?", ["oui", "non"]) == "oui":
                roche.append("Gypse")
                if st.radio("La roche a-t-elle une forme de pointe de lance ?", ["oui", "non"]) == "oui":
                    roche.append("Gypse fer de lance")
                else:
                    roche.append("Gypse saccharoïde")
            else:
                if st.radio("La roche est-elle orange ?", ["oui", "non"]) == "oui":
                    roche.append("sylvite KCl")
                else:
                    roche.append("halite NaCl")
    elif st.radio("La roche présente-t-elle des éléments figurés non issus d'êtres vivants ?", ["oui", "non"]) == "oui":
        roche.append("détritique")
        if st.radio("La taille des grains est-elle supérieure à 2mm ?", ["oui", "non"]) == "oui":
            roche.append("rudite")
            if st.radio("La roche est-elle meuble ?", ["oui", "non"]) == "oui":
                roche.append("blocs ou galets ou cailloutis")
            else:
                roche.append("conglomérat")
                if st.radio("La roche présente-t-elle des éléments anguleux ?", ["oui", "non"]) == "oui":
                    roche.append("brèche")
                else:
                    roche.append("poudingue")
        elif st.radio("La taille des éléments figurés est-elle entre 63μm et 2mm ?", ["oui", "non"]) == "oui":
            roche.append("arénite")
            if st.radio("La roche est-elle meuble ?", ["oui", "non"]) == "oui":
                roche.append("sable")
            else:
                if st.radio("La roche est-elle essentiellement faite de quartz et raye le verre ?", ["oui", "non"]) == "oui":
                    roche.append("grès")
                else:
                    roche.append("arkose")
        else:
            roche.append("lutite")
            if st.radio("La roche est-elle meuble ?", ["oui", "non"]) == "oui":
                roche.append("silts ou argiles")
            else:
                if st.radio("La roche happe-t-elle la langue ?", ["oui", "non"]) == "oui":
                    if st.radio("La roche fait-elle effervescence à l'acide ?", ["oui", "non"]) == "oui":
                        roche.append("marne")
                    else:
                        roche.append("pélite (argiles consolidés)")
                else:
                    roche.append("silite")
    else:
        roche.append("résiduelle")
        roche.append("beauxite")
    return roche

def identificationmagmatique():
    if st.radio("La roche est-elle grenue ?", ["oui", "non"]) == "non":
        roche.append("volcanique")
        if st.radio("La roche contient-elle du quartz ?", ["oui", "non"]) == "oui":
            roche.append("rhyolite")
        else:
            if st.radio("La roche contient-elle des feldspath potassiques (pâte claire, pas de macles polysynthétiques) ?", ["oui", "non"]) == "oui":
                roche.append("trachyte")
            else:
                if st.radio("Amphibole et biotite sont-ils fréquents ?", ["oui", "non"]) == "oui":
                    roche.append("andésite")
                else:
                    roche.append("basalte")
    else:
        roche.append("plutonique")
        if st.radio("La roche contient-elle du quartz (minéral qui ressemble à du gros sel et raye le verre) ?", ["oui", "non"]) == "oui":
            if st.radio("Micas fréquents (voir micas blanc) et feldspath potassique majoritaires ?", ["oui", "non"]) == "oui":
                roche.append("granite")
            else:
                roche.append("granodiorite")
        else:
            if st.radio("La roche contient-elle de l'olivine ?", ["oui", "non"]) == "oui":
                roche.append("péridotite")
            else:
                roche.append("gabbro")
    return roche

def identificationmetamorphique():
    if st.radio("La roche possède-t-elle des minéraux visibles à l'œil nu ?", ["oui", "non"]) == "oui":
        if st.radio("La roche a-t-elle une foliation très marquée ?", ["oui", "non"]) == "oui":
            if st.radio("La roche contient-elle des lits sombres (micas) et des lits clairs (quartz et feldspath) ?", ["oui", "non"]) == "oui":
                if st.radio("La roche est-elle très brillante, avec beaucoup de micas et peu de feldspaths ?", ["oui", "non"]) == "oui":
                    roche.append("micashiste")
                else:
                    roche.append("gneiss")
            elif st.radio("La roche est-elle sombre et contient des amphiboles noires (hornblende) ?", ["oui", "non"]) == "oui":
                roche.append("amphibolite")
            else:
                roche.append("schiste bleu")
        else:
            if st.radio("La roche présente-t-elle une abondance de grenat et de pyroxènes verts ?", ["oui", "non"]) == "oui":
                roche.append("éclogite")
            elif st.radio("La roche présente-t-elle une foliation que sur une partie, le reste est grenu, avec un mélange leucocrate et mélanocrate ?", ["oui", "non"]) == "oui":
                roche.append("migmatite")
            else:
                roche.append("cornéenne ou schiste tacheté")
    return roche

def main():
    st.title("Identificateur de roche")
    st.write("Répondez aux questions suivantes pour identifier la roche étudiée.")
    st.write("By Azoulay Edouard")
    
    global roche
    roche = []
    
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
    st.write(", ".join(result))

if __name__ == "__main__":
    main()
