import random
import math
import os

def euclidean_dist(p1, p2):
    """Calculate Euclidean distance between two points."""
    return int(math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)) + 1


def generate_hard_input(filename, alpha, num_nodes, num_friends, seed, layout_type):
    """
    Generate a hard input with metric (triangle inequality satisfying) distances.
    Uses coordinate-based distances to ensure triangle inequality.
    """
    random.seed(seed)

    # Generate node coordinates based on layout type
    coords = {}

    if layout_type == "star_clusters":
        # Node 0 at center, clusters of homes far from center
        # Optimal: use shared pickup points, not visit each home
        coords[0] = (500, 500)

        # Create 5 clusters around the perimeter
        cluster_centers = [
            (100, 100), (900, 100), (900, 900), (100, 900), (500, 50)
        ]

        # Place homes in clusters (hard to reach individually)
        homes = []
        home_idx = 1
        for ci, center in enumerate(cluster_centers):
            for j in range(num_friends // 5 + (1 if ci < num_friends % 5 else 0)):
                if home_idx <= num_friends:
                    # Homes clustered tightly
                    x = center[0] + random.randint(-30, 30)
                    y = center[1] + random.randint(-30, 30)
                    coords[home_idx] = (x, y)
                    homes.append(home_idx)
                    home_idx += 1

        # Add connector nodes between clusters and center (the "good" paths)
        connector_idx = num_friends + 1
        for ci, center in enumerate(cluster_centers):
            if connector_idx < num_nodes:
                # Connector halfway between center and cluster
                x = (500 + center[0]) // 2 + random.randint(-20, 20)
                y = (500 + center[1]) // 2 + random.randint(-20, 20)
                coords[connector_idx] = (x, y)
                connector_idx += 1

        # Fill remaining nodes scattered (some useful, some not)
        while connector_idx < num_nodes:
            coords[connector_idx] = (random.randint(50, 950), random.randint(50, 950))
            connector_idx += 1

    elif layout_type == "deep_tree":
        # Tree structure where homes are at leaves
        # Greedy goes deep; optimal picks up at intermediate nodes
        coords[0] = (500, 950)  # Root at bottom

        # Level 1: 4 nodes spreading out
        level1 = []
        for i, x in enumerate([200, 400, 600, 800]):
            node_id = num_friends + 1 + i
            if node_id < num_nodes:
                coords[node_id] = (x, 700)
                level1.append(node_id)

        # Level 2: branch further
        level2 = []
        for i, l1 in enumerate(level1):
            for dx in [-80, 80]:
                node_id = num_friends + 5 + len(level2)
                if node_id < num_nodes:
                    coords[node_id] = (coords[l1][0] + dx, 450)
                    level2.append(node_id)

        # Homes at the top (leaves), clustered near level2 nodes
        homes = []
        for i in range(1, num_friends + 1):
            parent = level2[i % len(level2)] if level2 else level1[i % len(level1)]
            px, py = coords[parent]
            coords[i] = (px + random.randint(-40, 40), py - 150 + random.randint(-30, 30))
            homes.append(i)

        # Fill remaining nodes
        next_id = max(coords.keys()) + 1
        while next_id < num_nodes:
            coords[next_id] = (random.randint(100, 900), random.randint(100, 900))
            next_id += 1

    elif layout_type == "grid_trap":
        # Grid layout with homes at intersections
        # Has many similar-cost paths, traps greedy with local optima
        coords[0] = (50, 50)

        # Create grid intersections
        grid_nodes = []
        node_id = num_friends + 1
        for row in range(4):
            for col in range(5):
                if node_id < num_nodes:
                    coords[node_id] = (150 + col * 180, 150 + row * 200)
                    grid_nodes.append(node_id)
                    node_id += 1

        # Place homes near grid intersections (multiple homes share intersections)
        homes = []
        for i in range(1, num_friends + 1):
            # Each home near a grid node
            grid_ref = grid_nodes[(i - 1) % len(grid_nodes)]
            gx, gy = coords[grid_ref]
            # Offset from grid node
            coords[i] = (gx + random.randint(-50, 50), gy + random.randint(-50, 50))
            homes.append(i)

        # Fill remaining nodes
        while node_id < num_nodes:
            coords[node_id] = (random.randint(100, 900), random.randint(100, 900))
            node_id += 1

    else:  # "cluster_chain"
        # Chain of clusters, each cluster has shared pickup point
        coords[0] = (50, 500)

        num_clusters = 5
        homes_per_cluster = num_friends // num_clusters

        homes = []
        home_idx = 1

        # Create clusters in a chain
        for ci in range(num_clusters):
            cluster_x = 150 + ci * 170
            cluster_y = 500 + (ci % 2) * 100 - 50  # Zigzag

            # Hub node for cluster
            hub_id = num_friends + 1 + ci
            if hub_id < num_nodes:
                coords[hub_id] = (cluster_x, cluster_y)

            # Homes around hub
            for j in range(homes_per_cluster + (1 if ci < num_friends % num_clusters else 0)):
                if home_idx <= num_friends:
                    angle = 2 * math.pi * j / homes_per_cluster
                    hx = cluster_x + int(40 * math.cos(angle))
                    hy = cluster_y + int(40 * math.sin(angle))
                    coords[home_idx] = (hx, hy)
                    homes.append(home_idx)
                    home_idx += 1

        # Fill remaining nodes
        next_id = num_friends + num_clusters + 1
        while next_id < num_nodes:
            coords[next_id] = (random.randint(100, 900), random.randint(100, 900))
            next_id += 1

    # Ensure all nodes have coordinates
    for i in range(num_nodes):
        if i not in coords:
            coords[i] = (random.randint(100, 900), random.randint(100, 900))

    # Build complete graph with Euclidean distances (guarantees triangle inequality)
    # But only keep edges that form interesting structure (not all edges)
    edges = {}

    # Add all edges (complete graph ensures connectivity and triangle inequality)
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            dist = euclidean_dist(coords[i], coords[j])
            edges[(i, j)] = dist

    # Write file
    write_input_file(filename, alpha, num_nodes, homes, edges, coords)


def write_input_file(filename, alpha, num_nodes, homes, edges, coords):
    """Write the input file."""
    # Build adjacency
    adj = {i: [] for i in range(num_nodes)}
    for (u, v), w in edges.items():
        adj[u].append((v, w))
        adj[v].append((u, w))

    lines = []
    lines.append(f"{alpha:.5f}")
    lines.append(f"{num_nodes} {len(homes)}")
    lines.append(" ".join(map(str, sorted(homes))))

    for node in range(num_nodes):
        neighbors = sorted(adj[node], key=lambda x: x[0])
        lines.append(f"{node} {len(neighbors)}")
        for neighbor, weight in neighbors:
            lines.append(f"{neighbor} {weight}")

    with open(filename, 'w') as f:
        f.write("\n".join(lines))

    print(f"Generated {filename}: {num_nodes} nodes, {len(homes)} friends, alpha={alpha}")


if __name__ == "__main__":
    os.makedirs("inputs", exist_ok=True)

    print("Generating HARD inputs with metric distances...\n")

    # 20_03: α=0.3 - low driving cost, should use shared pickups
    generate_hard_input("inputs/20_03.in", 0.3, 20, 10, seed=142, layout_type="star_clusters")

    # 20_10: α=1.0 - equal costs, balance driving vs walking
    generate_hard_input("inputs/20_10.in", 1.0, 20, 10, seed=143, layout_type="cluster_chain")

    # 40_03: α=0.3 - deep tree, optimal picks at intermediate depth
    generate_hard_input("inputs/40_03.in", 0.3, 40, 20, seed=144, layout_type="deep_tree")

    # 40_10: α=1.0 - grid with many similar paths
    generate_hard_input("inputs/40_10.in", 1.0, 40, 20, seed=145, layout_type="grid_trap")

    print("\nHard inputs generated!")
    print("\nStrategies to challenge other solvers:")
    print("- Clustered homes with shared optimal pickup points")
    print("- Deep structures where intermediate pickups are optimal")
    print("- Grid layouts with many local optima")
    print("- α values that make trade-offs tricky")
