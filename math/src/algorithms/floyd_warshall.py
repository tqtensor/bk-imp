import json
import os

import gdown

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def algorithm(G, src: str, dst: str) -> float:
    # Create a set of all nodes, including those in the graph
    all_nodes = set(G.nodes)
    for edge in G.graph:
        all_nodes.update(edge[:2])  # Add source and destination nodes

    # Map nodes to integer indices
    node_to_index = {node: i for i, node in enumerate(all_nodes)}

    # Calculate V
    V = len(all_nodes)

    dist = [[float("Inf") for _ in range(V)] for _ in range(V)]

    # Initialize distances with edge weights
    for edge in G.graph:
        s, d, w = edge
        if d in node_to_index:
            i, j = node_to_index[s], node_to_index[d]
            dist[i][j] = w

    # Set the diagonal to zero
    for i in range(V):
        dist[i][i] = 0

    # Floyd-Warshall algorithm
    for k in range(V):
        for i in range(V):
            for j in range(V):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    src_index = node_to_index[src]
    dst_index = node_to_index[dst]

    return dist[src_index][dst_index]


def main():
    # --- DONT CHANGE ANYTHING BELOW THIS LINE ------------------------------ #
    # Download data
    if not os.path.exists("data.json"):
        gdown.download(id="1TtyDKRnas9KEEnLtmskybLYAA8LCQEE3")

    # Load data
    data = json.load(open("data.json", "r"))
    graph = data["adjacency_matrix"]
    start, end = (
        str(data["start_node"]),
        str(data["end_node"]),
    )

    # Initializing the Graph Class
    class Graph:
        def __init__(self, vertices):
            self.V = vertices
            self.graph = []
            self.nodes = []

        def add_edge(
            self, s, d, w
        ):  # s: source, d: destination, w: weight (length)
            self.graph.append([s, d, w])

        def add_node(self, value):
            self.nodes.append(value)

    g = Graph(len(graph))
    for node in graph:
        g.add_node(node)
    for s in graph:
        for d in graph[s]:
            g.add_edge(s, d, graph[s][d])

    # Run the algorithm
    shortest_distance = algorithm(G=g, src=start, dst=end)
    assert (shortest_distance >= 5500) & (
        shortest_distance <= 7500
    ), f"Wrong answer! {shortest_distance}"
    print(
        "Shortest distance from {} to {} is {}".format(
            start, end, shortest_distance
        )
    )


if __name__ == "__main__":
    import cProfile
    import pstats

    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("tottime")

    # Save stats to file
    stats.dump_stats("profiling_results.pstats")
