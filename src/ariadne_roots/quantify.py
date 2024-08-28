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

from queue import Queue
from scipy.spatial import ConvexHull  # Import ConvexHull class

from ariadne_roots.pareto_functions import pareto_front, random_tree


# parser = argparse.ArgumentParser(description='select file')
# parser.add_argument('-i', '--input', help='Full path to input file', required=True)
# args = parser.parse_args()


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
                        q.put((node_num, list(map(int, child_node.strip("[]").split(",")))))

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
                            (node_num, list(map(int, child_node.strip("[]").split(","))))
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
    # plt.show()


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


def pareto_calcs(H):
    """Perform Pareto-related calculations."""
    front, actual = pareto_front(H)
    mactual, sactual = actual

    # for debug: show total_root_length, total_travel_distance
    print(list(front.items())[0:5])

    plant_alpha, plant_scaling = distance_from_front(front, actual)
    randoms = random_tree(H)

    # centroid of randoms
    mrand = np.mean([x[0] for x in randoms])
    srand = np.mean([x[1] for x in randoms])

    rand_alpha, rand_scaling = distance_from_front(front, (mrand, srand))

    # assemble dict for export
    results = {
        "material cost": mactual,
        "wiring cost": sactual,
        "alpha": plant_alpha,
        "scaling distance to front": plant_scaling,
        "material (random)": mrand,
        "wiring (random)": srand,
        "alpha (random)": rand_alpha,
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

    # Calculate lateral root distances with lengths and first-to-last distances
    lateral_root_info = calc_len_LRs_with_distances(H)
    num_LRs = len(lateral_root_info)

    # Extract lengths and distances
    lens_LRs = [info[0] for info in lateral_root_info.values()]
    distances_LRs = [info[1] for info in lateral_root_info.values()]

    # Calculate mean and median
    mean_LR_lengths = np.mean(lens_LRs)
    median_LR_lengths = np.median(lens_LRs)
    mean_LR_angles = np.mean(angles_LRs)
    median_LR_angles = np.median(angles_LRs)
    mean_LR_distances = np.mean(distances_LRs)
    median_LR_distances = np.median(distances_LRs)
    sum_LR_distances = np.sum(distances_LRs)

    # Calculate the total distance (sum of LR distances and PR minimal distance)
    total_distance = sum_LR_distances + distance_root

    # Add lateral root lengths and distances to the results dictionary
    results["Mean LR lengths"] = mean_LR_lengths
    results["Median LR lengths"] = median_LR_lengths
    results["Mean LR angles"] = mean_LR_angles
    results["Median LR angles"] = median_LR_angles
    results["Mean LR minimal distances"] = mean_LR_distances
    results["Median LR minimal distances"] = median_LR_distances
    results["sum LR minimal distances"] = sum_LR_distances
    results["PR_minimal_distances"] = distance_root
    results["PR length"] = len_PR
    results["LR count"] = num_LRs
    results["LR lengths"] = lens_LRs
    results["LR angles"] = angles_LRs
    results["LR minimal distances"] = distances_LRs
    results["LR density"] = density_LRs
    results["Total minimal Distance"] = (
        total_distance  # Add the total distance to the results
    )

    # Calculate the material cost (total root length)
    Total_root_length = len_PR + sum(lens_LRs)

    # Calculate the ratio of the material cost with the Total minimal Distance
    material_distance_ratio = Total_root_length / total_distance

    results["Material/TotalDistance Ratio"] = material_distance_ratio

    # Calculating convex hull area
    points = np.array([H.nodes[node]["pos"] for node in H.nodes()])
    hull = ConvexHull(points)
    convex_hull_area = hull.volume  # Convex hull area in 2D is the same as its volume

    results["Convex Hull Area"] = convex_hull_area

    return results, front, randoms
