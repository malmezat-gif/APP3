"""Tests simples pour vérifier le coeur du projet APP3."""

import os
import unittest

from graphe import (
    bfs,
    charger_reseau,
    construire_graphe,
    dfs,
    est_connexe,
    trouver_correspondances,
)
from itineraire import dijkstra


CHEMIN_MINI_RESEAU = os.path.join("donnees", "mini_reseau.json")


class TestAPP3(unittest.TestCase):
    """Tests sur le petit réseau fictif fourni."""

    def setUp(self):
        self.reseau = charger_reseau(CHEMIN_MINI_RESEAU)
        self.graphe = construire_graphe(self.reseau)

    def test_chargement(self):
        self.assertEqual(self.reseau["nom"], "Mini-réseau fictif")
        self.assertIn("lignes", self.reseau)

    def test_construction_graphe(self):
        self.assertIn("Alpha", self.graphe)
        voisins_alpha = []
        for connexion in self.graphe["Alpha"]:
            voisins_alpha.append(connexion["station"])
        self.assertIn("Bravo", voisins_alpha)

    def test_bfs(self):
        chemin = bfs(self.graphe, "Alpha")
        self.assertEqual(chemin[0], "Alpha")
        self.assertEqual(len(chemin), len(self.graphe))

    def test_dfs(self):
        chemin = dfs(self.graphe, "Alpha")
        self.assertEqual(chemin[0], "Alpha")
        self.assertEqual(len(chemin), len(self.graphe))

    def test_connexite(self):
        self.assertTrue(est_connexe(self.graphe))

    def test_dijkstra_meme_ligne(self):
        resultat = dijkstra(self.graphe, self.reseau, "Alpha", "Echo")
        self.assertTrue(resultat["trouve"])
        self.assertEqual(resultat["temps"], 480)

    def test_dijkstra_avec_correspondance(self):
        resultat = dijkstra(self.graphe, self.reseau, "Alpha", "Juliet")
        self.assertTrue(resultat["trouve"])
        self.assertEqual(resultat["temps"], 720)

    def test_correspondances(self):
        correspondances = trouver_correspondances(self.reseau)
        self.assertIn("Charlie", correspondances)
        self.assertEqual(correspondances["Charlie"], ["A", "B"])


if __name__ == "__main__":
    unittest.main()
