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
- `interface.py`
  Menu en console.
- `visualisation.py`
  Affichage du graphe avec `networkx` et `matplotlib`.
- `main.py`
  Lancement du programme.
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

## Visualisation

Le fichier `visualisation.py` permet d'afficher le graphe avec `networkx` et
`matplotlib`.

Ce bonus reste séparé du reste du code pour garder le coeur du projet simple.
