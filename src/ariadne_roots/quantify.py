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
from ariadne_roots import config


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


def make_graph(target):  # pragma: no cover
    """Construct graph from file and check for errors.

    Legacy function for text file format. Not used in current JSON workflow.
    """
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


def make_graph_alt(target):  # pragma: no cover
    """Construct a broken graph (without problematic edges).

    Legacy function for text file format. Not used in current JSON workflow.
    """
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
):  # pragma: no cover
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
    node_sizes = [node_base_size + G.degree(n) * node_size_factor for n in G.nodes()]

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
    edge_widths = [edge_width_factor * G[u][v].get("weight", 1) for u, v in G.edges()]

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


def save_plot(path, name, title):  # pragma: no cover
    """Plot a Pareto front and save to .jpg.

    GUI function for manual visualization. Not tested in automated test suite.
    """
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
    # CPL : Add a minimum LR_index. Main root is None
    min_num_LRs = min(idxs.values())  # should be 1
    results = {}

    for i in range(min_num_LRs, num_LRs):
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


def calc_density_LRs(G):  # pragma: no cover
    """Calculate lateral root density.

    Stub function - not yet implemented.
    """
    pass
    # add up to _n_ degrees


def calculate_plot_buffer(base_min, base_max, buffer_percent=0.20, min_buffer=1.0):
    """Calculate plot buffer for axis limits.

    Computes appropriate buffer margins for plot axes based on data range,
    handling edge cases like negative coordinates, zero values, and small ranges.

    Args:
        base_min: Minimum value in the data range
        base_max: Maximum value in the data range
        buffer_percent: Buffer size as fraction of range (default 0.20 = 20%)
        min_buffer: Minimum buffer to prevent degenerate plots (default 1.0)

    Returns:
        Tuple of (min_limit, max_limit) for axis

    Examples:
        >>> calculate_plot_buffer(0, 10)  # Normal positive range
        (-2.0, 12.0)

        >>> calculate_plot_buffer(-10, 10)  # Range crossing zero
        (-14.0, 14.0)

        >>> calculate_plot_buffer(0, 0)  # Degenerate range (all zeros)
        (-1.0, 1.0)

        >>> calculate_plot_buffer(-5, -3)  # Negative range
        (-5.4, -2.6)
    """
    data_range = abs(base_max - base_min)
    buffer = max(data_range * buffer_percent, min_buffer)
    return (base_min - buffer, base_max + buffer)


def plot_all(front, actual, randoms, mrand, srand, dest):  # pragma: no cover
    """Plot Pareto front with actual and random trees, with scaling and centering.

    GUI function for manual visualization. Not tested in automated test suite.
    Applies user-configured scaling and centers view on Pareto front.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)

    def scale_data(data):
        """Scale data by user-configured factor."""
        return data * config.length_scale_factor

    # Scale all data
    scaled_front_x = [scale_data(x[0]) for x in front.values()]
    scaled_front_y = [scale_data(x[1]) for x in front.values()]

    scaled_actual_x = scale_data(actual[0])
    scaled_actual_y = scale_data(actual[1])

    scaled_randoms_x = [scale_data(x[0]) for x in randoms]
    scaled_randoms_y = [scale_data(x[1]) for x in randoms]

    scaled_mrand = scale_data(mrand)
    scaled_srand = scale_data(srand)

    # Plot scaled data
    for x, y in zip(scaled_randoms_x, scaled_randoms_y):
        plt.plot(
            x,
            y,
            marker="+",
            color="green",
            markersize=2.5,
            zorder=0.5,
            markeredgewidth=0.5,
        )

    plt.plot(
        scaled_front_x,
        scaled_front_y,
        marker="s",
        linestyle="-",
        markeredgecolor="black",
    )
    plt.plot(
        scaled_actual_x,
        scaled_actual_y,
        marker="x",
        markersize=12,
        zorder=3,
        markeredgewidth=1.5,
    )
    plt.plot(
        scaled_mrand,
        scaled_srand,
        marker="+",
        color="red",
        markersize=12,
        zorder=3,
        markeredgewidth=1.5,
    )

    ax.set_xlabel(f"Total length ({config.length_scale_unit})", fontsize=15)
    ax.set_ylabel(f"Travel distance ({config.length_scale_unit})", fontsize=15)

    # Set limits to focus on the relevant area (Pareto front centered)
    front_x_min = min(scaled_front_x)
    front_x_max = max(scaled_front_x)
    front_y_min = min(scaled_front_y)
    front_y_max = max(scaled_front_y)

    # Create a bounding box that includes Pareto front and random centroid
    # Use absolute value to handle negative coordinates correctly
    base_x_min = min(front_x_min, scaled_mrand)
    base_x_max = max(front_x_max, scaled_mrand)
    base_y_min = min(front_y_min, scaled_srand)
    base_y_max = max(front_y_max, scaled_srand)

    # Calculate axis limits with 20% buffer
    x_min, x_max = calculate_plot_buffer(base_x_min, base_x_max)
    y_min, y_max = calculate_plot_buffer(base_y_min, base_y_max)

    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)

    # Save as PNG
    plt.savefig(dest, bbox_inches="tight", dpi=300)

    # Also save as SVG for better quality
    svg_dest = dest.with_suffix(".svg")
    plt.savefig(svg_dest, bbox_inches="tight", format="svg")

    plt.close(fig)


def plot_all_3d(
    front_3d, actual_3d, randoms_3d, mrand, srand, prand, save_path
):  # pragma: no cover
    """Plot the 3D Pareto front as a surface with actual plant and random trees.

    Creates a 3D visualization of the Pareto front using triangulated surface
    interpolation. The surface is colored by path coverage (z-axis) to show
    the gradient across the front.

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
    from matplotlib.tri import Triangulation
    from scipy.spatial import Delaunay

    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection="3d")

    # Set labels and title with units from config
    ax.set_xlabel(
        f"Total Root Length ({config.length_scale_unit})", fontsize=12, labelpad=10
    )
    ax.set_ylabel(
        f"Travel Distance ({config.length_scale_unit})", fontsize=12, labelpad=10
    )
    ax.set_zlabel("Path Coverage (ratio)", fontsize=12, labelpad=10)
    ax.set_title("3D Pareto Front: Root Architecture Trade-offs", fontsize=15, pad=20)

    logging.debug(f"Front 3D: {front_3d}")

    # Extract x, y, z values for the front
    x_values = np.array([x[0] for x in front_3d.values()])
    y_values = np.array([x[1] for x in front_3d.values()])
    z_values = np.array([x[2] for x in front_3d.values()])

    # Try to create a triangulated surface plot
    surface_plotted = False
    if len(x_values) >= 3:
        try:
            # Create 2D Delaunay triangulation on (x, y) coordinates
            points_2d = np.column_stack((x_values, y_values))
            tri = Delaunay(points_2d)

            # Create matplotlib Triangulation from Delaunay result
            triangulation = Triangulation(x_values, y_values, tri.simplices)

            # Plot the triangulated surface colored by path coverage
            surf = ax.plot_trisurf(
                triangulation,
                z_values,
                cmap="viridis",
                alpha=0.7,
                edgecolor="none",
                linewidth=0,
            )

            # Add colorbar for path coverage
            cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, pad=0.1)
            cbar.set_label("Path Coverage", fontsize=10)

            surface_plotted = True
            logging.debug("Successfully created triangulated surface plot")

        except Exception as e:
            # Triangulation failed (e.g., collinear points)
            logging.warning(f"Triangulation failed, falling back to scatter plot: {e}")

    # Fallback: scatter plot for Pareto front if surface failed or too few points
    if not surface_plotted:
        ax.scatter(
            x_values,
            y_values,
            z_values,
            c=z_values,
            cmap="viridis",
            marker="o",
            s=50,
            alpha=0.8,
            label="Pareto Front",
        )
        logging.info("Using scatter plot for Pareto front (triangulation not possible)")

    # Plot the actual plant (orange X marker)
    ax.scatter(
        [actual_3d[0]],
        [actual_3d[1]],
        [actual_3d[2]],
        color="orange",
        marker="X",
        s=150,
        edgecolors="black",
        linewidths=0.5,
        label="Actual Plant",
        zorder=5,
    )

    # Plot the random tree costs (green + markers)
    if len(randoms_3d) > 0:
        randoms_3d_array = np.array(randoms_3d)
        ax.scatter(
            randoms_3d_array[:, 0],
            randoms_3d_array[:, 1],
            randoms_3d_array[:, 2],
            color="green",
            marker="+",
            s=50,
            alpha=0.6,
            linewidths=1,
            label="Random Trees",
        )

    # Plot the centroid of random trees (red diamond)
    ax.scatter(
        [mrand],
        [srand],
        [prand],
        color="red",
        marker="D",
        s=100,
        edgecolors="black",
        linewidths=0.5,
        label="Random Centroid",
        zorder=5,
    )

    # Add legend
    ax.legend(loc="upper left", fontsize=9)

    # Enable grid
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)

    # Save as PNG
    plt.savefig(save_path, bbox_inches="tight", dpi=300)

    # Also save as SVG for better quality
    svg_dest = save_path.with_suffix(".svg")
    plt.savefig(svg_dest, bbox_inches="tight", format="svg")

    plt.close(fig)


def distance_from_front(front, actual_tree):
    """Return the interpolated alpha for the actual tree, and its distance to the front.

    Interpolates between the two closest discrete alpha values on the Pareto front
    for higher precision (based on Matt Platre's implementation).

    Args:
        actual_tree: Tuple of (total_root_length, total_travel_distance)
        front: Dict of form {alpha: [total_root_length, total_travel_distance]}

    Returns:
        Tuple of (interpolated_alpha, scaling_distance) as Python floats
    """
    # For each alpha value, find distance to the actual tree
    distances = {}

    for alpha_value, alpha_tree in front.items():
        # Guard against division by zero (unlikely with real root data)
        if alpha_tree[0] == 0 or alpha_tree[1] == 0:
            continue
        material_ratio = actual_tree[0] / alpha_tree[0]
        transport_ratio = actual_tree[1] / alpha_tree[1]
        distances[alpha_value] = max(material_ratio, transport_ratio)

    # Find the two closest alpha values
    sorted_alphas = sorted(distances.items(), key=lambda x: x[1])
    closest = sorted_alphas[0]
    second_closest = sorted_alphas[1] if len(sorted_alphas) > 1 else closest

    alpha1, dist1 = closest
    alpha2, dist2 = second_closest

    # Linear interpolation between the two closest alphas
    # Closer distance gets higher weight
    if math.isclose(dist1, dist2, rel_tol=1e-9):
        interpolated_alpha = float(alpha1)
    else:
        total_dist = dist1 + dist2
        weight1 = dist2 / total_dist  # Inverse weighting: closer = higher weight
        weight2 = dist1 / total_dist
        interpolated_alpha = float(alpha1 * weight1 + alpha2 * weight2)

    return interpolated_alpha, float(dist1)


def calculate_tradeoff(front, actual_tree):
    """Calculate a tradeoff metric comparing the actual root to optimal architectures.

    Conn et al., 2019 (https://doi.org/10.1371/journal.pcbi.1007325) describe
    a tradeoff feature in which:

        "The numerator quantifies the excess length of the plant compared to the
        optimal minimum length of the Steiner tree. Similarly, the denominator
        quantifies the excess travel distance of the plant compared to the optimal
        minimum travel distance of the Satellite tree. A high value of this feature
        (i.e., a large numerator and small denominator) indicates that the plant
        prioritizes minimizing travel distance; a low trade-off value indicates
        the plant prioritizes minimizing total length."

    That description corresponds to an excess-based metric roughly of the form:
        (actual_length - steiner_length) / (actual_distance - satellite_distance)

    In this implementation we use a related, ratio-based metric inspired by the
    same intuition, defined as a ratio of length-per-distance values:

        Tradeoff = Actual_ratio / Optimal_ratio
                 = (actual_length / actual_distance) / (steiner_length / satellite_distance)

    This represents an alternative way to quantify the prioritization between
    minimizing total root length (material cost) and minimizing travel distance
    (transport efficiency), complementary to the alpha value on the Pareto front.

    - Steiner architecture: Minimizes total root length (material cost)
    - Satellite architecture: Minimizes travel distance (transport efficiency)

    Args:
        front: Dict of {alpha: [total_length, travel_distance]} Pareto front points
        actual_tree: Tuple of (total_root_length, travel_distance)

    Returns:
        Dict with Tradeoff metric and component values:
        - Tradeoff: Ratio of actual to optimal efficiency
        - Steiner_length: Min total root length on Pareto front
        - Steiner_distance: Travel distance of the Steiner architecture
        - Satellite_length: Total root length of the Satellite architecture
        - Satellite_distance: Travel distance of the Satellite architecture
        - Actual_ratio: actual_length / actual_distance
        - Optimal_ratio: steiner_length / satellite_distance
    """
    # Extract Pareto front values
    front_points = list(front.values())  # List of [total_length, travel_distance] pairs

    if len(front_points) < 1:
        print("Warning: Pareto front is empty, cannot calculate Tradeoff")
        return {
            "Tradeoff": None,
            "Steiner_length": None,
            "Steiner_distance": None,
            "Satellite_length": None,
            "Satellite_distance": None,
            "Actual_ratio": None,
            "Optimal_ratio": None,
        }

    # Find Steiner architecture (minimizes total root length)
    steiner_point = min(front_points, key=lambda x: x[0])
    steiner_length, steiner_distance = steiner_point

    # Find Satellite architecture (minimizes travel distance)
    satellite_point = min(front_points, key=lambda x: x[1])
    satellite_length, satellite_distance = satellite_point

    # Actual tree values
    actual_length, actual_distance = actual_tree

    # Calculate ratios - handle division by zero
    if actual_distance == 0:
        actual_ratio = None
        print("Warning: Actual travel distance is 0, actual_ratio set to None")
    else:
        actual_ratio = float(actual_length / actual_distance)

    if satellite_distance == 0:
        optimal_ratio = None
        print("Warning: Satellite travel distance is 0, optimal_ratio set to None")
    else:
        optimal_ratio = float(steiner_length / satellite_distance)

    # Calculate tradeoff
    if optimal_ratio is None or optimal_ratio == 0 or actual_ratio is None:
        tradeoff = None
        print("Warning: Could not calculate tradeoff due to invalid ratios")
    else:
        tradeoff = float(actual_ratio / optimal_ratio)

    return {
        "Tradeoff": tradeoff,
        "Steiner_length": float(steiner_length),
        "Steiner_distance": float(steiner_distance),
        "Satellite_length": float(satellite_length),
        "Satellite_distance": float(satellite_distance),
        "Actual_ratio": actual_ratio,
        "Optimal_ratio": optimal_ratio,
    }


def distance_from_front_3d(front, actual_tree):
    """Compute the epsilon indicator distance from a tree to the 3D Pareto front.

    Uses the multiplicative ε-indicator, a standard metric in multi-objective
    optimization (Zitzler et al., 2003). The epsilon value represents the
    minimum scaling factor needed to make a Pareto-optimal tree dominate the
    actual tree in all objectives.

    Implements barycentric interpolation with the 3 nearest (α, β) points for
    higher precision, matching the 2D distance_from_front() approach.

    Formula: ε = min_{r ∈ Front} max_i (actual_i / front_i)

    Interpretation:
        - ε = 1.0: Tree is on the Pareto front
        - ε > 1.0: Tree is suboptimal; ε is the scaling factor
        - ε < 1.0: Tree dominates the front (should not happen)

    References:
        Zitzler et al. (2003), IEEE Trans. Evol. Comput. 7(2), 117-132
        Chandrasekhar & Navlakha (2019), Proc. Royal Society B, Supplementary Eq. 2

    Args:
        front: Dict mapping (alpha, beta) tuples to [length, distance, tortuosity] lists
        actual_tree: Tuple of (total_root_length, total_travel_distance, path_tortuosity)

    Returns:
        Dict with keys:
            - epsilon: float - multiplicative ε-indicator (scaling factor)
            - alpha: float - interpolated alpha parameter
            - beta: float - interpolated beta parameter
            - gamma: float - computed as 1 - alpha - beta
            - epsilon_components: dict with material/transport/coverage ratios
            - corner_costs: dict with steiner/satellite/coverage corner values
    """
    # For each (alpha, beta) value, find distance to the actual tree
    distances = {}
    ratios = {}  # Store component ratios for each point

    for alpha_beta_value, alpha_beta_tree in front.items():
        # Division-by-zero guard: skip points with any zero cost dimension
        if any(v == 0 for v in alpha_beta_tree):
            continue

        material_ratio = actual_tree[0] / alpha_beta_tree[0]
        transport_ratio = actual_tree[1] / alpha_beta_tree[1]
        path_coverage_ratio = actual_tree[2] / alpha_beta_tree[2]

        epsilon = max(material_ratio, transport_ratio, path_coverage_ratio)
        distances[alpha_beta_value] = epsilon
        ratios[alpha_beta_value] = (material_ratio, transport_ratio, path_coverage_ratio)

    # Handle edge case: no valid points
    if not distances:
        # Fall back to returning default values if all points have zeros
        return {
            "epsilon": float("inf"),
            "alpha": 0.0,
            "beta": 0.0,
            "gamma": 1.0,
            "epsilon_components": {
                "material": float("inf"),
                "transport": float("inf"),
                "coverage": float("inf"),
            },
            "corner_costs": {
                "steiner": (0.0, 0.0, 0.0),
                "satellite": (0.0, 0.0, 0.0),
                "coverage": (0.0, 0.0, 0.0),
            },
        }

    # Find the 3 nearest (alpha, beta) points by epsilon distance
    sorted_points = sorted(distances.items(), key=lambda x: x[1])

    # Get up to 3 closest points
    n_points = min(3, len(sorted_points))
    closest_points = sorted_points[:n_points]

    # Extract closest point's epsilon and ratios for the result
    closest_ab, closest_epsilon = closest_points[0]
    closest_ratios = ratios[closest_ab]

    # Barycentric interpolation using inverse-distance weighting
    if n_points == 1:
        # Single point: use directly
        alpha = float(closest_ab[0])
        beta = float(closest_ab[1])
    else:
        # Inverse distance weighting for 2 or 3 points
        # Add small epsilon to avoid division by zero when distance is exactly 0
        eps_guard = 1e-10

        weights = []
        for ab, dist in closest_points:
            weights.append(1.0 / (dist + eps_guard))

        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]

        # Interpolate alpha and beta
        alpha = sum(
            w * ab[0] for w, (ab, _) in zip(normalized_weights, closest_points)
        )
        beta = sum(
            w * ab[1] for w, (ab, _) in zip(normalized_weights, closest_points)
        )

        # Clamp to valid range (α ≥ 0, β ≥ 0, α + β ≤ 1)
        alpha = max(0.0, min(1.0, alpha))
        beta = max(0.0, min(1.0 - alpha, beta))

    # Compute gamma
    gamma = 1.0 - alpha - beta

    # Look up corner costs from the front
    # Steiner: α=1, β=0, γ=0 (minimizes length)
    # Satellite: α=0, β=1, γ=0 (minimizes distance)
    # Coverage: α=0, β=0, γ=1 (minimizes tortuosity)
    steiner_key = (1.0, 0.0)
    satellite_key = (0.0, 1.0)
    coverage_key = (0.0, 0.0)

    steiner_costs = front.get(steiner_key, [0.0, 0.0, 0.0])
    satellite_costs = front.get(satellite_key, [0.0, 0.0, 0.0])
    coverage_costs = front.get(coverage_key, [0.0, 0.0, 0.0])

    return {
        "epsilon": float(closest_epsilon),
        "alpha": float(alpha),
        "beta": float(beta),
        "gamma": float(gamma),
        "epsilon_components": {
            "material": float(closest_ratios[0]),
            "transport": float(closest_ratios[1]),
            "coverage": float(closest_ratios[2]),
        },
        "corner_costs": {
            "steiner": tuple(float(v) for v in steiner_costs),
            "satellite": tuple(float(v) for v in satellite_costs),
            "coverage": tuple(float(v) for v in coverage_costs),
        },
    }


def pareto_calcs(H):
    """Perform Pareto-related calculations."""
    front, actual = pareto_front(H)
    mactual, sactual = actual

    # for debug: show total_root_length, total_travel_distance
    # print(list(front.items())[0:5])

    # Calculate tradeoff metrics
    tradeoff_info = calculate_tradeoff(front, actual)

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

    # Merge tradeoff metrics into results
    results.update(tradeoff_info)

    return results, front, randoms


def pareto_calcs_3d_path_tortuosity(H):
    """Perform Pareto-related calculations using 3D Pareto Front with path tortuosity.

    Uses the multiplicative ε-indicator to measure distance from the Pareto front.
    Returns interpolated (α, β, γ) parameters and epsilon components.

    Args:
        H (nx.Graph): NetworkX graph representing the root system.

    Returns:
        tuple: (results_dict, front, randoms) where results_dict contains:
            - Total root length, Travel distance, Path tortuosity (actual tree)
            - alpha_3d, beta_3d, gamma_3d (interpolated Pareto weights)
            - epsilon_3d (multiplicative ε-indicator)
            - epsilon_3d_material/transport/coverage (ratio components)
            - Same fields for random trees with "(random)" suffix
            - Corner costs: Steiner_*_3d, Satellite_*_3d, Coverage_*_3d
    """
    # Calculate the Pareto front using the 3D path tortuosity
    front, actual = pareto_front_3d_path_tortuosity(H)
    # Extract the actual tree values
    # mactual is the total root length, sactual is the total travel distance, and pactual is the path tortuosity
    mactual, sactual, pactual = actual

    # Calculate the epsilon indicator and interpolated (alpha, beta, gamma)
    plant_result = distance_from_front_3d(front, actual)

    # Generate random trees
    randoms = random_tree_3d_path_tortuosity(H)

    # Calculate the mean costs of the random trees
    mrand = float(np.mean([x[0] for x in randoms]))
    srand = float(np.mean([x[1] for x in randoms]))
    prand = float(np.mean([x[2] for x in randoms]))

    # Calculate epsilon indicator for the random tree centroid
    rand_result = distance_from_front_3d(front, (mrand, srand, prand))

    # Extract corner costs from plant_result (same for both calls)
    corner_costs = plant_result["corner_costs"]

    # Assemble the results dictionary with _3d suffix for 3D-specific fields
    results = {
        # Actual tree measurements (same names as 2D for shared fields)
        "Total root length": float(mactual),
        "Travel distance": float(sactual),
        "Path tortuosity": float(pactual),
        # Interpolated Pareto parameters
        "alpha_3d": plant_result["alpha"],
        "beta_3d": plant_result["beta"],
        "gamma_3d": plant_result["gamma"],
        # Epsilon indicator (distance from front)
        "epsilon_3d": plant_result["epsilon"],
        # Epsilon components (which dimension drives epsilon)
        "epsilon_3d_material": plant_result["epsilon_components"]["material"],
        "epsilon_3d_transport": plant_result["epsilon_components"]["transport"],
        "epsilon_3d_coverage": plant_result["epsilon_components"]["coverage"],
        # Random tree measurements
        "Total root length (random)": mrand,
        "Travel distance (random)": srand,
        "Path tortuosity (random)": prand,
        # Random tree Pareto parameters
        "alpha_3d (random)": rand_result["alpha"],
        "beta_3d (random)": rand_result["beta"],
        "gamma_3d (random)": rand_result["gamma"],
        "epsilon_3d (random)": rand_result["epsilon"],
        # Corner architecture reference costs
        "Steiner_length_3d": corner_costs["steiner"][0],
        "Steiner_distance_3d": corner_costs["steiner"][1],
        "Steiner_tortuosity_3d": corner_costs["steiner"][2],
        "Satellite_length_3d": corner_costs["satellite"][0],
        "Satellite_distance_3d": corner_costs["satellite"][1],
        "Satellite_tortuosity_3d": corner_costs["satellite"][2],
        "Coverage_length_3d": corner_costs["coverage"][0],
        "Coverage_distance_3d": corner_costs["coverage"][1],
        "Coverage_tortuosity_3d": corner_costs["coverage"][2],
    }

    return results, front, randoms


### CONVEX HULL calculations


def distance(p1, p2):
    """Compute 2D Euclidian distance between two (x,y) points."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


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


def distance(pos1, pos2):
    """Calculate the Euclidean distance between two positions."""
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


def calc_zones(G, root_node):
    """Calculate the Branched Zone, Basal Zone, and Apical Zone lengths along the primary root."""
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
    min_num_LRs = min(idxs.values())  # should be 1

    results = {}

    for i in range(min_num_LRs, num_LRs):
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


def analyze(G, enable_3d=True):
    """Report basic root metrics for a given graph.

    Args:
        G: NetworkX graph representing the root system.
        enable_3d: If True, compute 3D Pareto analysis (slower).
                   If False, return empty 3D results.

    Returns:
        Tuple of (results, front, randoms, results_3d, front_3d, randoms_3d).
        When enable_3d=False, results_3d, front_3d, randoms_3d are empty.
    """
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

    # 3D Pareto analysis is optional (slower: 10,201 iterations vs 101 for 2D)
    if enable_3d:
        results_3d, front_3d, randoms_3d = pareto_calcs_3d_path_tortuosity(H)
    else:
        results_3d, front_3d, randoms_3d = {}, {}, []

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

    # Calculate mean and median (convert to Python floats for clean CSV serialization)
    mean_LR_lengths = float(np.mean(lens_LRs))
    median_LR_lengths = float(np.median(lens_LRs))
    median_LR_angles = float(np.median(angles_LRs))
    mean_LR_angles = float(np.mean(angles_LRs))
    mean_LR_distances = float(np.mean(distances_LRs))
    median_LR_distances = float(np.median(distances_LRs))
    sum_LR_distances = float(np.sum(distances_LRs))

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
    # Convert list elements to Python floats for clean CSV serialization
    results["LR lengths"] = [float(x) for x in lens_LRs]
    results["LR angles"] = [float(x) for x in angles_LRs]
    results["LR minimal lengths"] = [float(x) for x in distances_LRs]
    results["Barycenter x displacement"] = float(barycenter_x_displacement)
    results["Barycenter y displacement"] = float(barycenter_y_displacement)
    results["Total minimal Distance"] = (
        total_distance  # Add the total distance to the results
    )

    # Calculate the material cost (total root length)
    Total_root_length = len_PR + sum(lens_LRs)

    # Calculate the ratio of the material cost with the Total minimal Distance
    material_distance_ratio = Total_root_length / total_distance

    results["Tortuosity"] = material_distance_ratio

    # Calculating convex hull area
    points = np.array([H.nodes[node]["pos"] for node in H.nodes()])
    hull = ConvexHull(points)
    convex_hull_area = hull.volume  # Convex hull area in 2D is the same as its volume

    results["Convex Hull Area"] = float(convex_hull_area)

    return results, front, randoms, results_3d, front_3d, randoms_3d
