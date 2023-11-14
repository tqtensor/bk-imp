import json
import os
from collections import defaultdict

import requests

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 1. Find the latitude and longitude coordinates for Ho Chi Minh City.
lat_min = 10.772998489385182
lat_max = 10.773644541784831
lon_min = 106.65690841493029
lon_max = 106.69978032449819

# 2. Use the Overpass API to query OpenStreetMap for all ways (streets) within
# a certain bounding box around Ho Chi Minh City.
if not os.path.exists("data.json"):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
        [out:json];
        way({lat_min},{lon_min},{lat_max},{lon_max})["highway"];
        out;
    """
    response = requests.get(overpass_url, params={"data": overpass_query})
    data = response.json()

    # Cache the response
    with open("data.json", "w") as file:
        file.write(response.text)
else:
    with open("data.json", "r") as file:
        data = json.load(file)

# 3. For each way, extract all of its nodes (vertices).
nodes = defaultdict(list)
for element in data["elements"]:
    if (
        (element["type"] == "way")
        & (
            element["tags"]["highway"]
            in ["trunk", "primary", "secondary", "tertiary", "residential"]
        )
        & ("name" in element["tags"])
    ):
        for node_id in element["nodes"]:
            nodes[node_id].append(
                {"id": element["id"], "name": element["tags"]["name"]}
            )


# 4. Build a graph from the nodes (vertices).
class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = defaultdict(list)

    def addEdge(self, u, v):
        self.graph[u].append(v)

    def printAllPathsUtil(self, u, d, visited, path):
        visited[u] = True
        path.append(u)

        if u == d:
            print(path)
        else:
            for i in self.graph[u]:
                if visited[i] == False:
                    self.printAllPathsUtil(i, d, visited, path)

        path.pop()
        visited[u] = False

    def printAllPaths(self, s, d):
        visited = [False] * (self.V)
        path = []
        self.printAllPathsUtil(s, d, visited, path)


# Build the graph
graph = Graph(len(nodes))
for element in data["elements"]:
    if (
        (element["type"] == "way")
        & (
            element["tags"]["highway"]
            in ["trunk", "primary", "secondary", "tertiary", "residential"]
        )
        & ("name" in element["tags"])
    ):
        for i in range(len(element["nodes"]) - 1):
            graph.addEdge(element["nodes"][i], element["nodes"][i + 1])


Graph.printAllPaths(graph, 6766658627, 473382796)
