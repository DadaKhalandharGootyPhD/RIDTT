import networkx as nx
import matplotlib.pyplot as plt
import random

# ---------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------

NUM_NODES = 14
RANDOM_SEED = 42

random.seed(RANDOM_SEED)

# ---------------------------------------------------
# CREATE TREE 1
# ---------------------------------------------------

# Balanced binary tree
T1 = nx.balanced_tree(r=2, h=3)

nodes_to_keep = list(range(NUM_NODES))
T1 = T1.subgraph(nodes_to_keep).copy()

# ---------------------------------------------------
# CREATE TREE 2
# ---------------------------------------------------

# Create another binary tree with shuffled labels
T2_base = nx.balanced_tree(r=2, h=3)
T2_base = T2_base.subgraph(nodes_to_keep).copy()

shuffled_nodes = nodes_to_keep.copy()
random.shuffle(shuffled_nodes)

mapping = {
    old: shuffled_nodes[i]
    for i, old in enumerate(nodes_to_keep)
}

T2 = nx.relabel_nodes(T2_base, mapping)

# ---------------------------------------------------
# CREATE COMBINED GRAPH
# ---------------------------------------------------

G = nx.Graph()

# Add layered nodes
for node in nodes_to_keep:
    G.add_node(f"T1_{node}", layer="T1")
    G.add_node(f"T2_{node}", layer="T2")

# ---------------------------------------------------
# ADD TREE 1 EDGES
# ---------------------------------------------------

for u, v in T1.edges():
    G.add_edge(
        f"T1_{u}",
        f"T1_{v}",
        edge_type="tree1"
    )

# ---------------------------------------------------
# ADD TREE 2 EDGES
# ---------------------------------------------------

for u, v in T2.edges():
    G.add_edge(
        f"T2_{u}",
        f"T2_{v}",
        edge_type="tree2"
    )

# ---------------------------------------------------
# ADD IDENTITY EDGES
# ---------------------------------------------------

for node in nodes_to_keep:
    G.add_edge(
        f"T1_{node}",
        f"T2_{node}",
        edge_type="identity"
    )

# ---------------------------------------------------
# BASIC ANALYSIS
# ---------------------------------------------------

print("===================================")
print("RIDTT GRAPH ANALYSIS")
print("===================================")

print(f"Total Nodes: {G.number_of_nodes()}")
print(f"Total Edges: {G.number_of_edges()}")

print(f"Connected: {nx.is_connected(G)}")
print(f"Node Connectivity: {nx.node_connectivity(G)}")
print(f"Edge Connectivity: {nx.edge_connectivity(G)}")

# ---------------------------------------------------
# FAILURE SIMULATION
# ---------------------------------------------------

failed_node = random.choice(nodes_to_keep)

print("\n===================================")
print(f"Simulating Failure of Logical Node {failed_node}")
print("===================================")

G_failed = G.copy()

G_failed.remove_node(f"T1_{failed_node}")
G_failed.remove_node(f"T2_{failed_node}")

print(f"Connected After Failure: {nx.is_connected(G_failed)}")

components = list(nx.connected_components(G_failed))

print(f"Connected Components: {len(components)}")

largest_component = max(components, key=len)

print(f"Largest Component Size: {len(largest_component)}")

# ---------------------------------------------------
# HIERARCHICAL POSITION FUNCTION
# ---------------------------------------------------

def hierarchy_pos(G, root, width=1.0, vert_gap=0.2,
                  vert_loc=0, xcenter=0.5, pos=None,
                  parent=None):

    if pos is None:
        pos = {}

    pos[root] = (xcenter, vert_loc)

    children = list(G.neighbors(root))

    if parent is not None and parent in children:
        children.remove(parent)

    if len(children) != 0:
        dx = width / len(children)
        nextx = xcenter - width / 2 - dx / 2

        for child in children:
            nextx += dx

            pos = hierarchy_pos(
                G,
                child,
                width=dx,
                vert_gap=vert_gap,
                vert_loc=vert_loc - vert_gap,
                xcenter=nextx,
                pos=pos,
                parent=root
            )

    return pos

# ---------------------------------------------------
# CREATE POSITIONS
# ---------------------------------------------------

# Position Tree 1
pos1 = hierarchy_pos(T1, root=0)

# Shift Tree 1 left
for node in pos1:
    x, y = pos1[node]
    pos1[node] = (x * 8 - 6, y * 8)

# Position Tree 2
# Find root of T2
root_t2 = shuffled_nodes[0]

pos2 = hierarchy_pos(T2, root=root_t2)

# Shift Tree 2 right
for node in pos2:
    x, y = pos2[node]
    pos2[node] = (x * 8 + 6, y * 8)

# Combine positions
pos = {}

for node in T1.nodes():
    pos[f"T1_{node}"] = pos1[node]

for node in T2.nodes():
    pos[f"T2_{node}"] = pos2[node]

# ---------------------------------------------------
# EDGE GROUPS
# ---------------------------------------------------

tree1_edges = [
    (u, v)
    for u, v, d in G.edges(data=True)
    if d["edge_type"] == "tree1"
]

tree2_edges = [
    (u, v)
    for u, v, d in G.edges(data=True)
    if d["edge_type"] == "tree2"
]

identity_edges = [
    (u, v)
    for u, v, d in G.edges(data=True)
    if d["edge_type"] == "identity"
]

# ---------------------------------------------------
# DRAW GRAPH
# ---------------------------------------------------

plt.figure(figsize=(16, 10))

# Draw nodes
nx.draw_networkx_nodes(
    G,
    pos,
    node_size=700
)

# Draw labels
nx.draw_networkx_labels(
    G,
    pos,
    font_size=8,
    font_color="white"
)

# Draw Tree 1 edges (solid strong)
nx.draw_networkx_edges(
    G,
    pos,
    edgelist=tree1_edges,
    width=3
)

# Draw Tree 2 edges (solid strong)
nx.draw_networkx_edges(
    G,
    pos,
    edgelist=tree2_edges,
    width=3
)

# Draw identity edges (dotted/dashed)
nx.draw_networkx_edges(
    G,
    pos,
    edgelist=identity_edges,
    style="dashed",
    width=1.5,
    alpha=0.7
)

# ---------------------------------------------------
# FINALIZE
# ---------------------------------------------------

plt.title(
    "RIDTT Layered Dual Binary Tree Topology",
    fontsize=16
)

plt.axis("off")

plt.tight_layout()

plt.savefig("ridtt_topology.png", dpi=300)

plt.show()

print("\nTopology image saved as:")
print("ridtt_topology.png")
