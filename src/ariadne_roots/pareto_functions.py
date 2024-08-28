import networkx as nx
import numpy as np
import random

from bisect import insort


STEINER_MIDPOINTS = 10

DEFAULT_ALPHAS = np.arange(0, 1.01, 0.01)
DEFAULT_BETAS = np.arange(0, 1.01, 0.01)


def get_critical_nodes(G):
    """
    Given a graph G, return a list of its critical nodes (the main root base, which is the first node
    with index 0; and all root tips, which are nodes with degree 1).
    """
    critical_nodes = []
    for i in G.nodes():
        if i == 0 or G.degree(i) == 1:  # assumes root base node is 0
            critical_nodes.append(i)

    return critical_nodes


def graph_costs(G, critical_nodes=None):
    """Use BFS to compute the wiring cost, conduction delay of a graph G.

    Args:
        G (nx.Graph): The graph to compute the costs for
        critical_nodes (list): The list of critical nodes to consider. If None, all
            nodes are considered.

    Returns:
        total_root_length (float): The wiring cost of the graph. Wiring cost is the total length of
            the edges in the network.
        total_travel_distance (float): The conduction delay of the graph. Conduction delay is the sum of
            the distances from each point to the root. By default, computes conduction
            delay for all nodes. If you specify a set of critical nodes, then only those
            nodes are used for computing conduction delay.
    """
    # initialize costs
    total_root_length = 0
    total_travel_distance = 0

    # dictionary that stores each node's distance to the base_node
    distance_to_base = {}
    # this method assumes node 0 is the base_node
    base_node = 0
    # node 1 has distance 0 from the base_node
    distance_to_base[base_node] = 0

    # dictionary that stores each node's parent_node in the bfs
    # this way we avoid visiting the same node twice
    parent_node = {}
    parent_node[base_node] = None

    # nodes_to_visit: nodes that have been discovered but not yet visited
    nodes_to_visit = [base_node]
    visited_nodes = set()

    # lists that store the edge lengths and the distances from the nodes to each base_node
    edge_lengths = []
    travel_distances_to_base = []
    while len(nodes_to_visit) > 0:
        # visit the next discovered but not visited node
        current_node = nodes_to_visit.pop(0)

        # if we are trying to  visit an already-visited node, => we have a cycle
        if current_node in visited_nodes:
            return float("inf"), float("inf")

        # we've visited current_node
        visited_nodes.add(current_node)

        # go through current_node's children and add the unvisited nodes to the nodes_to_visit
        for child_node in G.neighbors(current_node):
            # ignore current_node's parent_node, this was already visited in the bfs
            if child_node != parent_node[current_node]:
                edge_length = G[current_node][child_node]["weight"]
                edge_lengths.append(edge_length)

                # to get to the base_node, the child_node must go to current_node and then to the base_node
                # thus, child_node's distance_to_base = distance from child_node to current_node + distance from current_node to base
                child_distance_to_base = edge_length + distance_to_base[current_node]
                distance_to_base[child_node] = child_distance_to_base

                # if we have specified a set of critical nodes, only those nodes contribute to conduction delay
                if critical_nodes == None or child_node in critical_nodes:
                    travel_distances_to_base.append(child_distance_to_base)
                parent_node[child_node] = current_node
                nodes_to_visit.append(child_node)

    # if not every node was visited, => graph is not connected
    assert len(visited_nodes) == G.number_of_nodes()

    total_root_length = sum(sorted(edge_lengths))
    total_travel_distance = sum(sorted(travel_distances_to_base))

    return total_root_length, total_travel_distance


def slope_vector(p1, p2):
    """
    Given two n-dimensional points, computes the slope m between p1 and p2

    We pick the slope specifically such that p1 = p0 + 1 * m

    This way, for 0 <= t <= 1, p0 + m*t gives us a point on the line segment from p0 to p1

    this is as simple as m = p1 - p0
    """
    # points must have the same dimension
    assert len(p1) == len(p2)

    slope_vec = []
    for i in range(len(p1)):
        slope_vec.append(p2[i] - p1[i])
    return slope_vec


def delta_point(p1, slope, t):
    """
    given a point p0 and a slope vector, computes p0 + t * slope

    works for any dimension
    """
    p2 = []
    assert len(p1) == len(slope)
    for i in range(len(p1)):
        p2.append(p1[i] + t * slope[i])
    return p2


def steiner_points(p1, p2, npoints=10):
    """
    Given two points p1 and p2, this method divides the p1-p2 line segment into several
    line segments.

    This method returns all of the intermediate points along the p1-p2 line

    npoints specifies how many intermediate points to create; the bigger this is, the
    more finely we divide the line segment
    """

    # get the slope such that p2 = p1 + m*t
    # for 0 <= t <= 1 this gives us a point along the p1-p2 line segment
    slope = slope_vector(p1, p2)

    # the more points, the smaller the gap between points
    delta = 1.0 / (npoints + 1)

    # we will vary t between 0 and 1 to get different points along the line segment
    t = delta
    midpoints = []
    while t < 1:
        p3 = delta_point(p1, slope, t)
        midpoints.append(tuple(p3))
        t += delta

    return midpoints


def pareto_cost(total_root_length, total_travel_distance, alpha):
    """
    Given a wiring cost, a conduction delay, and alpha, computes the overal pareto cost

    alpha tells us how much to prioritize each objective. If it's 0, we only care about
    conduction delay. If it's 1, we only care about wiring cost

    total_root_length: the wiring cost (a.k.a. the material cost)
    total_travel_distance: the conduction delay (a.k.a. the satellite cost)
    """
    assert 0 <= alpha <= 1

    total_root_length *= alpha
    total_travel_distance *= 1 - alpha
    cost = total_root_length + total_travel_distance
    return cost


def pareto_cost_3d_path_tortuosity(total_root_length, total_travel_distance, total_path_coverage, alpha, beta):
    """
    Computes the pareto cost.

    alpha * total_root_length + beta * total_travel_distance - gamma * total_path_coverage

    alpha + beta + gamma = 1

    When alpha = beta = 0, gamma = 1 => cost = -total_path_coverage will be minimized =>
        total_path_coverage will be maximized
    When alpha = gamma = 0, beta = 1 => cost = total_travel_distance will be minimized
    When beta = gamma = 0, alpha = 1 => cost = total_root_length will be minimized

    total_root_length: the sum of the lengths of the edges in the root network 
        (a.k.a. material cost, wiring cost)
    total_travel_distance: the sum of the lengths of the shortest paths from every
        lateral root tip to the base node of the network. (a.k.a. the satellite cost, 
        conduction delay)
    total_path_coverage: the sum of the tortuosity of all the root paths. The tortuosity per 
        path is defined as the ratio of the actual path length to the shortest path 
        length between the root and the root tip. The total root coverage is the sum of 
        the tortuosity of all the root paths.
    """
    assert 0 <= alpha <= 1
    assert 0 <= beta <= 1

    gamma = 1 - alpha - beta
    cost = alpha * total_root_length + beta * total_travel_distance - gamma * total_path_coverage

    return cost


def point_dist(p1, p2):
    """
    Euclidean distance between two different points (of any dimension)
    """
    assert len(p1) == len(p2)
    sq_dist = 0
    for i in range(len(p1)):
        x1, x2 = p1[i], p2[i]
        sq_dist += (x1 - x2) ** 2
    return sq_dist**0.5


def node_dist(G, u, v):
    """
    Gets the euclidean distance between two different nodes in a graph

    Assumes each node has an attribute 'pos' corresponding to its coordinate
    """
    p1 = G.nodes[u]["pos"]
    p2 = G.nodes[v]["pos"]
    return point_dist(p1, p2)


def k_nearest_neighbors(G, u, k=None, candidate_nodes=None):
    """
    Given a graph G and a node u, this method gets u's closest neighbors in G

    The closest neighbors are determined using the euclidean distance between the nodes

    if candidate_nodes is given, the method only considers the closest neighbor out of the candida
    """
    if candidate_nodes == None:
        candidate_nodes = list(G.nodes())

    if u in candidate_nodes:
        candidate_nodes.remove(u)

    nearest_neighbors = sorted(candidate_nodes, key=lambda v: node_dist(G, u, v))
    if k != None:
        assert type(k) == int
        nearest_neighbors = nearest_neighbors[:k]
    return nearest_neighbors


def satellite_tree(G):
    """
    Constructs the satellite tree out of G; this is a graph in which every node is connected
    to the root base by a direct line
    """

    # assume the _node is node 0
    base_node = 0

    H = nx.Graph()

    H.add_node(base_node)
    H.nodes[base_node]["distance_to_base"] = 0
    base_pos = G.nodes[base_node]["pos"]
    H.nodes[base_node]["pos"] = base_pos

    critical_nodes = get_critical_nodes(G)

    # connect every critical node to the base_node with a direct edge
    for u in critical_nodes:
        if u == base_node:
            continue
        H.add_edge(base_node, u)
        H.nodes[u]["pos"] = G.nodes[u]["pos"]
        H[base_node][u]["weight"] = node_dist(G, base_node, u)

    return H


def pareto_steiner_fast(G, alpha):
    """
    Given a graph G and a value 0 <= alpha <= 1, compute the Pareto-optimal tree connecting
    the root base_node to all of the lateral root tips of G

    The algorithm attempts to optimize alpha * D + (1 - alpha) * W

    D is the conduction delay: the sum of the lengths of the shortest paths from every
    lateral root tip to the root base_node of the network

    W is the wiring cost: the total length of the tree

    The algorithm uses a greedy approach: always take the edge that will reduce the
    pareto cost of the tree by the smallest amount
    """
    assert 0 <= alpha <= 1

    # assume the base_node is node 0
    base_node = 0

    H = nx.Graph()

    H.add_node(base_node)
    # every node will keep track of its distance to the base_node
    H.nodes[base_node]["distance_to_base"] = 0
    base_pos = G.nodes[base_node]["pos"]
    H.nodes[base_node]["pos"] = base_pos
    added_nodes = 1

    critical_nodes = get_critical_nodes(G)

    # critical nodes that have currently been added to the tree
    in_nodes = set([base_node])

    # critical nodes that have not yet been added to the tree
    out_nodes = set(critical_nodes)
    out_nodes.remove(base_node)

    graph_total_root_length = 0
    graph_total_travel_distance = 0

    """
    closest_neighbors is a dictionary. The keys are nodes that are currently in the tree.
    The value associated with each node u is list of nodes that need to  be added to the
    tree, sorted in order of how close each node is to u.
    """
    closest_neighbors = {}
    for u in critical_nodes:
        closest_neighbors[u] = k_nearest_neighbors(
            G, u, k=None, candidate_nodes=critical_nodes[:]
        )

    """
    unpaired_nodes contains the set of nodes for which we need to (re)-compute the closest
    node that has not been added to the tree.
    """
    unpaired_nodes = set([base_node])

    # keeps track of what the id of the next node added to the tree should be.
    node_index = max(critical_nodes) + 1

    steps = 0

    """
    The optimization this algorithm performs is that we don't need to consider every
    combination (u, v) where u is in the tree and v is not in the tree. We only need to
    consider combinations where u is in the tree, and v is the closest node to u that has
    not been added to the  tree. This is because any other combination would never be the
    optimal greedy choice.

    best_edges stores all of these potentially optimal edges to add
    """
    best_edges = []

    while added_nodes < len(critical_nodes):
        assert len(out_nodes) > 0
        best_edge = None
        best_total_root_length = None
        best_total_travel_distance = None
        best_cost = float("inf")

        best_choice = None
        best_midpoint = None

        # go through nodes for which we need to (re)-compute its closest neighbor outside the tree
        for u in unpaired_nodes:
            assert H.has_node(u)
            assert "distance_to_base" in H.nodes[u]

            invalid_neighbors = []
            closest_neighbor = None
            """
            Go through u's closest neighbors and find the closest one that has not been
            added to the tree
            """
            for i in range(len(closest_neighbors[u])):
                v = closest_neighbors[u][i]
                if H.has_node(v):
                    invalid_neighbors.append(v)
                else:
                    # once we find the closest neighbor not in the tree,
                    closest_neighbor = v
                    break

            """
            if any of the closest neighbors are no longer valid partners, remove them from
            the list of closest neighbors
            """
            for invalid_neighbor in invalid_neighbors:
                closest_neighbors[u].remove(invalid_neighbor)

            assert closest_neighbor != None
            assert not H.has_node(closest_neighbor)

            p1 = H.nodes[u]["pos"]
            p2 = G.nodes[closest_neighbor]["pos"]

            # compute hypothetical cost of connecting u to its closest neighbor
            edge_length = point_dist(p1, p2)
            total_root_length = edge_length
            total_travel_distance = edge_length + H.nodes[u]["distance_to_base"]
            cost = pareto_cost(
                total_root_length=total_root_length,
                total_travel_distance=total_travel_distance,
                alpha=alpha,
            )

            # add this candidate edge to the list of best edges
            # insort maintains the list in sorted order based on cost
            insort(best_edges, (cost, u, closest_neighbor))

        # We will add the candidate edge with the smallest cost
        # because we maintained these edges in sorted order, it's O(1) to get the next edge to add
        cost, u, v = best_edges.pop(0)

        # go through all the candidate edges and see which ones are no longer valid
        best_edges2 = []
        # u and v are now unpaired, we need to find their respective closest neighbors outside of the tree
        unpaired_nodes = set([u, v])
        for cost, x, y in best_edges:
            # if another node had v as its closet neighbor, we need to find its next-closest neighbor going forward
            if y == v:
                unpaired_nodes.add(x)
            else:
                best_edges2.append((cost, x, y))
        best_edges = best_edges2

        assert H.has_node(u)
        assert not H.has_node(v)
        H.add_node(v)
        H.nodes[v]["pos"] = G.nodes[v]["pos"]
        # v is now in the tree, not outside the tree
        in_nodes.add(v)
        out_nodes.remove(v)

        # connect u to v, adding several midpoints along the way
        p1 = H.nodes[u]["pos"]
        p2 = H.nodes[v]["pos"]
        midpoints = steiner_points(p1, p2, npoints=STEINER_MIDPOINTS)
        midpoint_nodes = []

        # add a new node for every midpoint being added along the u-v line segment
        for midpoint in midpoints:
            midpoint_node = node_index
            node_index += 1
            H.add_node(midpoint_node)
            H.nodes[midpoint_node]["pos"] = midpoint

            # get the distance from the midpoint  to all nodes that need to be added to t he tree
            neighbors = []
            for out_node in out_nodes:
                out_coord = G.nodes[out_node]["pos"]
                dist = point_dist(midpoint, out_coord)
                neighbors.append((dist, out_node))

            # add the newly-added midpoint node to closest_neighbors
            neighbors = sorted(neighbors)
            closest_neighbors[midpoint_node] = []
            for dist, neighbor in neighbors:
                closest_neighbors[midpoint_node].append(neighbor)

            midpoint_nodes.append(midpoint_node)

            # midpoint_node is unpaired, we need to add it to the candidate edges in the next iteration
            unpaired_nodes.add(midpoint_node)

        # connect all of the points in the line segment: u, v, and all the nodes in between
        line_nodes = [v] + list(reversed(midpoint_nodes)) + [u]
        for i in range(-1, -len(line_nodes), -1):
            n1 = line_nodes[i]
            n2 = line_nodes[i - 1]
            H.add_edge(n1, n2)
            H[n1][n2]["weight"] = node_dist(H, n1, n2)
            assert "distance_to_base" in H.nodes[n1]
            H.nodes[n2]["distance_to_base"] = (
                node_dist(H, n2, u) + H.nodes[u]["distance_to_base"]
            )

        added_nodes += 1
    return H


def pareto_steiner_fast_3d_path_tortuosity(G, alpha, beta):
    """
    Given a graph G and a value 0 <= {alpha, beta} <= 1, compute the Pareto-optimal tree
    connecting the base node to all of the lateral root tips of G.

    cost = alpha * total_root_length + beta * total_travel_distance - gamma * total_path_coverage

    alpha + beta + gamma = 1

    When alpha = beta = 0, gamma = 1 => cost = -total_path_coverage will be minimized =>
        total_path_coverage will be maximized
    When alpha = gamma = 0, beta = 1 => cost = total_travel_distance will be minimized
    When beta = gamma = 0, alpha = 1 => cost = total_root_length will be minimized

    total_root_length: the sum of the lengths of the edges in the root network 
        (a.k.a. material cost, wiring cost)
    total_travel_distance: the sum of the lengths of the shortest paths from every
        lateral root tip to the base node of the network. (a.k.a. the satellite cost, 
        conduction delay)
    total_path_coverage: the sum of the tortuosity of all the root paths. The tortuosity per 
        path is defined as the ratio of the actual path length to the shortest path 
        length between the root and the root tip. The total root coverage is the sum of 
        the tortuosity of all the root paths.

    The algorithm uses a greedy approach: always take the edge that will reduce the
    pareto cost of the tree by the smallest amount
    """
    assert 0 <= alpha <= 1
    assert 0 <= beta <= 1

    # assume the base_node is node 0
    base_node = 0

    H = nx.Graph()

    H.add_node(base_node)
    # every node will keep track of its distance to the base
    H.nodes[base_node]["distance_to_base"] = 0
    base_pos = G.nodes[base_node]["pos"]
    H.nodes[base_node]["pos"] = base_pos
    added_nodes = 1

    # every node will keep track of the shortest path to the base_node
    H.nodes[base_node]["straight_distance_to_base"] = 0

    critical_nodes = get_critical_nodes(G)

    # critical nodes that have currently been added to the tree
    in_nodes = set([base_node])

    # critical nodes that have not yet been added to the tree
    out_nodes = set(critical_nodes)
    out_nodes.remove(base_node)

    graph_total_root_length = 0
    graph_total_travel_distance = 0

    """
    closest_neighbors is a dictionary. The keys are nodes that are currently in the tree.
    The value associated with each node u is list of nodes that need to  be added to the
    tree, sorted in order of how close each node is to u.
    """
    closest_neighbors = {}
    for u in critical_nodes:
        closest_neighbors[u] = k_nearest_neighbors(
            G, u, k=None, candidate_nodes=critical_nodes[:]
        )

    """
    unpaired_nodes contains the set of nodes for which we need to (re)-compute the closest
    node that has not been added to the tree.
    """
    unpaired_nodes = set([base_node])

    # keeps track of what the id of the next node added to the tree should be.
    node_index = max(critical_nodes) + 1

    steps = 0

    """
    The optimization this algorithm performs is that we don't need to consider every
    combination (u, v) where u is in the tree and v is not in the tree. We only need to
    consider combinations where u is in the tree, and v is the closest node to u that has
    not been added to the  tree. This is because any other combination would never be the
    optimal greedy choice.

    best_edges stores all of these potentially optimal edges to add
    """
    best_edges = []

    while added_nodes < len(critical_nodes):
        assert len(out_nodes) > 0
        best_edge = None
        best_total_root_length = None
        best_total_travel_distance = None
        best_cost = float("inf")

        best_choice = None
        best_midpoint = None

        # go through nodes for which we need to (re)-compute its closest neighbor outside the tree
        for u in unpaired_nodes:
            assert H.has_node(u)
            assert "distance_to_base" in H.nodes[u]

            invalid_neighbors = []
            closest_neighbor = None
            """
            Go through u's closest neighbors and find the closest one that has not been
            added to the tree
            """
            for i in range(len(closest_neighbors[u])):
                v = closest_neighbors[u][i]
                if H.has_node(v):
                    invalid_neighbors.append(v)
                else:
                    # once we find the closest neighbor not in the tree,
                    closest_neighbor = v
                    break

            """
            if any of the closest neighbors are no longer valid partners, remove them from
            the list of closest neighbors
            """
            for invalid_neighbor in invalid_neighbors:
                closest_neighbors[u].remove(invalid_neighbor)

            assert closest_neighbor != None
            assert not H.has_node(closest_neighbor)

            p1 = H.nodes[u]["pos"]
            p2 = G.nodes[closest_neighbor]["pos"]

            # compute hypothetical cost of connecting u to its closest neighbor
            edge_length = point_dist(p1, p2)
            total_root_length = edge_length
            total_travel_distance = edge_length + H.nodes[u]["distance_to_base"]
            total_path_coverage = total_travel_distance / point_dist(base_pos, p2)
            cost = pareto_cost_3d_path_tortuosity(
                total_root_length=total_root_length,
                total_travel_distance=total_travel_distance,
                total_path_coverage=total_path_coverage,
                alpha=alpha,
                beta=beta,
            )

            # add this candidate edge to the list of best edges
            # insort maintains the list in sorted order based on cost
            insort(best_edges, (cost, u, closest_neighbor))

        # We will add the candidate edge with the smallest cost
        # because we maintained these edges in sorted order, it's O(1) to get the next edge to add
        cost, u, v = best_edges.pop(0)

        # go through all the candidate edges and see which ones are no longer valid
        best_edges2 = []
        # u and v are now unpaired, we need to find their respective closest neighbors outside of the tree
        unpaired_nodes = set([u, v])
        for cost, x, y in best_edges:
            # if another node had v as its closet neighbor, we need to find its next-closest neighbor going forward
            if y == v:
                unpaired_nodes.add(x)
            else:
                best_edges2.append((cost, x, y))
        best_edges = best_edges2

        assert H.has_node(u)
        assert not H.has_node(v)
        H.add_node(v)
        H.nodes[v]["pos"] = G.nodes[v]["pos"]
        # v is now in the tree, not outside the tree
        in_nodes.add(v)
        out_nodes.remove(v)

        # connect u to v, adding several midpoints along the way
        p1 = H.nodes[u]["pos"]
        p2 = H.nodes[v]["pos"]
        midpoints = steiner_points(p1, p2, npoints=STEINER_MIDPOINTS)
        midpoint_nodes = []

        # add a new node for every midpoint being added along the u-v line segment
        for midpoint in midpoints:
            midpoint_node = node_index
            node_index += 1
            H.add_node(midpoint_node)
            H.nodes[midpoint_node]["pos"] = midpoint

            # get the distance from the midpoint  to all nodes that need to be added to t he tree
            neighbors = []
            for out_node in out_nodes:
                out_coord = G.nodes[out_node]["pos"]
                dist = point_dist(midpoint, out_coord)
                neighbors.append((dist, out_node))

            # add the newly-added midpoint node to closest_neighbors
            neighbors = sorted(neighbors)
            closest_neighbors[midpoint_node] = []
            for dist, neighbor in neighbors:
                closest_neighbors[midpoint_node].append(neighbor)

            midpoint_nodes.append(midpoint_node)

            # midpoint_node is unpaired, we need to add it to the candidate edges in the next iteration
            unpaired_nodes.add(midpoint_node)

        # connect all of the points in the line segment: u, v, and all the nodes in between
        line_nodes = [v] + list(reversed(midpoint_nodes)) + [u]
        for i in range(-1, -len(line_nodes), -1):
            n1 = line_nodes[i]
            n2 = line_nodes[i - 1]
            H.add_edge(n1, n2)
            H[n1][n2]["weight"] = node_dist(H, n1, n2)
            assert "distance_to_base" in H.nodes[n1]
            H.nodes[n2]["distance_to_base"] = (
                node_dist(H, n2, u) + H.nodes[u]["distance_to_base"]
            )
            H.nodes[n2]["straight_distance_to_base"] = H.nodes[n2]["distance_to_base"] / node_dist(H, n2, base_node)

        added_nodes += 1
    return H


def pareto_front(G):
    """
    Given a graph G, compute the Pareto front of optimal solutions

    This allows to compare how G was connected and how G could have been connected had it
    been trying to optimize wiring cost and conduction delay
    """

    critical_nodes = get_critical_nodes(G)

    # test: compute the actual total_root_length, total_travel_distance for the original plant
    mactual, sactual = graph_costs(G, critical_nodes=critical_nodes)
    actual = (mactual, sactual)

    # dictionary of edge_lengths, travel_distances_to_base for each alpha value on the front
    front = {}

    for alpha in DEFAULT_ALPHAS:
        H = None
        # if alpha = 0 compute the satellite tree in linear time
        if alpha == 0:
            H = satellite_tree(G)
        else:
            H = pareto_steiner_fast(G, alpha)

        # compute the wiring cost and conduction delay
        # only the original critical nodes contribute to conduction delay
        total_root_length, total_travel_distance = graph_costs(
            H, critical_nodes=critical_nodes
        )
        front[alpha] = [total_root_length, total_travel_distance]

    return front, actual


def random_tree(G):
    """
    Given a graph G, compute 1000 random spanning trees as in Conn et al. 2017.
    Only consider the critical nodes (and root node) of G.
    """
    random.seed(a=None)
    random_trees = []  # list of 1000 random trees
    costs = []

    for i in range(1000):  # 1000 random trees
        # instantiate random tree
        R = nx.Graph()
        G_critical_nodes = get_critical_nodes(G)

        while len(G_critical_nodes) > 0:
            # randomly draw 1 node from G's critical nodes
            index = random.randrange(len(G_critical_nodes))
            g = G_critical_nodes[index]

            if len(R.nodes) > 0:  # if R is not empty
                # add the new point AND a random edge
                r_index = random.randrange(len(R.nodes))  # get a random node from R
                r = list(R.nodes)[r_index]
                R.add_node(g, pos=G.nodes.data()[g]["pos"])
                R.add_edge(r, g, weight=node_dist(R, r, g))

            else:  # if R is empty
                # add the new point
                R.add_node(g, pos=G.nodes.data()[g]["pos"])

            # remove added node from candidate list and repeat
            del G_critical_nodes[index]

        random_trees.append(R)

    for R in random_trees:
        # compute costs for each R, to compare with G
        mactual, sactual = graph_costs(R)
        costs.append((mactual, sactual))

    return costs
