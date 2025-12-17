import random
import math
import os

def generate_metric_graph(num_nodes, seed=None):
    """
    Generate a connected metric graph using Euclidean distances.
    Places nodes on a 2D grid and uses Euclidean distances as edge weights.
    """
    if seed is not None:
        random.seed(seed)

    # Place nodes randomly on a grid
    coords = []
    for _ in range(num_nodes):
        x = random.randint(1, 1000)
        y = random.randint(1, 1000)
        coords.append((x, y))

    # Compute all distances (Euclidean - ensures triangle inequality)
    distances = [[0] * num_nodes for _ in range(num_nodes)]
    for i in range(num_nodes):
        for j in range(num_nodes):
            if i != j:
                dx = coords[i][0] - coords[j][0]
                dy = coords[i][1] - coords[j][1]
                dist = int(math.sqrt(dx * dx + dy * dy)) + 1  # +1 to avoid zero distances
                distances[i][j] = dist

    return distances, coords


def select_edges_for_connected_graph(num_nodes, distances):
    """
    Select edges to form a connected graph.
    We'll use a spanning tree + some additional edges to make it interesting.
    """
    edges = set()

    # First, create a spanning tree using nearest neighbor starting from node 0
    in_tree = {0}
    while len(in_tree) < num_nodes:
        best_edge = None
        best_dist = float('inf')
        for u in in_tree:
            for v in range(num_nodes):
                if v not in in_tree:
                    if distances[u][v] < best_dist:
                        best_dist = distances[u][v]
                        best_edge = (u, v)
        if best_edge:
            edges.add((min(best_edge), max(best_edge)))
            in_tree.add(best_edge[1])

    # Add some random additional edges to make the graph more interesting
    # (but not too many to keep it sparse)
    num_extra_edges = min(num_nodes, num_nodes * 2)
    attempts = 0
    while len(edges) < num_nodes - 1 + num_extra_edges and attempts < num_nodes * num_nodes:
        u = random.randint(0, num_nodes - 1)
        v = random.randint(0, num_nodes - 1)
        if u != v:
            edge = (min(u, v), max(u, v))
            edges.add(edge)
        attempts += 1

    return edges


def generate_input_file(filename, alpha, num_nodes, num_friends, seed=None):
    """Generate an input file for the PTP problem."""
    distances, coords = generate_metric_graph(num_nodes, seed)

    # Select edges for connected graph
    edges = select_edges_for_connected_graph(num_nodes, distances)

    # Select home nodes (excluding node 0)
    available_nodes = list(range(1, num_nodes))
    random.shuffle(available_nodes)
    home_nodes = sorted(available_nodes[:num_friends])

    # Build adjacency list
    adj_list = {i: [] for i in range(num_nodes)}
    for u, v in edges:
        adj_list[u].append((v, distances[u][v]))
        adj_list[v].append((u, distances[u][v]))

    # Write to file
    lines = []
    lines.append(f"{alpha:.5f}")
    lines.append(f"{num_nodes} {num_friends}")
    lines.append(" ".join(map(str, home_nodes)))

    for node in range(num_nodes):
        neighbors = adj_list[node]
        lines.append(f"{node} {len(neighbors)}")
        for neighbor, weight in neighbors:
            lines.append(f"{neighbor} {weight}")

    with open(filename, 'w') as f:
        f.write("\n".join(lines))

    print(f"Generated {filename}: {num_nodes} nodes, {num_friends} friends, alpha={alpha}")


if __name__ == "__main__":
    # Create inputs directory if it doesn't exist
    os.makedirs("inputs", exist_ok=True)

    # Generate 4 input files
    generate_input_file("inputs/20_03.in", 0.3, 20, 10, seed=42)
    generate_input_file("inputs/20_10.in", 1.0, 20, 10, seed=43)
    generate_input_file("inputs/40_03.in", 0.3, 40, 20, seed=44)
    generate_input_file("inputs/40_10.in", 1.0, 40, 20, seed=45)

    print("\nAll input files generated successfully!")
