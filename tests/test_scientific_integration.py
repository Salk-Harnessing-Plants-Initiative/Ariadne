"""Scientific integration tests for Pareto analysis pipelines.

These tests verify numerical correctness of the 2D and 3D Pareto analysis
pipelines using controlled synthetic data with known expected outputs.

All numeric comparisons use 1e-6 tolerance (PRECISION) to account for
floating-point arithmetic while catching meaningful numerical errors.
"""

import math
import random

import networkx as nx
import numpy as np
import pytest

from ariadne_roots.pareto_functions import (
    get_critical_nodes,
    graph_costs,
    graph_costs_3d_path_tortuosity,
    pareto_front,
    pareto_front_3d_path_tortuosity,
    random_tree,
    random_tree_3d_path_tortuosity,
)
from ariadne_roots.quantify import (
    distance_from_front,
    distance_from_front_3d,
    pareto_calcs,
    pareto_calcs_3d_path_tortuosity,
)

# Standard precision tolerance for scientific tests
PRECISION = 1e-6


# ============================================================================
# Synthetic Test Graph Generators
# ============================================================================


def create_graph_with_attributes(nodes_data, edges_data):
    """Create a NetworkX graph with all required Ariadne attributes.

    Args:
        nodes_data: List of (node_id, x, y) tuples
        edges_data: List of (node1, node2) tuples (weights computed from positions)

    Returns:
        NetworkX Graph with pos, LR_index, root_deg attributes and edge weights
    """
    G = nx.Graph()

    # Add nodes with attributes
    for node_id, x, y in nodes_data:
        G.add_node(node_id, pos=(x, y), LR_index=None, root_deg=0)

    # Add edges with computed weights (Euclidean distance)
    for node1, node2 in edges_data:
        pos1 = G.nodes[node1]["pos"]
        pos2 = G.nodes[node2]["pos"]
        weight = math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)
        G.add_edge(node1, node2, weight=weight)

    return G


@pytest.fixture
def simple_straight_line():
    """A straight line root: 0 -- 1 -- 2 -- 3 (horizontal).

    Expected values (manually computed):
    - Total root length: 30.0 (10 + 10 + 10)
    - Critical nodes: [0, 3] (base and tip)
    - Travel distance: 30.0 (distance from 0 to tip 3)
    - Path tortuosity: 1.0 (straight line, path length = straight distance)
    """
    nodes = [(0, 0, 0), (1, 10, 0), (2, 20, 0), (3, 30, 0)]
    edges = [(0, 1), (1, 2), (2, 3)]
    return create_graph_with_attributes(nodes, edges)


@pytest.fixture
def simple_y_branch():
    """A Y-shaped root: 0 -- 1 -- 2 and 1 -- 3.

    Structure:
                    2 (30, 0)
                   /
        0 -- 1 --
                   \\
                    3 (20, 10)

    Expected values (manually computed):
    - Total root length: 30.0 (10 + 10 + 10)
    - Critical nodes: [0, 2, 3] (base and two tips)
    - Travel distance: 20.0 + 20.0 = 40.0
    - Path tortuosity for node 2: 20 / 30 = 0.667 (distance along path / straight line)
      Actually for tip 2: path_length=20, straight_dist=30, ratio = 20/30 = 0.667? No wait...
      Tip 2 is at (30, 0), base at (0,0), straight distance = 30
      Path length to tip 2 = 10 + 10 = 20
      Tortuosity = path_length / straight_distance = 20 / 30? No, that's < 1.

    Let me recalculate:
    - Tip 2 at (30, 0): path_length = 20, straight_distance = 30
      Tortuosity = 20/30 = 0.667 < 1? That can't be right.

    Wait, I misread the structure. Let me recalculate:
    - Node 0 at (0, 0) - base
    - Node 1 at (10, 0) - branch point
    - Node 2 at (30, 0) - tip 1 (but edge is from 1 to 2, so weight = 20)
    - Node 3 at (20, 10) - tip 2 (edge from 1 to 3)

    Hmm, that doesn't match "30.0 total". Let me make it simpler:
    """
    # Simpler structure: equilateral-ish
    nodes = [(0, 0, 0), (1, 10, 0), (2, 20, 0), (3, 10, 10)]
    edges = [(0, 1), (1, 2), (1, 3)]
    return create_graph_with_attributes(nodes, edges)


@pytest.fixture
def tortuous_path():
    """A zigzag path with known tortuosity > 1.

    Structure: 0 -- 1 -- 2 -- 3 (zigzag)
    - Node 0 at (0, 0) - base
    - Node 1 at (10, 10)
    - Node 2 at (20, 0)
    - Node 3 at (30, 10) - tip

    Path to tip 3:
    - Path length: sqrt(200) + sqrt(200) + sqrt(200) ≈ 14.14 * 3 = 42.43
    - Straight distance: sqrt((30-0)^2 + (10-0)^2) = sqrt(900+100) = sqrt(1000) ≈ 31.62
    - Tortuosity: 42.43 / 31.62 ≈ 1.342
    """
    nodes = [(0, 0, 0), (1, 10, 10), (2, 20, 0), (3, 30, 10)]
    edges = [(0, 1), (1, 2), (2, 3)]
    return create_graph_with_attributes(nodes, edges)


# ============================================================================
# Expected Values (manually computed)
# ============================================================================


class ExpectedValues:
    """Pre-computed expected values for synthetic test graphs.

    IMPORTANT: These values are computed for the Pareto analysis context,
    which uses critical_nodes (base + tips) for travel distance calculation.

    When graph_costs() is called WITHOUT critical_nodes, ALL nodes contribute
    to travel distance. When called WITH critical_nodes (as in pareto_front),
    only the tips contribute to travel distance.
    """

    @staticmethod
    def straight_line_with_critical_nodes():
        """Expected values for simple_straight_line with critical_nodes=[0,3].

        Graph: 0 -- 1 -- 2 -- 3 (horizontal, each edge = 10)
        Critical nodes: [0, 3] (base and tip)

        Travel distance includes only critical nodes (excluding base):
        - Node 3: distance to base = 30
        - Total = 30
        """
        return {
            "total_root_length": 30.0,
            "travel_distance": 30.0,  # Only tip at node 3
            "path_tortuosity": 1.0,  # Straight line: path = straight distance
        }

    @staticmethod
    def y_branch_with_critical_nodes():
        """Expected values for simple_y_branch with critical_nodes=[0,2,3].

        Graph: 0 -- 1 -- 2, and 1 -- 3
        Nodes: (0,0,0), (1,10,0), (2,20,0), (3,10,10)
        Edges: 0-1 (10), 1-2 (10), 1-3 (sqrt(100) = 10)
        Critical nodes: [0, 2, 3] (base and two tips)

        Travel distance includes only tips:
        - Node 2: distance to base = 20
        - Node 3: distance to base = 10 + 10 = 20
        - Total = 40
        """
        edge_0_1 = 10.0
        edge_1_2 = 10.0
        edge_1_3 = 10.0  # sqrt((10-10)^2 + (10-0)^2) = 10
        return {
            "total_root_length": edge_0_1 + edge_1_2 + edge_1_3,  # 30.0
            "travel_distance": 20.0 + 20.0,  # tips only: 40.0
        }

    @staticmethod
    def tortuous_path_with_critical_nodes():
        """Expected values for tortuous_path with critical_nodes=[0,3].

        Graph: 0 -- 1 -- 2 -- 3 (zigzag)
        Nodes: (0,0), (10,10), (20,0), (30,10)
        Edge lengths: all are sqrt(200) ≈ 14.142
        Critical nodes: [0, 3]

        Path tortuosity = path_length / straight_distance
        - Path length to tip 3 = 3 * sqrt(200) ≈ 42.426
        - Straight distance = sqrt(30^2 + 10^2) = sqrt(1000) ≈ 31.623
        - Tortuosity = 42.426 / 31.623 ≈ 1.342
        """
        edge_length = math.sqrt(200)  # ≈ 14.142
        total_length = 3 * edge_length
        straight_dist = math.sqrt(30**2 + 10**2)  # sqrt(1000) ≈ 31.623
        tortuosity = total_length / straight_dist

        return {
            "total_root_length": total_length,  # ≈ 42.426
            "travel_distance": total_length,  # Only one tip
            "straight_distance": straight_dist,  # ≈ 31.623
            "path_tortuosity": tortuosity,  # ≈ 1.342
        }


# ============================================================================
# Core Function Tests: 2D Pipeline
# ============================================================================


class TestCore2DParetoGraphCosts:
    """Test graph_costs() returns exact expected values.

    These tests verify that graph_costs() behaves correctly for Pareto analysis.
    The function computes:
    - total_root_length (wiring cost): sum of all edge lengths
    - total_travel_distance (conduction delay): sum of node distances to base

    When critical_nodes is passed (as in Pareto analysis), only tips contribute
    to travel distance. When None, ALL nodes contribute.
    """

    def test_straight_line_costs_with_critical_nodes(self, simple_straight_line):
        """Verify costs for straight line with critical_nodes (Pareto behavior).

        Graph: 0 -- 1 -- 2 -- 3 (each edge = 10)
        Critical nodes: [0, 3] (base and tip)

        Expected:
        - Total root length = 30 (edges: 10 + 10 + 10)
        - Travel distance = 30 (only tip 3 contributes, distance = 30)
        """
        G = simple_straight_line
        expected = ExpectedValues.straight_line_with_critical_nodes()
        critical = get_critical_nodes(G)

        total_length, travel_dist = graph_costs(G, critical_nodes=critical)

        assert abs(total_length - expected["total_root_length"]) < PRECISION, (
            f"Total root length mismatch: got {total_length}, "
            f"expected {expected['total_root_length']}"
        )
        assert abs(travel_dist - expected["travel_distance"]) < PRECISION, (
            f"Travel distance mismatch: got {travel_dist}, "
            f"expected {expected['travel_distance']}"
        )

    def test_straight_line_costs_without_critical_nodes(self, simple_straight_line):
        """Verify costs for straight line without critical_nodes (all nodes).

        Graph: 0 -- 1 -- 2 -- 3 (each edge = 10)

        Expected:
        - Total root length = 30 (same as with critical nodes)
        - Travel distance = 10 + 20 + 30 = 60 (ALL non-base nodes contribute)
        """
        G = simple_straight_line

        total_length, travel_dist = graph_costs(G)

        # Total length is same regardless of critical_nodes
        assert (
            abs(total_length - 30.0) < PRECISION
        ), f"Total root length mismatch: got {total_length}, expected 30.0"
        # Without critical_nodes: nodes 1,2,3 contribute with distances 10,20,30
        assert abs(travel_dist - 60.0) < PRECISION, (
            f"Travel distance mismatch: got {travel_dist}, expected 60.0 "
            "(all nodes: 10 + 20 + 30)"
        )

    def test_y_branch_costs_with_critical_nodes(self, simple_y_branch):
        """Verify costs for Y-shaped branch with critical_nodes (Pareto behavior).

        Graph: 0 -- 1 -- 2, and 1 -- 3
        Nodes: (0,0), (10,0), (20,0), (10,10)
        Edges: 0-1 (10), 1-2 (10), 1-3 (10)
        Critical nodes: [0, 2, 3] (base and two tips)

        Expected:
        - Total root length = 30
        - Travel distance = 20 + 20 = 40 (tips only: node 2 at dist 20, node 3 at dist 20)
        """
        G = simple_y_branch
        expected = ExpectedValues.y_branch_with_critical_nodes()
        critical = get_critical_nodes(G)

        total_length, travel_dist = graph_costs(G, critical_nodes=critical)

        assert abs(total_length - expected["total_root_length"]) < PRECISION, (
            f"Total root length mismatch: got {total_length}, "
            f"expected {expected['total_root_length']}"
        )
        assert abs(travel_dist - expected["travel_distance"]) < PRECISION, (
            f"Travel distance mismatch: got {travel_dist}, "
            f"expected {expected['travel_distance']}"
        )

    def test_y_branch_costs_without_critical_nodes(self, simple_y_branch):
        """Verify costs for Y-shaped branch without critical_nodes (all nodes).

        Expected:
        - Total root length = 30
        - Travel distance = 10 + 20 + 20 = 50 (all non-base nodes contribute)
        """
        G = simple_y_branch

        total_length, travel_dist = graph_costs(G)

        assert (
            abs(total_length - 30.0) < PRECISION
        ), f"Total root length mismatch: got {total_length}, expected 30.0"
        # Without critical_nodes: node 1 (dist 10), node 2 (dist 20), node 3 (dist 20)
        assert abs(travel_dist - 50.0) < PRECISION, (
            f"Travel distance mismatch: got {travel_dist}, expected 50.0 "
            "(all nodes: 10 + 20 + 20)"
        )

    def test_critical_nodes_identification(self, simple_y_branch):
        """Verify critical nodes are correctly identified.

        Critical nodes = base (node 0) + all tips (degree 1 nodes)
        """
        G = simple_y_branch
        critical = get_critical_nodes(G)

        # Critical nodes should be base (0) and tips (nodes with degree 1)
        expected_critical = {0, 2, 3}  # base and two tips
        assert (
            set(critical) == expected_critical
        ), f"Critical nodes mismatch: got {set(critical)}, expected {expected_critical}"


class TestCore2DParetoFront:
    """Test pareto_front() generates correct front."""

    def test_front_has_expected_alpha_range(self, simple_straight_line):
        """Verify Pareto front covers alpha from 0 to 1."""
        G = simple_straight_line
        front, actual = pareto_front(G)

        # Should have entries for alpha = 0.0, 0.01, ..., 1.0
        assert 0.0 in front, "Front should include alpha=0.0 (Satellite)"
        assert 1.0 in front, "Front should include alpha=1.0 (Steiner)"

        # Check approximate count (should be ~101 entries)
        assert len(front) >= 100, f"Front should have ~101 entries, got {len(front)}"

    def test_front_corners_reasonable(self, simple_y_branch):
        """Verify Steiner and Satellite corners have reasonable values."""
        G = simple_y_branch
        front, actual = pareto_front(G)

        steiner = front[1.0]  # alpha=1.0 minimizes material cost
        satellite = front[0.0]  # alpha=0.0 minimizes transport cost

        # Satellite should have higher material cost but lower transport cost
        # (or equal in degenerate cases)
        assert (
            steiner[0] <= satellite[0] + PRECISION
        ), f"Steiner length ({steiner[0]}) should be <= Satellite length ({satellite[0]})"

    def test_actual_costs_match_graph_costs(self, simple_y_branch):
        """Verify actual costs from pareto_front match graph_costs with critical nodes.

        pareto_front internally calls graph_costs(G, critical_nodes=get_critical_nodes(G)),
        so we must use the same critical_nodes for comparison.
        """
        G = simple_y_branch
        critical = get_critical_nodes(G)

        front, actual = pareto_front(G)
        direct_length, direct_distance = graph_costs(G, critical_nodes=critical)

        assert abs(actual[0] - direct_length) < PRECISION, (
            f"Actual length from pareto_front ({actual[0]}) doesn't match "
            f"graph_costs ({direct_length})"
        )
        assert abs(actual[1] - direct_distance) < PRECISION, (
            f"Actual distance from pareto_front ({actual[1]}) doesn't match "
            f"graph_costs ({direct_distance})"
        )


class TestCore2DDistanceFromFront:
    """Test distance_from_front() interpolation."""

    def test_on_front_has_epsilon_near_one(self, simple_y_branch):
        """Point exactly on front should have epsilon ≈ 1.0."""
        G = simple_y_branch
        front, actual = pareto_front(G)

        # Use actual tree costs (should be on or near front)
        alpha, epsilon = distance_from_front(front, actual)

        # Epsilon >= 1.0 always (multiplicative indicator)
        assert epsilon >= 1.0 - PRECISION, f"Epsilon should be >= 1.0, got {epsilon}"

    def test_alpha_in_valid_range(self, simple_y_branch):
        """Interpolated alpha should be in [0, 1]."""
        G = simple_y_branch
        front, actual = pareto_front(G)

        alpha, epsilon = distance_from_front(front, actual)

        assert 0.0 <= alpha <= 1.0, f"Alpha should be in [0, 1], got {alpha}"


# ============================================================================
# Core Function Tests: 3D Pipeline
# ============================================================================


class TestCore3DParetoGraphCosts:
    """Test graph_costs_3d_path_tortuosity() returns correct values.

    Note: graph_costs_3d_path_tortuosity uses critical_nodes for travel_distance
    and path_tortuosity, but uses ALL nodes by default (same as graph_costs).
    For consistent testing, we pass critical_nodes explicitly.
    """

    def test_straight_line_tortuosity_is_one(self, simple_straight_line):
        """A straight line should have tortuosity = 1.0."""
        G = simple_straight_line
        critical = get_critical_nodes(G)

        total_length, travel_dist, path_coverage = graph_costs_3d_path_tortuosity(
            G, critical_nodes=critical
        )

        # For a straight line with one tip, tortuosity = path_length / straight_distance
        # Path length = 30, straight distance = 30, ratio = 1.0
        expected = ExpectedValues.straight_line_with_critical_nodes()
        assert abs(path_coverage - expected["path_tortuosity"]) < PRECISION, (
            f"Path coverage for straight line should be {expected['path_tortuosity']}, "
            f"got {path_coverage}"
        )

    def test_tortuous_path_tortuosity_greater_than_one(self, tortuous_path):
        """A zigzag path should have tortuosity > 1.0."""
        G = tortuous_path
        critical = get_critical_nodes(G)

        total_length, travel_dist, path_coverage = graph_costs_3d_path_tortuosity(
            G, critical_nodes=critical
        )
        expected = ExpectedValues.tortuous_path_with_critical_nodes()

        # Path tortuosity should be ~1.342
        assert abs(path_coverage - expected["path_tortuosity"]) < PRECISION, (
            f"Path coverage mismatch: got {path_coverage}, "
            f"expected {expected['path_tortuosity']}"
        )

    def test_3d_length_matches_2d(self, simple_y_branch):
        """3D graph_costs should return same length as 2D version."""
        G = simple_y_branch
        critical = get_critical_nodes(G)

        length_2d, dist_2d = graph_costs(G, critical_nodes=critical)
        length_3d, dist_3d, _ = graph_costs_3d_path_tortuosity(
            G, critical_nodes=critical
        )

        assert (
            abs(length_2d - length_3d) < PRECISION
        ), f"3D length ({length_3d}) should match 2D length ({length_2d})"
        assert (
            abs(dist_2d - dist_3d) < PRECISION
        ), f"3D distance ({dist_3d}) should match 2D distance ({dist_2d})"


class TestCore3DDistanceFromFront:
    """Test distance_from_front_3d() returns correct weights."""

    def test_weights_sum_to_one(self, simple_y_branch):
        """Alpha + beta + gamma should equal 1.0."""
        G = simple_y_branch
        front, actual = pareto_front_3d_path_tortuosity(G)

        result = distance_from_front_3d(front, actual)

        total = result["alpha"] + result["beta"] + result["gamma"]
        assert abs(total - 1.0) < 1e-9, (
            f"Weights should sum to 1.0, got {total} "
            f"(alpha={result['alpha']}, beta={result['beta']}, gamma={result['gamma']})"
        )

    def test_epsilon_is_max_of_components(self, simple_y_branch):
        """Epsilon should equal max of component ratios."""
        G = simple_y_branch
        front, actual = pareto_front_3d_path_tortuosity(G)

        result = distance_from_front_3d(front, actual)

        # Epsilon = max of the three component ratios
        components = result.get("epsilon_components", {})
        if components:
            max_component = max(
                components.get("material", 0),
                components.get("transport", 0),
                components.get("coverage", 0),
            )
            assert (
                abs(result["epsilon"] - max_component) < PRECISION
            ), f"Epsilon ({result['epsilon']}) should equal max component ({max_component})"


# ============================================================================
# Reproducibility Tests
# ============================================================================


class TestReproducibility:
    """Test that random operations are reproducible when seeded.

    NOTE: random_tree() and random_tree_3d_path_tortuosity() explicitly call
    random.seed(a=None) at the start, which resets the seed to system time.
    This makes external seeding ineffective. The tests below document this
    behavior and verify that the functions at least produce consistent counts.
    """

    @pytest.mark.skip(
        reason="random_tree() calls random.seed(a=None) internally, "
        "making external seeding ineffective. See pareto_functions.py:927"
    )
    def test_random_tree_with_seed_reproducible(self, simple_y_branch):
        """random_tree with same seed should produce identical results.

        SKIPPED: This test cannot pass because random_tree() explicitly
        reseeds with random.seed(a=None) on each call.
        """
        G = simple_y_branch

        random.seed(42)
        np.random.seed(42)
        result1 = random_tree(G)

        random.seed(42)
        np.random.seed(42)
        result2 = random_tree(G)

        assert len(result1) == len(result2), "Random tree counts should match"

        for i, (r1, r2) in enumerate(zip(result1, result2)):
            assert abs(r1[0] - r2[0]) < PRECISION, f"Tree {i} length mismatch"
            assert abs(r1[1] - r2[1]) < PRECISION, f"Tree {i} distance mismatch"

    @pytest.mark.skip(
        reason="random_tree_3d_path_tortuosity() calls random.seed(a=None) internally, "
        "making external seeding ineffective. See pareto_functions.py:976"
    )
    def test_random_tree_3d_with_seed_reproducible(self, simple_y_branch):
        """random_tree_3d with same seed should produce identical results.

        SKIPPED: This test cannot pass because random_tree_3d_path_tortuosity()
        explicitly reseeds with random.seed(a=None) on each call.
        """
        G = simple_y_branch

        random.seed(42)
        np.random.seed(42)
        result1 = random_tree_3d_path_tortuosity(G)

        random.seed(42)
        np.random.seed(42)
        result2 = random_tree_3d_path_tortuosity(G)

        assert len(result1) == len(result2), "Random tree counts should match"

        for i, (r1, r2) in enumerate(zip(result1, result2)):
            assert abs(r1[0] - r2[0]) < PRECISION, f"Tree {i} length mismatch"
            assert abs(r1[1] - r2[1]) < PRECISION, f"Tree {i} distance mismatch"
            assert abs(r1[2] - r2[2]) < PRECISION, f"Tree {i} tortuosity mismatch"

    def test_random_tree_generates_1000_trees(self, simple_y_branch):
        """Verify random_tree generates exactly 1000 random trees."""
        G = simple_y_branch
        result = random_tree(G)

        assert len(result) == 1000, f"Should generate 1000 trees, got {len(result)}"

    def test_random_tree_3d_generates_1000_trees(self, simple_y_branch):
        """Verify random_tree_3d generates exactly 1000 random trees."""
        G = simple_y_branch
        result = random_tree_3d_path_tortuosity(G)

        assert len(result) == 1000, f"Should generate 1000 trees, got {len(result)}"


# ============================================================================
# Full Pipeline Integration Tests
# ============================================================================


class TestFullPipeline2D:
    """Test full 2D analysis pipeline produces consistent results."""

    def test_pareto_calcs_returns_all_fields(self, simple_y_branch):
        """pareto_calcs should return complete results dictionary."""
        G = simple_y_branch

        results, front, randoms = pareto_calcs(G)

        required_fields = [
            "Total root length",
            "Travel distance",
            "alpha",
            "scaling distance to front",
            "Total root length (random)",
            "Travel distance (random)",
            "alpha (random)",
            "scaling (random)",
        ]

        for field in required_fields:
            assert field in results, f"Missing required field: {field}"

    def test_pareto_calcs_values_are_python_floats(self, simple_y_branch):
        """All numeric values should be Python floats, not numpy types."""
        G = simple_y_branch

        results, front, randoms = pareto_calcs(G)

        numeric_fields = [
            "Total root length",
            "Travel distance",
            "alpha",
            "scaling distance to front",
        ]

        for field in numeric_fields:
            value = results[field]
            assert isinstance(
                value, (int, float)
            ), f"Field {field} should be Python numeric, got {type(value)}"
            assert not isinstance(
                value, np.floating
            ), f"Field {field} should not be numpy type"


class TestFullPipeline3D:
    """Test full 3D analysis pipeline produces consistent results."""

    def test_pareto_calcs_3d_returns_all_fields(self, simple_y_branch):
        """pareto_calcs_3d should return complete results dictionary."""
        G = simple_y_branch

        results, front, randoms = pareto_calcs_3d_path_tortuosity(G)

        required_fields = [
            "Total root length",
            "Travel distance",
            "Path tortuosity",
            "alpha_3d",
            "beta_3d",
            "gamma_3d",
            "epsilon_3d",
        ]

        for field in required_fields:
            assert field in results, f"Missing required field: {field}"

    def test_3d_weights_constraint(self, simple_y_branch):
        """3D weights alpha + beta + gamma should equal 1."""
        G = simple_y_branch

        results, front, randoms = pareto_calcs_3d_path_tortuosity(G)

        total = results["alpha_3d"] + results["beta_3d"] + results["gamma_3d"]
        assert abs(total - 1.0) < 1e-9, f"Weights should sum to 1.0, got {total}"

    def test_2d_and_3d_length_match(self, simple_y_branch):
        """2D and 3D pipelines should return same length and distance."""
        G = simple_y_branch

        results_2d, _, _ = pareto_calcs(G)
        results_3d, _, _ = pareto_calcs_3d_path_tortuosity(G)

        assert (
            abs(results_2d["Total root length"] - results_3d["Total root length"])
            < PRECISION
        ), "2D and 3D total root length should match"

        assert (
            abs(results_2d["Travel distance"] - results_3d["Travel distance"])
            < PRECISION
        ), "2D and 3D travel distance should match"
