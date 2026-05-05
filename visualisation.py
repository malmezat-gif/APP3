"""Visualisation simple du graphe avec networkx et matplotlib."""


def afficher_graphe(graphe, chemin=None, titre="Réseau"):
    """Affiche le graphe et met le chemin en couleur si on en reçoit un."""
    try:
        import matplotlib.pyplot as plt
        import networkx as nx
    except ImportError:
        print("Visualisation impossible : networkx ou matplotlib manque.")
        return

    graphe_nx = nx.Graph()

    for station, connexions in graphe.items():
        graphe_nx.add_node(station)

        for connexion in connexions:
            graphe_nx.add_edge(station, connexion["station"], ligne=connexion["ligne"])

    stations_chemin = []
    aretes_chemin = []

    if chemin:
        for etape in chemin:
            stations_chemin.append(etape["station"])

        for i in range(len(stations_chemin) - 1):
            a = stations_chemin[i]
            b = stations_chemin[i + 1]
            aretes_chemin.append((a, b))
            aretes_chemin.append((b, a))

    couleurs_noeuds = []
    for station in graphe_nx.nodes:
        if station in stations_chemin:
            couleurs_noeuds.append("tomato")
        else:
            couleurs_noeuds.append("lightblue")

    couleurs_aretes = []
    for depart, arrivee in graphe_nx.edges:
        if (depart, arrivee) in aretes_chemin:
            couleurs_aretes.append("tomato")
        else:
            couleurs_aretes.append("gray")

    positions = nx.spring_layout(graphe_nx, seed=4)

    plt.figure(figsize=(12, 8))
    nx.draw_networkx_nodes(graphe_nx, positions, node_color=couleurs_noeuds, node_size=90)
    nx.draw_networkx_edges(graphe_nx, positions, edge_color=couleurs_aretes, width=1)

    if len(graphe_nx.nodes) <= 80:
        nx.draw_networkx_labels(graphe_nx, positions, font_size=7)
    elif stations_chemin:
        labels = {}
        for station in stations_chemin:
            labels[station] = station
        nx.draw_networkx_labels(graphe_nx, positions, labels=labels, font_size=8)

    plt.title(titre)
    plt.axis("off")
    plt.tight_layout()
    plt.show()
