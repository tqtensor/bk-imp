import copy
import multiprocessing
import os
import pickle
import random

import networkx as nx
import numpy as np
import osmnx as ox
import pulp as pl
from haversine import Unit, haversine_vector
from networkx import Graph
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
LD_LIBRARY_PATH = os.environ.get("LD_LIBRARY_PATH")
if LD_LIBRARY_PATH:
    os.environ["LD_LIBRARY_PATH"] = LD_LIBRARY_PATH + (
        ":"
        + os.environ["CPLEX_HOME"]
        + "/bin/x86-64_linux:"
        + os.environ["CPO_HOME"]
        + "/bin/x86-64_linux"
    )
else:
    os.environ["LD_LIBRARY_PATH"] = (
        ":"
        + os.environ["CPLEX_HOME"]
        + "/bin/x86-64_linux:"
        + os.environ["CPO_HOME"]
        + "/bin/x86-64_linux"
    )
os.environ[
    "PYTHONPATH"
] = "/opt/ibm/ILOG/CPLEX_Studio2211/cplex/python/3.10/x86-64_linux"


# Number of threads
threads = multiprocessing.cpu_count() - 2


def check_early_stopping(log_file, window_size=10, threshold=10):
    num_updated_distances = []
    with open(log_file, "r") as file:
        lines = file.readlines()

    for line in lines:
        if line.startswith("Num of updated distances:"):
            num_updated = int(line.split(":")[-1].strip())
            num_updated_distances.append(num_updated)

    if len(num_updated_distances) < window_size:
        return False  # Not enough iterations for early stopping

    last_window = num_updated_distances[-window_size:]
    for i in range(window_size - 1):
        if abs((last_window[i + 1] / (last_window[i] + 1)) - 1) > (
            threshold / 100
        ):
            return False  # Continue optimization
    return True  # Perform early stopping


def calculate_distance(
    graph: Graph, source_node: int, target_node: int
) -> int:
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


def update_distance(args):
    w, s = args
    new_cost = calculate_distance(graph, warehouses[w][0], stores[s][0])
    return w, s, new_cost


def update_distance_matrix(wr: dict):
    to_update = []
    for w in warehouse_ids:
        for s in store_ids:
            if (pl.value(wr[w][s]) == 1) and (not updated_cost[w][s]):
                to_update.append((w, s))

    num_processes = max(threads, 1)
    pool = multiprocessing.Pool(processes=num_processes)
    results = list(
        tqdm(
            pool.imap(update_distance, to_update),
            total=len(to_update),
            desc="Updating distance matrix",
        )
    )

    # Update d_cost with the collected new_cost values
    for w, s, new_cost in results:
        d_cost[w][s] = new_cost
        updated_cost[w][s] = True

    pool.close()
    pool.join()


def solve_problem(exp: int, it: int, time_limit: int):
    # Set up the problem
    problem = pl.LpProblem("Warehouse_Optimization", pl.LpMinimize)

    # Decision variables
    wr = pl.LpVariable.dicts(
        "warehouse_store_connection", (warehouse_ids, store_ids), cat="Binary"
    )

    chosen_warehouse = pl.LpVariable.dicts(
        "chosen_warehouse", warehouse_ids, cat="Binary"
    )

    # Objective function
    total_cost = pl.lpSum(
        chosen_warehouse[w]
        * (w_cost[w] + pl.lpSum(d_cost[w][s] * wr[w][s] for s in store_ids))
        for w in warehouse_ids
    )
    problem += total_cost

    # Constraints
    # Each store must be assigned to one warehouse
    for s in store_ids:
        problem += pl.lpSum(wr[w][s] for w in warehouse_ids) == 1

    # Total demand of assigned stores for a warehouse
    # must be smaller than its capacity
    for w in warehouse_ids:
        problem += (
            pl.lpSum(demands[s] * wr[w][s] for s in store_ids) <= w_capacity[w]
        )

    # The number of chosen warehouses should be less than 19
    problem += pl.lpSum(chosen_warehouse[w] for w in warehouse_ids) <= 19

    # If a warehouse is chosen, then at least one store must be assigned
    for w in warehouse_ids:
        problem += (
            pl.lpSum(wr[w][s] for s in store_ids) <= N * chosen_warehouse[w]
        )

    # Solve the problem using CPLEX solver
    problem.solve(pl.CPLEX_CMD(timeLimit=time_limit, msg=1))

    # Print the total cost
    print("Total cost: ", pl.value(problem.objective))

    # Save the results
    with open(f"results/exp{exp+1}/result.txt", "a") as f:
        f.write(f"Iteration {it+1}\n")
        f.write(f"Total cost: {pl.value(problem.objective)}\n")
        f.write(
            "Num of updated distances: {}\n".format(
                np.sum(updated_cost == True)  # noqa
            )
        )

    with open(f"results/exp{exp+1}/wr.pkl", "wb") as f:
        f.write(pickle.dumps(wr))

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
        master_warehouses = pickle.load(f)
    with open("stores.pkl", "rb") as f:
        master_stores = pickle.load(f)

    for exp in range(10):
        try:
            print(f"Experiment {exp+1}")
            os.makedirs(f"results/exp{exp+1}", exist_ok=True)

            M = 50  # Number of warehouses
            N = 1000  # Number of stores

            # Randomly select M warehouses and N stores
            warehouses = random.sample(master_warehouses, k=M)
            stores = random.sample(master_stores, k=N)

            # Save the selected warehouses and stores
            with open(f"results/exp{exp+1}/warehouses.pkl", "wb") as f:
                pickle.dump(warehouses, f)
            with open(f"results/exp{exp+1}/stores.pkl", "wb") as f:
                pickle.dump(stores, f)
            with open(f"results/exp{exp+1}/result.txt", "a") as f:
                f.write(f"Number of warehouses: {M}\n")
                f.write(f"Number of stores: {N}\n")

            # Calculate distance matrix based on Harversine formula
            dinstance_matrix = haversine_vector(
                [(store[1], store[2]) for store in stores],
                [(warehouse[1], warehouse[2]) for warehouse in warehouses],
                Unit.KILOMETERS,
                comb=True,
            )

            # Define problem variables
            store_ids = range(N)
            demands = [
                random.randint(100, 200) for _ in range(N)
            ]  # Daily demand of stores
            total_demand = sum(demands)

            d_cost = copy.copy(
                dinstance_matrix
            )  # Delivery cost between warehouses vs stores
            updated_cost = np.full_like(
                d_cost, False
            )  # Whether the cost is updated based on actual map distance

            warehouse_ids = range(M)
            w_cost = [
                random.randint(100, 200) for _ in range(M)
            ]  # Operational cost of warehouses
            # Generate warehouse capacities until the sum is larger than
            # the total demands
            w_capacity_sum = 0
            w_capacity = []
            start_capacity = 100
            while (
                w_capacity_sum / 50 * 19 <= total_demand
            ):  # because we want to select 19 from 50 warehouses
                w_capacity = [
                    random.randint(start_capacity - 50, start_capacity + 50)
                    for _ in range(M)
                ]  # Operational cost of warehouses
                w_capacity_sum = sum(w_capacity)
                start_capacity += 100

            assert sum(w_capacity) > sum(
                demands
            ), "All warehouses' capacity is less than stores' demands"

            # We will continously update the distance matrix
            # until there is no change
            for i in range(10000):
                print(f"Iteration {i+1}")

                # Solve the problem and update distance matrix
                solve_problem(exp=exp, it=i, time_limit=300)

                # Check early stopping condition
                if check_early_stopping(
                    f"results/exp{exp+1}/result.txt", 5, 5
                ):
                    # Solve the problem one more time with very small gap
                    # to make sure the solution is optimal
                    print(f"Final iteration {i+1}")
                    solve_problem(exp=exp, it=i + 1, time_limit=3600)
                    break
        except Exception as ex:
            print(ex)
