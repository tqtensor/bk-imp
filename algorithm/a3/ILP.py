import copy
import os
import pickle
import random

import networkx as nx
import numpy as np
import osmnx as ox
import pulp as pl
from haversine import Unit, haversine_vector
from networkx.exception import NetworkXNoPath
from tqdm.auto import tqdm

# CPLEX solver
os.environ["CPLEX_HOME"] = "/opt/ibm/ILOG/CPLEX_Studio2211/cplex"
os.environ["CPO_HOME"] = "/opt/ibm/ILOG/CPLEX_Studio2211/cpoptimizer"
os.environ["PATH"] += (
    ":"
    + os.environ["CPLEX_HOME"]
    + "/bin/x86-64_linux:"
    + os.environ["CPO_HOME"]
    + "/bin/x86-64_linux"
)
os.environ["LD_LIBRARY_PATH"] += (
    ":"
    + os.environ["CPLEX_HOME"]
    + "/bin/x86-64_linux:"
    + os.environ["CPO_HOME"]
    + "/bin/x86-64_linux"
)
os.environ[
    "PYTHONPATH"
] = "/opt/ibm/ILOG/CPLEX_Studio2211/cplex/python/3.10/x86-64_linux"


def calculate_distance(graph, source_node, target_node):
    try:
        shortest_path_length = (
            nx.shortest_path_length(
                graph, source_node, target_node, weight="length"
            )
            / 1000
        )
    except NetworkXNoPath:
        shortest_path_length = 999999
    return shortest_path_length


def update_distance_matrix(wr: dict):
    to_update = []
    for w in warehouse_ids:
        for s in store_ids:
            if (pl.value(wr[w][s]) == 1) & (not updated_cost[w][s]):
                to_update.append((w, s))

    for w, s in tqdm(
        to_update, total=len(to_update), desc="Updating distance matrix"
    ):
        new_cost = calculate_distance(
            graph,
            warehouses[w][0],
            stores[s][0],
        )
        d_cost[w][s] = new_cost
        updated_cost[w][s] = True


def solve_problem():
    # Set up the problem
    problem = pl.LpProblem("Warehouse_Optimization", pl.LpMinimize)

    # Decision variables
    wr = pl.LpVariable.dicts(
        "warehouse_store_connection", (warehouse_ids, store_ids), cat="Binary"
    )

    # Objective function
    total_cost = pl.lpSum(
        w_cost[w] * wr[w][s] + d_cost[w][s] * wr[w][s]
        for w in warehouse_ids
        for s in store_ids
    )
    problem += total_cost

    # Constraints
    # Each store must be assigned to one warehouse
    for i in store_ids:
        problem += pl.lpSum(wr[j][i] for j in warehouse_ids) == 1

    # Total demand of assigned stores for a warehouse
    # must be smaller than its capacity
    for w in warehouse_ids:
        problem += (
            pl.lpSum(demands[s] * wr[w][s] for s in store_ids) <= w_capacity[w]
        )

    # Solve the problem using CPLEX solver
    problem.solve(pl.CPLEX_CMD(timeLimit=120, threads=6, msg=0))

    # Print the total cost
    print("Total Cost: ", pl.value(problem.objective))

    # Update distance matrix
    update_distance_matrix(wr)


if __name__ == "__main__":
    # Create OSM map of HCMC
    if not os.path.exists("ho_chi_minh_city.graphml"):
        graph = ox.graph_from_place(
            "Ho Chi Minh City", network_type="drive", simplify=False
        )
        ox.save_graphml(graph, filepath="ho_chi_minh_city.graphml")
    else:
        graph = ox.io.load_graphml("ho_chi_minh_city.graphml")

    # Load warehouses and stores data
    with open("warehouses.pkl", "rb") as f:
        warehouses = pickle.load(f)
    with open("stores.pkl", "rb") as f:
        stores = pickle.load(f)

    M = 100  # Number of warehouses
    N = 1000  # Number of stores

    # Randomly select M warehouses and N stores
    warehouses = random.sample(warehouses, k=M)
    stores = random.sample(stores, k=N)

    # Calculate distance matrix
    dinstance_matrix = haversine_vector(
        [(store[1], store[2]) for store in stores],
        [(warehouse[1], warehouse[2]) for warehouse in warehouses],
        Unit.KILOMETERS,
        comb=True,
    )

    # Define problem variables
    warehouse_ids = range(M)
    w_cost = random.sample(
        range(100, 201), M
    )  # Operational cost of warehouses
    w_capacity = random.sample(
        range(13000, 15001), M
    )  # Operational cost of warehouses
    store_ids = range(N)
    demands = random.sample(range(10, 1101), N)  # Daily demand of stores
    d_cost = copy.copy(
        dinstance_matrix
    )  # Delivery cost between warehouses vs stores
    updated_cost = np.full_like(
        d_cost, False
    )  # Whether the cost is updated based on actual map distance

    assert sum(w_capacity) > sum(
        demands
    ), "All warehouses' capacity is less than stores' demands"

    # We will continously update the distance matrix until there is no change
    for i in range(100):
        print(f"Iteration {i+1}")

        # Capture the current distance matrix
        d_cost_old = copy.copy(d_cost)

        # Solve the problem and update distance matrix
        solve_problem()

        # Check if the distance matrix is updated
        if np.array_equal(d_cost, d_cost_old):
            break
