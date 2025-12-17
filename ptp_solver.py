import networkx as nx
from student_utils import *

def ptp_solver(G: nx.DiGraph, H: list, alpha: float):
    """
    PTP solver using insert/delete heuristic algorithm.

    Parameters:
        G (nx.DiGraph): A NetworkX graph representing the city.
            This directed graph is equivalent to an undirected one by construction.
        H (list): A list of home nodes.
        alpha (float): The coefficient for calculating cost.

    Returns:
        tuple: A tuple containing:
            - tour (list): A list of nodes traversed by your car.
            - pick_up_locs_dict (dict): A dictionary where:
                - Keys are pick-up locations.
                - Values are lists or tuples containing friends who get picked up
                  at that specific pick-up location. Friends are represented by
                  their home nodes.

    Notes:
    - All nodes are represented as integers.
    - The tour must begin and end at node 0.
    - The tour can only go through existing edges in the graph.
    - Pick-up locations must be part of the tour.
    - Each friend should be picked up exactly once.
    - The pick-up locations must be neighbors of the friends' home nodes or their homes.
    """
    # Precompute all-pairs shortest paths
    all_sp = dict(nx.all_pairs_dijkstra(G))
    # all_sp[u] = (distances_from_u, paths_from_u)

    dist = {}
    paths = {}
    for u in G.nodes():
        dist[u] = all_sp[u][0]
        paths[u] = all_sp[u][1]

    n = G.number_of_nodes()
    nodes = list(G.nodes())

    # For each home, get valid pickup locations (home or neighbors)
    valid_pickups = {}
    for h in H:
        valid_pickups[h] = set([h])
        for neighbor in G.neighbors(h):
            valid_pickups[h].add(neighbor)
        # Also check predecessors for directed graph
        for neighbor in G.predecessors(h):
            valid_pickups[h].add(neighbor)

    def get_infeasibility(tour_nodes):
        """Count friends that cannot be picked up from current tour."""
        tour_set = set(tour_nodes)
        infeasible = 0
        for h in H:
            # Check if any valid pickup location is in tour
            if not (valid_pickups[h] & tour_set):
                infeasible += 1
        return infeasible

    def get_best_pickup_locations(tour_nodes):
        """For each friend, find the best pickup location from the tour."""
        tour_set = set(tour_nodes)
        pickup_dict = {}
        total_walking = 0

        for h in H:
            best_loc = None
            best_dist = float('inf')
            # Check all valid pickup locations in the tour
            for loc in valid_pickups[h] & tour_set:
                d = dist[h][loc]
                if d < best_dist:
                    best_dist = d
                    best_loc = loc

            if best_loc is not None:
                if best_loc not in pickup_dict:
                    pickup_dict[best_loc] = []
                pickup_dict[best_loc].append(h)
                total_walking += best_dist

        return pickup_dict, total_walking

    def compute_tour_length(tour):
        """Compute the total length of the tour."""
        if len(tour) <= 1:
            return 0
        length = 0
        for i in range(len(tour) - 1):
            length += dist[tour[i]][tour[i + 1]]
        return length

    def compute_cost(tour):
        """Compute total cost = alpha * driving_cost + walking_cost."""
        tour_nodes = set(tour)
        _, walking_cost = get_best_pickup_locations(tour_nodes)
        driving_cost = compute_tour_length(tour)
        return alpha * driving_cost + walking_cost

    def expand_tour(tour_nodes):
        """Expand tour_nodes into actual path using shortest paths."""
        tour_nodes_list = list(tour_nodes)
        if len(tour_nodes_list) == 0:
            return [0, 0]
        if len(tour_nodes_list) == 1:
            return [0, 0]

        if 0 not in tour_nodes:
            tour_nodes_list = [0] + tour_nodes_list
        else:
            tour_nodes_list.remove(0)
            tour_nodes_list = [0] + tour_nodes_list

        if len(tour_nodes_list) == 1:
            return [0, 0]

        # Simple nearest neighbor ordering for the nodes
        unvisited = set(tour_nodes_list[1:])
        ordered = [0]
        current = 0

        while unvisited:
            nearest = min(unvisited, key=lambda x: dist[current][x])
            ordered.append(nearest)
            unvisited.remove(nearest)
            current = nearest

        ordered.append(0)

        # Expand to actual path using shortest paths
        expanded = [ordered[0]]
        for i in range(len(ordered) - 1):
            u, v = ordered[i], ordered[i + 1]
            path = paths[u][v]
            # Add all nodes in path except the first one (already in expanded)
            expanded.extend(path[1:])

        return expanded

    def try_insert(tour_set, node):
        """Try inserting a node into the tour and return the cost."""
        new_set = tour_set | {node}
        expanded = expand_tour(new_set)
        return compute_cost(expanded), new_set, expanded

    def try_remove(tour_set, node):
        """Try removing a node from the tour and return the cost."""
        if node == 0:
            return float('inf'), tour_set, None
        new_set = tour_set - {node}
        if len(new_set) <= 1:
            expanded = [0, 0]
        else:
            expanded = expand_tour(new_set)
        return compute_cost(expanded), new_set, expanded

    # Initialize tour with just node 0
    current_tour_set = {0}
    current_tour = [0, 0]
    current_cost = compute_cost(current_tour)
    current_b = get_infeasibility(current_tour_set)

    max_iterations = n * n  # Safety limit

    for iteration in range(max_iterations):
        best_new_set = None
        best_new_tour = None
        best_new_cost = float('inf')
        best_new_b = float('inf')

        # Try all one-node changes
        for node in nodes:
            if node in current_tour_set:
                # Try removing
                cost, new_set, new_tour = try_remove(current_tour_set, node)
            else:
                # Try inserting
                cost, new_set, new_tour = try_insert(current_tour_set, node)

            if new_tour is None:
                continue

            new_b = get_infeasibility(new_set)

            if current_b == 0:
                # Current is feasible, select minimum cost feasible tour
                if new_b == 0 and cost < best_new_cost:
                    best_new_cost = cost
                    best_new_set = new_set
                    best_new_tour = new_tour
                    best_new_b = new_b
            else:
                # Current is infeasible, select tour that improves feasibility
                if new_b < current_b:
                    if new_b < best_new_b or (new_b == best_new_b and cost < best_new_cost):
                        best_new_cost = cost
                        best_new_set = new_set
                        best_new_tour = new_tour
                        best_new_b = new_b

        # Check termination
        if current_b == 0:
            # Stop if no feasible improvement
            if best_new_tour is None or best_new_cost >= current_cost:
                break
        else:
            # Stop if no feasibility improvement
            if best_new_tour is None:
                break

        # Apply the best change
        current_tour_set = best_new_set
        current_tour = best_new_tour
        current_cost = best_new_cost
        current_b = best_new_b

    # If still infeasible, greedily add required nodes
    while current_b > 0:
        best_node = None
        best_cost = float('inf')
        best_new_set = None
        best_new_tour = None

        for h in H:
            tour_set = set(current_tour)
            if valid_pickups[h] & tour_set:
                continue  # Already can pick up this friend

            # Add the home node or a neighbor
            for loc in valid_pickups[h]:
                if loc in current_tour_set:
                    continue
                cost, new_set, new_tour = try_insert(current_tour_set, loc)
                if cost < best_cost:
                    best_cost = cost
                    best_node = loc
                    best_new_set = new_set
                    best_new_tour = new_tour

        if best_node is not None:
            current_tour_set = best_new_set
            current_tour = best_new_tour
            current_cost = best_cost
            current_b = get_infeasibility(current_tour_set)
        else:
            break

    # Get final pickup locations
    pick_up_locs_dict, _ = get_best_pickup_locations(set(current_tour))

    return current_tour, pick_up_locs_dict


if __name__ == "__main__":
    pass
