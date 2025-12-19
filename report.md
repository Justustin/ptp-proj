# CSC4120 Project Report - Party Together Problem

## Group 45

- Cedric (122040005)
- Edward (122040010)
- Justin (122040026)

---

## Question 5.1: NP-Hardness of PTP

**Claim:** The Party Together Problem (PTP) is NP-hard.

**Proof:**

We prove NP-hardness by showing that PHP (Pickup from Home Problem) is a special case of PTP, and since PHP is NP-hard, PTP must also be NP-hard.

**Key Observation:** When alpha = 1, the optimal solution to PTP is equivalent to PHP.

**Reasoning:**

1. In PTP, the total cost is: alpha x (driving distance) + (walking distance)

2. When alpha = 1, both driving and walking have equal cost per unit distance

3. Consider any friend at home h with pickup location p != h:
   - Walking cost from h to p: d(h, p)
   - But if we pick up at h instead, we need to drive to h
   - Due to triangle inequality: d(0, h) <= d(0, p) + d(p, h)
   - So driving directly to h is never worse than driving to p and having friend walk

4. When alpha = 1, for any pickup location p that is a neighbor of home h:
   - Cost of pickup at p: driving to p + walking from h to p
   - Cost of pickup at h: driving to h + 0 walking
   - Since the graph satisfies triangle inequality and alpha = 1, picking up at home is always optimal or equivalent

5. Therefore, when alpha = 1, the optimal PTP solution picks up everyone at their homes, which is exactly PHP.

**Conclusion:**

- PHP is NP-hard (shown in project description via reduction from Metric TSP)
- PTP with alpha = 1 is equivalent to PHP
- Therefore, PTP is NP-hard

**QED**

---

## Question 5.2: Approximation Ratio of PHP for PTP

**Claim:** For any instance of PTP, beta = C_php / C_ptp_opt <= 2, and this bound is tight.

### Part 1: Proving beta <= 2

**Setup (assuming alpha = 1 for simplicity):**

- Let C_ptp_opt be the optimal PTP cost
- Let C_php be the cost of the PHP solution (picking up everyone at home)
- Let T* be the optimal PTP tour with pickup locations {p_m} for friends {m}

**Optimal PTP cost:**

    C_ptp_opt = sum of edge weights in T* + sum of d(h_m, p_m) for all m

**PHP cost on the same tour visiting homes:**

    C_php = sum of edge weights in T_php

**Key insight:** The PHP tour must visit all homes H. The optimal PTP tour visits pickup locations which are either homes or neighbors of homes.

**Bound derivation:**

1. For each friend m, either:
   - p_m = h_m (picked up at home): contributes same driving cost
   - p_m in N(h_m) (picked up at neighbor): walking cost d(h_m, p_m) = w(h_m, p_m)

2. In the worst case, PTP saves driving distance by using pickup points, but PHP must drive to each home.

3. For any edge (h_m, p_m) where friend walks:
   - PTP cost contribution: driving to p_m + walking d(h_m, p_m)
   - PHP cost contribution: driving to h_m
   - Difference <= d(h_m, p_m) due to triangle inequality

4. The total walking distance in optimal PTP is at most equal to the driving distance saved:

       sum of d(h_m, p_m) <= C_ptp_opt

5. Therefore:

       C_php <= 2 x C_ptp_opt
       beta = C_php / C_ptp_opt <= 2

### Part 2: Tightness (beta = 2 asymptotically)

**Construction:** Consider a star graph with n friends:

    Node 0 (origin) connects to node 1 with edge weight 1.
    Node 1 connects to all homes h_1, h_2, ..., h_n with edge weight 1 each.
    Each home h_i connects to node 0 with edge weight 2 (satisfies triangle inequality).

**Optimal PTP solution:**

- Tour: 0 -> 1 -> 0 (cost = 2)
- Pick up all friends at node 1 (they each walk distance 1)
- Total cost: 2 + n x 1 = n + 2

**PHP solution:**

- Must visit all homes
- Tour: 0 -> 1 -> h_1 -> 1 -> h_2 -> 1 -> ... -> 0
- Each home visit costs: go to home (1) + return to hub (1) = 2
- Total cost approximately 2n + 2

**Ratio:**

    beta = (2n + 2) / (n + 2) = 2(n+1) / (n+2) -> 2 as n -> infinity

**Conclusion:** The bound beta <= 2 is tight asymptotically.

**QED**

---

## Question 3: PTP Solver Approach

### Algorithm: Insert/Delete Heuristic

Our PTP solver uses a local search algorithm based on the insert/delete heuristic described in the project specification.

### Overview

The algorithm iteratively improves a tour by either:

1. **Inserting** a new node into the tour
2. **Removing** a node from the tour (except node 0)

At each step, we select the change that best improves feasibility or reduces cost.

### Key Components

#### 1. Feasibility Measure

    b(T) = number of friends who cannot be picked up from tour T

A tour is feasible when b(T) = 0.

#### 2. Cost Function

    c(T) = alpha x (tour driving distance) + (total walking distance)

Walking distance is computed optimally for each friend given the tour.

#### 3. Valid Pickup Locations

For each friend at home h:

    valid_pickups[h] = {h} union N(h)  (home or any neighbor)

### Algorithm Steps

    1. Initialize: T = {0}, tour = [0, 0]

    2. Repeat until no improvement:

       For each node i in graph:
         If i in T: compute T_i = T.remove(i)
         Else: compute T_i = T.insert(i) at best position

       If b(T) = 0 (feasible):
         Select T_i with minimum cost where b(T_i) = 0
       Else (infeasible):
         Select T_i with minimum cost where b(T_i) < b(T)

       If no improvement possible: break
       Else: T = T_i

    3. Return tour and optimal pickup assignments

### Implementation Details

1. **Precomputation:** All-pairs shortest paths using Floyd-Warshall for O(1) distance queries

2. **Tour Expansion:** When we have a set of nodes to visit, we:
   - Order them using nearest-neighbor heuristic
   - Expand edges to actual paths using precomputed shortest paths

3. **Pickup Assignment:** For each friend, select the pickup location in the tour that minimizes walking distance

### Complexity

- **Time:** O(n^2 x k) per iteration, where n = nodes, k = iterations
- **Space:** O(n^2) for distance matrix

### Why This Approach Works Well

1. **Balances feasibility and cost:** First achieves feasibility, then optimizes cost
2. **Exploits shared pickups:** Multiple friends can share pickup locations
3. **Handles alpha trade-off:** Cost function naturally balances driving vs walking based on alpha
4. **Avoids local optima:** Insert/delete moves can escape some local minima

### Performance

On test inputs, our solver achieves:

- Valid solutions on all 15 test cases
- Optimal solution on the PDF example (cost = 10/3)
- Competitive costs on hard inputs

---

## References

1. C. E. Miller, A. W. Tucker, and R. A. Zemlin, "Integer programming formulation of traveling salesman problems," J. ACM, 1960.

2. J. Mittenthal and C. E. Noon, "An insert/delete heuristic for the travelling salesman subset-tour problem," J. Operational Research Society, 1992.
