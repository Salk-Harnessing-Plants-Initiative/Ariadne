import networkx as nx
import numpy as np
import random

from bisect import insort


STEINER_MIDPOINTS = 10

DEFAULT_ALPHAS = np.arange(0, 1.01, 0.01)


def get_critical_nodes(G):
    """
    Given a graph G, return a list of its critical nodes (the main root base, which is the first node
    with index 0; and all root tips, which are nodes with degree 1).
    """
    critical_nodes = []
    for i in G.nodes():
        if i == 0 or G.degree(i) == 1:  # assumes root node is 0
            critical_nodes.append(i)

    return critical_nodes


def graph_costs(G, critical_nodes=None):
    """
    Uses a breadth first search to compute the wiring cost and conduction delay of G

    Wiring cost is the total length of the edges in the network

    Conduction delay is the sum of the distances from each point to the root.

    By default, computes conduction delay for all nodes. If you specify a set of critical
    nodes, then only those nodes are used for computing conduction delay
    """
    scost = 0
    mcost = 0

    # dictionary that stores each node's distance to the root
    droot = {}
    # this method assumes node 0 is the root
    root = 0
    # node 1 has distance 0 from the root
    droot[root] = 0

    # dictionary that stores each node's parent in the bfs
    # this way we avoid visiting the same node twice
    parent = {}
    parent[root] = None

    # queue of nodes that have been discovered but not yet visited
    queue = [root]
    visited = set()

    # lists that store the edge lengths and the distances from the nodes to each root
    mcosts = []
    scosts = []
    while len(queue) > 0:
        # visit the next discovered but not yet visited node
        curr = queue.pop(0)

        # if we are trying to  visit an already-visited node, we have a cycle
        if curr in visited:
            return float("inf"), float("inf")

        # we've visited curr
        visited.add(curr)

        # go through curr's children and add the unvisited ones to the queue
        for child in G.neighbors(curr):
            # ignore curr's parent, this was already visited in the bfs
            if child != parent[curr]:
                length = G[curr][child]["weight"]
                mcosts.append(length)

                # to get to the root, the child must go to curr and then to the root
                # thus, child's distance to root = distance from child to curr + distance from curr to root
                child_droot = length + droot[curr]
                droot[child] = child_droot

                # if we have specified a set of critical nodes, only those nodes contribute to conduction delay
                if critical_nodes == None or child in critical_nodes:
                    scosts.append(child_droot)
                parent[child] = curr
                queue.append(child)

    # if not every node was visited, graph is not connected
    assert len(visited) == G.number_of_nodes()

    mcost = sum(sorted(mcosts))
    scost = sum(sorted(scosts))

    return mcost, scost


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


def pareto_cost(mcost, scost, alpha):
    """
    Given a wiring cost, a conduction delay, and alpha, computes the overal pareto cost

    alpha tells us how much to prioritize each objective. If it's 0, we only care about
    conduction delay. If it's 1, we only care about wiring cost

    mcost: the wiring cost (a.k.a. the material cost)
    scost: the conduction delay (a.k.a. the satellite cost)
    """
    assert 0 <= alpha <= 1

    mcost *= alpha
    scost *= 1 - alpha
    cost = mcost + scost
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
    to the root by a direct line
    """

    # assume the root is node 0
    root = 0

    H = nx.Graph()

    H.add_node(root)
    H.nodes[root]["droot"] = 0
    root_pos = G.nodes[root]["pos"]
    H.nodes[root]["pos"] = root_pos

    critical_nodes = get_critical_nodes(G)

    # connect every critical node to the root with a direct edge
    for u in critical_nodes:
        if u == root:
            continue
        H.add_edge(root, u)
        H.nodes[u]["pos"] = G.nodes[u]["pos"]
        H[root][u]["weight"] = node_dist(G, root, u)

    return H


def pareto_steiner_fast(G, alpha):
    """
    Given a graph G and a value 0 <= alpha <= 1, compute the Pareto-optimal tree connecting
    the root to all of the lateral root tips of G

    The algorithm attempts to optimize alpha * D + (1 - alpha) * W

    D is the conduction delay: the sum of the lengths of the shortest paths from every
    lateral root tip to the root

    W is the wiring cost: the total length of the tree

    The algorithm uses a greedy approach: always take the edge that will reduce the
    pareto cost of the tree by the smallest amount
    """
    assert 0 <= alpha <= 1

    # assume the root is node 0
    root = 0

    H = nx.Graph()

    H.add_node(root)
    # every node will keep track of its distance to the root
    H.nodes[root]["droot"] = 0
    root_pos = G.nodes[root]["pos"]
    H.nodes[root]["pos"] = root_pos
    added_nodes = 1

    critical_nodes = get_critical_nodes(G)

    # critical nodes that have currently been added to the tree
    in_nodes = set([root])

    # critical nodes that have not yet been added to the tree
    out_nodes = set(critical_nodes)
    out_nodes.remove(root)

    graph_mcost = 0
    graph_scost = 0

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
    unpaired_nodes = set([root])

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
        best_mcost = None
        best_scost = None
        best_cost = float("inf")

        best_choice = None
        best_midpoint = None

        # go through nodes for which we need to (re)-compute its closest neighbor outside the tree
        for u in unpaired_nodes:
            assert H.has_node(u)
            assert "droot" in H.nodes[u]

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
            length = point_dist(p1, p2)
            mcost = length
            scost = length + H.nodes[u]["droot"]
            cost = pareto_cost(mcost=mcost, scost=scost, alpha=alpha)

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
            assert "droot" in H.nodes[n1]
            H.nodes[n2]["droot"] = node_dist(H, n2, u) + H.nodes[u]["droot"]

        added_nodes += 1
    return H


def pareto_front(G):
    """
    Given a graph G, compute the Pareto front of optimal solutions

    This allows to compare how G was connected and how G could have been connected had it
    been trying to optimize wiring cost and conduction delay
    """

    critical_nodes = get_critical_nodes(G)

    # test: compute the actual mcost, scost for the original plant
    mactual, sactual = graph_costs(G, critical_nodes=critical_nodes)
    actual = (mactual, sactual)

    # dictionary of mcosts, scosts for each alpha value on the front
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
        mcost, scost = graph_costs(H, critical_nodes=critical_nodes)
        front[alpha] = [mcost, scost]

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
