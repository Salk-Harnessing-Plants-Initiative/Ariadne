"""Parse graphs in custom .xyz format, and measure traits.
Points are stored in a tree using an undirected NetworkX graph.
Each node has a unique numerical identifier (node_num), and an attribute "pos": an (x,y) coordinate pair corresponding to its position in 2D space.
Each edge has an attribute "length": the Euclidean distance between the nodes it connects.
TO-DO:
Trait measurement
Time series
"""

import matplotlib.pyplot as plt
import re
import numpy as np
import copy
import networkx as nx
import math
import logging

from queue import Queue
from scipy.spatial import ConvexHull  # Import ConvexHull class

from ariadne_roots.pareto_functions import (
    pareto_front,
    random_tree,
    pareto_front_3d_path_tortuosity,
    random_tree_3d_path_tortuosity,
    get_critical_nodes,
)


# parser = argparse.ArgumentParser(description='select file')
# parser.add_argument('-i', '--input', help='Full path to input file', required=True)
# args = parser.parse_args()

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


def distance(p1, p2):
    """Compute 2D Euclidian distance between two (x,y) points."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def make_graph(target):
    """Construct graph from file and check for errors."""
    G = nx.Graph()
    with open(target, "r") as f:  # parse input file
        q = Queue()
        node_num = 1  # label nodes with unique identifiers
        for line in f:
            if line.startswith("##"):  # Level heading
                group_num = 0  # count nodes per level, and reset on level change, to match hierarchy info from tuples
                level = int(line.rstrip().split(": ")[1])
                continue
            else:
                info = line.rstrip().split("; ")

                coords = tuple(int(float(i)) for i in info[0].split())[
                    0:2
                ]  # change output coords from floats to ints
                metadata = re.findall(
                    r"\(.+?\)|\[.+?\]", info[1]
                )  # find chunks in brackets or parenthesis

                root_metadata = metadata[-1]  # eg (PR, None)
                child_metadata = []  # eg ['[1,0]']

                for el in metadata:
                    if el != root_metadata:
                        child_metadata.append(el)

                if not child_metadata:  # terminal node, no children
                    G.add_node(node_num, pos=coords)
                    parent_node = q.get()

                    parent_level = parent_node[1][0]
                    parent_group = parent_node[1][1]

                    if level == parent_level and group_num == parent_group:
                        G.add_edge(
                            node_num,
                            parent_node[0],
                            length=distance(
                                G.nodes[node_num]["pos"], G.nodes[parent_node[0]]["pos"]
                            ),
                        )
                    else:
                        print("ERROR: edge assignment failed (terminal node)")

                else:
                    G.add_node(node_num, pos=coords)

                    if not q.empty():
                        parent_node = q.get()

                        parent_level = parent_node[1][0]
                        parent_group = parent_node[1][1]

                        if level == parent_level and group_num == parent_group:
                            G.add_edge(
                                node_num,
                                parent_node[0],
                                length=distance(
                                    G.nodes[node_num]["pos"],
                                    G.nodes[parent_node[0]]["pos"],
                                ),
                            )
                        else:
                            print("Error: edge assignment failed")

                    for child_node in child_metadata:
                        q.put(
                            (
                                node_num,
                                list(map(int, child_node.strip("[]").split(","))),
                            )
                        )

                node_num += 1
                group_num += 1

    # return "Done!" (used for csv creation)
    return G


# G = make_graph('/Users/kianfaizi/projects/ariadne/color-final_plantA_day1.txt')


def make_graph_alt(target):
    """Construct a broken graph (without problematic edges)."""
    G = nx.Graph()
    with open(target, "r") as f:  # parse input file
        q = Queue()
        node_num = 1  # label nodes with unique identifiers
        for line in f:
            if line.startswith("##"):  # Level heading
                group_num = 0  # count nodes per level, and reset on level change, to match hierarchy info from tuples
                level = int(line.rstrip().split(": ")[1])
                continue
            else:
                info = line.rstrip().split("; ")
                if len(info) > 1:  # node has degree > 1
                    coords = tuple(int(float(i)) for i in info[0].split())[
                        0:2
                    ]  # change output coords from floats to ints
                    G.add_node(node_num, pos=coords)
                    if not q.empty():
                        parent_node = q.get()
                        # print(parent_node, level, group_num, info)
                        if (
                            level == parent_node[1][0]
                            and group_num == parent_node[1][1]
                        ):  # check that the expected and actual positions of the child match
                            G.add_edge(
                                node_num,
                                parent_node[0],
                                length=distance(
                                    G.nodes[node_num]["pos"],
                                    G.nodes[parent_node[0]]["pos"],
                                ),
                            )
                        else:
                            print(
                                f"Edge assignment failed: {parent_node}; {level}; {group_num}; {info}"
                            )
                    # place all descendants of the current node in the queue for processing in future rounds
                    children = info[1].split()
                    for child_node in children:
                        q.put(
                            (
                                node_num,
                                list(map(int, child_node.strip("[]").split(","))),
                            )
                        )  # converts each child object from list of strings to list of ints
                else:  # terminal node (degree == 1)
                    coords = tuple(int(float(i)) for i in info[0].rstrip(";").split())[
                        0:2
                    ]
                    G.add_node(node_num, pos=coords)
                    children = None
                    parent_node = q.get()
                    if level == parent_node[1][0] and group_num == parent_node[1][1]:
                        G.add_edge(
                            node_num,
                            parent_node[0],
                            length=distance(
                                G.nodes[node_num]["pos"], G.nodes[parent_node[0]]["pos"]
                            ),
                        )
                    else:
                        print("Edge assignment failed: terminal node.")
                node_num += 1
                group_num += 1
    return G


def plot_graph(
    G,
    node_size_factor=20,
    node_base_size=2,
    edge_width_factor=1.0,
    base_node_color="#2E8B57",
    secondary_node_color="#A0522D",
    edge_color="#3D2B1F",
    critical_node_color="#FF0000",
    with_labels=False,
    title="Root System Graph",
    figsize=(10, 15),
    show_grid=True,
    save_path=None,
):
    """Plots a root-system graph using node positions from their attributes, with axes and optional grid.

    Args:
        G (networkx.DiGraph): The graph to be plotted. Must have node positions stored 
            as attributes. Assumes the graph is directed.
        node_size_factor (float, optional): Multiplier for node sizes based on degree. 
            Defaults to 20.
        node_base_size (int, optional): Base size for all nodes. 
            Defaults to 2.
        edge_width_factor (float, optional): Multiplier for edge widths. 
            Defaults to 1.0.
        base_node_color (str, optional): Color for the base node (node 0). 
            Defaults to "#2E8B57".
        secondary_node_color (str, optional): Color for all other nodes. 
            Defaults to "#A0522D".
        edge_color (str, optional): Color of the edges. Defaults to 
            "#3D2B1F".
        critical_node_color (str, optional): Color for nodes with degree == 1 (critical nodes). 
            Defaults to "#FF0000".
        with_labels (bool, optional): Whether to display labels on nodes. 
            Defaults to False.
        title (str, optional): Title for the plot. Defaults to "Root System Graph".
        figsize (tuple, optional): Size of the plot figure (width, height). 
            Defaults to (10, 15).
        show_grid (bool, optional): Whether to display a grid. Defaults to True.
        save_path (str, optional): The file path to save the plot. Defaults to None.

    Raises:
        ValueError: If any node is missing a "pos" attribute.

    Returns:
        Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
            The matplotlib figure and axes objects for further customization.
    """
    # Extract positions from the nodes' "pos" attribute
    try:
        pos = nx.get_node_attributes(G, "pos")
        if len(pos) != len(G.nodes()):
            raise ValueError("Not all nodes have a 'pos' attribute.")
    except KeyError:
        raise ValueError("Nodes must have a 'pos' attribute for plotting.")

    # Define the base node explicitly as node 0
    base_node = 0
    if base_node not in G.nodes():
        raise ValueError("Node 0 (base node) is not present in the graph.")

    # Node sizes
    node_sizes = [
        node_base_size + G.degree(n) * node_size_factor for n in G.nodes()
    ]

    # Assign node colors based on conditions
    node_colors = []
    for n in G.nodes():
        if n == base_node:
            node_colors.append(base_node_color)  # Base node
        elif G.degree(n) == 1:
            node_colors.append(critical_node_color)  # critical nodes
        else:
            node_colors.append(secondary_node_color)  # Other nodes

    # Edge widths
    edge_widths = [
        edge_width_factor * G[u][v].get("weight", 1) for u, v in G.edges()
    ]

    # Create a matplotlib figure and axes
    fig, ax = plt.subplots(figsize=figsize)

    # Draw the graph on the given axes
    nx.draw(
        G,
        pos,
        ax,
        with_labels=with_labels,
        node_size=node_sizes,
        node_color=node_colors,
        edge_color=edge_color,
        width=edge_widths,
        arrows=True,  # Show direction since the graph is directed
    )

    # Invert the y-axis to match the coordinate system
    ax.invert_yaxis()

    # Add x and y axes to plot
    ax.set_axis_on()
    ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)

    # Set grid and axis labels
    if show_grid:
        ax.grid(color="lightgray", linestyle="--", linewidth=0.5)
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xlabel("X Position", fontsize=12)
    ax.set_ylabel("Y Position", fontsize=12)

    # Add title
    ax.set_title(title, fontsize=14)

    # Save the plot if a save path is provided
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=300, facecolor="w")
        print(f"Plot saved to {save_path}")

    return fig, ax



def save_plot(path, name, title):
    """Plot a Pareto front and save to .jpg."""

    G = make_graph(path)
    # check that graph is indeed a tree (acyclic, undirected, connected)
    assert nx.is_tree(G)

    edge_lengths, travel_distances_to_base, actual = pareto_front(G)
    randoms = random_tree(G)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title(title)
    ax.set_xlabel("Total length", fontsize=15)
    ax.set_ylabel("Travel distance", fontsize=15)

    plt.plot(
        edge_lengths,
        travel_distances_to_base,
        marker="s",
        linestyle="-",
        markeredgecolor="black",
    )
    plt.plot(actual[0], actual[1], marker="x", markersize=12)
    for i in randoms:
        plt.plot(i[0], i[1], marker="+", color="green", markersize=4)

    plt.show()


def calc_len_PR(G, root_node):
    """For a given graph and the uppermost node, calculate the PR length."""
    bfs_paths = dict(nx.bfs_successors(G, root_node))

    PRs = []  # list of PR nodes in order of increasing depth

    for node, children in bfs_paths.items():
        if G.nodes[node]["LR_index"] is None:
            PRs.append(node)
            for child_node in children:
                if G.nodes[child_node]["LR_index"] is None:
                    # catch the last node in the PR, which won't appear in the iterator since it has no children
                    final = child_node

    PRs.append(final)

    # calculate pairwise Euclidean distances and sum
    return calc_root_len(G, PRs)


def calc_root_len(G, nodes):
    """Return the pairwise Euclidean distance along a list of consecutive nodes."""
    dist = 0

    # order matters! assumes consecutive, increasing depth
    for prev, current_node in zip(nodes, nodes[1:]):
        segment = distance(G.nodes[prev]["pos"], G.nodes[current_node]["pos"])
        dist += segment
        # might as well annotate the edges while I'm here
        G.edges[prev, current_node]["weight"] = segment

    return dist


def calc_len_LRs(H):
    """Find the total length of each LR type in the graph."""
    # minimum length (px) for LR to be considered part of the network
    # based on root hair emergence times
    # threshold = 117
    threshold = 0

    # dict of node ids : LR index, for each LR node
    idxs = nx.get_node_attributes(H, "LR_index")
    idxs = {k: v for k, v in idxs.items() if v is not None}  # drop empty (PR) nodes

    num_LRs = max(idxs.values()) + 1

    results = {}

    for i in range(num_LRs):
        # gather nodes corresponding to the current LR index
        selected = []

        for node in H.nodes(data="LR_index"):
            if node[1] == i:
                selected.append(node[0])
                # make note of the root degree (should be the same for all nodes in loop)
                current_degree = H.nodes[node[0]]["root_deg"]

        # to find the shallowest node in LR, we iterate through them
        # until we find the one whose parent_node has a lesser root degree
        sub = H.subgraph(selected)
        for node in sub.nodes():
            parent_node = list(H.predecessors(node))
            # print(node, parent_node)
            assert len(parent_node) == 1  # should be a tree
            if H.nodes[parent_node[0]]["root_deg"] < current_degree:
                sub_top = node

        # now we can DFS to order all nodes by increasing depth
        ordered = list(nx.dfs_tree(sub, sub_top).nodes())

        # also include the parent_node of the shallowest node in the LR (the 'branch point')
        parent_node = list(H.predecessors(ordered[0]))
        assert len(parent_node) == 1

        nodes_list = parent_node + ordered

        length = calc_root_len(H, nodes_list)

        if length < threshold:
            H.remove_nodes_from(ordered)
        else:
            # now we can calculate the gravitropic set point angle
            # branch coordinates
            p2 = np.array(H.nodes[parent_node[0]]["pos"])
            # LR coordinates
            p3 = np.array(H.nodes[ordered[0]]["pos"])

            # recall: in our coordinate system, the top node is (0,0)
            # x increases to the right; y increases downwards
            # unit vector of gravity
            g = np.array([0, 1])
            # normalized vector of LR emergence
            lr = p3 - p2
            norm_lr = np.linalg.norm(lr)
            assert norm_lr > 0
            lr = lr / norm_lr

            # angle between LR emergence and the vector of gravity:
            # this will be symmetric, whichever side of the PR the LR is on
            theta = np.rad2deg(math.acos(np.dot(lr, g)))

            # print(f'The ordered list of nodes that make up LR #{i} is:', nodes_list)
            results[i] = [length, theta]

    assert nx.is_tree(H)
    return results
    # add LR_index awareness: all, 1 deg, 2 deg, n deg


def calc_density_LRs(G):
    pass
    # add up to _n_ degrees


def plot_all(front, actual, randoms, mrand, srand, dest):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # ax.set_title(title)
    ax.set_xlabel("Total length (px)", fontsize=15)
    ax.set_ylabel("Travel distance (px)", fontsize=15)

    plt.plot(
        [x[0] for x in front.values()],
        [x[1] for x in front.values()],
        marker="s",
        linestyle="-",
        markeredgecolor="black",
    )
    plt.plot(actual[0], actual[1], marker="x", markersize=12)
    for i in randoms:
        plt.plot(i[0], i[1], marker="+", color="green", markersize=4)

    plt.plot(mrand, srand, marker="+", color="red", markersize=12)

    plt.savefig(dest, bbox_inches="tight", dpi=300)
    print(f"Plot saved to {dest}")


def plot_all_3d(front_3d, actual_3d, randoms_3d, mrand, srand, prand, save_path):
    """Plot the 3D Pareto front with the actual plant and random tree costs.

    Args:
        front_3d (dict): A dictionary of total root lengths, total distances to the base and
            path_coverages for each (alpha, beta) value on the front
        actual_3d (tuple): The actual total_root_length, total_travel_distance, and
            total_path_coverage of the original plant
        randoms_3d (list): A list of random tree costs
        mrand (float): The mean total root length of the random trees
        srand (float): The mean total travel distance of the random trees
        prand (float): The mean path coverage of the random trees
        save_path (str): The file path to save the plot
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    # Set labels and title
    ax.set_xlabel("Total Root Length", fontsize=12, labelpad=10)
    ax.set_ylabel("Travel Distance", fontsize=12, labelpad=10)
    ax.set_zlabel("Path Coverage", fontsize=12, labelpad=10)
    ax.set_title("3D Pareto Front Visualization", fontsize=15, pad=20)

    logging.debug(f"Front 3D: {front_3d}")

    # Extract x, y, z values for the front
    x_values = [x[0] for x in front_3d.values()]
    y_values = [x[1] for x in front_3d.values()]
    z_values = [x[2] for x in front_3d.values()]

    # Plot the front_3d
    ax.plot(
        x_values,
        y_values,
        z_values,
        marker="o",
        linestyle="-",
        color="blue",
        label="Pareto Front",
    )

    # Plot the actual plant
    ax.scatter(
        [actual_3d[0]],
        [actual_3d[1]],
        [actual_3d[2]],
        color="orange",
        marker="X",
        s=100,
        label="Actual Plant",
    )

    # Plot the random tree costs
    randoms_3d_array = np.array(randoms_3d)
    ax.scatter(
        randoms_3d_array[:, 0],
        randoms_3d_array[:, 1],
        randoms_3d_array[:, 2],
        color="green",
        marker="+",
        s=50,
        alpha=0.6,
        label="Random Trees",
    )

    # Plot the centroid of random trees
    ax.scatter(
        [mrand],
        [srand],
        [prand],
        color="red",
        marker="D",
        s=80,
        label="Random Trees Centroid",
    )

    # Add legend
    ax.legend(loc="best", fontsize=10)

    # Enable grid and adjust scaling
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)

    # Save and show the plot
    plt.savefig(save_path, bbox_inches="tight", dpi=300)
    plt.show()
    print(f"Plot saved to {save_path}")


def distance_from_front(front, actual_tree):
    """
    Return the closest alpha for the actual tree, and its distance to the front.

    actual_tree is just (mactual, sactual)
    front is a dict of form {alpha : [total_root_length, total_travel_distance]}
    """

    # for each alpha value, find distance to the actual tree
    distances = {}

    for alpha in front.items():
        alpha_value = alpha[0]
        alpha_tree = alpha[1]

        material_ratio = actual_tree[0] / alpha_tree[0]
        transport_ratio = actual_tree[1] / alpha_tree[1]

        distances[alpha_value] = max(material_ratio, transport_ratio)

    # print(distances)
    closest = min(distances.items(), key=lambda x: x[1])
    # print(closest)

    characteristic_alpha, scaling_distance = closest

    return characteristic_alpha, scaling_distance


def distance_from_front_3d(front, actual_tree):
    """Return the closest (alpha, beta) for the actual tree, and its distance to the 3D front.

    Args:
        front (dict): A dictionary of edge_lengths, travel_distances_to_base, and
            path_coverages for (each alpha, beta) value on the front
        actual (tuple): The actual total_root_length, total_travel_distance, and
            total_path_coverage of the original plant

    Returns:
        tuple: A tuple containing the characteristic (alpha, beta) value, and the scaling distance
    """
    # for each (alpha, beta) value, find distance to the actual tree
    distances = {}

    for alpha_beta in front.items():
        alpha_beta_value = alpha_beta[0]
        alpha_beta_tree = alpha_beta[1]

        material_ratio = actual_tree[0] / alpha_beta_tree[0]
        transport_ratio = actual_tree[1] / alpha_beta_tree[1]
        path_coverage_ratio = actual_tree[2] / alpha_beta_tree[2]

        distances[alpha_beta_value] = max(
            material_ratio, transport_ratio, path_coverage_ratio
        )

    closest = min(distances.items(), key=lambda x: x[1])

    characteristic_alpha_beta, scaling_distance = closest

    return characteristic_alpha_beta, scaling_distance


def pareto_calcs(H):
    """Perform Pareto-related calculations."""
    front, actual = pareto_front(H)
    mactual, sactual = actual

    # for debug: show total_root_length, total_travel_distance
    # print(list(front.items())[0:5])

    plant_alpha, plant_scaling = distance_from_front(front, actual)
    randoms = random_tree(H)

    # centroid of randoms
    mrand = np.mean([x[0] for x in randoms])
    srand = np.mean([x[1] for x in randoms])

    rand_alpha, rand_scaling = distance_from_front(front, (mrand, srand))

    # assemble dict for export
    results = {
        "Total root length": mactual,
        "Travel distance": sactual,
        "alpha": plant_alpha,
        "scaling distance to front": plant_scaling,
        "Total root length (random)": mrand,
        "Travel distance (random)": srand,
        "alpha (random)": rand_alpha,
        "scaling (random)": rand_scaling,
    }

    return results, front, randoms


def pareto_calcs_3d_path_tortuosity(H):
    """Perform Pareto-related calculations using 3d Pareto Front with path tortuosity.

    Args:
        H (nx.Graph): NetworkX graph representing the root system.

    Returns:
        tuple: Tuple containing the results dictionary, the 3D Pareto front, and the random tree costs.
    """
    # Calculate the Pareto front using the 3D path tortuosity
    front, actual = pareto_front_3d_path_tortuosity(H)
    # Extract the actual tree values
    # mactual is the total root length, sactual is the total travel distance, and pactual is the path tortuosity
    mactual, sactual, pactual = actual

    # Calculate the characteristic (alpha, beta) value and the scaling distance
    plant_alpha_beta, plant_scaling = distance_from_front_3d(front, actual)
    # Generate random trees
    randoms = random_tree_3d_path_tortuosity(H)

    # Calculate the mean total root length and mean total travel distance and mean path tortuosity of the random trees
    mrand = np.mean([x[0] for x in randoms])
    srand = np.mean([x[1] for x in randoms])
    prand = np.mean([x[2] for x in randoms])

    # Calculate the characteristic (alpha, beta) value and the scaling distance for the random trees
    rand_alpha_beta, rand_scaling = distance_from_front_3d(front, (mrand, srand, prand))

    # Assemble the results dictionary
    results = {
        "Total root length": mactual,
        "Travel distance": sactual,
        "Path tortuosity": pactual,
        "alpha_beta": plant_alpha_beta,
        "scaling distance to front": plant_scaling,
        "Total root length (random)": mrand,
        "Travel distance (random)": srand,
        "Path tortuosity (random)": prand,
        "alpha_beta (random)": rand_alpha_beta,
        "scaling (random)": rand_scaling,
    }

    return results, front, randoms


### CONVEX HULL calculations


from scipy.spatial import ConvexHull
import numpy as np
import networkx as nx
import math


def distance(p1, p2):
    """Compute 2D Euclidian distance between two (x,y) points."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


from scipy.spatial import ConvexHull
import numpy as np


def calculate_convex_hull_area(G):
    # Check if the graph has at least 3 nodes
    if len(G.nodes) < 3:
        print("The graph must have at least 3 nodes to calculate the convex hull.")
        return None

    # Get the positions of the nodes
    positions = np.array([data["pos"] for node, data in G.nodes(data=True)])

    # Calculate the convex hull
    hull = ConvexHull(positions)

    # Get the area of the convex hull
    hull_area = hull.area

    return hull_area


import networkx as nx
import math


def distance(pos1, pos2):
    """Calculate the Euclidean distance between two positions."""
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


def calc_zones(G, root_node):
    """
    Calculate the Branched Zone, Basal Zone, and Apical Zone lengths along the primary root.
    """
    # Perform BFS to find nodes along the primary root
    bfs_paths = dict(nx.bfs_successors(G, root_node))

    # Collect primary root nodes
    PR_nodes = []
    for node, children in bfs_paths.items():
        if G.nodes[node].get("LR_index") is None:  # Primary root node
            PR_nodes.append(node)
            for child in children:
                if G.nodes[child].get("LR_index") is None:
                    PR_nodes.append(child)

    # Ensure PR_nodes are in order along the root path
    PR_nodes = list(dict.fromkeys(PR_nodes))

    # Identify the first and last lateral root insertion points
    first_lr_insertion_point = None
    last_lr_insertion_point = None

    for node in PR_nodes:
        neighbors = list(G.neighbors(node))
        if any(G.nodes[neighbor].get("LR_index") is not None for neighbor in neighbors):
            if first_lr_insertion_point is None:
                first_lr_insertion_point = node
            last_lr_insertion_point = node

    # Calculate zone lengths
    branched_zone_length = 0
    basal_zone_length = 0
    apical_zone_length = 0

    found_first = False
    found_last = False

    for prev, current in zip(PR_nodes, PR_nodes[1:]):
        segment_length = distance(G.nodes[prev]["pos"], G.nodes[current]["pos"])

        if current == first_lr_insertion_point:
            found_first = True
        if current == last_lr_insertion_point:
            found_last = True

        if found_first and not found_last:
            branched_zone_length += segment_length
        elif not found_first:
            basal_zone_length += segment_length
        elif found_last:
            apical_zone_length += segment_length

    return {
        "branched_zone_length": branched_zone_length,
        "basal_zone_length": basal_zone_length,
        "apical_zone_length": apical_zone_length,
    }


def calc_len_LRs_with_distances(H):
    """Calculate the 2D Euclidean distance for each lateral root from the first node to the last node, excluding intermediate nodes, and return the total length of each LR type in the graph."""
    # minimum length (px) for LR to be considered part of the network

    threshold = 0

    # dict of node ids : LR index, for each LR node
    idxs = nx.get_node_attributes(H, "LR_index")
    idxs = {k: v for k, v in idxs.items() if v is not None}  # drop empty (PR) nodes

    num_LRs = max(idxs.values()) + 1

    results = {}

    for i in range(num_LRs):
        # gather nodes corresponding to the current LR index
        selected = []

        for node in H.nodes(data="LR_index"):
            if node[1] == i:
                selected.append(node[0])
                # make note of the root degree (should be the same for all nodes in loop)
                current_degree = H.nodes[node[0]]["root_deg"]

        # to find the shallowest node in LR, we iterate through them
        # until we find the one whose parent_node has a lesser root degree
        sub = H.subgraph(selected)
        for node in sub.nodes():
            parent_node = list(H.predecessors(node))
            # print(node, parent_node)
            assert len(parent_node) == 1  # should be a tree
            if H.nodes[parent_node[0]]["root_deg"] < current_degree:
                sub_top = node

        # now we can DFS to order all nodes by increasing depth
        ordered = list(nx.dfs_tree(sub, sub_top).nodes())

        # also include the parent_node of the shallowest node in the LR (the 'branch point')
        parent_node = list(H.predecessors(ordered[0]))
        assert len(parent_node) == 1

        nodes_list = parent_node + ordered

        # Calculate the distance for the LR
        length = calc_root_len(H, nodes_list)

        # Exclude intermediate nodes
        if length < threshold:
            H.remove_nodes_from(ordered)
        else:
            # Now we can calculate the Euclidean distance from the first node to the last node
            # excluding intermediate nodes
            first_node_pos = H.nodes[nodes_list[0]]["pos"]
            last_node_pos = H.nodes[nodes_list[-1]]["pos"]
            distance_lr = distance(first_node_pos, last_node_pos)

            results[i] = [length, distance_lr]

    assert nx.is_tree(H)
    return results


def find_lowermost_node_of_primary_root(G, root_node):
    """Find the lowermost node of the primary root."""
    descendants = nx.descendants(G, root_node)
    lowermost_node = max(
        descendants, key=lambda node: G.nodes[node]["pos"][1]
    )  # Find the node with the maximum y-coordinate
    return G.nodes[lowermost_node]["pos"]


def calculate_distance(p1, p2):
    """Compute 2D Euclidean distance between two (x,y) points."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


import numpy as np


def analyze(G):
    """Report basic root metrics for a given graph."""
    # check that graph is indeed a tree (acyclic, undirected, connected)
    assert nx.is_tree(G)

    # independent deep copy of G, with LRs below threshold excluded
    H = copy.deepcopy(G)

    # find top ("root") node
    for node in H.nodes(data="pos"):

        if node[1] == [0, 0]:
            root_node = node[0]
    # the pareto functions are hardcoded to assume node 0 is the top.

    assert root_node == 0

    # PR len
    len_PR = calc_len_PR(H, root_node)
    # print('PR length is:', len_PR)

    # LR len/number
    LR_info = calc_len_LRs(H)
    num_LRs = len(LR_info)
    lens_LRs = [x[0] for x in LR_info.values()]
    angles_LRs = [x[1] for x in LR_info.values()]
    # print('LR lengths are:', lens_LRs)
    # print('Set point angles are:', angles_LRs)

    # primary LR density
    density_LRs = num_LRs / len_PR
    # print('LR density is:', num_LRs/len_PR)

    # Calculate the Euclidean distance between the uppermost node and the lowermost node of the primary root
    uppermost_node_pos = H.nodes[root_node]["pos"]
    lowermost_node_pos = find_lowermost_node_of_primary_root(H, root_node)
    distance_root = calculate_distance(uppermost_node_pos, lowermost_node_pos)

    results, front, randoms = pareto_calcs(H)
    results_3d, front_3d, randoms_3d = pareto_calcs_3d_path_tortuosity(H)

    # Calculate lateral root distances with lengths and first-to-last distances
    lateral_root_info = calc_len_LRs_with_distances(H)
    num_LRs = len(lateral_root_info)

    # Extract lengths and distances
    lens_LRs = [info[0] for info in lateral_root_info.values()]
    distances_LRs = [info[1] for info in lateral_root_info.values()]

    # Convex Hull calculations
    points = np.array([H.nodes[node]["pos"] for node in H.nodes()])
    hull = ConvexHull(points)

    # Barycenter (centroid) of the Convex Hull
    # Centroid formula: (mean x, mean y) of the vertices of the convex hull
    hull_points = points[hull.vertices]
    barycenter_x = np.mean(hull_points[:, 0])
    barycenter_y = np.mean(hull_points[:, 1])
    barycenter = (barycenter_x, barycenter_y)

    # Find the uppermost node (node with the minimum y-coordinate)
    uppermost_node = min(H.nodes(data="pos"), key=lambda node: node[1][1])
    uppermost_node_pos = uppermost_node[1]

    # Build quadrilateral (barycenter and uppermost node form the quadrilateral)
    barycenter_y_displacement = abs(
        barycenter_y - uppermost_node_pos[1]
    )  # Displacement in y-direction
    barycenter_x_displacement = abs(
        barycenter_x - uppermost_node_pos[0]
    )  # Displacement in x-direction

    # Calculate Branched, Basal, and Apical Zones
    zone_lengths = calc_zones(H, root_node)
    branched_zone_length = zone_lengths["branched_zone_length"]
    basal_zone_length = zone_lengths["basal_zone_length"]
    apical_zone_length = zone_lengths["apical_zone_length"]

    # Ensure basal zone length is 0 if it equals the primary root length
    if basal_zone_length == len_PR:
        basal_zone_length = 0

    # Branched Zone density

    branched_zone_density = (
        num_LRs / branched_zone_length if branched_zone_length != 0 else 0
    )

    # Calculate mean and median
    mean_LR_lengths = np.mean(lens_LRs)
    median_LR_lengths = np.median(lens_LRs)
    median_LR_angles = np.median(angles_LRs)
    mean_LR_angles = np.mean(angles_LRs)
    mean_LR_distances = np.mean(distances_LRs)
    median_LR_distances = np.median(distances_LRs)
    sum_LR_distances = np.sum(distances_LRs)

    # Calculate the total distance (sum of LR distances and PR minimal distance)
    total_distance = sum_LR_distances + distance_root

    # Add lateral root lengths and distances to the results dictionary
    results["PR length"] = len_PR
    results["PR_minimal_length"] = distance_root
    results["Basal Zone length"] = basal_zone_length
    results["Branched Zone length"] = branched_zone_length
    results["Apical Zone length"] = apical_zone_length
    results["Mean LR lengths"] = mean_LR_lengths
    results["Mean LR minimal lengths"] = mean_LR_distances
    results["Median LR lengths"] = median_LR_lengths
    results["Median LR minimal lengths"] = median_LR_distances
    results["sum LR minimal lengths"] = sum_LR_distances
    results["Mean LR angles"] = mean_LR_angles
    results["Median LR angles"] = median_LR_angles
    results["LR count"] = num_LRs
    results["LR density"] = density_LRs
    results["Branched Zone density"] = branched_zone_density
    results["LR lengths"] = lens_LRs
    results["LR angles"] = angles_LRs
    results["LR minimal lengths"] = distances_LRs
    results["Barycenter x displacement"] = barycenter_x_displacement
    results["Barycenter y displacement"] = barycenter_y_displacement
    results["Total minimal Distance"] = (
        total_distance  # Add the total distance to the results
    )

    # Calculate the material cost (total root length)
    Total_root_length = len_PR + sum(lens_LRs)

    # Calculate the ratio of the material cost with the Total minimal Distance
    material_distance_ratio = Total_root_length / total_distance

    results["Material Cost to Travel Distance Ratio"] = material_distance_ratio

    # Calculating convex hull area
    points = np.array([H.nodes[node]["pos"] for node in H.nodes()])
    hull = ConvexHull(points)
    convex_hull_area = hull.volume  # Convex hull area in 2D is the same as its volume

    results["Convex Hull Area"] = convex_hull_area

    return results, front, randoms, results_3d, front_3d, randoms_3d
