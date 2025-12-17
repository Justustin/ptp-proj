import networkx as nx
from mtsp_dp import mtsp_dp
from student_utils import *

def php_solver_from_tsp(G, H):
    """
    PHP solver via reduction to Euclidean TSP.

    Parameters:
        G (nx.Graph): A NetworkX graph representing the city.
            This directed graph is equivalent to an undirected one by construction.
        H (list): A list of home nodes that must be visited.

    Returns:
        list: A list of nodes traversed by your car (the computed tour).

    Notes:
        - All nodes are represented as integers.
        - Solve the problem by first transforming the PTHP problem to a TSP problem.
        - Use the dynamic programming algorithm introduced in lectures to solve TSP.
        - Construct a solution for the original PTHP problem after solving TSP.

    Constraints:
        - The tour must begin and end at node 0.
        - The tour can only traverse existing edges in the graph.
        - The tour must visit every node in H.
    """
    # Step 1: Compute all-pairs shortest paths in G
    all_shortest_paths = dict(nx.all_pairs_dijkstra(G))
    # all_shortest_paths[u] = (distances_from_u, paths_from_u)

    # Step 2: Construct the reduced complete graph G'
    # V' = H ∪ {0}
    nodes_prime = [0] + [h for h in H if h != 0]
    nodes_prime = list(set(nodes_prime))  # Ensure unique nodes

    reduced_graph = nx.DiGraph()
    reduced_graph.add_nodes_from(nodes_prime)

    # Add edges with weights = shortest path distances
    for u in nodes_prime:
        for v in nodes_prime:
            if u != v:
                dist = all_shortest_paths[u][0][v]
                reduced_graph.add_edge(u, v, weight=dist)

    # Step 3: Solve M-TSP on the reduced graph
    tsp_tour = mtsp_dp(reduced_graph)

    # Step 4: Reconstruct the tour in original graph by substituting edges with shortest paths
    tour = [tsp_tour[0]]
    for i in range(len(tsp_tour) - 1):
        u, v = tsp_tour[i], tsp_tour[i + 1]
        # Get the shortest path from u to v in original graph
        path = all_shortest_paths[u][1][v]
        # Add all nodes in path except the first one (already in tour)
        tour.extend(path[1:])

    return tour


if __name__ == "__main__":
    pass
