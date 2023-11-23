import os

import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def plot_solution(G, path, algorithm: str):
    # Create a list of colors for the nodes
    node_colors = []
    for node in G.nodes():
        if node in path:
            node_colors.append("yellow")  # Nodes in the path are yellow
        elif node == start_node:
            node_colors.append("green")  # Start node is green
        elif node == end_node:
            node_colors.append("red")  # End node is red
        else:
            node_colors.append("black")  # All other nodes are black

    # Plot the graph on OSM
    fig, ax = ox.plot_graph(
        G,
        bgcolor="white",
        node_color=node_colors,
        edge_color="blue",
    )

    # Save the plot to a file with high resolution
    plt.savefig(f"graph_plot_{algorithm}.png", dpi=600)


if __name__ == "__main__":
    # Load graph from GraphML file
    G = ox.load_graphml("sub_graph.graphml")

    # Start and end nodes
    start_node = 3118842029
    end_node = 411926438

    # Find shortest path using Bellman-Ford algorithm
    path = nx.bellman_ford_path(G, start_node, end_node)
    plot_solution(G, path, "bellman_ford")

    # Find 5 shortest paths using Yen algorithm
    paths = list(
        nx.shortest_simple_paths(
            nx.DiGraph(G), start_node, end_node, weight="length"
        )
    )
    for i in range(5):
        path = paths[i]
        plot_solution(G, path, f"yen_k{i}")
