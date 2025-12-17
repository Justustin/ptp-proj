import networkx as nx

def mtsp_dp(G):
    """
    Solve the Traveling Salesman Problem (TSP) using dynamic programming.

    Parameters:
        G (nx.Graph): A NetworkX graph representing the city.

    Returns:
        list: A list of nodes representing the computed tour.

    Notes:
        - All nodes are represented as integers.
        - The solution must use dynamic programming.
        - The tour must begin and end at node 0.
        - The tour can only traverse existing edges in the graph.
        - The tour must visit every node in G exactly once.
    """
    nodes = list(G.nodes())
    n = len(nodes)

    if n == 0:
        return [0]
    if n == 1:
        return [0, 0]

    # Create node index mapping
    node_to_idx = {node: i for i, node in enumerate(nodes)}
    idx_to_node = {i: node for i, node in enumerate(nodes)}

    # Compute all-pairs shortest paths for distances
    dist = dict(nx.floyd_warshall(G))

    # Create distance matrix
    INF = float('inf')
    d = [[INF] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                d[i][j] = 0
            else:
                d[i][j] = dist[idx_to_node[i]][idx_to_node[j]]

    # Held-Karp algorithm
    # dp[mask][i] = minimum cost to visit all nodes in mask starting from node 0 and ending at node i
    # mask is a bitmask representing visited nodes

    dp = [[INF] * n for _ in range(1 << n)]
    parent = [[-1] * n for _ in range(1 << n)]

    # Start at node 0
    start_idx = node_to_idx[0]
    dp[1 << start_idx][start_idx] = 0

    # Fill DP table
    for mask in range(1 << n):
        # Skip if node 0 not in mask
        if not (mask & (1 << start_idx)):
            continue

        for last in range(n):
            if not (mask & (1 << last)):
                continue
            if dp[mask][last] == INF:
                continue

            # Try extending to next node
            for next_node in range(n):
                if mask & (1 << next_node):
                    continue

                new_mask = mask | (1 << next_node)
                new_cost = dp[mask][last] + d[last][next_node]

                if new_cost < dp[new_mask][next_node]:
                    dp[new_mask][next_node] = new_cost
                    parent[new_mask][next_node] = last

    # Find minimum cost tour (return to node 0)
    full_mask = (1 << n) - 1
    min_cost = INF
    last_node = -1

    for i in range(n):
        if i == start_idx:
            continue
        total_cost = dp[full_mask][i] + d[i][start_idx]
        if total_cost < min_cost:
            min_cost = total_cost
            last_node = i

    # Reconstruct the tour
    tour_indices = []
    mask = full_mask
    current = last_node

    while current != -1:
        tour_indices.append(current)
        prev = parent[mask][current]
        mask ^= (1 << current)
        current = prev

    # Reverse to get correct order (from node 0)
    tour_indices = tour_indices[::-1]

    # Convert indices back to node labels and add return to start
    tour = [idx_to_node[i] for i in tour_indices]
    tour.append(0)  # Return to start

    return tour
