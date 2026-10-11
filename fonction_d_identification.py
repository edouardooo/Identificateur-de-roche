import urllib.parse

import streamlit as st

# Résultat affiché quand aucune roche de la clé ne correspond aux réponses
NON_IDENTIFIEE = "non identifiée"

# Recherche à lancer sur la lithothèque de l'ENS de Lyon pour chaque roche
# (une recherche renvoie la liste de leurs échantillons, avec photos).
# Les roches absentes de ce dictionnaire n'ont pas d'échantillon sur leur site.
RECHERCHES_LITHOTHEQUE = {
    "tourbe": "tourbe",
    "houille": "charbon",
    "brèche": "breche",
    "poudingue": "poudingue",
    "sable": "sable",
    "grès": "gres",
    "arkose": "arkose",
    "argilite": "argilite",
    "siltite": "siltite",
    "argile ou silt": "argile",
    "calcaire": "calcaire",
    "craie": "craie",
    "marne": "marne",
    "dolomie": "dolomie",
    "radiolarite": "radiolarite",
    "silex": "silex",
    "diatomite": "diatomite",
    "halite": "halite",
    "sylvite": "sylvite",
    "gypse en fer de lance": "gypse",
    "gypse saccharoïde": "gypse",
    "bauxite": "bauxite",
    "obsidienne": "obsidienne",
    "ponce": "ponce",
    "rhyolite": "rhyolite",
    "trachyte": "trachyte",
    "andésite": "andesite",
    "basalte": "basalte",
    "granite": "granite",
    "granodiorite": "granodiorite",
    "diorite": "diorite",
    "gabbro": "gabbro",
    "péridotite": "peridotite",
    "marbre": "marbre",
    "éclogite": "eclogite",
    "migmatite": "migmatite",
    "micaschiste": "micaschiste",
    "gneiss": "gneiss",
    "schiste bleu": "schiste bleu",
    "amphibolite": "amphibolite",
    "quartzite": "quartzite",
    "cornéenne": "corneenne",
}


def lien_lithotheque(nom_roche):
    """Lien vers les échantillons de cette roche sur la lithothèque ENS de Lyon, ou None."""
    recherche = RECHERCHES_LITHOTHEQUE.get(nom_roche)
    if recherche is None:
        return None
    return ("https://lithotheque.ens-lyon.fr/Lithotheque/FormRech/cindex.php?Type="
            + urllib.parse.quote(recherche))


def question(roche, texte):
    """Pose une question oui/non. Arrête la page tant que l'utilisateur n'a pas répondu.

    La clé du bouton contient le chemin déjà parcouru : deux questions identiques
    dans deux branches différentes de la clé ne partagent donc pas leur réponse."""
    reponse = st.radio(texte, ["oui", "non"], index=None, horizontal=True,
                       key=" > ".join(roche) + " | " + texte)
    if reponse is None:
        st.stop()
    return reponse == "oui"


def identificationsedimentaire(roche):
    if question(roche, "La roche est-elle noire ou brun foncé, légère, d'aspect charbonneux ou faite de débris végétaux ?"):
        roche.append("carbonée")
        if question(roche, "Est-ce un liquide noir, visqueux et odorant ?"):
            roche.append("pétrole")
        elif question(roche, "Voit-on des débris végétaux peu transformés (mousses, fibres) ? La roche est-elle légère et spongieuse ?"):
            roche.append("tourbe")
        elif question(roche, "La roche est-elle brune et mate, avec parfois des restes de bois reconnaissables ?"):
            roche.append("lignite")
        elif question(roche, "La roche est-elle noire et tache-t-elle les doigts ?"):
            roche.append("houille")
        else:
            roche.append("anthracite")
    elif question(roche, "Voit-on à l'œil nu des grains ou des fragments (sable, graviers, galets) arrachés à d'autres roches ?"):
        roche.append("détritique")
        if question(roche, "Les éléments sont-ils plus gros que 2 mm (graviers, galets, blocs) ?"):
            roche.append("rudite")
            if question(roche, "La roche est-elle meuble (les éléments ne sont pas soudés entre eux) ?"):
                roche.append("galets et graviers")
            elif question(roche, "Les éléments sont-ils anguleux ?"):
                roche.append("brèche")
            else:
                roche.append("poudingue")
        else:
            roche.append("arénite")
            if question(roche, "La roche est-elle meuble (les grains ne sont pas soudés entre eux) ?"):
                roche.append("sable")
            elif question(roche, "Voit-on de nombreux grains de feldspath (blancs ou roses, opaques, à faces planes) en plus du quartz ?"):
                roche.append("arkose")
            else:
                roche.append("grès")
    elif question(roche, "La roche fait-elle effervescence (elle mousse) à froid avec de l'acide chlorhydrique dilué ?"):
        roche.append("carbonatée")
        if question(roche, "La roche sent-elle la terre mouillée quand on souffle dessus, et l'acide laisse-t-il une trace boueuse d'argile ?"):
            roche.append("marne")
        elif question(roche, "La roche est-elle blanche, tendre, légère, et tache-t-elle les doigts comme une craie de tableau ?"):
            roche.append("craie")
        else:
            roche.append("calcaire")
    elif question(roche, "La roche fait-elle effervescence seulement à chaud, ou une fois réduite en poudre ?"):
        roche.append("carbonatée")
        roche.append("dolomie")
    elif question(roche, "La roche raye-t-elle le verre (roche très dure, à grain très fin, sans grains visibles) ?"):
        roche.append("biogène siliceuse")
        if question(roche, "La roche est-elle rouge lie-de-vin, souvent en bancs fins ?"):
            roche.append("radiolarite")
        else:
            roche.append("silex")
    elif question(roche, "La roche a-t-elle un goût salé ou amer quand on la goûte (elle se dissout dans l'eau) ?"):
        roche.append("évaporitique")
        if question(roche, "Le goût est-il simplement salé, comme le sel de cuisine ?"):
            roche.append("halite")
        else:
            roche.append("sylvite")
    elif question(roche, "La roche est-elle blanche, très légère (elle peut flotter), poreuse et friable ?"):
        roche.append("biogène siliceuse")
        roche.append("diatomite")
    elif question(roche, "La roche est-elle faite de cristaux (brillants, translucides ou en grains de sucre) si tendres qu'ils se rayent à l'ongle ?"):
        roche.append("évaporitique")
        roche.append("gypse")
        if question(roche, "Est-ce un cristal en forme de fer de lance (deux cristaux accolés en V) ?"):
            roche.append("gypse en fer de lance")
        else:
            roche.append("gypse saccharoïde")
    elif question(roche, "La roche est-elle à grain très fin (grains invisibles à l'œil nu), d'aspect terreux, et sent-elle la terre mouillée quand on souffle dessus ?"):
        roche.append("détritique")
        roche.append("lutite")
        if question(roche, "La roche est-elle meuble, ou devient-elle pâteuse dans l'eau ?"):
            roche.append("argile ou silt")
        elif question(roche, "La roche crisse-t-elle sous la dent (on sent de tout petits grains) ?"):
            roche.append("siltite")
        else:
            roche.append("argilite")
    elif question(roche, "La roche est-elle rouge-brun à blanchâtre, souvent formée de petites billes (pisolithes) ?"):
        roche.append("résiduelle")
        roche.append("bauxite")
    else:
        roche.append(NON_IDENTIFIEE)
    return roche


def identificationmagmatique(roche):
    if not question(roche, "La roche est-elle entièrement formée de cristaux jointifs, tous visibles à l'œil nu (structure grenue), sans pâte fine ni verre ?"):
        roche.append("volcanique")
        if question(roche, "La roche a-t-elle l'aspect d'un verre (brillante, cassure conchoïdale coupante) ?"):
            roche.append("obsidienne")
        elif question(roche, "La roche est-elle très légère, criblée de bulles, au point de flotter sur l'eau ?"):
            roche.append("ponce")
        elif question(roche, "La roche est-elle claire (blanche, rose ou rouge) et contient-elle de petits cristaux de quartz ?"):
            roche.append("rhyolite")
        elif question(roche, "La pâte est-elle claire (grise ou beige), rugueuse au toucher, avec des baguettes de feldspath potassique (sanidine, sans macles polysynthétiques) ?"):
            roche.append("trachyte")
        elif question(roche, "La roche est-elle grise, avec des cristaux de plagioclase blanc et d'amphibole ou de pyroxène noirs dans une pâte fine ?"):
            roche.append("andésite")
        else:
            roche.append("basalte")
    else:
        roche.append("plutonique")
        if question(roche, "La roche contient-elle du quartz (minéral gris et translucide qui ressemble à du gros sel et raye le verre) ?"):
            if question(roche, "Le feldspath potassique (souvent rose ou blanc laiteux, en grands cristaux) est-il abondant, accompagné de micas ?"):
                roche.append("granite")
            else:
                roche.append("granodiorite")
        elif question(roche, "La roche est-elle essentiellement verte (olivine), très dense, sans feldspath blanc ?"):
            roche.append("péridotite")
        elif question(roche, "Les minéraux sombres sont-ils surtout des amphiboles (baguettes noires brillantes) mêlées à du plagioclase blanc, donnant un aspect « poivre et sel » ?"):
            roche.append("diorite")
        else:
            roche.append("gabbro")
    return roche


def identificationmetamorphique(roche):
    if question(roche, "La roche fait-elle effervescence à l'acide chlorhydrique dilué ?"):
        roche.append("marbre")
    elif question(roche, "La roche contient-elle beaucoup de grenats rouges dans une masse de pyroxène vert (omphacite) ?"):
        roche.append("éclogite")
    elif question(roche, "La roche mélange-t-elle des zones foliées sombres et des zones grenues claires, comme un granite en train de se former ?"):
        roche.append("migmatite")
    elif question(roche, "La roche a-t-elle une foliation bien marquée (feuillets ou lits parallèles) ?"):
        if question(roche, "La roche est-elle à grain très fin et se débite-t-elle en plaques fines et régulières ?"):
            roche.append("ardoise")
        elif question(roche, "La roche est-elle très brillante, avec beaucoup de micas et peu de feldspaths ?"):
            roche.append("micaschiste")
        elif question(roche, "Voit-on une alternance de lits sombres (micas) et de lits clairs (quartz et feldspaths) ?"):
            roche.append("gneiss")
        elif question(roche, "La roche a-t-elle une teinte bleutée (glaucophane), souvent avec des grenats rouges ou de l'épidote vert-jaune ?"):
            roche.append("schiste bleu")
        elif question(roche, "La roche est-elle sombre (vert-noir), faite surtout d'amphiboles noires (hornblende) et de plagioclase ?"):
            roche.append("amphibolite")
        else:
            roche.append(NON_IDENTIFIEE)
    elif question(roche, "La roche est-elle claire et très dure (raye le verre), faite de grains de quartz soudés (la cassure traverse les grains) ?"):
        roche.append("quartzite")
    elif question(roche, "La roche est-elle sombre, très dure, à grain très fin, parfois avec des taches ou des baguettes de minéraux (andalousite) ?"):
        roche.append("cornéenne")
    else:
        roche.append(NON_IDENTIFIEE)
    return roche
