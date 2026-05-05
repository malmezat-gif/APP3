"""Interface console du calculateur d'itinéraires."""

import os

from graphe import (
    charger_reseau,
    construire_graphe,
    est_connexe,
    lister_fichiers_reseaux,
    stations_du_reseau,
    trouver_correspondances,
)
from itineraire import decrire_itineraire, dijkstra
from visualisation import afficher_graphe


def nom_ville_depuis_chemin(chemin):
    """Transforme donnees/paris.json en paris."""
    nom = os.path.basename(chemin)
    return nom.replace(".json", "")


def trouver_station(nom_saisi, stations):
    """Trouve une station même si la casse n'est pas exactement la même."""
    if nom_saisi in stations:
        return nom_saisi

    nom_saisi_minuscule = nom_saisi.lower()

    for station in stations:
        if station.lower() == nom_saisi_minuscule:
            return station

    return None


def choisir_ville():
    """Demande à l'utilisateur de choisir un fichier de réseau."""
    fichiers = lister_fichiers_reseaux()

    if not fichiers:
        print("Aucun fichier JSON trouvé dans le dossier donnees.")
        return None

    print()
    print("Villes disponibles :")

    for i in range(len(fichiers)):
        print(str(i + 1) + ". " + nom_ville_depuis_chemin(fichiers[i]))

    while True:
        choix = input("Choisir une ville (ou q pour quitter) : ").strip()

        if choix.lower() == "q":
            return None

        if choix.isdigit():
            numero = int(choix)
            if 1 <= numero <= len(fichiers):
                return fichiers[numero - 1]

        print("Choix invalide.")


def demander_station(message, stations):
    """Demande une station et vérifie qu'elle existe."""
    while True:
        reponse = input(message).strip()

        if reponse == "?":
            print("Quelques stations disponibles :")
            for station in stations[:30]:
                print("- " + station)
            print("Il y a " + str(len(stations)) + " stations au total.")
            continue

        station = trouver_station(reponse, stations)

        if station is not None:
            return station

        print("Station inconnue. Tapez ? pour voir quelques exemples.")


def afficher_infos_reseau(reseau, graphe):
    """Affiche quelques informations simples sur le réseau choisi."""
    correspondances = trouver_correspondances(reseau)

    print()
    print("Réseau chargé :", reseau.get("nom", "sans nom"))
    print("Nombre de stations :", len(graphe))
    print("Nombre de correspondances :", len(correspondances))

    if est_connexe(graphe):
        print("Toutes les stations sont accessibles entre elles.")
    else:
        print("Attention : le réseau n'est pas entièrement connexe.")


def lancer():
    """Lance le menu principal."""
    print("Calculateur d'itinéraires APP3")

    while True:
        chemin_fichier = choisir_ville()

        if chemin_fichier is None:
            print("Fin du programme.")
            return

        try:
            reseau = charger_reseau(chemin_fichier)
            graphe = construire_graphe(reseau)
        except Exception as erreur:
            print("Impossible de charger le réseau :", erreur)
            continue

        afficher_infos_reseau(reseau, graphe)
        stations = stations_du_reseau(graphe)

        while True:
            print()
            print("Tapez le nom exact d'une station ou ? pour avoir des exemples.")
            depart = demander_station("Station de départ : ", stations)
            arrivee = demander_station("Station d'arrivée : ", stations)

            if depart == arrivee:
                print("La station de départ et d'arrivée est la même.")
                continue

            resultat = dijkstra(graphe, reseau, depart, arrivee)
            print()
            print(decrire_itineraire(resultat))

            if resultat["trouve"]:
                choix_graphe = input("Afficher le graphe ? (o/n) : ").strip().lower()
                if choix_graphe == "o":
                    afficher_graphe(graphe, resultat["chemin"], reseau.get("nom", "Réseau"))

            autre = input("Calculer un autre trajet dans cette ville ? (o/n) : ")
            if autre.strip().lower() != "o":
                break

        changer = input("Choisir une autre ville ? (o/n) : ")
        if changer.strip().lower() != "o":
            print("Fin du programme.")
            return
