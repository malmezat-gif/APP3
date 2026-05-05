"""Interface graphique cliquable pour le calculateur d'itinéraires."""

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from graphe import (
    charger_reseau,
    construire_graphe,
    est_connexe,
    lister_fichiers_reseaux,
    stations_du_reseau,
    trouver_correspondances,
)
from interface import nom_ville_depuis_chemin
from itineraire import decrire_itineraire, dijkstra, formater_temps


COULEURS_LIGNES = {
    "rouge": "#d83a34",
    "bleu": "#2d6cdf",
    "bleue": "#2d6cdf",
    "jaune": "#e5b700",
    "vert": "#249b54",
    "verte": "#249b54",
    "orange": "#f28c28",
    "rose": "#e05297",
    "violet": "#7a4cc2",
    "marron": "#8b5a2b",
    "gris": "#737373",
    "olive": "#8a8f28",
}


def couleur_ligne(reseau, code_ligne):
    """Renvoie une couleur simple pour une ligne."""
    ligne = reseau.get("lignes", {}).get(code_ligne, {})
    couleur = ligne.get("couleur", "")
    couleur = couleur.lower()

    if couleur in COULEURS_LIGNES:
        return COULEURS_LIGNES[couleur]

    return "#2d6cdf"


class ApplicationItineraire:
    """Fenêtre principale de l'application."""

    def __init__(self, fenetre):
        self.fenetre = fenetre
        self.fenetre.title("APP3 - Calculateur d'itinéraires")
        self.fenetre.geometry("1120x720")
        self.fenetre.minsize(900, 620)

        self.fichiers = lister_fichiers_reseaux()
        self.reseau = None
        self.graphe = None
        self.stations = []
        self.resultat = None

        self.creer_style()
        self.creer_interface()
        self.charger_premiere_ville()

    def creer_style(self):
        """Prépare un style sobre pour les composants."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f5f6f8")
        style.configure("Panel.TFrame", background="white", relief="solid", borderwidth=1)
        style.configure("TLabel", background="#f5f6f8", foreground="#1f2933")
        style.configure("Panel.TLabel", background="white", foreground="#1f2933")
        style.configure("Title.TLabel", font=("Arial", 18, "bold"))
        style.configure("SubTitle.TLabel", font=("Arial", 11, "bold"))
        style.configure("TButton", padding=8)
        style.configure("Primary.TButton", padding=8)

    def creer_interface(self):
        """Crée tous les éléments visibles."""
        self.fenetre.configure(bg="#f5f6f8")

        principal = ttk.Frame(self.fenetre, padding=16)
        principal.pack(fill="both", expand=True)

        haut = ttk.Frame(principal)
        haut.pack(fill="x")

        titre = ttk.Label(haut, text="Calculateur d'itinéraires", style="Title.TLabel")
        titre.pack(side="left")

        bouton_console = ttk.Button(
            haut,
            text="Quitter",
            command=self.fenetre.destroy,
        )
        bouton_console.pack(side="right")

        contenu = ttk.Frame(principal)
        contenu.pack(fill="both", expand=True, pady=(14, 0))

        gauche = ttk.Frame(contenu, style="Panel.TFrame", padding=14)
        gauche.pack(side="left", fill="y")

        droite = ttk.Frame(contenu)
        droite.pack(side="left", fill="both", expand=True, padx=(14, 0))

        self.creer_panneau_choix(gauche)
        self.creer_panneau_resultat(droite)

    def creer_panneau_choix(self, parent):
        """Crée le panneau de gauche avec les choix utilisateur."""
        largeur = 32

        ttk.Label(parent, text="Ville", style="Panel.TLabel").pack(anchor="w")
        self.choix_ville = ttk.Combobox(parent, state="readonly", width=largeur)
        self.choix_ville.pack(fill="x", pady=(4, 12))
        self.choix_ville.bind("<<ComboboxSelected>>", self.changer_ville)

        ttk.Label(parent, text="Départ", style="Panel.TLabel").pack(anchor="w")
        self.choix_depart = ttk.Combobox(parent, width=largeur)
        self.choix_depart.pack(fill="x", pady=(4, 12))
        self.choix_depart.bind("<KeyRelease>", self.filtrer_depart)

        ttk.Label(parent, text="Arrivée", style="Panel.TLabel").pack(anchor="w")
        self.choix_arrivee = ttk.Combobox(parent, width=largeur)
        self.choix_arrivee.pack(fill="x", pady=(4, 12))
        self.choix_arrivee.bind("<KeyRelease>", self.filtrer_arrivee)

        boutons = ttk.Frame(parent, style="Panel.TFrame")
        boutons.pack(fill="x", pady=(2, 12))

        ttk.Button(boutons, text="Inverser", command=self.inverser_stations).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(boutons, text="Effacer", command=self.effacer).pack(
            side="left", fill="x", expand=True, padx=(8, 0)
        )

        ttk.Button(
            parent,
            text="Calculer l'itinéraire",
            style="Primary.TButton",
            command=self.calculer,
        ).pack(fill="x", pady=(0, 12))

        ttk.Button(
            parent,
            text="Voir le réseau simplifié",
            command=self.dessiner_reseau,
        ).pack(fill="x")

        separateur = ttk.Separator(parent)
        separateur.pack(fill="x", pady=16)

        ttk.Label(parent, text="Informations", style="SubTitle.TLabel").pack(anchor="w")
        self.infos = tk.Text(parent, width=34, height=10, wrap="word", borderwidth=0)
        self.infos.pack(fill="x", pady=(6, 0))
        self.infos.configure(state="disabled", background="white", foreground="#1f2933")

    def creer_panneau_resultat(self, parent):
        """Crée la zone de résultat et le dessin."""
        self.resume = ttk.Label(parent, text="Choisis une ville et deux stations.")
        self.resume.pack(anchor="w")

        zone = ttk.PanedWindow(parent, orient="vertical")
        zone.pack(fill="both", expand=True, pady=(8, 0))

        panneau_texte = ttk.Frame(zone, style="Panel.TFrame", padding=10)
        panneau_dessin = ttk.Frame(zone, style="Panel.TFrame", padding=10)
        zone.add(panneau_texte, weight=1)
        zone.add(panneau_dessin, weight=3)

        ttk.Label(panneau_texte, text="Itinéraire", style="Panel.TLabel").pack(anchor="w")
        self.resultat_texte = tk.Text(panneau_texte, height=9, wrap="word", borderwidth=0)
        self.resultat_texte.pack(fill="both", expand=True, pady=(6, 0))
        self.resultat_texte.configure(state="disabled", background="white")

        entete_dessin = ttk.Frame(panneau_dessin, style="Panel.TFrame")
        entete_dessin.pack(fill="x")

        ttk.Label(entete_dessin, text="Vue cliquable du trajet", style="Panel.TLabel").pack(
            side="left"
        )

        zone_canvas = ttk.Frame(panneau_dessin, style="Panel.TFrame")
        zone_canvas.pack(fill="both", expand=True, pady=(8, 0))

        self.canvas = tk.Canvas(
            zone_canvas,
            background="white",
            highlightthickness=0,
            scrollregion=(0, 0, 1200, 600),
        )
        barre_y = ttk.Scrollbar(zone_canvas, orient="vertical", command=self.canvas.yview)
        barre_x = ttk.Scrollbar(zone_canvas, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=barre_x.set, yscrollcommand=barre_y.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        barre_y.grid(row=0, column=1, sticky="ns")
        barre_x.grid(row=1, column=0, sticky="ew")
        zone_canvas.columnconfigure(0, weight=1)
        zone_canvas.rowconfigure(0, weight=1)

    def charger_premiere_ville(self):
        """Charge la première ville disponible."""
        noms = []
        for fichier in self.fichiers:
            noms.append(nom_ville_depuis_chemin(fichier))

        self.choix_ville["values"] = noms

        if self.fichiers:
            self.choix_ville.current(0)
            self.charger_ville(self.fichiers[0])
        else:
            messagebox.showerror("Erreur", "Aucun fichier JSON trouvé dans donnees.")

    def changer_ville(self, evenement=None):
        """Charge la ville sélectionnée dans la liste."""
        index = self.choix_ville.current()

        if index >= 0:
            self.charger_ville(self.fichiers[index])

    def charger_ville(self, chemin_fichier):
        """Charge les données, le graphe et les stations d'une ville."""
        try:
            self.reseau = charger_reseau(chemin_fichier)
            self.graphe = construire_graphe(self.reseau)
            self.stations = stations_du_reseau(self.graphe)
        except Exception as erreur:
            messagebox.showerror("Erreur", "Impossible de charger le réseau : " + str(erreur))
            return

        self.choix_depart["values"] = self.stations
        self.choix_arrivee["values"] = self.stations
        self.choix_depart.set("")
        self.choix_arrivee.set("")
        self.resultat = None

        self.mettre_infos_a_jour()
        self.ecrire_resultat("")
        self.resume.configure(text="Réseau chargé : " + self.reseau.get("nom", "sans nom"))
        self.dessiner_message("Choisis deux stations puis clique sur Calculer.")

    def mettre_infos_a_jour(self):
        """Affiche les informations du réseau sélectionné."""
        correspondances = trouver_correspondances(self.reseau)
        lignes = self.reseau.get("lignes", {})

        texte = ""
        texte += "Réseau : " + self.reseau.get("nom", "sans nom") + "\n"
        texte += "Lignes : " + str(len(lignes)) + "\n"
        texte += "Stations : " + str(len(self.graphe)) + "\n"
        texte += "Correspondances : " + str(len(correspondances)) + "\n"

        if est_connexe(self.graphe):
            texte += "Connexité : oui\n"
        else:
            texte += "Connexité : non\n"

        texte += "\nAstuce : tape quelques lettres dans les champs pour chercher."

        self.infos.configure(state="normal")
        self.infos.delete("1.0", "end")
        self.infos.insert("1.0", texte)
        self.infos.configure(state="disabled")

    def filtrer_depart(self, evenement=None):
        """Filtre la liste de départ selon ce que l'utilisateur tape."""
        self.filtrer_combobox(self.choix_depart)

    def filtrer_arrivee(self, evenement=None):
        """Filtre la liste d'arrivée selon ce que l'utilisateur tape."""
        self.filtrer_combobox(self.choix_arrivee)

    def filtrer_combobox(self, combo):
        """Garde seulement les stations qui contiennent le texte saisi."""
        texte = combo.get().lower()

        if not texte:
            combo["values"] = self.stations
            return

        valeurs = []
        for station in self.stations:
            if texte in station.lower():
                valeurs.append(station)

        combo["values"] = valeurs

    def trouver_station(self, nom):
        """Retrouve une station avec une comparaison sans tenir compte de la casse."""
        for station in self.stations:
            if station.lower() == nom.lower():
                return station

        return None

    def inverser_stations(self):
        """Inverse départ et arrivée."""
        depart = self.choix_depart.get()
        arrivee = self.choix_arrivee.get()
        self.choix_depart.set(arrivee)
        self.choix_arrivee.set(depart)

    def effacer(self):
        """Efface les choix et le résultat."""
        self.choix_depart.set("")
        self.choix_arrivee.set("")
        self.ecrire_resultat("")
        self.resultat = None
        self.dessiner_message("Choisis deux stations puis clique sur Calculer.")
        self.resume.configure(text="Réseau chargé : " + self.reseau.get("nom", "sans nom"))

    def calculer(self):
        """Calcule et affiche le meilleur itinéraire."""
        depart = self.trouver_station(self.choix_depart.get().strip())
        arrivee = self.trouver_station(self.choix_arrivee.get().strip())

        if depart is None:
            messagebox.showwarning("Station inconnue", "La station de départ n'existe pas.")
            return

        if arrivee is None:
            messagebox.showwarning("Station inconnue", "La station d'arrivée n'existe pas.")
            return

        if depart == arrivee:
            messagebox.showinfo("Même station", "Le départ et l'arrivée sont identiques.")
            return

        self.resultat = dijkstra(self.graphe, self.reseau, depart, arrivee)
        texte = decrire_itineraire(self.resultat)
        self.ecrire_resultat(texte)

        if self.resultat["trouve"]:
            temps = formater_temps(self.resultat["temps"])
            self.resume.configure(text="Trajet trouvé en " + temps)
            self.dessiner_itineraire()
        else:
            self.resume.configure(text="Aucun trajet trouvé.")
            self.dessiner_message("Aucun chemin trouvé entre ces deux stations.")

    def ecrire_resultat(self, texte):
        """Écrit le résultat dans la zone de texte."""
        self.resultat_texte.configure(state="normal")
        self.resultat_texte.delete("1.0", "end")
        self.resultat_texte.insert("1.0", texte)
        self.resultat_texte.configure(state="disabled")

    def dessiner_message(self, message):
        """Affiche un message au centre du canvas."""
        self.canvas.delete("all")
        self.canvas.create_text(
            450,
            230,
            text=message,
            fill="#4b5563",
            font=("Arial", 15),
        )

    def dessiner_itineraire(self):
        """Dessine le trajet calculé sous forme de ligne simple."""
        self.canvas.delete("all")

        if not self.resultat or not self.resultat["trouve"]:
            self.dessiner_message("Aucun itinéraire à afficher.")
            return

        chemin = self.resultat["chemin"]
        largeur = max(900, len(chemin) * 135)
        hauteur = 430
        self.canvas.configure(scrollregion=(0, 0, largeur, hauteur))

        y = 200
        marge = 70
        espace = 120

        for i in range(len(chemin) - 1):
            x1 = marge + i * espace
            x2 = marge + (i + 1) * espace
            ligne = chemin[i + 1]["ligne"]
            couleur = couleur_ligne(self.reseau, ligne)
            self.canvas.create_line(x1, y, x2, y, fill=couleur, width=6)

        for i in range(len(chemin)):
            x = marge + i * espace
            station = chemin[i]["station"]
            ligne = chemin[i]["ligne"]
            rayon = 11

            if i == 0:
                couleur = "#249b54"
                texte = "Départ"
            elif i == len(chemin) - 1:
                couleur = "#d83a34"
                texte = "Arrivée"
            else:
                couleur = "#ffffff"
                texte = ""

            self.canvas.create_oval(
                x - rayon,
                y - rayon,
                x + rayon,
                y + rayon,
                fill=couleur,
                outline="#1f2933",
                width=2,
            )

            if texte:
                self.canvas.create_text(x, y - 34, text=texte, font=("Arial", 10, "bold"))

            station_courte = station
            if len(station_courte) > 24:
                station_courte = station_courte[:21] + "..."

            self.canvas.create_text(
                x,
                y + 38,
                text=station_courte,
                angle=30,
                anchor="w",
                font=("Arial", 9),
                fill="#1f2933",
            )

            if ligne is not None:
                self.canvas.create_text(
                    x,
                    y + 18,
                    text="ligne " + ligne,
                    font=("Arial", 8),
                    fill="#4b5563",
                )

            if 0 < i < len(chemin) - 1:
                ligne_avant = chemin[i]["ligne"]
                ligne_apres = chemin[i + 1]["ligne"]
                if ligne_avant != ligne_apres:
                    self.canvas.create_text(
                        x,
                        y - 52,
                        text="Correspondance",
                        fill="#b45309",
                        font=("Arial", 9, "bold"),
                    )

        self.canvas.create_text(
            70,
            35,
            anchor="w",
            text="Trajet calculé : " + formater_temps(self.resultat["temps"]),
            font=("Arial", 14, "bold"),
            fill="#111827",
        )

    def dessiner_reseau(self):
        """Dessine les lignes du réseau de manière simplifiée."""
        if self.reseau is None:
            return

        self.canvas.delete("all")
        lignes = self.reseau.get("lignes", {})
        hauteur = max(500, len(lignes) * 70 + 80)
        largeur = 1250
        self.canvas.configure(scrollregion=(0, 0, largeur, hauteur))

        self.canvas.create_text(
            45,
            30,
            anchor="w",
            text="Réseau simplifié : une ligne horizontale par ligne de transport",
            font=("Arial", 13, "bold"),
            fill="#111827",
        )

        y = 80
        for code_ligne, ligne in lignes.items():
            stations = ligne.get("stations", [])
            couleur = couleur_ligne(self.reseau, code_ligne)
            nom_ligne = ligne.get("nom", "Ligne " + code_ligne)

            self.canvas.create_text(
                45,
                y,
                anchor="w",
                text=code_ligne + " - " + nom_ligne,
                font=("Arial", 10, "bold"),
                fill="#1f2933",
            )

            x_depart = 220
            x_fin = 1160
            self.canvas.create_line(x_depart, y, x_fin, y, fill=couleur, width=4)

            if len(stations) <= 1:
                y += 65
                continue

            pas = (x_fin - x_depart) / (len(stations) - 1)

            for i in range(len(stations)):
                x = x_depart + i * pas
                self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="white", outline=couleur)

                if i == 0 or i == len(stations) - 1:
                    station = stations[i]
                    if len(station) > 18:
                        station = station[:15] + "..."
                    self.canvas.create_text(
                        x,
                        y + 15,
                        text=station,
                        font=("Arial", 8),
                        fill="#4b5563",
                    )

            y += 65


def lancer_graphique():
    """Lance l'application graphique."""
    fenetre = tk.Tk()
    ApplicationItineraire(fenetre)
    fenetre.mainloop()
