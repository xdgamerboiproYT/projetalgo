import networkx as nx
import matplotlib.pyplot as plt

class Node:
    """Modélise un sommet du réseau (Dépôt ou Client) avec ses paramètres."""
    def __init__(self, node_id, demand=0, earliest_time=0, latest_time=float('inf'), service_time=0):
        self.node_id = node_id  # Indice i
        self.q = demand         # Demande q_i
        self.e = earliest_time  # Ouverture de la fenêtre e_i
        self.l = latest_time    # Fermeture de la fenêtre l_i
        self.s = service_time   # Temps de service s_i

class CVRPTW_Network:
    """Modélise le graphe orienté complet G = (V, E) et les paramètres du CVRPTW."""
    def __init__(self, n_customers, k_trucks, capacity):
        self.N = n_customers    # Nombre total de clients N
        self.K = k_trucks       # Nombre de camions K
        self.Q = capacity       # Capacité maximale d'un camion Q
        self.B = float('inf')   # Borne de coût B' initialisée par défaut

        # V = {0, 1, ..., N} où 0 est le dépôt
        self.V = list(range(self.N + 1))
        # C = V \ {0} : Ensemble des clients uniquement
        self.C = [node for node in self.V if node != 0]
        # E = {(i, j) : i, j in V, i != j} : Graphe orienté complet
        self.E = [(i, j) for i in self.V for j in self.V if i != j]

        self.nodes = {}
        self.travel_times = {}  # Temps de trajet t_ij

    def add_node(self, node_id, demand=0, e=0, l=float('inf'), s=0):
        self.nodes[node_id] = Node(node_id, demand, e, l, s)

    def set_travel_time(self, i, j, time_val):
        if (i, j) in self.E:
            self.travel_times[(i, j)] = time_val

    def calculate_objective(self, routes):
        """Calcule la fonction objectif Z = Somme(C_ij * X_ij)."""
        total_time = 0
        for route in routes:
            for idx in range(len(route) - 1):
                i = route[idx]
                j = route[idx + 1]
                total_time += self.travel_times.get((i, j), 0)
        return total_time











def reduce_hc_to_tsp(hc_vertices, hc_edges, plot=True):
    tsp_costs = {}
    bound_b = len(hc_vertices)

    for i in hc_vertices:
        for j in hc_vertices:
            if i != j:
                if (i, j) in hc_edges or (j, i) in hc_edges:
                    tsp_costs[(i, j)] = 1
                else:
                    tsp_costs[(i, j)] = 2

    tsp_instance = {
        "vertices": hc_vertices,
        "original_edges": hc_edges,
        "costs": tsp_costs,
        "bound_B": bound_b
    }

    g_hc = nx.Graph()
    g_hc.add_nodes_from(hc_vertices)
    g_hc.add_edges_from(hc_edges)
    pos = nx.circular_layout(g_hc)

    if plot:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        axes[0].set_title("1. Instance Cycle Hamiltonien (HC)", fontweight="bold")
        nx.draw_networkx_nodes(g_hc, pos, ax=axes[0], node_color="#64B5F6", node_size=800, edgecolors="black")
        nx.draw_networkx_labels(g_hc, pos, ax=axes[0], font_weight="bold")
        nx.draw_networkx_edges(g_hc, pos, ax=axes[0], width=2.5)
        axes[0].axis("off")

        g_tsp = nx.Graph()
        g_tsp.add_nodes_from(hc_vertices)
        edges_cost_1 = [(i, j) for (i, j), c in tsp_costs.items() if i < j and c == 1]
        edges_cost_2 = [(i, j) for (i, j), c in tsp_costs.items() if i < j and c == 2]

        axes[1].set_title(f"2. Instance TSP réduite\nBorne cible B = {bound_b}", fontweight="bold")
        nx.draw_networkx_nodes(g_tsp, pos, ax=axes[1], node_color="#81C784", node_size=800, edgecolors="black")
        nx.draw_networkx_labels(g_tsp, pos, ax=axes[1], font_weight="bold")
        nx.draw_networkx_edges(g_tsp, pos, edgelist=edges_cost_1, ax=axes[1], width=2.5, edge_color="#2E7D32")
        nx.draw_networkx_edges(g_tsp, pos, edgelist=edges_cost_2, ax=axes[1], width=1.5, style="dashed", edge_color="#E53935")
        axes[1].axis("off")
        plt.tight_layout()
        plt.show()

    return tsp_instance, pos











    
def reduce_tsp_to_cvrptw(tsp_instance, pos=None, plot=True):
    """
    Réduit une instance TSP en une instance CVRPTW en utilisant les classes Node et CVRPTW_Network[cite: 6, 11].
    Affiche le réseau logistique orienté avec le Dépôt v0 et les paramètres clients relaxés[cite: 6, 11].
    """
    tsp_vertices = tsp_instance["vertices"]
    tsp_costs = tsp_instance["costs"]
    bound_b = tsp_instance["bound_B"]
    n_total = len(tsp_vertices)

    # Correspondance entre les sommets TSP et les indices [0, 1, ..., n-1] du CVRPTW (0 = Dépôt v0)[cite: 6, 11]
    node_mapping = {original_v: idx for idx, original_v in enumerate(tsp_vertices)}
    reverse_mapping = {idx: original_v for original_v, idx in node_mapping.items()}

    # 1. Instanciation de CVRPTW_Network : k = 1 camion, Q = n (capacité totale)[cite: 11]
    # L'argument bound_b est retiré de l'initialisation pour correspondre à votre classe en mémoire
    cvrptw_net = CVRPTW_Network(
        n_customers=n_total - 1,
        k_trucks=1,
        capacity=n_total
    )
    # Ajout manuel de la borne B' = B[cite: 11]
    cvrptw_net.B = bound_b

    # 2. Création du Dépôt (0) et des Clients (1..n-1) avec relaxation des contraintes[cite: 6, 11]
    for idx in cvrptw_net.V:
        if idx == 0:
            # Dépôt v0 : demande nulle, fenêtre [0, +inf], service 0[cite: 6, 11]
            cvrptw_net.add_node(node_id=0, demand=0, e=0, l=float('inf'), s=0)
        else:
            # Client i in C : demande q_i = 1, fenêtre [0, +inf], service s_i = 0[cite: 11]
            cvrptw_net.add_node(node_id=idx, demand=1, e=0, l=float('inf'), s=0)

    # 3. Transfert des coûts TSP vers les temps de trajet t_ij = c_ij[cite: 11]
    for (u_orig, v_orig), cost in tsp_costs.items():
        i = node_mapping[u_orig]
        j = node_mapping[v_orig]
        cvrptw_net.set_travel_time(i, j, cost)

    # 4. Affichage graphique du réseau CVRPTW orienté
    if plot:
        g_cvrp = nx.DiGraph()
        g_cvrp.add_nodes_from(cvrptw_net.V)

        # Adaptation des positions géométriques aux nouveaux indices 0..N
        if pos is not None:
            pos_cvrp = {node_mapping[orig_v]: coord for orig_v, coord in pos.items()}
        else:
            pos_cvrp = nx.circular_layout(g_cvrp)

        fig, ax = plt.subplots(figsize=(9, 7))
        ax.set_title(
            f"3. Instance CVRPTW (CVRPTW_Network)\n"
            f"Flotte K = {cvrptw_net.K} | Capacité Q = {cvrptw_net.Q} | Borne B' = {cvrptw_net.B}",
            fontsize=13, fontweight="bold"
        )

        # Séparation visuelle entre le Dépôt (0) et les Clients (C)[cite: 6, 11]
        nx.draw_networkx_nodes(g_cvrp, pos_cvrp, nodelist=[0], ax=ax, node_color="#FF7043", node_size=1100, edgecolors="black", label="Dépôt v0 (i=0)")
        nx.draw_networkx_nodes(g_cvrp, pos_cvrp, nodelist=cvrptw_net.C, ax=ax, node_color="#4FC3F7", node_size=850, edgecolors="black", label="Clients C (i=1..N)")

        # Étiquettes internes des sommets
        node_labels = {0: f"v0\n(HC:{reverse_mapping[0]})"}
        for c in cvrptw_net.C:
            node_labels[c] = f"v{c}\n(HC:{reverse_mapping[c]})"
        nx.draw_networkx_labels(g_cvrp, pos_cvrp, labels=node_labels, ax=ax, font_size=9, font_weight="bold")

        # Annotations des paramètres Node (q_i, [e_i, l_i], s_i) sous chaque sommet[cite: 6, 11]
        for idx, (x, y) in pos_cvrp.items():
            node_obj = cvrptw_net.nodes[idx]
            param_text = f"q={node_obj.q} | TW=[{node_obj.e}, ∞] | s={node_obj.s}"
            ax.text(x, y - 0.15, param_text, fontsize=8.5, ha="center",
                    bbox=dict(boxstyle="round,pad=0.2", fc="#FFF9C4", ec="black", alpha=0.85))

        # Tracé des arcs orientés E = {(i, j)}[cite: 2, 6]
        edges_t1 = [(i, j) for (i, j), t in cvrptw_net.travel_times.items() if t == 1]
        edges_t2 = [(i, j) for (i, j), t in cvrptw_net.travel_times.items() if t == 2]

        nx.draw_networkx_edges(g_cvrp, pos_cvrp, edgelist=edges_t1, ax=ax, width=2.0, edge_color="#2E7D32",
                               arrows=True, arrowsize=18, connectionstyle="arc3,rad=0.08")
        nx.draw_networkx_edges(g_cvrp, pos_cvrp, edgelist=edges_t2, ax=ax, width=1.0, style="dashed", edge_color="#BDBDBD",
                               arrows=True, arrowsize=12, connectionstyle="arc3,rad=0.08")

        ax.legend(loc="upper right")
        ax.margins(0.2)
        ax.axis("off")
        plt.tight_layout()
        plt.show()

    return cvrptw_net








import networkx as nx
import matplotlib.pyplot as plt
# --- 1. Définition d'un graphe HC initial à 5 sommets ---
# Cycle existant : 1 -> 2 -> 3 -> 4 -> 5 -> 1 (plus une corde 2-5)
hc_vertices = [1, 2, 3, 4, 5]
hc_edges = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1), (2, 5)]

# --- 2. Étape 1 : Réduction HC -> TSP (avec affichage des 2 premiers graphes) ---
tsp_instance, fixed_pos = reduce_hc_to_tsp(hc_vertices, hc_edges, plot=True)

# --- 3. Étape 2 : Réduction TSP -> CVRPTW (avec affichage du réseau orienté CVRPTW) ---
cvrptw_network = reduce_tsp_to_cvrptw(tsp_instance, pos=fixed_pos, plot=True)

# --- 4. Vérification via la fonction objectif de CVRPTW_Network ---
# Route valide suivant les vraies arêtes : Dépôt(0) -> v1 -> v2 -> v3 -> v4 -> Dépôt(0)
valid_route = [[0, 1, 2, 3, 4, 0]]
cost_valid = cvrptw_network.calculate_objective(valid_route)

# Route invalide empruntant des arêtes de pénalité (ex: 0 -> 2 -> 4 -> 1 -> 3 -> 0)
invalid_route = [[0, 2, 4, 1, 3, 0]]
cost_invalid = cvrptw_network.calculate_objective(invalid_route)

print(f"Borne B' maximale autorisée : {cvrptw_network.B}")
print(f"Temps de conduite de la tournée valide {valid_route[0]} : {cost_valid} (<= B' : Solution réalisable)")
print(f"Temps de conduite de la tournée invalide {invalid_route[0]} : {cost_invalid} (> B' : Pas un cycle Hamiltonien)")


