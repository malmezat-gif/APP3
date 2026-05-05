# APP3 - Calculateur d'itinéraires

## Groupe

- Titouan
- Illyas
- Maxime
- Thibault

## Idée générale

Le projet calcule un itinéraire dans un réseau de métro ou de tramway.

Le programme lit un fichier JSON, construit un graphe, puis cherche le trajet
le plus rapide entre deux stations avec l'algorithme de Dijkstra.

Le programme fonctionne hors ligne. Il n'utilise pas d'API externe.

## Lancement

Depuis le dossier du projet :

```bash
python main.py
```

Le programme ouvre une fenêtre. On choisit une ville, une station de départ et
une station d'arrivée, puis on clique sur le bouton de calcul.

Pour lancer les tests :

```bash
python -m unittest
```

## Organisation des fichiers

- `donnees/`
  Les fichiers JSON des villes.
- `graphe.py`
  Chargement des réseaux, création du graphe, BFS, DFS et connexité.
- `itineraire.py`
  Calcul du plus court chemin avec Dijkstra.
- `interface_graphique.py`
  Fenêtre du programme avec `tkinter`.
- `main.py`
  Lancement de l'interface graphique.
- `test_app3.py`
  Tests simples du coeur du projet.
- `PLAN.md`
  Résumé de l'organisation et réponses utiles pour l'oral.

## Choix techniques

Le réseau est représenté avec une liste d'adjacence.

On utilise un dictionnaire Python :

```text
station -> liste des connexions possibles
```

Chaque connexion contient :

- la station voisine ;
- le temps de trajet ;
- la ligne utilisée.

Ce choix est adapté car une station est reliée seulement à quelques stations
voisines. Une matrice d'adjacence serait plus lourde pour ce type de graphe.

Pour les fichiers où les connexions ne sont pas écrites directement, le
programme les crée automatiquement avec l'ordre des stations de chaque ligne.

## Algorithmes utilisés

- BFS : parcours en largeur.
- DFS : parcours en profondeur.
- Dijkstra : plus court chemin en temps.

Quand le trajet change de ligne, on ajoute un temps de correspondance de
120 secondes.

## Interface

Le fichier `interface_graphique.py` contient la fenêtre du programme.

Elle affiche :

- les informations du réseau choisi ;
- les champs de recherche des stations ;
- le trajet sous forme de texte ;
- un dessin simple du trajet ;
- une vue simplifiée du réseau complet.

Le calcul principal reste dans `graphe.py` et `itineraire.py`, donc il reste
facile à expliquer.
