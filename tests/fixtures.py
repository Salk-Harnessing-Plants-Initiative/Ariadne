import pytest
import json
import numpy as np
import networkx as nx


# ========== Helper Functions ==========


def create_simple_graph(nodes_data, edges_data):
    """Helper function to create a NetworkX graph from node and edge data.

    Args:
        nodes_data: List of tuples (node_id, x, y, lr_index, root_deg)
        edges_data: List of tuples (node1, node2, weight)

    Returns:
        nx.Graph: NetworkX graph with pos, LR_index, and root_deg attributes
    """
    G = nx.Graph()

    # Add nodes with attributes
    for node_id, x, y, lr_index, root_deg in nodes_data:
        G.add_node(node_id, pos=(x, y), LR_index=lr_index, root_deg=root_deg)

    # Add edges with weights
    for node1, node2, weight in edges_data:
        G.add_edge(node1, node2, weight=weight)

    return G


def get_expected_lr_lengths(graph, analyze_func=None):
    """Extract expected lateral root lengths from a graph.

    Args:
        graph: NetworkX graph with LR_index attributes
        analyze_func: Optional analyze function to compute results

    Returns:
        List of lateral root lengths
    """
    if analyze_func is not None:
        results, _, _ = analyze_func(graph)
        return results.get('lr_lengths', [])
    return []


# ========== Minimal Synthetic Fixtures ==========


@pytest.fixture
def simple_linear_graph():
    """Minimal 3-node linear graph: 0 -- 1 -- 2.

    Expected behavior:
    - Node 0 is root (critical node)
    - Node 2 is tip (critical node, degree 1)
    - Total wiring cost: 20.0 (10 + 10)
    - Conduction delay (critical nodes): 20.0 (node 2 distance to base)
    """
    nodes = [
        (0, 0, 0, None, 0),    # Root node at origin
        (1, 10, 0, None, 0),   # Middle node
        (2, 20, 0, None, 0),   # Tip node
    ]
    edges = [
        (0, 1, 10.0),
        (1, 2, 10.0),
    ]
    return create_simple_graph(nodes, edges)


@pytest.fixture
def simple_branching_graph():
    """Minimal 4-node branching graph: 0 -- 1 -- 2
                                            \\-- 3

    Expected behavior:
    - Node 0 is root (critical node)
    - Nodes 2, 3 are tips (critical nodes, degree 1)
    - Total wiring cost: 30.0 (10 + 10 + 10)
    - Conduction delay (critical nodes): 40.0 (node 2: 20, node 3: 20)
    """
    nodes = [
        (0, 0, 0, None, 0),     # Root node at origin
        (1, 10, 0, None, 0),    # Branch point
        (2, 20, 0, None, 0),    # Tip 1
        (3, 10, 10, None, 0),   # Tip 2
    ]
    edges = [
        (0, 1, 10.0),
        (1, 2, 10.0),
        (1, 3, 10.0),
    ]
    return create_simple_graph(nodes, edges)


@pytest.fixture
def simple_lateral_root_graph():
    """5-node graph with one lateral root: PR nodes 0-2, LR nodes 3-4.

    Structure:
        0 (PR) -- 1 (PR) -- 2 (PR)
                  |
                  3 (LR) -- 4 (LR)

    Expected behavior:
    - Primary root: nodes 0, 1, 2 (LR_index=None)
    - Lateral root: nodes 3, 4 (LR_index=0)
    - One lateral root with length ~14.14 (10 + sqrt(2)*3 ≈ 10 + 4.24)
    """
    nodes = [
        (0, 0, 0, None, 0),      # Primary root base
        (1, 10, 0, None, 0),     # Primary root
        (2, 20, 0, None, 0),     # Primary root tip
        (3, 10, 10, 0, 1),       # Lateral root node 1
        (4, 13, 13, 0, 1),       # Lateral root tip
    ]
    edges = [
        (0, 1, 10.0),
        (1, 2, 10.0),
        (1, 3, 10.0),            # LR attachment
        (3, 4, 4.242640687119285),  # sqrt((13-10)^2 + (13-10)^2)
    ]
    return create_simple_graph(nodes, edges)


@pytest.fixture
def edge_case_single_node():
    """Edge case: single node graph (just root)."""
    nodes = [(0, 0, 0, None, 0)]
    edges = []
    return create_simple_graph(nodes, edges)


@pytest.fixture
def edge_case_disconnected():
    """Edge case: disconnected graph (should raise assertion or return inf costs)."""
    nodes = [
        (0, 0, 0, None, 0),
        (1, 10, 0, None, 0),  # Not connected to node 0
    ]
    edges = []
    return create_simple_graph(nodes, edges)


# ========== Real Dataset Fixtures ==========


@pytest.fixture
def plantB_day11_json():
    file_path = "tests/data/_set1_day1_20230509-125420_014_plantB_day11.json"
    return file_path


@pytest.fixture
def plantB_day11_lr_lengths():
    expected_lr_lengths = [
        1299.4431334224817,
        1236.6014320540264,
        1228.5963860520767,
        952.7713742563988,
        879.1183979771527,
        863.5252625696759,
        311.396706279508,
        333.9846140690007,
        360.5595167620837,
        379.49156249870816,
        226.77786080674062,
        212.80744824836734,
        229.14727474598988,
        206.3351185009592,
        98.39719713844252,
        197.03910510337516,
        146.26858189513956,
        44.77722635447622,
        29.154759474226502,
        53.84441020371192,
        88.43348558962596,
        88.78383424258348,
        65.05198917205088,
        53.33854141237835,
    ]
    return expected_lr_lengths


@pytest.fixture
def plantB_day11_lr_angles():
    expected_lr_angles = [
        np.float64(48.81407483429036),
        np.float64(46.63657704161672),
        np.float64(54.6887865603668),
        np.float64(73.49563861824498),
        np.float64(86.63353933657021),
        np.float64(46.16913932790742),
        np.float64(57.9946167919165),
        np.float64(58.3924977537511),
        np.float64(75.96375653207352),
        np.float64(86.63353933657021),
        np.float64(66.03751102542181),
        np.float64(60.64224645720873),
        np.float64(51.14662565964668),
        np.float64(42.70938995736147),
        np.float64(67.06789956241022),
        np.float64(69.86369657175187),
        np.float64(59.34933204294713),
        np.float64(60.57254359681026),
        np.float64(84.0938588862295),
        np.float64(36.86989764584401),
        np.float64(55.885527054658745),
        np.float64(47.91083782616775),
        np.float64(73.49563861824498),
        np.float64(59.58891873287464),
    ]
    return expected_lr_angles


@pytest.fixture
def plantB_day11_lr_minimal_lengths():
    expected_lr_minimal_lengths = [
        1258.3803081739638,
        1205.9029811722003,
        1195.940215897099,
        916.4764044971371,
        848.1945531539329,
        814.5900809609702,
        290.2430016382824,
        316.6591227171578,
        343.9127796404199,
        347.936775865961,
        211.62466774929618,
        208.33866659840174,
        220.1181500921721,
        203.35437049643167,
        97.3498844375277,
        190.370691021491,
        139.84634424968,
        44.77722635447622,
        29.154759474226502,
        53.075418038862395,
        87.78382538941898,
        88.45903006477066,
        64.40496875241847,
        53.33854141237835,
    ]
    return expected_lr_minimal_lengths
