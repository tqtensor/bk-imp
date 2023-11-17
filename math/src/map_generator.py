import json
import os
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

# Create adjacency matrix
adjacency_matrix = defaultdict(dict)
for u, v, data in graph.edges(data=True):
    if data["highway"] in [
        "trunk",
        "primary",
        "secondary",
        "tertiary",
        "residential",
    ]:
        adjacency_matrix[u][v] = data["length"]
print("Number of nodes:", len(adjacency_matrix))

# Find the nodes nearest to the start and end coordinates
start_node = ox.distance.nearest_nodes(
    G=graph, Y=start_coords[0], X=start_coords[1]
)
end_node = ox.distance.nearest_nodes(G=graph, Y=end_coords[0], X=end_coords[1])

# Store data for further analysis
data = {
    "start_node": start_node,
    "end_node": end_node,
    "adjacency_matrix": adjacency_matrix,
}
with open("data.json", "w") as f:
    json.dump(data, f)
