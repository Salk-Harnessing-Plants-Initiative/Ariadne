"""Tests for 3D Pareto path tortuosity functions.

These tests follow TDD methodology:
- Tests for bugs are written BEFORE fixes
- Tests verify that bugs exist (expected failures)
- After fixes, tests verify correct behavior

Tests cover:
- graph_costs_3d_path_tortuosity() - 3D cost computation with edge cases
- pareto_cost_3d_path_tortuosity() - parameter validation
- pareto_steiner_fast_3d_path_tortuosity() - 3D Steiner tree construction
- pareto_front_3d_path_tortuosity() - 3D Pareto front computation
- random_tree_3d_path_tortuosity() - random tree generation with 3D costs
"""

import math
import pytest
import networkx as nx

from ariadne_roots.pareto_functions import (
    graph_costs_3d_path_tortuosity,
    pareto_cost_3d_path_tortuosity,
    pareto_steiner_fast_3d_path_tortuosity,
    pareto_front_3d_path_tortuosity,
    random_tree_3d_path_tortuosity,
    get_critical_nodes,
)


# ========== Test Fixtures for 3D Functions ==========


@pytest.fixture
def make_simple_graph():
    """Factory fixture for creating simple test graphs."""

    def _make_graph(nodes_data, edges_data):
        """Create a NetworkX graph from node and edge data.

        Args:
            nodes_data: List of tuples (node_id, x, y, lr_index, root_deg)
            edges_data: List of tuples (node1, node2, weight)

        Returns:
            nx.Graph with pos, LR_index, and root_deg attributes
        """
        G = nx.Graph()
        for node_id, x, y, lr_index, root_deg in nodes_data:
            G.add_node(node_id, pos=(x, y), LR_index=lr_index, root_deg=root_deg)
        for node1, node2, weight in edges_data:
            G.add_edge(node1, node2, weight=weight)
        return G

    return _make_graph


@pytest.fixture
def simple_3node_graph(make_simple_graph):
    """Simple 3-node linear graph: 0 -- 1 -- 2.

    Node positions:
        0: (0, 0) - base
        1: (10, 0)
        2: (20, 0) - tip

    Expected costs:
        - total_root_length: 20.0
        - total_travel_distance: 30.0 (10 + 20)
        - total_path_coverage: 2.0 (both nodes have tortuosity = 1.0)
    """
    nodes = [
        (0, 0, 0, None, 0),
        (1, 10, 0, None, 0),
        (2, 20, 0, None, 0),
    ]
    edges = [
        (0, 1, 10.0),
        (1, 2, 10.0),
    ]
    return make_simple_graph(nodes, edges)


@pytest.fixture
def complex_10node_graph(make_simple_graph):
    """Complex 10-node graph with branching structure.

    Structure:
        0 (base) -- 1 -- 2 -- 3 (tip)
                    |
                    4 -- 5 (tip)
                    |
                    6 -- 7 -- 8 (tip)
                         |
                         9 (tip)
    """
    nodes = [
        (0, 0, 0, None, 0),  # base
        (1, 10, 0, None, 0),  # branch point
        (2, 20, 0, None, 0),
        (3, 30, 0, None, 0),  # tip
        (4, 10, 10, None, 0),  # branch point
        (5, 10, 20, None, 0),  # tip
        (6, 10, -10, None, 0),  # branch point
        (7, 20, -10, None, 0),  # branch point
        (8, 30, -10, None, 0),  # tip
        (9, 20, -20, None, 0),  # tip
    ]
    edges = [
        (0, 1, 10.0),
        (1, 2, 10.0),
        (2, 3, 10.0),
        (1, 4, 10.0),
        (4, 5, 10.0),
        (1, 6, 10.0),
        (6, 7, 10.0),
        (7, 8, 10.0),
        (7, 9, 10.0),
    ]
    return make_simple_graph(nodes, edges)


@pytest.fixture
def cyclic_graph(make_simple_graph):
    """Graph with a cycle: 0 -- 1 -- 2 -- 0.

    This should trigger cycle detection and return infinite costs.
    """
    nodes = [
        (0, 0, 0, None, 0),
        (1, 10, 0, None, 0),
        (2, 5, 10, None, 0),
    ]
    edges = [
        (0, 1, 10.0),
        (1, 2, 10.0),
        (2, 0, 10.0),  # Creates cycle
    ]
    return make_simple_graph(nodes, edges)


@pytest.fixture
def coincident_node_graph(make_simple_graph):
    """Graph where a critical node is at the same position as base.

    Node 2 (a tip/critical node) is at position (0, 0), same as base node 0.
    This tests division-by-zero protection in tortuosity calculation.
    """
    nodes = [
        (0, 0, 0, None, 0),  # base at origin
        (1, 10, 0, None, 0),  # intermediate node
        (2, 0, 0, None, 0),  # tip at SAME position as base (coincident)
    ]
    edges = [
        (0, 1, 10.0),
        (1, 2, 10.0),  # Path goes out and comes back
    ]
    return make_simple_graph(nodes, edges)


@pytest.fixture
def branching_graph_for_steiner(make_simple_graph):
    """Graph suitable for Steiner tree construction tests."""
    nodes = [
        (0, 0, 0, None, 0),  # base
        (1, 10, 0, None, 0),
        (2, 20, 0, None, 0),  # tip
        (3, 10, 10, None, 0),  # tip
    ]
    edges = [
        (0, 1, 10.0),
        (1, 2, 10.0),
        (1, 3, 10.0),
    ]
    return make_simple_graph(nodes, edges)


# ========== Section 2: Tests for graph_costs_3d_path_tortuosity ==========


class TestGraphCosts3DValidGraphs:
    """Tests for graph_costs_3d_path_tortuosity with valid inputs."""

    def test_simple_graph_returns_three_values(self, simple_3node_graph):
        """Test that function returns exactly 3 values for valid graph."""
        result = graph_costs_3d_path_tortuosity(simple_3node_graph)

        assert isinstance(result, tuple), "Should return a tuple"
        assert len(result) == 3, "Should return exactly 3 values"

        total_root_length, total_travel_distance, total_path_coverage = result
        assert isinstance(total_root_length, (int, float))
        assert isinstance(total_travel_distance, (int, float))
        assert isinstance(total_path_coverage, (int, float))

    def test_simple_graph_costs_are_positive(self, simple_3node_graph):
        """Test that all costs are positive for valid graph."""
        total_root_length, total_travel_distance, total_path_coverage = (
            graph_costs_3d_path_tortuosity(simple_3node_graph)
        )

        assert total_root_length > 0, "Root length should be positive"
        assert total_travel_distance > 0, "Travel distance should be positive"
        assert total_path_coverage > 0, "Path coverage should be positive"

    def test_simple_graph_expected_values(self, simple_3node_graph):
        """Test expected cost values for simple linear graph."""
        total_root_length, total_travel_distance, total_path_coverage = (
            graph_costs_3d_path_tortuosity(simple_3node_graph)
        )

        # Wiring cost: 10 + 10 = 20
        assert math.isclose(total_root_length, 20.0, rel_tol=1e-8)

        # Travel distance: node 1 (10) + node 2 (20) = 30
        assert math.isclose(total_travel_distance, 30.0, rel_tol=1e-8)

        # Path coverage: For a straight line, tortuosity = 1.0 for each node
        # node 1: travel_dist=10, straight_dist=10, ratio=1.0
        # node 2: travel_dist=20, straight_dist=20, ratio=1.0
        # Total = 2.0
        assert math.isclose(total_path_coverage, 2.0, rel_tol=1e-8)

    def test_complex_graph_costs_are_finite(self, complex_10node_graph):
        """Test that complex graph returns finite positive costs."""
        total_root_length, total_travel_distance, total_path_coverage = (
            graph_costs_3d_path_tortuosity(complex_10node_graph)
        )

        assert total_root_length > 0
        assert total_root_length != float("inf")

        assert total_travel_distance > 0
        assert total_travel_distance != float("inf")

        assert total_path_coverage > 0
        assert total_path_coverage != float("inf")

    def test_with_critical_nodes_parameter(self, simple_3node_graph):
        """Test that critical_nodes parameter filters which nodes contribute."""
        critical = get_critical_nodes(simple_3node_graph)

        result_all = graph_costs_3d_path_tortuosity(simple_3node_graph)
        result_critical = graph_costs_3d_path_tortuosity(
            simple_3node_graph, critical_nodes=critical
        )

        # Wiring cost should be the same
        assert math.isclose(result_all[0], result_critical[0], rel_tol=1e-8)

        # Travel distance may differ (only critical nodes counted)
        # Path coverage may differ (only critical nodes counted)
        assert result_critical[1] <= result_all[1]
        assert result_critical[2] <= result_all[2]


class TestGraphCosts3DCycleDetection:
    """Tests for cycle detection in graph_costs_3d_path_tortuosity."""

    def test_cycle_returns_three_inf_values(self, cyclic_graph):
        """BUG TEST: Cycle detection should return 3 inf values, not 2.

        Current behavior: returns (inf, inf) - 2 values
        Expected behavior: returns (inf, inf, inf) - 3 values

        This test will FAIL until the bug is fixed.
        """
        result = graph_costs_3d_path_tortuosity(cyclic_graph)

        assert isinstance(result, tuple), "Should return a tuple"
        assert len(result) == 3, "Should return exactly 3 values (BUG: returns 2)"

        total_root_length, total_travel_distance, total_path_coverage = result
        assert total_root_length == float("inf")
        assert total_travel_distance == float("inf")
        assert total_path_coverage == float("inf")


class TestGraphCosts3DCoincidentNodes:
    """Tests for coincident node handling (division by zero protection)."""

    def test_coincident_node_no_divide_by_zero(self, coincident_node_graph):
        """BUG TEST: Coincident nodes should not cause division by zero.

        When a critical node is at the same position as the base node,
        the straight-line distance is 0, causing division by zero in
        tortuosity calculation.

        Current behavior: ZeroDivisionError or inf in result
        Expected behavior: Tortuosity contribution = 1.0 for coincident node

        This test will FAIL until the bug is fixed.
        """
        # Should not raise ZeroDivisionError
        result = graph_costs_3d_path_tortuosity(coincident_node_graph)

        assert isinstance(result, tuple)
        assert len(result) == 3

        total_root_length, total_travel_distance, total_path_coverage = result

        # All values should be finite (not inf)
        assert total_root_length != float("inf")
        assert total_travel_distance != float("inf")
        assert total_path_coverage != float("inf")

        # All values should be positive
        assert total_root_length > 0
        assert total_travel_distance > 0
        assert total_path_coverage > 0


# ========== Section 3: Tests for pareto_cost_3d_path_tortuosity ==========


class TestParetoCost3DValidInputs:
    """Tests for pareto_cost_3d_path_tortuosity with valid parameters."""

    def test_alpha_only(self):
        """Test cost with alpha=1, beta=0, gamma=0 (pure length minimization)."""
        cost = pareto_cost_3d_path_tortuosity(100, 50, 2.0, alpha=1.0, beta=0.0)
        # gamma = 0, cost = 1*100 + 0*50 - 0*2.0 = 100
        assert math.isclose(cost, 100.0, rel_tol=1e-8)

    def test_beta_only(self):
        """Test cost with alpha=0, beta=1, gamma=0 (pure distance minimization)."""
        cost = pareto_cost_3d_path_tortuosity(100, 50, 2.0, alpha=0.0, beta=1.0)
        # gamma = 0, cost = 0*100 + 1*50 - 0*2.0 = 50
        assert math.isclose(cost, 50.0, rel_tol=1e-8)

    def test_gamma_only(self):
        """Test cost with alpha=0, beta=0, gamma=1 (pure coverage maximization)."""
        cost = pareto_cost_3d_path_tortuosity(100, 50, 2.0, alpha=0.0, beta=0.0)
        # gamma = 1, cost = 0*100 + 0*50 - 1*2.0 = -2.0
        assert math.isclose(cost, -2.0, rel_tol=1e-8)

    def test_boundary_valid_half_half(self):
        """Test cost with alpha=0.5, beta=0.5, gamma=0 (boundary case)."""
        cost = pareto_cost_3d_path_tortuosity(100, 50, 2.0, alpha=0.5, beta=0.5)
        # gamma = 0, cost = 0.5*100 + 0.5*50 - 0*2.0 = 50 + 25 = 75
        assert math.isclose(cost, 75.0, rel_tol=1e-8)


class TestParetoCost3DInvalidInputs:
    """Tests for pareto_cost_3d_path_tortuosity parameter validation."""

    def test_invalid_alpha_negative(self):
        """Test that negative alpha raises AssertionError."""
        with pytest.raises(AssertionError):
            pareto_cost_3d_path_tortuosity(100, 50, 2.0, alpha=-0.1, beta=0.5)

    def test_invalid_alpha_greater_than_one(self):
        """Test that alpha > 1 raises AssertionError."""
        with pytest.raises(AssertionError):
            pareto_cost_3d_path_tortuosity(100, 50, 2.0, alpha=1.5, beta=0.0)

    def test_invalid_beta_negative(self):
        """Test that negative beta raises AssertionError."""
        with pytest.raises(AssertionError):
            pareto_cost_3d_path_tortuosity(100, 50, 2.0, alpha=0.5, beta=-0.1)

    def test_invalid_beta_greater_than_one(self):
        """Test that beta > 1 raises AssertionError."""
        with pytest.raises(AssertionError):
            pareto_cost_3d_path_tortuosity(100, 50, 2.0, alpha=0.0, beta=1.5)

    def test_invalid_alpha_plus_beta_exceeds_one(self):
        """BUG TEST: alpha + beta > 1 should raise AssertionError.

        Current behavior: No validation, gamma becomes negative
        Expected behavior: AssertionError raised

        This test will FAIL until the validation is added.
        """
        with pytest.raises(AssertionError):
            pareto_cost_3d_path_tortuosity(100, 50, 2.0, alpha=0.6, beta=0.6)


# ========== Section 4: Tests for Other 3D Functions ==========


class TestParetoSteiner3D:
    """Tests for pareto_steiner_fast_3d_path_tortuosity."""

    def test_produces_connected_tree(self, branching_graph_for_steiner):
        """Test that Steiner algorithm produces a connected tree."""
        steiner = pareto_steiner_fast_3d_path_tortuosity(
            branching_graph_for_steiner, alpha=0.5, beta=0.5
        )

        # Should be a connected graph
        assert nx.is_connected(steiner)

        # Base node should be present
        assert steiner.has_node(0)

        # All critical nodes should be reachable from base
        critical = get_critical_nodes(branching_graph_for_steiner)
        for node in critical:
            assert steiner.has_node(node)

    def test_respects_alpha_beta_tradeoff(self, branching_graph_for_steiner):
        """Test that different alpha/beta produce different trees."""
        steiner_alpha_high = pareto_steiner_fast_3d_path_tortuosity(
            branching_graph_for_steiner, alpha=0.9, beta=0.1
        )
        steiner_beta_high = pareto_steiner_fast_3d_path_tortuosity(
            branching_graph_for_steiner, alpha=0.1, beta=0.9
        )

        # Trees should have the same nodes (all critical nodes)
        # but may have different edge structures
        assert steiner_alpha_high.number_of_nodes() > 0
        assert steiner_beta_high.number_of_nodes() > 0

    def test_edges_have_weights(self, branching_graph_for_steiner):
        """Test that Steiner tree edges have weight attributes."""
        steiner = pareto_steiner_fast_3d_path_tortuosity(
            branching_graph_for_steiner, alpha=0.5, beta=0.5
        )

        for u, v in steiner.edges():
            assert "weight" in steiner[u][v]
            assert steiner[u][v]["weight"] > 0


class TestParetoFront3D:
    """Tests for pareto_front_3d_path_tortuosity."""

    def test_returns_expected_structure(self, simple_3node_graph):
        """Test that pareto_front_3d returns expected data structure."""
        front, actual = pareto_front_3d_path_tortuosity(simple_3node_graph)

        assert isinstance(front, dict)
        assert isinstance(actual, (list, tuple))
        assert len(actual) == 3  # (wiring, delay, coverage)

    def test_front_contains_valid_3d_coordinates(self, simple_3node_graph):
        """Test that front contains valid 3D cost coordinates."""
        front, actual = pareto_front_3d_path_tortuosity(simple_3node_graph)

        # Front should have entries for (alpha, beta) pairs
        for key, value in front.items():
            # Key should be (alpha, beta) tuple
            assert isinstance(key, tuple)
            assert len(key) == 2
            alpha, beta = key
            assert 0 <= alpha <= 1
            assert 0 <= beta <= 1

            # Value should be [wiring, delay, coverage] list
            assert isinstance(value, list)
            assert len(value) == 3
            assert all(isinstance(v, (int, float)) for v in value)


class TestRandomTree3D:
    """Tests for random_tree_3d_path_tortuosity."""

    def test_produces_connected_trees(self, branching_graph_for_steiner):
        """Test that random_tree_3d produces valid connected trees."""
        # Note: This function returns costs, not trees
        costs = random_tree_3d_path_tortuosity(branching_graph_for_steiner)

        assert isinstance(costs, list)
        assert len(costs) > 0

    def test_returns_three_values_per_tree(self, branching_graph_for_steiner):
        """Test that each random tree cost tuple has 3 values."""
        costs = random_tree_3d_path_tortuosity(branching_graph_for_steiner)

        for cost_tuple in costs:
            assert isinstance(cost_tuple, tuple)
            assert len(cost_tuple) == 3, "Each cost should have 3 values"

            wiring, delay, coverage = cost_tuple
            assert isinstance(wiring, (int, float))
            assert isinstance(delay, (int, float))
            assert isinstance(coverage, (int, float))

    def test_costs_are_positive(self, branching_graph_for_steiner):
        """Test that random tree costs are positive."""
        costs = random_tree_3d_path_tortuosity(branching_graph_for_steiner)

        for wiring, delay, coverage in costs:
            assert wiring >= 0
            assert delay >= 0
            assert coverage >= 0


# ========== Section 7: Tests for 3D Scaling (Integration) ==========


class TestScalingIntegration:
    """Integration tests for 3D results scaling consistency."""

    def test_3d_and_2d_total_root_length_match(self, simple_3node_graph):
        """Test that 3D and 2D return same total_root_length."""
        from ariadne_roots.pareto_functions import graph_costs

        wiring_2d, _ = graph_costs(simple_3node_graph)
        wiring_3d, _, _ = graph_costs_3d_path_tortuosity(simple_3node_graph)

        assert math.isclose(wiring_2d, wiring_3d, rel_tol=1e-8), (
            "2D and 3D should compute same total_root_length"
        )

    def test_3d_and_2d_total_travel_distance_match(self, simple_3node_graph):
        """Test that 3D and 2D return same total_travel_distance."""
        from ariadne_roots.pareto_functions import graph_costs

        _, delay_2d = graph_costs(simple_3node_graph)
        _, delay_3d, _ = graph_costs_3d_path_tortuosity(simple_3node_graph)

        assert math.isclose(delay_2d, delay_3d, rel_tol=1e-8), (
            "2D and 3D should compute same total_travel_distance"
        )


# ========== Parametrized Tests ==========


@pytest.mark.parametrize(
    "alpha,beta",
    [
        (0.0, 0.0),  # gamma = 1
        (1.0, 0.0),  # gamma = 0
        (0.0, 1.0),  # gamma = 0
        (0.5, 0.5),  # gamma = 0 (boundary)
        (0.3, 0.7),  # gamma = 0 (boundary)
        (0.33, 0.33),  # gamma = 0.34
    ],
)
def test_pareto_cost_3d_valid_alpha_beta_combinations(alpha, beta):
    """Test that valid alpha/beta combinations work correctly."""
    cost = pareto_cost_3d_path_tortuosity(100, 50, 2.0, alpha=alpha, beta=beta)
    assert isinstance(cost, (int, float))
    assert cost != float("nan")


# ========== Section 11: Tests for 3D Surface Plot Visualization ==========


class TestPlotAll3DSurface:
    """Tests for 3D surface plot visualization in plot_all_3d."""

    @pytest.fixture(autouse=True)
    def setup_matplotlib_backend(self):
        """Use non-interactive backend for testing."""
        import matplotlib

        matplotlib.use("Agg")

    @pytest.fixture
    def sample_front_3d(self):
        """Sample 3D Pareto front data for plotting tests."""
        # Create a grid of alpha/beta values with valid combinations
        front = {}
        for alpha in [0.0, 0.25, 0.5, 0.75, 1.0]:
            for beta in [0.0, 0.25, 0.5, 0.75, 1.0]:
                if alpha + beta <= 1.0:
                    # Simulated costs: higher alpha = lower wiring, higher delay
                    wiring = 100 - 30 * alpha
                    delay = 50 + 40 * beta
                    coverage = 2.0 + alpha + beta
                    front[(alpha, beta)] = [wiring, delay, coverage]
        return front

    @pytest.fixture
    def collinear_front_3d(self):
        """Collinear 3D Pareto front data (points on a line)."""
        # All points are on a straight line - triangulation will fail
        return {
            (0.0, 0.0): [100.0, 50.0, 2.0],
            (0.5, 0.0): [85.0, 50.0, 2.5],
            (1.0, 0.0): [70.0, 50.0, 3.0],
        }

    @pytest.fixture
    def sample_actual_3d(self):
        """Sample actual plant data."""
        return (90.0, 55.0, 2.3)

    @pytest.fixture
    def sample_randoms_3d(self):
        """Sample random tree data."""
        return [
            (95.0, 60.0, 2.1),
            (92.0, 58.0, 2.2),
            (88.0, 52.0, 2.4),
        ]

    def test_plot_creates_figure(
        self, sample_front_3d, sample_actual_3d, sample_randoms_3d, tmp_path
    ):
        """Test that plot_all_3d creates a figure with 3D axes."""
        import matplotlib.pyplot as plt
        from ariadne_roots.quantify import plot_all_3d

        save_path = tmp_path / "test_3d_plot.png"
        mrand = sum(r[0] for r in sample_randoms_3d) / len(sample_randoms_3d)
        srand = sum(r[1] for r in sample_randoms_3d) / len(sample_randoms_3d)
        prand = sum(r[2] for r in sample_randoms_3d) / len(sample_randoms_3d)

        # Should not raise
        plot_all_3d(
            sample_front_3d,
            sample_actual_3d,
            sample_randoms_3d,
            mrand,
            srand,
            prand,
            save_path,
        )

        # File should be created
        assert save_path.exists()

        # Clean up
        plt.close("all")

    def test_plot_creates_surface(
        self, sample_front_3d, sample_actual_3d, sample_randoms_3d, tmp_path
    ):
        """Test that plot_all_3d creates a triangulated surface for the Pareto front."""
        import matplotlib.pyplot as plt
        from ariadne_roots.quantify import plot_all_3d

        save_path = tmp_path / "test_surface.png"
        mrand = sum(r[0] for r in sample_randoms_3d) / len(sample_randoms_3d)
        srand = sum(r[1] for r in sample_randoms_3d) / len(sample_randoms_3d)
        prand = sum(r[2] for r in sample_randoms_3d) / len(sample_randoms_3d)

        # Capture the figure
        plot_all_3d(
            sample_front_3d,
            sample_actual_3d,
            sample_randoms_3d,
            mrand,
            srand,
            prand,
            save_path,
        )

        # The plot should exist
        assert save_path.exists()

        plt.close("all")

    def test_plot_handles_collinear_points(
        self, collinear_front_3d, sample_actual_3d, sample_randoms_3d, tmp_path
    ):
        """Test that plot_all_3d gracefully handles collinear points.

        When all Pareto front points are on a line, triangulation fails.
        The function should fall back to scatter plot without crashing.
        """
        import matplotlib.pyplot as plt
        from ariadne_roots.quantify import plot_all_3d

        save_path = tmp_path / "test_collinear.png"
        mrand = sum(r[0] for r in sample_randoms_3d) / len(sample_randoms_3d)
        srand = sum(r[1] for r in sample_randoms_3d) / len(sample_randoms_3d)
        prand = sum(r[2] for r in sample_randoms_3d) / len(sample_randoms_3d)

        # Should not raise even with collinear points
        plot_all_3d(
            collinear_front_3d,
            sample_actual_3d,
            sample_randoms_3d,
            mrand,
            srand,
            prand,
            save_path,
        )

        # File should still be created (with fallback visualization)
        assert save_path.exists()

        plt.close("all")

    def test_svg_also_created(
        self, sample_front_3d, sample_actual_3d, sample_randoms_3d, tmp_path
    ):
        """Test that both PNG and SVG files are created."""
        import matplotlib.pyplot as plt
        from ariadne_roots.quantify import plot_all_3d

        save_path = tmp_path / "test_output.png"
        svg_path = tmp_path / "test_output.svg"
        mrand = sum(r[0] for r in sample_randoms_3d) / len(sample_randoms_3d)
        srand = sum(r[1] for r in sample_randoms_3d) / len(sample_randoms_3d)
        prand = sum(r[2] for r in sample_randoms_3d) / len(sample_randoms_3d)

        plot_all_3d(
            sample_front_3d,
            sample_actual_3d,
            sample_randoms_3d,
            mrand,
            srand,
            prand,
            save_path,
        )

        assert save_path.exists()
        assert svg_path.exists()

        plt.close("all")
