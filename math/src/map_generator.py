import json
import os
import random
from collections import defaultdict

import geopy
import geopy.distance
import osmnx as ox

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# GPS coordinates
start_coords = (10.772646642773418, 106.65934087496362)
end_coords = (10.772527329147216, 106.69805298186968)

# Calculate the bounding box with 1 km padding
start_point = geopy.Point(start_coords)
end_point = geopy.Point(end_coords)

north = (
    geopy.distance.geodesic(kilometers=1)
    .destination(
        geopy.Point(
            max(start_point.latitude, end_point.latitude),
            start_point.longitude,
        ),
        0,
    )
    .latitude
)
south = (
    geopy.distance.geodesic(kilometers=1)
    .destination(
        geopy.Point(
            min(start_point.latitude, end_point.latitude),
            start_point.longitude,
        ),
        180,
    )
    .latitude
)
east = (
    geopy.distance.geodesic(kilometers=1)
    .destination(
        geopy.Point(
            start_point.latitude,
            max(start_point.longitude, end_point.longitude),
        ),
        90,
    )
    .longitude
)
west = (
    geopy.distance.geodesic(kilometers=1)
    .destination(
        geopy.Point(
            start_point.latitude,
            min(start_point.longitude, end_point.longitude),
        ),
        270,
    )
    .longitude
)

# Create OSM map of HCMC
if not os.path.exists("ho_chi_minh_city.graphml"):
    graph = ox.graph_from_place(
        "Ho Chi Minh City", network_type="drive", simplify=False
    )
    ox.save_graphml(graph, filepath="ho_chi_minh_city.graphml")
else:
    graph = ox.io.load_graphml("ho_chi_minh_city.graphml")

# Prune nodes outside the bounding box
graph = ox.truncate.truncate_graph_bbox(
    graph, north, south, east, west, retain_all=True
)

# Filter the edges in the graph
edges = [
    (u, v, k)
    for u, v, k, data in graph.edges(data=True, keys=True)
    if data["highway"] in ["primary", "secondary", "tertiary"]
]

# Create a new graph from the filtered edges
sub_graph = graph.edge_subgraph(edges)

# Find the nodes nearest to the start and end coordinates
start_node = ox.distance.nearest_nodes(
    G=sub_graph, Y=start_coords[0], X=start_coords[1]
)
end_node = ox.distance.nearest_nodes(
    G=sub_graph, Y=end_coords[0], X=end_coords[1]
)

# Find shortest paths between the start and end nodes
paths = ox.distance.k_shortest_paths(
    G=sub_graph,
    orig=start_node,
    dest=end_node,
    weight="length",
    k=100,
)

# Collect nodes of these paths
path_nodes = set()
for path in paths:
    path_nodes.update(path)

# Remove nodes that are not in the paths
non_connected_nodes = [
    (u, v, k)
    for u, v, k, _ in graph.edges(data=True, keys=True)
    if (u not in path_nodes) and (v not in path_nodes)
]
connected_edges = [
    (u, v, k)
    for u, v, k, _ in graph.edges(data=True, keys=True)
    if u in path_nodes and v in path_nodes
]

# Shuffle non_connected_nodes
random.shuffle(non_connected_nodes)

# Take 20% of non_connected_nodes
half_non_connected_nodes = non_connected_nodes[
    : int(len(non_connected_nodes) * 0.20)
]

# Combine half_non_connected_nodes with connected_edges
edges = half_non_connected_nodes + connected_edges

# Create a new graph from the filtered edges
sub_graph = graph.edge_subgraph(edges)

# Store subgraph
ox.save_graphml(sub_graph, filepath="sub_graph.graphml")

# Create adjacency matrix
adjacency_matrix = defaultdict(dict)
for u, v, data in sub_graph.edges(data=True):
    adjacency_matrix[u][v] = data["length"]
print("Number of nodes:", len(adjacency_matrix))

# Store data for further analysis
data = {
    "start_node": start_node,
    "end_node": end_node,
    "adjacency_matrix": adjacency_matrix,
}
with open("data.json", "w") as f:
    json.dump(data, f)
