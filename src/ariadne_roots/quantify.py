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
import matplotlib.ticker as ticker



from queue import Queue
from scipy.spatial import ConvexHull  # Import ConvexHull class
from ariadne_roots.pareto_functions import pareto_front, random_tree

try:
    import config
except ImportError:
    # Create a mock config if not available
    class MockConfig:
        length_scale_factor = 1.0
        length_scale_unit = "px"
    config = MockConfig()
    print("Warning: config.py not found, using default scaling (1 px = 1.0 unit)")


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

    
#Scaled plot (px)

def plot_all(front, actual, randoms, mrand, srand, dest, scale_factor, scale_unit):
    #try:
       # import config
       # scale_factor = getattr(config, 'length_scale_factor', 1.0)
        #scale_unit = getattr(config, 'length_scale_unit', 'px')
    #except ImportError:
        #scale_factor = 1.0
        #scale_unit = "px"

    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    def scale_data(data):
        return data * scale_factor
    
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
    for i, (x, y) in enumerate(zip(scaled_randoms_x, scaled_randoms_y)):
        plt.plot(x, y, marker="+", color="green", markersize=2.5, zorder=0.5, markeredgewidth=0.5)

    plt.plot(scaled_front_x, scaled_front_y, marker="s", linestyle="-", markeredgecolor="black")
    plt.plot(scaled_actual_x, scaled_actual_y, marker="x", markersize=12, zorder=3, markeredgewidth=1.5)    
    plt.plot(scaled_mrand, scaled_srand, marker="+", color="red", markersize=12, zorder=3, markeredgewidth=1.5)
    
    ax.set_xlabel(f"Total length ({scale_unit})", fontsize=15)
    ax.set_ylabel(f"Travel distance ({scale_unit})", fontsize=15)

    # Set limits to focus on the relevant area
    front_x_min = min(scaled_front_x)
    front_x_max = max(scaled_front_x)
    front_y_min = min(scaled_front_y)
    front_y_max = max(scaled_front_y)
    
    # Create a bounding box that includes Pareto front and random centroid
    x_min = min(front_x_min, scaled_mrand) * 0.80  # 20% buffer
    x_max = max(front_x_max, scaled_mrand) * 1.2   # 20% buffer
    y_min = min(front_y_min, scaled_srand) * 0.80  # 20% buffer  
    y_max = max(front_y_max, scaled_srand) * 1.20  # 20% buffer
    
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    
    # Save as PNG (
    plt.savefig(dest, bbox_inches="tight", dpi=300)

    # Also save as SVG
    svg_dest = dest.with_suffix('.svg')
    plt.savefig(svg_dest, bbox_inches="tight", format='svg')
    plt.close(fig)


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
# Get scale factor from config
    try:
        import config
        scale_factor = getattr(config, 'length_scale_factor', 1.0)
        scale_unit = getattr(config, 'length_scale_unit', 'px')
    except ImportError:
        scale_factor = 1.0
        scale_unit = "px"

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

     # Calculate the material cost (total root length)
    
    Total_root_length = len_PR + sum(lens_LRs)
  

    # Calculate the ratio of the material cost with the Total minimal Distance
    material_distance_ratio = Total_root_length / total_distance

     # Calculating convex hull area
    points = np.array([H.nodes[node]["pos"] for node in H.nodes()])
    hull = ConvexHull(points)
    convex_hull_area = hull.volume  # Convex hull area in 2D is the same as its volume
    


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
    results["LR angles"] = [angle.item() for angle in angles_LRs] if angles_LRs else []
    results["LR minimal lengths"] = distances_LRs
    results["Barycenter x displacement"]= barycenter_x_displacement
    results["Barycenter y displacement"]= barycenter_y_displacement
    results["Total minimal Distance"] = total_distance  # Add the total distance to the results
    results["Tortuosity"] = material_distance_ratio   
    results["Convex Hull Area"] = convex_hull_area                                 
    
    results["Barycenter x displacement"] = barycenter_x_displacement
    results["Barycenter y displacement"] = barycenter_y_displacement
    results["Total minimal Distance"] = (
        total_distance  # Add the total distance to the results
    )

    # Calculate the material cost (total root length)
    Total_root_length = len_PR + sum(lens_LRs)

    scaled_results = {}
    for key, value in results.items():
        # Don't scale these fields
        if any(excl in key for excl in ["LR density", "alpha", "Mean LR angles", 
                                       "Median LR angles", "LR count", "Branched Zone density", 
                                       "scaling distance to front", "Tortuosity", "scaling (random)"]):
            scaled_results[key] = value
        else:
            try:
                scaled_results[key] = float(value) 
            except (ValueError, TypeError):
                scaled_results[key] = value
    
    return scaled_results, front, randoms




