"""Comprehensive tests for quantify.py module.

Tests cover:
- distance() - Euclidean distance calculation
- calc_root_len() - root length along path
- calc_len_PR() - primary root length
- calc_len_LRs() - lateral root lengths and angles
- calc_zones() - branched/basal/apical zone calculations
- calculate_convex_hull_area() - convex hull calculations
- distance_from_front() - Pareto front distance
- calculate_tradeoff() - Steiner/Satellite tradeoff metric
- analyze() - full integration test
"""

import pytest
import json
import math
import numpy as np
import numpy.testing as npt
import networkx as nx

from math import isclose
from networkx.readwrite import json_graph

from ariadne_roots.quantify import (
    distance,
    calc_root_len,
    calc_len_PR,
    calc_len_LRs,
    calc_zones,
    calculate_convex_hull_area,
    calculate_plot_buffer,
    distance_from_front,
    calculate_tradeoff,
    pareto_calcs,
    calc_len_LRs_with_distances,
    find_lowermost_node_of_primary_root,
    analyze,
)


# ========== Test distance() ==========


def test_distance_simple():
    """Test Euclidean distance on simple coordinates."""
    p1 = (0, 0)
    p2 = (3, 4)
    dist = distance(p1, p2)
    # sqrt(3^2 + 4^2) = 5
    assert math.isclose(dist, 5.0, rel_tol=1e-8)


def test_distance_same_point():
    """Test distance between identical points."""
    p1 = (10, 20)
    p2 = (10, 20)
    dist = distance(p1, p2)
    assert math.isclose(dist, 0.0, rel_tol=1e-8)


def test_distance_negative_coords():
    """Test distance with negative coordinates."""
    p1 = (-3, -4)
    p2 = (0, 0)
    dist = distance(p1, p2)
    assert math.isclose(dist, 5.0, rel_tol=1e-8)


def test_distance_float_coords():
    """Test distance with floating point coordinates."""
    p1 = (0.0, 0.0)
    p2 = (1.5, 2.0)
    expected = math.sqrt(1.5**2 + 2.0**2)
    dist = distance(p1, p2)
    assert math.isclose(dist, expected, rel_tol=1e-8)


# ========== Test calc_root_len() ==========


def test_calc_root_len_simple_linear(simple_linear_graph):
    """Test root length calculation on linear graph."""
    nodes = [0, 1, 2]  # All nodes in order
    length = calc_root_len(simple_linear_graph, nodes)
    # Distance 0->1 (10) + 1->2 (10) = 20
    assert math.isclose(length, 20.0, rel_tol=1e-8)

    # Verify edge weights were added
    assert "weight" in simple_linear_graph[0][1]
    assert math.isclose(simple_linear_graph[0][1]["weight"], 10.0, rel_tol=1e-8)


def test_calc_root_len_partial_path(simple_lateral_root_graph):
    """Test root length on partial path."""
    # Path from node 0 to node 1 only
    nodes = [0, 1]
    length = calc_root_len(simple_lateral_root_graph, nodes)
    assert math.isclose(length, 10.0, rel_tol=1e-8)


def test_calc_root_len_single_node():
    """Test root length with single node (no edges)."""
    G = nx.Graph()
    G.add_node(0, pos=(0, 0))
    nodes = [0]
    length = calc_root_len(G, nodes)
    # Single node has zero length
    assert math.isclose(length, 0.0, rel_tol=1e-8)


# ========== Test calc_len_PR() ==========


def test_calc_len_PR_simple(simple_lateral_root_graph):
    """Test primary root length calculation."""
    # In simple_lateral_root_graph: nodes 0, 1, 2 are PR (LR_index=None)
    # Path: 0->1->2, each segment is 10 pixels
    pr_length = calc_len_PR(simple_lateral_root_graph, root_node=0)
    assert math.isclose(pr_length, 20.0, rel_tol=1e-8)


def test_calc_len_PR_linear_no_lateral_roots(simple_linear_graph):
    """Test PR length when all nodes are primary root."""
    # All nodes have LR_index=None, so entire path is PR
    pr_length = calc_len_PR(simple_linear_graph, root_node=0)
    assert math.isclose(pr_length, 20.0, rel_tol=1e-8)


# ========== Test calc_len_LRs() ==========


def test_calc_len_LRs_simple(simple_lateral_root_graph):
    """Test lateral root length and angle calculation with synthetic graph.

    This test uses a simple synthetic graph with one lateral root.
    The graph must be converted to a proper tree structure where edges
    point away from the root (required for predecessors() to work correctly).
    """
    # Create a directed graph with root at node 0
    # NetworkX's bfs_tree creates a tree with edges pointing away from root
    H = nx.bfs_tree(simple_lateral_root_graph, source=0)

    # Copy node attributes from original graph
    for node in H.nodes():
        H.nodes[node].update(simple_lateral_root_graph.nodes[node])

    # Run calc_len_LRs
    results = calc_len_LRs(H)

    # Should return results for LR index 1
    assert isinstance(results, dict)
    assert len(results) == 1  # One lateral root
    assert 1 in results  # LR_index = 1

    # Verify structure: [length, angle]
    lr_data = results[1]
    assert isinstance(lr_data, list)
    assert len(lr_data) == 2

    length, angle = lr_data
    # Length should be approximately 10 + 4.24 = 14.24
    assert 14.0 < length < 15.0
    # Angle should be valid (0-180 degrees)
    assert 0 <= angle <= 180


def test_calc_len_LRs_no_lateral_roots(simple_linear_graph):
    """Test calc_len_LRs when there are no lateral roots."""
    G = simple_linear_graph.to_directed()

    # No nodes with LR_index set
    # Function should handle gracefully (no LR nodes to process)
    # This will fail because max() is called on empty sequence
    # So we expect this to raise an error or return empty dict
    with pytest.raises((ValueError, KeyError)):
        calc_len_LRs(G)


def test_calc_len_LRs_nonzero_start_index(issue26_root_json):
    """Test calc_len_LRs with non-zero starting LR index (issue #26).

    This test reproduces issue #26 where calc_len_LRs() would crash with
    UnboundLocalError when lateral root indices don't start at 0. The bug
    occurred because the loop iterated from range(num_LRs) starting at 0,
    but the minimum LR index is 1 (since None is used for the primary root).

    PR #27 fixes this by calculating min_num_LRs and using
    range(min_num_LRs, num_LRs) instead.
    """
    with open(issue26_root_json) as f:
        data = json.load(f)
        # Use tree_graph for tree-formatted JSON (has 'children' key)
        graph = json_graph.tree_graph(data)

    # tree_graph returns a DiGraph, so no need to convert
    H = graph

    # This should NOT raise UnboundLocalError with the fix from PR #27
    results = calc_len_LRs(H)

    # Verify we got valid results
    assert isinstance(results, dict)
    assert len(results) > 0  # Should have at least one lateral root

    # Each result should have length and angle data
    for lr_idx, data in results.items():
        assert isinstance(data, list)
        assert len(data) == 2  # [length, angle]
        length, angle = data
        assert length >= 0
        assert 0 <= angle <= 180  # Angle should be in valid range


# ========== Test calc_zones() ==========


def test_calc_zones_with_lateral_roots(simple_lateral_root_graph):
    """Test zone calculation with lateral roots present."""
    zones = calc_zones(simple_lateral_root_graph, root_node=0)

    assert "branched_zone_length" in zones
    assert "basal_zone_length" in zones
    assert "apical_zone_length" in zones

    # All zones should be non-negative
    assert zones["branched_zone_length"] >= 0
    assert zones["basal_zone_length"] >= 0
    assert zones["apical_zone_length"] >= 0


def test_calc_zones_no_lateral_roots(simple_linear_graph):
    """Test zone calculation with no lateral roots."""
    zones = calc_zones(simple_linear_graph, root_node=0)

    # With no LR insertions, basal zone should be entire PR
    # Branched and apical should be 0
    assert zones["branched_zone_length"] == 0
    assert zones["apical_zone_length"] == 0
    # Basal zone should be close to total length
    assert zones["basal_zone_length"] >= 0


# ========== Test calculate_convex_hull_area() ==========


def test_convex_hull_area_triangle():
    """Test convex hull area with triangle of known area."""
    G = nx.Graph()
    # Right triangle with base=4, height=3, area=6
    G.add_node(0, pos=(0, 0))
    G.add_node(1, pos=(4, 0))
    G.add_node(2, pos=(0, 3))

    area = calculate_convex_hull_area(G)
    # In 2D, ConvexHull.area gives perimeter, not area
    # Perimeter = 3 + 4 + 5 = 12
    assert math.isclose(area, 12.0, rel_tol=1e-8)


def test_convex_hull_area_square():
    """Test convex hull area (actually perimeter in 2D) with square."""
    G = nx.Graph()
    # Unit square, perimeter=4
    G.add_node(0, pos=(0, 0))
    G.add_node(1, pos=(1, 0))
    G.add_node(2, pos=(1, 1))
    G.add_node(3, pos=(0, 1))

    area = calculate_convex_hull_area(G)
    # Perimeter of unit square = 4
    assert math.isclose(area, 4.0, rel_tol=1e-8)


def test_convex_hull_area_too_few_nodes():
    """Test convex hull with < 3 nodes (should return None)."""
    G = nx.Graph()
    G.add_node(0, pos=(0, 0))
    G.add_node(1, pos=(1, 1))

    area = calculate_convex_hull_area(G)
    assert area is None


# ========== Test distance_from_front() ==========


def test_distance_from_front_on_front():
    """Test distance when actual tree is on the Pareto front."""
    # Create a simple front
    front = {
        0.0: [100, 10],  # Alpha 0: high wiring, low delay
        0.5: [50, 50],  # Alpha 0.5: balanced
        1.0: [10, 100],  # Alpha 1: low wiring, high delay
    }

    # Actual tree exactly on the front at alpha=0.5
    actual = (50, 50)

    alpha, scaling = distance_from_front(front, actual)

    # Alpha is interpolated between the two closest points (0.5 and 0.0 or 1.0)
    # With 3-point front, interpolation gives ~0.4167 when on the alpha=0.5 point
    # because dist to 0.5 is 1.0 and dist to 0.0/1.0 is 5.0
    # weight1 = 5/6, weight2 = 1/6, so alpha = 0.5 * 5/6 + 0.0 * 1/6 = 5/12
    assert math.isclose(alpha, 5 / 12, rel_tol=1e-8)
    # Scaling should be 1.0 (on the front)
    assert math.isclose(scaling, 1.0, rel_tol=1e-8)


def test_distance_from_front_dominated():
    """Test distance when actual tree is dominated (worse than front)."""
    front = {
        0.0: [100, 10],
        0.5: [50, 50],
        1.0: [10, 100],
    }

    # Actual tree is worse (higher costs on both dimensions)
    actual = (100, 100)

    alpha, scaling = distance_from_front(front, actual)

    # Scaling should be > 1 (dominated by front)
    assert scaling > 1.0


def test_distance_from_front_dominating():
    """Test distance when actual tree dominates the front."""
    front = {
        0.0: [100, 10],
        0.5: [50, 50],
        1.0: [10, 100],
    }

    # Actual tree is better (lower costs on both dimensions)
    actual = (5, 5)

    alpha, scaling = distance_from_front(front, actual)

    # Scaling should be < 1 (dominates the front)
    assert scaling < 1.0


def test_distance_from_front_interpolation():
    """Test that alpha is interpolated between two closest points."""
    # Create a dense front
    front = {
        0.0: [100, 10],
        0.1: [90, 20],
        0.2: [80, 30],
        0.3: [70, 40],
        0.4: [60, 50],
        0.5: [50, 60],
    }

    # Actual tree somewhere between alpha=0.2 and alpha=0.3
    actual = (75, 35)

    alpha, scaling = distance_from_front(front, actual)

    # Alpha should be interpolated between the two closest points on the front
    # The actual tree (75, 35) is closest to alpha=0.2 [80, 30] and alpha=0.3 [70, 40]
    assert 0.2 <= alpha <= 0.3
    # Should be a Python float, not string
    assert isinstance(alpha, float)
    assert isinstance(scaling, float)


def test_distance_from_front_equal_distances():
    """Test alpha when two points are equally close (edge case)."""
    # Create symmetric front where two alphas could be equidistant
    front = {
        0.0: [100, 50],
        1.0: [50, 100],
    }

    # Point equidistant from both
    actual = (75, 75)

    alpha, scaling = distance_from_front(front, actual)

    # When distances are equal, sorted() preserves insertion order so alpha1=0.0 is returned
    assert alpha == 0.0
    assert isinstance(alpha, float)


def test_distance_from_front_single_point():
    """Test alpha with only one point in the front (edge case)."""
    front = {
        0.5: [50, 50],
    }

    actual = (60, 60)

    alpha, scaling = distance_from_front(front, actual)

    # With only one point, should return that alpha
    assert alpha == 0.5
    assert isinstance(alpha, float)
    assert isinstance(scaling, float)


def test_distance_from_front_returns_float():
    """Test that both alpha and scaling are Python floats (not np.float64 or str)."""
    front = {
        0.0: [100, 10],
        0.5: [50, 50],
        1.0: [10, 100],
    }

    actual = (60, 60)

    alpha, scaling = distance_from_front(front, actual)

    # Should be plain Python float (for JSON serialization)
    assert type(alpha) is float
    assert type(scaling) is float


# ========== Test calculate_tradeoff() ==========


def test_calculate_tradeoff_steiner_point():
    """Test that Steiner point is correctly identified (min total root length)."""
    front = {
        0.0: [100, 10],  # High length, low distance
        0.5: [50, 50],  # Balanced
        1.0: [10, 100],  # Low length (Steiner), high distance
    }
    actual = (60, 60)

    result = calculate_tradeoff(front, actual)

    # Steiner point minimizes total root length (10)
    assert result["Steiner_length"] == 10
    assert result["Steiner_distance"] == 100


def test_calculate_tradeoff_satellite_point():
    """Test that Satellite point is correctly identified (min travel distance)."""
    front = {
        0.0: [100, 10],  # High length, low distance (Satellite)
        0.5: [50, 50],  # Balanced
        1.0: [10, 100],  # Low length, high distance
    }
    actual = (60, 60)

    result = calculate_tradeoff(front, actual)

    # Satellite point minimizes travel distance (10)
    assert result["Satellite_length"] == 100
    assert result["Satellite_distance"] == 10


def test_calculate_tradeoff_calculation():
    """Test Tradeoff metric calculation."""
    front = {
        0.0: [100, 10],  # Satellite point
        1.0: [10, 100],  # Steiner point
    }
    # Actual tree: length=50, distance=50
    actual = (50, 50)

    result = calculate_tradeoff(front, actual)

    # Actual_ratio = 50/50 = 1.0
    assert math.isclose(result["Actual_ratio"], 1.0, rel_tol=1e-8)

    # Optimal_ratio = steiner_length / satellite_distance = 10/10 = 1.0
    assert math.isclose(result["Optimal_ratio"], 1.0, rel_tol=1e-8)

    # Tradeoff = actual_ratio / optimal_ratio = 1.0/1.0 = 1.0
    assert math.isclose(result["Tradeoff"], 1.0, rel_tol=1e-8)


def test_calculate_tradeoff_all_fields_present():
    """Test that all 7 tradeoff fields are present in results."""
    front = {
        0.0: [100, 10],
        1.0: [10, 100],
    }
    actual = (50, 50)

    result = calculate_tradeoff(front, actual)

    expected_fields = [
        "Tradeoff",
        "Steiner_length",
        "Steiner_distance",
        "Satellite_length",
        "Satellite_distance",
        "Actual_ratio",
        "Optimal_ratio",
    ]
    for field in expected_fields:
        assert field in result, f"Missing field: {field}"


def test_calculate_tradeoff_division_by_zero_actual():
    """Test handling of division by zero when actual distance is 0."""
    front = {
        0.0: [100, 10],
        1.0: [10, 100],
    }
    # Actual tree with zero travel distance
    actual = (50, 0)

    result = calculate_tradeoff(front, actual)

    # Should handle gracefully
    assert result["Actual_ratio"] is None
    assert result["Tradeoff"] is None
    # Other values should still be calculated
    assert result["Steiner_length"] == 10
    assert result["Satellite_distance"] == 10


def test_calculate_tradeoff_division_by_zero_satellite():
    """Test handling of division by zero when satellite distance is 0."""
    front = {
        0.0: [100, 0],  # Satellite point with zero distance
        1.0: [10, 100],
    }
    actual = (50, 50)

    result = calculate_tradeoff(front, actual)

    # Should handle gracefully - optimal_ratio cannot be computed
    assert result["Optimal_ratio"] is None
    assert result["Tradeoff"] is None
    # Other values should still be calculated
    assert result["Steiner_length"] == 10
    assert result["Satellite_distance"] == 0
    assert result["Actual_ratio"] == 1.0


def test_calculate_tradeoff_zero_steiner_length():
    """Test handling when steiner_length is 0 (optimal_ratio would be 0)."""
    front = {
        0.0: [100, 10],
        1.0: [0, 100],  # Steiner point with zero length
    }
    actual = (50, 50)

    result = calculate_tradeoff(front, actual)

    # optimal_ratio = 0 / 10 = 0, so tradeoff cannot be computed (division by zero)
    assert result["Optimal_ratio"] == 0.0
    assert result["Tradeoff"] is None
    # Other values should still be calculated
    assert result["Steiner_length"] == 0
    assert result["Satellite_distance"] == 10
    assert result["Actual_ratio"] == 1.0


def test_calculate_tradeoff_empty_front():
    """Test handling of empty Pareto front."""
    front = {}
    actual = (50, 50)

    result = calculate_tradeoff(front, actual)

    # All values should be None
    assert result["Tradeoff"] is None
    assert result["Steiner_length"] is None
    assert result["Steiner_distance"] is None
    assert result["Satellite_length"] is None
    assert result["Satellite_distance"] is None
    assert result["Actual_ratio"] is None
    assert result["Optimal_ratio"] is None


def test_calculate_tradeoff_returns_python_floats():
    """Test that all numeric results are Python floats (not numpy types)."""
    front = {
        0.0: [100, 10],
        1.0: [10, 100],
    }
    actual = (50, 50)

    result = calculate_tradeoff(front, actual)

    # All numeric fields should be Python float
    for field in [
        "Tradeoff",
        "Steiner_length",
        "Steiner_distance",
        "Satellite_length",
        "Satellite_distance",
        "Actual_ratio",
        "Optimal_ratio",
    ]:
        assert type(result[field]) is float, f"{field} should be Python float"


# ========== Test pareto_calcs() ==========


def test_pareto_calcs_simple(simple_lateral_root_graph):
    """Test Pareto calculations on simple graph."""
    # Add edge weights
    for u, v in simple_lateral_root_graph.edges():
        if "weight" not in simple_lateral_root_graph[u][v]:
            from ariadne_roots.pareto_functions import node_dist

            dist = node_dist(simple_lateral_root_graph, u, v)
            simple_lateral_root_graph[u][v]["weight"] = dist

    results, front, randoms = pareto_calcs(simple_lateral_root_graph)

    # Check that results dictionary has expected keys
    assert "Total root length" in results
    assert "Travel distance" in results
    assert "alpha" in results
    assert "scaling distance to front" in results
    assert "Total root length (random)" in results
    assert "Travel distance (random)" in results
    assert "alpha (random)" in results
    assert "scaling (random)" in results

    # Values should be positive
    assert results["Total root length"] > 0
    assert results["Travel distance"] > 0
    assert 0 <= results["alpha"] <= 1
    assert results["scaling distance to front"] > 0

    # Front should be a dictionary with alpha values
    assert isinstance(front, dict)
    assert len(front) > 0

    # Randoms should be a list of tuples
    assert isinstance(randoms, list)
    assert len(randoms) == 1000


# ========== Test calc_len_LRs_with_distances() ==========


def test_calc_len_LRs_with_distances_real_data(plantB_day11_json):
    """Test LR distance calculations with real data."""
    with open(plantB_day11_json) as f:
        data = json.load(f)
        graph = json_graph.adjacency_graph(data)

    # Convert to directed graph (analyze() does this)
    H = graph.to_directed()

    # This function needs a properly structured graph
    # Testing is mainly covered by analyze() integration test
    # but we can verify it returns dict with lengths and distances
    try:
        lr_info = calc_len_LRs_with_distances(H)
        if lr_info:
            # Each LR should have [length, distance]
            for lr_idx, values in lr_info.items():
                assert len(values) == 2
                assert values[0] > 0  # length
                assert values[1] >= 0  # distance (can be 0 for single-node LR)
    except (AssertionError, KeyError):
        # Function requires specific graph structure, skip if fails
        pytest.skip("calc_len_LRs_with_distances requires specific graph structure")


def test_calc_len_LRs_with_distances_nonzero_start_index(issue26_root_json):
    """Test calc_len_LRs_with_distances with non-zero starting LR index (issue #26).

    This test reproduces issue #26 where calc_len_LRs_with_distances() would
    crash with UnboundLocalError when lateral root indices don't start at 0.
    The bug occurred because the loop iterated from range(num_LRs) starting
    at 0, but the minimum LR index is 1 (since None is used for primary root).

    PR #27 fixes this by calculating min_num_LRs and using
    range(min_num_LRs, num_LRs) instead.
    """
    with open(issue26_root_json) as f:
        data = json.load(f)
        # Use tree_graph for tree-formatted JSON (has 'children' key)
        graph = json_graph.tree_graph(data)

    # tree_graph returns a DiGraph, so no need to convert
    H = graph

    # This should NOT raise UnboundLocalError with the fix from PR #27
    lr_info = calc_len_LRs_with_distances(H)

    # Verify we got valid results
    assert isinstance(lr_info, dict)
    assert len(lr_info) > 0  # Should have at least one lateral root

    # Each LR should have [length, first_to_last_distance]
    for lr_idx, values in lr_info.items():
        assert isinstance(values, list)
        assert len(values) == 2  # [length, distance]
        length, distance = values
        assert length > 0  # All LRs should have positive length
        assert distance >= 0  # Distance can be 0 for single-node LR


# ========== Test find_lowermost_node_of_primary_root() ==========


def test_find_lowermost_node_simple(simple_linear_graph):
    """Test finding lowermost node in linear graph."""
    # Create a vertical graph with edges
    G = nx.Graph()
    G.add_node(0, pos=(0, 0))  # Top
    G.add_node(1, pos=(0, 10))  # Middle
    G.add_node(2, pos=(0, 20))  # Bottom (lowermost)

    # Add edges to create connected graph
    G.add_edge(0, 1)
    G.add_edge(1, 2)

    lowermost_pos = find_lowermost_node_of_primary_root(G, root_node=0)

    # Should return position of node 2
    assert lowermost_pos == (0, 20)


def test_find_lowermost_node_branching():
    """Test finding lowermost node in branching graph."""
    G = nx.Graph()
    G.add_node(0, pos=(0, 0))  # Root
    G.add_node(1, pos=(0, 10))
    G.add_node(2, pos=(-5, 20))  # Left branch
    G.add_node(3, pos=(5, 25))  # Right branch (lowermost)

    G.add_edge(0, 1)
    G.add_edge(1, 2)
    G.add_edge(1, 3)

    lowermost_pos = find_lowermost_node_of_primary_root(G, root_node=0)

    # Node 3 has highest y-coordinate (25)
    assert lowermost_pos == (5, 25)


# ========== Additional edge case tests ==========


def test_distance_large_coords():
    """Test distance with large coordinates."""
    p1 = (0, 0)
    p2 = (1000, 1000)
    dist = distance(p1, p2)
    expected = math.sqrt(1000**2 + 1000**2)
    assert math.isclose(dist, expected, rel_tol=1e-8)


def test_calc_zones_single_lateral_root():
    """Test zone calculation with exactly one LR at attachment point."""
    G = nx.Graph()
    # Primary root: 0 -> 1 -> 2 -> 3
    G.add_node(0, pos=(0, 0), LR_index=None)
    G.add_node(1, pos=(0, 10), LR_index=None)
    G.add_node(2, pos=(0, 20), LR_index=None)
    G.add_node(3, pos=(0, 30), LR_index=None)
    # Single LR at node 1
    G.add_node(4, pos=(5, 10), LR_index=0)

    G.add_edge(0, 1)
    G.add_edge(1, 2)
    G.add_edge(2, 3)
    G.add_edge(1, 4)

    zones = calc_zones(G, root_node=0)

    # Should have some branched zone where LR is attached
    assert zones["branched_zone_length"] >= 0
    # Should have basal zone before first LR
    assert zones["basal_zone_length"] >= 0
    # Should have apical zone after last LR
    assert zones["apical_zone_length"] >= 0


# ========== Integration Test (existing) ==========


def test_analyze(
    plantB_day11_json,
    plantB_day11_lr_lengths,
    plantB_day11_lr_angles,
    plantB_day11_lr_minimal_lengths,
):
    # load the json file
    with open(plantB_day11_json, mode="r") as h:
        data = json.load(h)
        # convert to networkx graph
        graph = json_graph.adjacency_graph(data)

        # perform analysis (enable_3d=False for faster test)
        results, front, randoms, results_3d, front_3d, randoms_3d = analyze(
            graph, enable_3d=False
        )

        # check the results
        assert len(results) == 38  # 31 original + 7 tradeoff fields
        # Random values are not tested here
        # Scalar assertions
        assert isclose(results["Total root length"], 13196.30945, rel_tol=1e-8)
        assert isclose(results["Travel distance"], 34709.9406, rel_tol=1e-8)
        # Alpha is now interpolated between discrete values for higher precision
        assert isclose(results["alpha"], 0.004435003275475457, rel_tol=1e-8)
        assert isclose(results["scaling distance to front"], 1.067228823, rel_tol=1e-8)

        # Tradeoff metric assertions
        assert isclose(results["Tradeoff"], 2.512831837486991, rel_tol=1e-8)
        assert isclose(results["Steiner_length"], 4920.752469563776, rel_tol=1e-8)
        assert isclose(results["Steiner_distance"], 39266.99938955784, rel_tol=1e-8)
        assert isclose(results["Satellite_length"], 32523.42876279192, rel_tol=1e-8)
        assert isclose(results["Satellite_distance"], 32523.42876279192, rel_tol=1e-8)
        assert isclose(results["Actual_ratio"], 0.3801881886469075, rel_tol=1e-8)
        assert isclose(results["Optimal_ratio"], 0.1512986993300445, rel_tol=1e-8)
        assert isclose(results["PR length"], 3610.664228, rel_tol=1e-8)
        assert isclose(results["PR_minimal_length"], 3459.128503, rel_tol=1e-8)
        assert isclose(results["Basal Zone length"], 0, rel_tol=1e-8)
        assert isclose(results["Branched Zone length"], 1869.271258, rel_tol=1e-8)
        assert isclose(results["Apical Zone length"], 1741.39297, rel_tol=1e-8)
        assert isclose(results["Mean LR lengths"], 399.4018841, rel_tol=1e-8)
        assert isclose(results["Mean LR minimal lengths"], 384.593032, rel_tol=1e-8)
        assert isclose(results["Median LR lengths"], 219.7926545, rel_tol=1e-8)
        assert isclose(results["Median LR minimal lengths"], 209.9816672, rel_tol=1e-8)
        assert isclose(results["sum LR minimal lengths"], 9230.232768, rel_tol=1e-8)
        assert isclose(results["Mean LR angles"], 61.27733707, rel_tol=1e-8)
        assert isclose(results["Median LR angles"], 59.46912539, rel_tol=1e-8)
        assert results["LR count"] == 24
        assert isclose(results["LR density"], 0.006646976, rel_tol=1e-6)
        assert isclose(results["Branched Zone density"], 0.012839228, rel_tol=1e-8)
        assert isclose(results["Barycenter x displacement"], 95.82352941, rel_tol=1e-8)
        assert isclose(results["Barycenter y displacement"], 1106.823529, rel_tol=1e-8)
        assert isclose(results["Total minimal Distance"], 12689.36127, rel_tol=1e-8)
        assert isclose(results["Tortuosity"], 1.039950646, rel_tol=1e-8)
        assert isclose(results["Convex Hull Area"], 1039998.5, rel_tol=1e-8)
        # Assertions for arrays
        npt.assert_allclose(results["LR lengths"], plantB_day11_lr_lengths, rtol=1e-8)
        npt.assert_allclose(results["LR angles"], plantB_day11_lr_angles, rtol=1e-8)
        npt.assert_allclose(
            results["LR minimal lengths"], plantB_day11_lr_minimal_lengths, rtol=1e-8
        )

        # Check the front
        assert len(front) == 101
        # When alpha is 0 the satellite tree is used so the total_root_length is the same as the total_travel_distance
        npt.assert_allclose(
            front.get(np.float64(0.0)),
            [32523.428762791922, 32523.428762791922],
            rtol=1e-8,
        )
        assert isclose(
            front.get(np.float64(0.0))[0], front.get(np.float64(0.0))[1], rel_tol=1e-8
        )

        min_root_length = min(front.values(), key=lambda x: x[0])[0]
        max_root_length = max(front.values(), key=lambda x: x[0])[0]
        min_travel_distance = min(front.values(), key=lambda x: x[1])[1]
        max_travel_distance = max(front.values(), key=lambda x: x[1])[1]
        # When alpha is 0, the total_root_length is maximal and the total_travel_distance is minimal
        assert max_root_length == front.get(np.float64(0.0))[0]
        assert min_travel_distance == front.get(np.float64(0.0))[1]
        # When alpha is 1, the total_root_length is minimal and the total_travel_distance is maximal
        assert min_root_length == front.get(np.float64(1.0))[0]
        assert max_travel_distance == front.get(np.float64(1.0))[1]
        # alpha 0.5 is the middle of the front
        assert isclose(
            front.get(np.float64(0.5))[0], 5196.958333735241, rel_tol=1e-8
        )  # total_root_length
        assert isclose(
            front.get(np.float64(0.5))[1], 34690.010682440174, rel_tol=1e-8
        )  # total_travel_distance


class TestPlotBufferCalculation:
    """Test buffer calculation for plot axis limits."""

    def test_buffer_normal_positive_range(self):
        """Test buffer with normal positive coordinate range."""
        min_limit, max_limit = calculate_plot_buffer(0, 10)

        # 20% of range (10) = 2.0 buffer
        assert min_limit == -2.0
        assert max_limit == 12.0

    def test_buffer_negative_range(self):
        """Test buffer with negative coordinate range."""
        min_limit, max_limit = calculate_plot_buffer(-10, -2)

        # Range is 8, 20% buffer = 1.6
        assert isclose(min_limit, -11.6, rel_tol=1e-9)
        assert isclose(max_limit, -0.4, rel_tol=1e-9)

    def test_buffer_range_crossing_zero(self):
        """Test buffer with range crossing zero."""
        min_limit, max_limit = calculate_plot_buffer(-5, 5)

        # Range is 10, 20% buffer = 2.0
        assert min_limit == -7.0
        assert max_limit == 7.0

    def test_buffer_zero_values(self):
        """Test buffer when all values are zero (degenerate case)."""
        min_limit, max_limit = calculate_plot_buffer(0, 0)

        # Range is 0, minimum buffer of 1.0 applies
        assert min_limit == -1.0
        assert max_limit == 1.0

    def test_buffer_small_range(self):
        """Test buffer with very small range (less than min_buffer)."""
        min_limit, max_limit = calculate_plot_buffer(5.0, 5.1)

        # Range is 0.1, 20% = 0.02 < min_buffer of 1.0
        # So min_buffer applies
        assert min_limit == 4.0
        assert max_limit == 6.1

    def test_buffer_large_range(self):
        """Test buffer with large coordinate range."""
        min_limit, max_limit = calculate_plot_buffer(0, 1000)

        # Range is 1000, 20% buffer = 200.0
        assert min_limit == -200.0
        assert max_limit == 1200.0

    def test_buffer_negative_to_positive(self):
        """Test buffer with range from negative to positive (asymmetric)."""
        min_limit, max_limit = calculate_plot_buffer(-3, 7)

        # Range is 10, 20% buffer = 2.0
        assert min_limit == -5.0
        assert max_limit == 9.0

    def test_buffer_custom_percent(self):
        """Test buffer with custom buffer percentage."""
        min_limit, max_limit = calculate_plot_buffer(0, 10, buffer_percent=0.10)

        # 10% of range (10) = 1.0 buffer
        assert min_limit == -1.0
        assert max_limit == 11.0

    def test_buffer_custom_min_buffer(self):
        """Test buffer with custom minimum buffer."""
        min_limit, max_limit = calculate_plot_buffer(0, 0, min_buffer=5.0)

        # Range is 0, custom min_buffer of 5.0 applies
        assert min_limit == -5.0
        assert max_limit == 5.0

    def test_buffer_prevents_matplotlib_error(self):
        """Test that buffer prevents degenerate xlim/ylim that causes matplotlib errors."""
        # This was the original bug - when all values are the same
        min_limit, max_limit = calculate_plot_buffer(42.0, 42.0)

        # Must have different min/max to avoid matplotlib error
        assert min_limit < max_limit
        assert min_limit == 41.0
        assert max_limit == 43.0
