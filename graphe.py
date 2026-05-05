"""Fonctions de base pour charger un réseau et le transformer en graphe.

Le graphe est représenté avec une liste d'adjacence :

    station -> liste des stations voisines

Chaque voisin contient aussi le temps de trajet et la ligne utilisée.
Cette représentation est simple et pratique pour un réseau de transport,
car chaque station n'est reliée qu'à quelques autres stations.
"""

import json
import os


def lister_fichiers_reseaux(dossier="donnees"):
    """Renvoie la liste des fichiers JSON disponibles dans le dossier."""
    fichiers = []

    if not os.path.isdir(dossier):
        return fichiers

    for nom in os.listdir(dossier):
        if nom.endswith(".json"):
            fichiers.append(os.path.join(dossier, nom))

    fichiers.sort()
    return fichiers


def charger_reseau(chemin):
    """Charge un fichier JSON et renvoie les données du réseau."""
    with open(chemin, "r", encoding="utf-8") as fichier:
        return json.load(fichier)


def ajouter_connexion(graphe, depart, arrivee, temps, ligne):
    """Ajoute une connexion dans la liste d'adjacence."""
    if depart not in graphe:
        graphe[depart] = []

    if arrivee not in graphe:
        graphe[arrivee] = []

    graphe[depart].append(
        {
            "station": arrivee,
            "temps": temps,
            "ligne": ligne,
        }
    )


def construire_graphe(reseau):
    """Construit un graphe pondéré à partir des données du réseau.

    Certains fichiers donnent directement les connexions.
    D'autres donnent seulement l'ordre des stations sur chaque ligne.
    Dans ce cas, on crée les connexions entre deux stations consécutives.
    """
    graphe = {}
    lignes = reseau.get("lignes", {})

    for ligne in lignes.values():
        for station in ligne.get("stations", []):
            if station not in graphe:
                graphe[station] = []

    connexions = reseau.get("connexions", [])

    if connexions:
        for connexion in connexions:
            ajouter_connexion(
                graphe,
                connexion["de"],
                connexion["vers"],
                connexion["temps"],
                connexion["ligne"],
            )
    else:
        temps_moyen = reseau.get("temps_moyen", 120)

        for code_ligne, ligne in lignes.items():
            stations = ligne.get("stations", [])

            for i in range(len(stations) - 1):
                depart = stations[i]
                arrivee = stations[i + 1]

                ajouter_connexion(graphe, depart, arrivee, temps_moyen, code_ligne)
                ajouter_connexion(graphe, arrivee, depart, temps_moyen, code_ligne)

    return graphe


def voisins_simples(graphe, station):
    """Renvoie les voisins d'une station sans répéter les doublons."""
    voisins = []

    for connexion in graphe.get(station, []):
        voisin = connexion["station"]
        if voisin not in voisins:
            voisins.append(voisin)

    return voisins


def bfs(graphe, depart):
    """Parcours en largeur depuis une station de départ."""
    if depart not in graphe:
        return []

    couleur = {}
    for station in graphe:
        couleur[station] = "blanc"

    chemin = []
    couleur[depart] = "gris"
    file = [depart]

    while file:
        station = file[0]
        chemin.append(station)

        for voisin in voisins_simples(graphe, station):
            if couleur[voisin] == "blanc":
                couleur[voisin] = "gris"
                file.append(voisin)

        file.pop(0)
        couleur[station] = "noir"

    return chemin


def dfs(graphe, depart):
    """Parcours en profondeur depuis une station de départ."""
    if depart not in graphe:
        return []

    couleur = {}
    for station in graphe:
        couleur[station] = "blanc"

    chemin = [depart]
    couleur[depart] = "gris"
    pile = [depart]

    while pile:
        station = pile[-1]
        voisins_blancs = []

        for voisin in voisins_simples(graphe, station):
            if couleur[voisin] == "blanc":
                voisins_blancs.append(voisin)

        if voisins_blancs:
            voisin = voisins_blancs[0]
            couleur[voisin] = "gris"
            chemin.append(voisin)
            pile.append(voisin)
        else:
            pile.pop()
            couleur[station] = "noir"

    return chemin


def est_connexe(graphe):
    """Vérifie si toutes les stations sont accessibles entre elles."""
    if not graphe:
        return False

    premiere_station = list(graphe.keys())[0]
    stations_visitees = bfs(graphe, premiere_station)

    return len(stations_visitees) == len(graphe)


def trouver_correspondances(reseau):
    """Renvoie les stations de correspondance indiquées dans le JSON."""
    correspondances = {}

    for correspondance in reseau.get("correspondances", []):
        station = correspondance["station"]
        lignes = correspondance.get("lignes", [])
        correspondances[station] = lignes

    return correspondances


def stations_du_reseau(graphe):
    """Renvoie les stations du graphe dans l'ordre alphabétique."""
    stations = list(graphe.keys())
    stations.sort()
    return stations
