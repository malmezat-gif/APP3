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
from itineraire import decrire_itineraire, dijkstra, formater_temps


FOND = "#edf2f7"
CARTE = "#ffffff"
TEXTE = "#172033"
TEXTE_DISCRET = "#64748b"
BLEU = "#2563eb"
BLEU_FONCE = "#1d4ed8"
VERT = "#16a34a"
ROUGE = "#dc2626"
BORDURE = "#d8dee9"

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


def nom_ville_depuis_chemin(chemin):
    """Transforme donnees/paris.json en paris."""
    nom = chemin.split("/")[-1]
    return nom.replace(".json", "")


class ApplicationItineraire:
    """Fenêtre principale de l'application."""

    def __init__(self, fenetre):
        self.fenetre = fenetre
        self.fenetre.title("APP3 - Calculateur d'itinéraires")
        self.fenetre.geometry("1180x760")
        self.fenetre.minsize(980, 650)

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
        style.configure("TFrame", background=FOND)
        style.configure("Panel.TFrame", background=CARTE, relief="flat")
        style.configure("TLabel", background=FOND, foreground=TEXTE)
        style.configure("Panel.TLabel", background=CARTE, foreground=TEXTE)
        style.configure("Title.TLabel", font=("Arial", 22, "bold"), foreground=TEXTE)
        style.configure("Small.TLabel", font=("Arial", 10), foreground=TEXTE_DISCRET)
        style.configure(
            "SubTitle.TLabel",
            background=CARTE,
            foreground=TEXTE,
            font=("Arial", 11, "bold"),
        )
        style.configure("TButton", padding=8, font=("Arial", 10))
        style.configure("Primary.TButton", padding=10, font=("Arial", 10, "bold"))
        style.configure(
            "Primary.TButton",
            background=BLEU,
            foreground="white",
            bordercolor=BLEU,
            lightcolor=BLEU,
            darkcolor=BLEU,
        )
        style.configure("TCombobox", padding=5)

    def creer_interface(self):
        """Crée tous les éléments visibles."""
        self.fenetre.configure(bg=FOND)

        principal = ttk.Frame(self.fenetre, padding=18)
        principal.pack(fill="both", expand=True)

        haut = ttk.Frame(principal)
        haut.pack(fill="x")

        bloc_titre = ttk.Frame(haut)
        bloc_titre.pack(side="left")

        titre = ttk.Label(bloc_titre, text="Calculateur d'itinéraires", style="Title.TLabel")
        titre.pack(anchor="w")
        sous_titre = ttk.Label(
            bloc_titre,
            text="Métro et tramway - recherche du trajet le plus rapide",
            style="Small.TLabel",
        )
        sous_titre.pack(anchor="w", pady=(2, 0))

        bouton_console = ttk.Button(
            haut,
            text="Quitter",
            command=self.fenetre.destroy,
        )
        bouton_console.pack(side="right")

        contenu = ttk.Frame(principal)
        contenu.pack(fill="both", expand=True, pady=(18, 0))

        gauche = ttk.Frame(contenu, style="Panel.TFrame", padding=18)
        gauche.pack(side="left", fill="y")

        droite = ttk.Frame(contenu)
        droite.pack(side="left", fill="both", expand=True, padx=(18, 0))

        self.creer_panneau_choix(gauche)
        self.creer_panneau_resultat(droite)

    def creer_panneau_choix(self, parent):
        """Crée le panneau de gauche avec les choix utilisateur."""
        largeur = 32

        ttk.Label(parent, text="Préparer le trajet", style="SubTitle.TLabel").pack(anchor="w")
        ttk.Label(
            parent,
            text="Choisis le réseau puis les deux stations.",
            style="Panel.TLabel",
        ).pack(anchor="w", pady=(3, 18))

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
        self.infos = tk.Text(parent, width=34, height=11, wrap="word", borderwidth=0)
        self.infos.pack(fill="x", pady=(6, 0))
        self.infos.configure(
            state="disabled",
            background="#f8fafc",
            foreground=TEXTE,
            font=("Arial", 10),
            padx=10,
            pady=8,
        )

    def creer_panneau_resultat(self, parent):
        """Crée la zone de résultat et le dessin."""
        self.resume = tk.Label(
            parent,
            text="Choisis une ville et deux stations.",
            background="#dbeafe",
            foreground=BLEU_FONCE,
            font=("Arial", 11, "bold"),
            padx=12,
            pady=8,
            anchor="w",
        )
        self.resume.pack(fill="x")

        zone = ttk.PanedWindow(parent, orient="vertical")
        zone.pack(fill="both", expand=True, pady=(8, 0))

        panneau_texte = ttk.Frame(zone, style="Panel.TFrame", padding=14)
        panneau_dessin = ttk.Frame(zone, style="Panel.TFrame", padding=14)
        zone.add(panneau_texte, weight=1)
        zone.add(panneau_dessin, weight=3)

        ttk.Label(panneau_texte, text="Itinéraire", style="SubTitle.TLabel").pack(anchor="w")
        self.resultat_texte = tk.Text(panneau_texte, height=9, wrap="word", borderwidth=0)
        self.resultat_texte.pack(fill="both", expand=True, pady=(6, 0))
        self.resultat_texte.configure(
            state="disabled",
            background="#f8fafc",
            foreground=TEXTE,
            font=("Arial", 11),
            padx=10,
            pady=8,
        )

        entete_dessin = ttk.Frame(panneau_dessin, style="Panel.TFrame")
        entete_dessin.pack(fill="x")

        ttk.Label(entete_dessin, text="Vue du trajet", style="SubTitle.TLabel").pack(
            side="left"
        )

        zone_canvas = ttk.Frame(panneau_dessin, style="Panel.TFrame")
        zone_canvas.pack(fill="both", expand=True, pady=(8, 0))

        self.canvas = tk.Canvas(
            zone_canvas,
            background="#fbfdff",
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
        self.canvas.configure(scrollregion=(0, 0, 900, 480))
        self.canvas.create_rectangle(28, 28, 872, 452, fill="#f8fafc", outline=BORDURE)
        self.canvas.create_oval(382, 128, 518, 264, fill="#dbeafe", outline="")
        self.canvas.create_text(
            450,
            168,
            text="APP3",
            fill=BLEU_FONCE,
            font=("Arial", 22, "bold"),
        )
        self.canvas.create_text(
            450,
            300,
            text=message,
            fill=TEXTE_DISCRET,
            font=("Arial", 15, "bold"),
        )

    def dessiner_itineraire(self):
        """Dessine le trajet calculé sous forme de ligne plus lisible."""
        self.canvas.delete("all")

        if not self.resultat or not self.resultat["trouve"]:
            self.dessiner_message("Aucun itinéraire à afficher.")
            return

        chemin = self.resultat["chemin"]
        largeur = max(980, len(chemin) * 150)
        hauteur = 520
        self.canvas.configure(scrollregion=(0, 0, largeur, hauteur))

        self.canvas.create_rectangle(24, 24, largeur - 24, hauteur - 24, fill="#f8fafc", outline=BORDURE)
        self.canvas.create_rectangle(46, 46, largeur - 46, 112, fill="#eff6ff", outline="")
        self.canvas.create_text(
            70,
            70,
            anchor="w",
            text="Trajet calculé",
            font=("Arial", 18, "bold"),
            fill=TEXTE,
        )
        self.canvas.create_text(
            70,
            96,
            anchor="w",
            text="Temps total estimé : " + formater_temps(self.resultat["temps"]),
            font=("Arial", 11),
            fill=BLEU_FONCE,
        )

        y = 250
        marge = 90
        espace = 140

        for i in range(len(chemin) - 1):
            x1 = marge + i * espace
            x2 = marge + (i + 1) * espace
            ligne = chemin[i + 1]["ligne"]
            couleur = couleur_ligne(self.reseau, ligne)
            self.canvas.create_line(x1, y, x2, y, fill="#dbe4ef", width=14)
            self.canvas.create_line(x1, y, x2, y, fill=couleur, width=7)

            milieu = (x1 + x2) / 2
            self.canvas.create_rectangle(
                milieu - 25,
                y - 34,
                milieu + 25,
                y - 12,
                fill="white",
                outline=BORDURE,
            )
            self.canvas.create_text(
                milieu,
                y - 23,
                text="ligne " + ligne,
                fill=TEXTE_DISCRET,
                font=("Arial", 8, "bold"),
            )

        for i in range(len(chemin)):
            x = marge + i * espace
            station = chemin[i]["station"]
            ligne = chemin[i]["ligne"]
            rayon = 17

            if i == 0:
                couleur = VERT
                texte = "Départ"
            elif i == len(chemin) - 1:
                couleur = ROUGE
                texte = "Arrivée"
            else:
                couleur = CARTE
                texte = ""

            self.canvas.create_oval(
                x - rayon - 6,
                y - rayon - 6,
                x + rayon + 6,
                y + rayon + 6,
                fill="#e2e8f0",
                outline="",
            )
            self.canvas.create_oval(
                x - rayon,
                y - rayon,
                x + rayon,
                y + rayon,
                fill=couleur,
                outline=CARTE,
                width=2,
            )
            self.canvas.create_text(
                x,
                y,
                text=str(i + 1),
                font=("Arial", 9, "bold"),
                fill="white" if i == 0 or i == len(chemin) - 1 else TEXTE,
            )

            if texte:
                self.canvas.create_rectangle(
                    x - 34,
                    y - 64,
                    x + 34,
                    y - 39,
                    fill=CARTE,
                    outline=BORDURE,
                )
                self.canvas.create_text(
                    x,
                    y - 52,
                    text=texte,
                    fill=TEXTE,
                    font=("Arial", 9, "bold"),
                )

            station_courte = station
            if len(station_courte) > 24:
                station_courte = station_courte[:21] + "..."

            largeur_carte = 112
            self.canvas.create_rectangle(
                x - largeur_carte / 2,
                y + 40,
                x + largeur_carte / 2,
                y + 105,
                fill=CARTE,
                outline=BORDURE,
            )
            self.canvas.create_text(
                x,
                y + 58,
                text=station_courte,
                width=100,
                font=("Arial", 9, "bold"),
                fill=TEXTE,
            )

            if ligne is not None:
                self.canvas.create_text(
                    x,
                    y + 88,
                    text="ligne " + ligne,
                    font=("Arial", 8),
                    fill=TEXTE_DISCRET,
                )

            if 0 < i < len(chemin) - 1:
                ligne_avant = chemin[i]["ligne"]
                ligne_apres = chemin[i + 1]["ligne"]
                if ligne_avant != ligne_apres:
                    self.canvas.create_rectangle(
                        x - 58,
                        y - 92,
                        x + 58,
                        y - 68,
                        fill="#fff7ed",
                        outline="#fed7aa",
                    )
                    self.canvas.create_text(
                        x,
                        y - 80,
                        text="Correspondance",
                        fill="#b45309",
                        font=("Arial", 9, "bold"),
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

        self.canvas.create_rectangle(24, 24, largeur - 24, hauteur - 24, fill="#f8fafc", outline=BORDURE)
        self.canvas.create_text(
            45,
            34,
            anchor="w",
            text="Réseau simplifié",
            font=("Arial", 17, "bold"),
            fill=TEXTE,
        )
        self.canvas.create_text(
            45,
            60,
            anchor="w",
            text="Une ligne horizontale par ligne de transport",
            font=("Arial", 10),
            fill=TEXTE_DISCRET,
        )

        y = 105
        for code_ligne, ligne in lignes.items():
            stations = ligne.get("stations", [])
            couleur = couleur_ligne(self.reseau, code_ligne)
            nom_ligne = ligne.get("nom", "Ligne " + code_ligne)

            self.canvas.create_rectangle(44, y - 24, 1190, y + 38, fill=CARTE, outline=BORDURE)

            self.canvas.create_text(
                62,
                y,
                anchor="w",
                text=code_ligne + " - " + nom_ligne,
                font=("Arial", 10, "bold"),
                fill=TEXTE,
            )

            x_depart = 250
            x_fin = 1160
            self.canvas.create_line(x_depart, y, x_fin, y, fill="#dbe4ef", width=10)
            self.canvas.create_line(x_depart, y, x_fin, y, fill=couleur, width=5)

            if len(stations) <= 1:
                y += 65
                continue

            pas = (x_fin - x_depart) / (len(stations) - 1)

            for i in range(len(stations)):
                x = x_depart + i * pas
                self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=CARTE, outline=couleur)

                if i == 0 or i == len(stations) - 1:
                    station = stations[i]
                    if len(station) > 18:
                        station = station[:15] + "..."
                    self.canvas.create_text(
                        x,
                        y + 15,
                        text=station,
                        font=("Arial", 8),
                        fill=TEXTE_DISCRET,
                    )

            y += 72


def lancer_graphique():
    """Lance l'application graphique."""
    fenetre = tk.Tk()
    ApplicationItineraire(fenetre)
    fenetre.mainloop()
