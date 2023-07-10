#import "template.typ": *
#let title = "Project: NYC Taxi Demand Forecasting"
#let author = "Do Vo Hoang Hung, Ngo Trieu Long, Tang Quoc Thai"
#let course_id = "CO5241"
#let instructor = "Quan Thanh Tho"
#let semester = "Spring 2023"
#set enum(numbering: "a)")
#set heading(numbering: "1.1)")
#set par(justify: true)
#show: assignment_class.with(title, author, course_id, instructor, semester)

#prob[
TODO: add problem description
Expectations from the professor:
- Project description
- Background theory
- The dataset and preprocessing steps
- The details about the pipeline from input-->output
- Results evaluation (state clearly about the used metrics)
]

= Solution

== Problem Formulation
The goal of this Capacitated Facility Location Problem (CFLP) is to determine the number and location of warehouses that will meet the stores demand while reducing fixed and transportation costs. Therefore, we can pose the problem as the minimization of the following objective function:

$ sum_(i=0)^M (w_(i) * (f_(i) + sum_(j=0)^N c_(i j) * r_(i j))) $

Where,

N is a set of stores locations.

M is a set of candidate warehouse locations.

$w_(i)$ is a binary variable that indicates whether warehouse i is open or not.

$f_(i)$ is the fixed cost of opening warehouse i.

$c_(i j)$ is the cost of shipping from warehouse i to store j.

$r_(i j)$ is the binary variable that indicates whether warehouse i is used to supply store j or not.

=== Decision Variables

- $w_(i)$ is a binary variable that indicates whether warehouse i is open or not.

- $r_(i j)$ is the binary variable that indicates whether warehouse i is used to supply store j or not.

=== Constraints

==== Each store must be assigned to one warehouse

$ sum_(i=0)^M r_(i j) = 1, forall j in N $

==== The number of packages shipped from a warehouse must not exceed its capacity

$ sum_(j=0)^N r_(i j) <= u_(i), forall i in M $

==== The number of chosen warehouses should be less than 19 (approximately the number of districts in Ho Chi Minh City)

$ sum_(i=0)^M w_(i) <= 19 $

==== If a warehouse is chosen, then at least one store must be assigned to it

$ sum_(j=0)^N r_(i j) <= N * w_(i), forall i in M $

- If $w_(i) = 0$, then $sum_(j=0)^N r_(i j) = 0$, means that warehouse i is not chosen, then it is not used to supply any store.

- If $w_(i) = 1$, then $ N >= sum_(j=0)^N r_(i j) >= 1$, means that warehouse i is chosen, then it is used to supply at least one store.

=== Distance Calculation
While the current assignment assumes a manageable number of 1000 stores, real-life applications often rely on expensive map provider APIs like Google Maps for determining the shortest distances. To address this issue, I propose an alternative approach that optimizes the number of distance calculations using the Haversine formula as an approximation. The algorithm can be summarized as follows:

- *Step 1*: The Haversine formula is employed to compute the distance matrix between all warehouses and stores. This provides an estimate of the distances.
- *Step 2*: CPLEX solver is utilized to solve the optimization problem and determine the optimal paths connecting the stores and warehouses.
- *Step 3*: The connected paths obtained from the solver are used to update the distances. To achieve this, the actual distances between the connected warehouse and shop locations are obtained by performing a shortest path search using the OSM data (simulating actual Google Maps API).
- *Step 4*: The algorithm checks if the number of updated distances changes by less than 5% over five consecutive iterations.
    - *Step 4.1*: If the number of updated distances changes by less than 5% for five consecutive steps, the algorithm terminates.
    - *Step 4.2*: If the number of updated distances changes by more than 5%, the algorithm returns to step 2 to run the solver again with updated distances.

To keep track of the updated distances, I use a variable $d_(i j)$, intialized to be 0, to indicate whether the distance between warehouse i and store j is updated or not. If the distance is updated, then $d_(i j) = 1$, otherwise $d_(i j) = 0$.

The number of updated distances is computed as follows:
$ sum d $

=== Solver
The solver used for this assignment is CPLEX. The solver is invoked using the following command:

```python
problem.solve(pl.CPLEX_CMD(timeLimit=time_limit, msg=1))
```

Where `time_limit` is the maximum time allowed for the solver to run.

In each iteration, the solver is invoked with a time limit of 300 seconds, and in the final iteration, the solver is invoked with a time limit of 3600 seconds to further fine-tune the solution.

== Results

There are 10 experiments conducted to evaluate the performance of the proposed algorithm. In each experiment, there are 50 random warehouses and 1000 random stores generated. The results are summarized in the following chart:

#figure(
  image("experiments.png", width: 80%),
  caption: [
    Total cost and Number of updated distances for 10 experiments
  ],
)

In general, the proposed algorithm is able to find the optimal solution for all experiments. The number of distances we need to query from API is 50,000 ($N * M$) but in this setup we can reduce the number of API calls to approximately 4,000. In this case, we can save 92% of the cost for using the API.

The overall map of Ho Chi Minh City with the optimal allocation is shown as follows:

#figure(
  image("overall_map.png", width: 80%),
  caption: [
    Map of Ho Chi Minh City with the optimal allocation (car icon: warehouse, cart icon: store)
  ],
)

== Conclusion

In this assignment, I have proposed an algorithm to solve the Capacitated Facility Location Problem (CFLP) by formulating it as a Mixed Integer Linear Programming (MILP) problem. The proposed algorithm optimizes the number of distance calculations by using the Haversine formula as an approximation for the distance calculation. The proposed algorithm is able to find the optimal solution for all experiments. Moreover, the algorithm can reduce the number of distance calculations by 92% compared to the naive approach.

=== Future Work

- Using clustering techniques to initialize the warehouses and stores connections, as we can see in the map, the warehouses are not evenly distributed, so we can use clustering techniques to group the warehouses and stores into clusters, then we can query the map API for distances inside each cluster.

- Post analysis, we can analyze the seems to be outliers in the map, for example, the store looks very far from the warehouse, we can analyze the reason for that and propose a solution to fix it, such as the figure below:

#figure(
  image("zoomed_map.png", width: 80%),
  caption: [
    An outlier store in the map (purple cluster)
  ],
)
