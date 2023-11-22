import heapq
import json
import os

import gdown

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def algorithm(G, src: str, dst: str) -> float:
    # Create a set of all nodes, including those in the graph
    all_nodes = set(G.nodes)
    for edge in G.graph:
        all_nodes.update(edge[:2])  # Add source and destination nodes

    edges = G.graph

    dist = {i: float("Inf") for i in all_nodes}
    dist[src] = 0

    g = {i: 0 for i in all_nodes}

    heap = [(0, src)]

    while heap:
        f, current = heapq.heappop(heap)
        if current == dst:
            return dist[dst]

        if dist[current] < f:
            continue

        for s, d, w in edges:
            if s == current:
                neighbor, weight = d, w
                new_g = g[current] + weight
                new_f = new_g + bellman_ford(G, current, dst)

                if new_f < dist[neighbor]:
                    dist[neighbor] = new_f
                    g[neighbor] = new_g
                    heapq.heappush(heap, (new_f, neighbor))

    return dist[dst]


def bellman_ford(G, src, dst):
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
    stats = pstats.Stats(profiler).sort_stats("tottime")

    # Save stats to file
    stats.dump_stats("profiling_results.pstats")
