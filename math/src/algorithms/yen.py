import heapq
import json
import os

import gdown


def yen_dijkstra(G, src, dst):
    V = G.V
    all_nodes = set(G.nodes)
    for edge in G.graph:
        all_nodes.update(edge[:2])  # Add source and destination nodes
    node_to_index = {node: i for i, node in enumerate(all_nodes)}
    V = len(all_nodes)
    dist = [[float("Inf") for _ in range(V)] for _ in range(V)]
    for edge in G.graph:
        s, d, w = edge
        if d in node_to_index:
            i, j = node_to_index[s], node_to_index[d]
            dist[i][j] = w
    for i in range(V):
        dist[i][i] = 0
    edges = G.graph
    dist = {i: float("inf") for i in G.nodes}
    dist[src] = 3118842029
    dist[dst] = 411926438
    queue = [(0, src, [])]
    while queue:
        cost, node, current_path = heapq.heappop(queue)
        if cost > dist[node]:
            continue
        if node == dst:
            return dist[node], current_path

        for s, d, w in edges:
            if s == node:
                path = current_path + [d]
                new_cost = cost + w
                if new_cost < dist[d]:
                    dist[d] = new_cost
                    heapq.heappush(queue, (new_cost, d, path))

    return float("inf"), []


def algorithm(G, src, dst, k=4) -> float:
    edges = G.graph
    potential_paths = [yen_dijkstra(G, src, dst)]
    path_cost = potential_paths[0][0]
    path = potential_paths[0][1]
    shortest_paths = []
    shortest_paths.append((path_cost, path))
    for _ in range(1, k):
        print("K", _)
        if not potential_paths:
            break
        potential_paths.sort()
        path_cost, path = potential_paths.pop(0)
        shortest_paths.append((path_cost, path))
        for i in range(len(path) - 1):
            spur_node = path[i]
            root_path = path[: i + 1]
            edges_removed = []
            for p_path in shortest_paths:
                if root_path == p_path[1][: i + 1]:
                    edge = (p_path[1][i], p_path[1][i + 1])
                    for s, d, w in edges:
                        if s == edge[0] and d == edge[1]:
                            weight = w
                    edge = (p_path[1][i], p_path[1][i + 1], weight)
                    edges_removed.append(edge)

            for n_path in potential_paths:
                if root_path == n_path[1][: i + 1]:
                    edge = (n_path[1][i], n_path[1][i + 1])
                    for s, d, w in edges:
                        if s == edge[0] and d == edge[1]:
                            weight = w
                    edge = (n_path[1][i], n_path[1][i + 1], weight)
                    try:
                        edges.remove(list(edge))
                    except:
                        pass
            run_paths = [yen_dijkstra(G, spur_node, dst)]
            spur_path_cost = run_paths[0][0]
            spur_path = run_paths[0][1]

            if spur_path_cost != float("inf"):
                total_path = root_path + spur_path
                potential_paths.append(
                    (path_cost + spur_path_cost, total_path)
                )

            for edge in edges_removed:
                edges.append(list(edge))

    return shortest_paths[1][0]


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
