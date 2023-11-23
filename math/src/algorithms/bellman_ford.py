import json
import os

import gdown

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def algorithm(G, src: str, dst: str) -> float:
    V = G.V
    edges = G.graph

    dist = {i: float("Inf") for i in G.nodes}
    dist[src] = 0

    for _ in range(V - 1):
        for s, d, w in edges:
            if d not in dist:
                dist[d] = float("Inf")
            else:
                if dist[s] != float("Inf") and dist[s] + w < dist[d]:
                    dist[d] = dist[s] + w
                    if d == dst:
                        return dist[dst]

    for s, d, w in edges:
        if dist[s] != float("Inf") and dist[s] + w < dist[d]:
            print("Graph contains negative cycle")
            return

    return dist[dst]


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

    # Save profiling stats to a file
    stats = pstats.Stats(
        profiler, stream=open("bellman_ford_report.txt", "w")
    ).sort_stats("tottime")
    stats.print_stats()
