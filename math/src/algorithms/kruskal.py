import json
import os

import gdown

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def find(parent, i):
    if parent[i] != i:
        parent[i] = find(parent, parent[i])  # Path compression
    return parent[i]


def union(parent, rank, x, y):
    x_root = find(parent, x)
    y_root = find(parent, y)

    if x_root != y_root:
        if rank[x_root] < rank[y_root]:
            parent[x_root] = y_root
        elif rank[x_root] > rank[y_root]:
            parent[y_root] = x_root
        else:
            parent[y_root] = x_root
            rank[x_root] += 1


def kruskal(G, src, dst):
    result = []
    i = 0
    e = 0

    parent = {}
    rank = {}

    for src, dst, _ in G.graph:
        parent[src] = src
        parent[dst] = dst
        rank[src] = 0
        rank[dst] = 0

    while e < len(parent) - 1:
        if i >= len(G.graph):
            break

        src, dst, weight = G.graph[i]
        i += 1
        x = find(parent, src)
        y = find(parent, dst)

        if x != y:
            e += 1
            result.append((src, dst, weight))
            union(parent, rank, x, y)

    return result


def algorithm(G, src, dst) -> float:
    minimum_spanning_tree = kruskal(G, src, dst)

    # Convert the minimum spanning tree to an adjacency list
    adjacency_list = {}
    for edge in minimum_spanning_tree:
        u, v, weight = edge
        adjacency_list.setdefault(u, []).append((v, weight))
        adjacency_list.setdefault(v, []).append((u, weight))

    def dfs_helper(src, dst):
        stack = [(src, 0)]
        visited = set()

        while stack:
            current_node, current_weight = stack.pop()

            if current_node == dst:
                return current_weight

            if current_node not in visited:
                visited.add(current_node)

                for neighbor, weight in adjacency_list.get(current_node, []):
                    # print("{} - {}".format(current_node, neighbor))
                    stack.append((neighbor, current_weight + weight))

        return float("inf")

    # Find the weight of the path between src and dst
    min_weight = dfs_helper(src, dst)

    return min_weight if min_weight != float("inf") else None


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
