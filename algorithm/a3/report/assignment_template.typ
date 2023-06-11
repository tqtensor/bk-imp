#import "template.typ": *
#let title = "Assignment #3"
#let author = "Tang Quoc Thai"
#let course_id = "CO5127"
#let instructor = "Tran Van Hoai"
#let semester = "Spring 2023"
#set enum(numbering: "a)")
#set heading(numbering: "1.1)")
#set par(justify: true)
#show: assignment_class.with(title, author, course_id, instructor, semester)

#prob[
The programmer has to decide which warehouses in a given set will be open and which shops an individual warehouse supplies. The detailed problem statement is given as follows.

There are n possible warehouses and m shops. The programmer wishes to choose 
- (1) which of the n warehouses to open, and
- (2) which (open) warehouses to use to supply the m shops, in order to satisfy some fixed daily demand (of shops) at minimum cost. It is assumed that there is a (fixed) cost to open a warehouse, denoted by $f_{i}$. Let shop j denoted by ${j}$ and $c_{i j}$ denote the cost to ship a package of goods from warehouse i to shop j.

Let $d_{j}$ denote the daily demand (in package) of shop j. Moreover, a warehouse has a maximum output. Let $u_{i}$ denote the maximum number of packages which is manageable by warehouse i (i.e., $u_{i}$ denotes the capacity of warehouse i). Note that shipping cost $c_{i j}$ is computed by the travel distance from warehouse i to shop j (shortest path).
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
While the current assignment assumes a manageable number of 1000 stores, real-life applications often rely on expensive map provider APIs like Google Maps for determining the shortest distances. To address this issue, we propose an alternative approach that optimizes the number of distance calculations using the Haversine formula as an approximation. The algorithm can be summarized as follows:

- *Step 1*: The Haversine formula is employed to compute the distance matrix between all warehouses and stores. This provides an estimate of the distances.
- *Step 2*: CPLEX solver is utilized to solve the optimization problem and determine the optimal paths connecting the stores and warehouses.
- *Step 3*: The connected paths obtained from the solver are used to update the distances. To achieve this, the actual distances between the connected warehouse and shop locations are obtained by performing a shortest path search using the OSM data.
- *Step 4*: The algorithm checks if the number of updated distances changes by less than 5% over five consecutive iterations.
    - *Step 4.1*: If the number of updated distances changes by less than 5% for five consecutive steps, the algorithm terminates.
    - *Step 4.2*: If the number of updated distances changes by more than 5%, the algorithm returns to step 2 to run the solver again with updated distances.

To keep track of the updated distances, we use a variable $d_(i j)$, intialized to be 0, to indicate whether the distance between warehouse i and store j is updated or not. If the distance is updated, then $d_(i j) = 1$, otherwise $d_(i j) = 0$.

The number of updated distances is computed as follows:
$ sum d $

=== Solver
The solver used for this assignment is CPLEX. The solver is invoked using the following command:

```python
problem.solve(pl.CPLEX_CMD(timeLimit=time_limit, msg=1))
```

Where `time_limit` is the maximum time allowed for the solver to run.
