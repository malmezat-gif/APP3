# PLAN.md

## Groupe

- Titouan
- Illyas
- Maxime
- Thibault

## Idée générale

On veut créer un calculateur d'itinéraires pour des réseaux de métro et de
tramway.

Pour chaque trajet :

- on choisit une ville ;
- on charge le fichier JSON de cette ville ;
- on transforme les stations et les lignes en graphe ;
- on demande une station de départ et une station d'arrivée ;
- on cherche le trajet le plus rapide avec Dijkstra ;
- on affiche les stations traversées, les correspondances et le temps total.

## Organisation des fichiers

- `donnees/`
  Les données des réseaux.
- `graphe.py`
  Le chargement du JSON et les fonctions de graphe.
- `itineraire.py`
  Le calcul du meilleur itinéraire.
- `interface.py`
  Le menu en console, gardé comme secours.
- `interface_graphique.py`
  L'interface cliquable avec `tkinter`.
- `visualisation.py`
  L'ancienne visualisation avec `networkx`.
- `main.py`
  Le fichier à lancer pour ouvrir la fenêtre.
- `test_app3.py`
  Les vérifications automatiques simples.

## Ce qu'il faut pouvoir montrer

- lecture d'un fichier JSON ;
- construction d'une liste d'adjacence ;
- parcours BFS ;
- parcours DFS ;
- vérification que le réseau est connexe ;
- recherche des stations de correspondance ;
- calcul du plus court chemin avec Dijkstra ;
- ajout du temps de correspondance quand on change de ligne ;
- fonctionnement avec plusieurs villes ;
- interface cliquable ;
- dessin simple du trajet ;
- vue simplifiée du réseau.

## Réponses simples pour l'oral

- Pourquoi utiliser une liste d'adjacence ?
  Parce qu'une station n'a que quelques voisines. C'est plus simple et plus
  léger qu'une grande matrice.

- Pourquoi utiliser Dijkstra ?
  Parce que les trajets ont des poids différents en secondes. Dijkstra permet
  de trouver le chemin le plus court en temps.

- Quelle est la différence entre BFS et Dijkstra ?
  BFS trouve un chemin avec peu d'arrêts si toutes les arêtes valent pareil.
  Dijkstra prend en compte le temps de chaque connexion.

- Comment sont gérées les correspondances ?
  Quand le trajet change de ligne, on ajoute 120 secondes au temps total.

- Comment ajouter une nouvelle ville ?
  Il suffit d'ajouter un nouveau fichier JSON dans le dossier `donnees`.
  Le code lit automatiquement les fichiers disponibles.

- Pourquoi séparer la visualisation ?
  Pour garder le calcul principal simple. Le graphe fonctionne même sans
  ouvrir la fenêtre graphique.

- Pourquoi utiliser tkinter ?
  Parce que c'est fourni avec Python. On peut faire une interface cliquable
  sans ajouter une grosse bibliothèque.

## Ce qu'on a choisi

- Code simple et lisible.
- Fonctions courtes avec des noms explicites.
- Docstrings en français simple.
- Interface console sobre.
- Interface graphique simple avec `tkinter`.
- Visualisation du trajet directement dans la fenêtre.
- Tests automatiques sur le mini réseau fourni.
