"""Calcul du meilleur itinéraire avec l'algorithme de Dijkstra."""

import heapq


def temps_de_correspondance(reseau, station):
    """Renvoie le temps de correspondance pour une station.

    Les fichiers fournis utilisent presque toujours 120 secondes.
    Si la station n'est pas trouvée dans la liste, on garde 120 secondes
    comme valeur simple par défaut.
    """
    for correspondance in reseau.get("correspondances", []):
        if correspondance.get("station") == station:
            return correspondance.get("temps", 120)

    return 120


def dijkstra(graphe, reseau, depart, arrivee):
    """Calcule le trajet le plus court en temps entre deux stations.

    L'état contient la station actuelle et la ligne utilisée pour arriver.
    Cela permet d'ajouter un temps de correspondance quand la ligne change.
    """
    if depart not in graphe or arrivee not in graphe:
        return {"trouve": False, "temps": None, "chemin": []}

    if depart == arrivee:
        return {
            "trouve": True,
            "temps": 0,
            "chemin": [{"station": depart, "ligne": None}],
        }

    depart_etat = (depart, None)
    distances = {depart_etat: 0}
    parents = {}
    file = [(0, depart, None)]
    visites = set()

    while file:
        temps_actuel, station, ligne_actuelle = heapq.heappop(file)
        etat = (station, ligne_actuelle)

        if etat in visites:
            continue

        visites.add(etat)

        if station == arrivee and ligne_actuelle is not None:
            return reconstruire_resultat(parents, etat, temps_actuel)

        for connexion in graphe[station]:
            voisin = connexion["station"]
            nouvelle_ligne = connexion["ligne"]
            nouveau_temps = temps_actuel + connexion["temps"]

            if ligne_actuelle is not None and nouvelle_ligne != ligne_actuelle:
                nouveau_temps += temps_de_correspondance(reseau, station)

            nouvel_etat = (voisin, nouvelle_ligne)

            if nouveau_temps < distances.get(nouvel_etat, float("inf")):
                distances[nouvel_etat] = nouveau_temps
                parents[nouvel_etat] = etat
                heapq.heappush(file, (nouveau_temps, voisin, nouvelle_ligne))

    return {"trouve": False, "temps": None, "chemin": []}


def reconstruire_resultat(parents, etat_final, temps_total):
    """Reconstruit le chemin à partir du dictionnaire des parents."""
    chemin = []
    etat = etat_final

    while etat in parents:
        station, ligne = etat
        chemin.append({"station": station, "ligne": ligne})
        etat = parents[etat]

    station_depart, ligne_depart = etat
    chemin.append({"station": station_depart, "ligne": ligne_depart})
    chemin.reverse()

    return {
        "trouve": True,
        "temps": temps_total,
        "chemin": chemin,
    }


def formater_temps(secondes):
    """Transforme un temps en secondes en texte lisible."""
    minutes = secondes // 60
    reste = secondes % 60

    if minutes == 0:
        return str(reste) + " secondes"

    if reste == 0:
        return str(minutes) + " minutes"

    return str(minutes) + " minutes " + str(reste) + " secondes"


def decrire_itineraire(resultat):
    """Prépare un affichage simple de l'itinéraire."""
    if not resultat["trouve"]:
        return "Aucun itinéraire trouvé."

    chemin = resultat["chemin"]

    if len(chemin) == 1:
        station = chemin[0]["station"]
        return "Vous êtes déjà à la station " + station + "."

    lignes = []
    premiere_ligne = chemin[1]["ligne"]
    derniere_ligne = chemin[-1]["ligne"]

    lignes.append("Monter station " + chemin[0]["station"] + ", ligne " + premiere_ligne)

    for i in range(1, len(chemin) - 1):
        station = chemin[i]["station"]
        ligne = chemin[i]["ligne"]
        ligne_suivante = chemin[i + 1]["ligne"]

        lignes.append("Continuer station " + station)

        if ligne_suivante != ligne:
            texte = "Correspondance station "
            texte += station
            texte += ", prendre la ligne "
            texte += ligne_suivante
            lignes.append(texte)

    lignes.append("Descendre station " + chemin[-1]["station"] + ", ligne " + derniere_ligne)
    lignes.append("")
    lignes.append("Temps total estimé : " + formater_temps(resultat["temps"]))

    return "\n".join(lignes)
