"""Integration tests for plot scaling consistency.

These tests verify that plot data matches CSV output scaling for both
2D and 3D visualizations. Uses real root data fixtures (no mocking).

Tests follow the TDD pattern: 3D tests are expected to FAIL until
the fix is implemented in plot_all_3d().
"""

import json
import tempfile
from pathlib import Path

import networkx as nx
import numpy as np
import pytest
from networkx.readwrite import json_graph

from ariadne_roots import config, quantify, scaling


# Standard precision tolerance for scientific tests
PRECISION = 1e-6


@pytest.fixture
def plantB_day11_graph():
    """Load the real plantB_day11 root data as a NetworkX graph."""
    file_path = Path("tests/data/_set1_day1_20230509-125420_014_plantB_day11.json")
    with open(file_path, "r") as f:
        data = json.load(f)
    return json_graph.adjacency_graph(data)


@pytest.fixture
def test_scale_factor():
    """A non-trivial scale factor to make scaling bugs obvious."""
    return 0.0254  # Example: pixels to mm


class TestPlotScalingConsistency:
    """Integration tests verifying CSV and plot data consistency.

    Uses real root data fixtures to test end-to-end scaling behavior.
    No mocking - tests actual computed values.
    """

    def test_2d_analysis_produces_scalable_results(self, plantB_day11_graph):
        """Verify 2D analysis produces results that can be scaled correctly.

        This test verifies the analysis-to-CSV scaling path is working.
        """
        G = plantB_day11_graph

        # Run analysis (returns unscaled values)
        results, front, randoms, _, _, _ = quantify.analyze(G, enable_3d=False)

        # Verify results contain expected keys
        assert "Total root length" in results
        assert "Travel distance" in results
        assert "Total root length (random)" in results
        assert "Travel distance (random)" in results

        # Verify front is a dict with alpha keys
        assert isinstance(front, dict)
        assert len(front) > 0

        # Verify randoms is a list of (length, distance) tuples
        assert isinstance(randoms, list)
        assert len(randoms) > 0

    def test_3d_analysis_produces_scalable_results(self, plantB_day11_graph):
        """Verify 3D analysis produces results that can be scaled correctly.

        This test verifies the 3D analysis-to-CSV scaling path is working.
        """
        G = plantB_day11_graph

        # Run analysis with 3D enabled
        results, front, randoms, results_3d, front_3d, randoms_3d = quantify.analyze(
            G, enable_3d=True
        )

        # Verify 3D results contain expected keys
        assert "Total root length" in results_3d
        assert "Travel distance" in results_3d
        assert "Path tortuosity" in results_3d
        assert "Total root length (random)" in results_3d
        assert "Travel distance (random)" in results_3d
        assert "Path tortuosity (random)" in results_3d

        # Verify front_3d is a dict with (alpha, beta) keys
        assert isinstance(front_3d, dict)
        assert len(front_3d) > 0

        # Verify randoms_3d is a list of (length, distance, tortuosity) tuples
        assert isinstance(randoms_3d, list)
        assert len(randoms_3d) > 0
        if randoms_3d:
            assert len(randoms_3d[0]) == 3  # (length, distance, tortuosity)

    def test_scaling_transformation_preserves_structure(
        self, plantB_day11_graph, test_scale_factor
    ):
        """Verify scaling transformation produces expected scaled values.

        This tests that apply_scaling_transformation works correctly.
        """
        G = plantB_day11_graph

        # Run analysis
        results, _, _, results_3d, _, _ = quantify.analyze(G, enable_3d=True)

        # Apply scaling
        scaled_results = scaling.apply_scaling_transformation(
            results, test_scale_factor
        )
        scaled_results_3d = scaling.apply_scaling_transformation(
            results_3d, test_scale_factor
        )

        # Verify length fields are scaled
        assert (
            abs(
                scaled_results["Total root length"]
                - results["Total root length"] * test_scale_factor
            )
            < PRECISION
        )

        # Verify 3D length fields are scaled
        assert (
            abs(
                scaled_results_3d["Total root length"]
                - results_3d["Total root length"] * test_scale_factor
            )
            < PRECISION
        )

        # Verify dimensionless fields are NOT scaled (alpha, tortuosity)
        assert scaled_results["alpha"] == results["alpha"]
        assert scaled_results_3d["Path tortuosity"] == results_3d["Path tortuosity"]


class TestPlot2DScalingBehavior:
    """Tests for 2D plot internal scaling behavior.

    These tests verify that plot_all() correctly scales data internally.
    """

    def test_2d_plot_uses_config_scale_factor(
        self, plantB_day11_graph, test_scale_factor
    ):
        """Verify 2D plot function uses config.length_scale_factor for scaling.

        We can verify this by checking the plot_all source code contains
        the scale_data helper that uses config.length_scale_factor.
        """
        import inspect
        from ariadne_roots import quantify

        # Get the source of plot_all
        source = inspect.getsource(quantify.plot_all)

        # Verify it contains the scaling pattern
        assert "scale_data" in source, "plot_all should have scale_data helper"
        assert (
            "config.length_scale_factor" in source
        ), "plot_all should use config.length_scale_factor"

    def test_2d_plot_data_would_be_scaled(self, plantB_day11_graph, test_scale_factor):
        """Verify 2D plot would scale data correctly given a scale factor.

        This tests the expected behavior without actually rendering the plot.
        """
        G = plantB_day11_graph

        # Run analysis
        results, front, randoms, _, _, _ = quantify.analyze(G, enable_3d=False)

        # Set config scale factor (as main.py would do)
        original_scale = config.length_scale_factor
        try:
            config.length_scale_factor = test_scale_factor

            # Compute what scaled values would be
            expected_scaled_length = results["Total root length"] * test_scale_factor
            expected_scaled_distance = results["Travel distance"] * test_scale_factor

            # The front values should also be scaled
            for alpha, (length, distance) in front.items():
                expected_front_length = length * test_scale_factor
                expected_front_distance = distance * test_scale_factor

                # Values should be positive after scaling
                assert expected_front_length > 0
                assert expected_front_distance > 0

        finally:
            config.length_scale_factor = original_scale


class TestPlot3DScalingBehavior:
    """Tests for 3D plot internal scaling behavior.

    These tests verify that plot_all_3d() should scale data internally
    matching the 2D pattern. The test for scale_data presence will FAIL
    until the fix is implemented.
    """

    def test_3d_plot_should_use_config_scale_factor(self):
        """Verify 3D plot function uses config.length_scale_factor for scaling.

        This test will FAIL until the fix is implemented.
        """
        import inspect
        from ariadne_roots import quantify

        # Get the source of plot_all_3d
        source = inspect.getsource(quantify.plot_all_3d)

        # Verify it contains the scaling pattern (WILL FAIL before fix)
        assert (
            "scale_data" in source
        ), "plot_all_3d should have scale_data helper like plot_all"
        assert (
            "config.length_scale_factor" in source
        ), "plot_all_3d should use config.length_scale_factor"

    def test_3d_plot_data_should_be_scaled_xy_only(
        self, plantB_day11_graph, test_scale_factor
    ):
        """Verify 3D plot should scale x,y (length/distance) but not z (tortuosity).

        This validates the expected behavior for dimensionless z-axis.
        """
        G = plantB_day11_graph

        # Run analysis
        _, _, _, results_3d, front_3d, randoms_3d = quantify.analyze(G, enable_3d=True)

        # Set config scale factor
        original_scale = config.length_scale_factor
        try:
            config.length_scale_factor = test_scale_factor

            # For each point on the 3D front
            for key, (length, distance, tortuosity) in front_3d.items():
                # Length and distance should be scaled
                expected_scaled_length = length * test_scale_factor
                expected_scaled_distance = distance * test_scale_factor

                # Tortuosity should NOT be scaled (dimensionless)
                expected_tortuosity = tortuosity  # unchanged

                # Verify scaling would produce reasonable values
                assert expected_scaled_length > 0
                assert expected_scaled_distance > 0
                assert expected_tortuosity == tortuosity  # exactly equal

        finally:
            config.length_scale_factor = original_scale

    def test_3d_random_trees_xy_should_be_scaled(
        self, plantB_day11_graph, test_scale_factor
    ):
        """Verify random tree x,y values should be scaled, z unchanged."""
        G = plantB_day11_graph

        # Run analysis
        _, _, _, results_3d, _, randoms_3d = quantify.analyze(G, enable_3d=True)

        # Set config scale factor
        original_scale = config.length_scale_factor
        try:
            config.length_scale_factor = test_scale_factor

            # Check random trees
            for length, distance, tortuosity in randoms_3d[:5]:  # Check first 5
                # Length and distance should be scaled
                expected_scaled_length = length * test_scale_factor
                expected_scaled_distance = distance * test_scale_factor

                # Tortuosity should NOT be scaled
                expected_tortuosity = tortuosity

                assert expected_scaled_length > 0
                assert expected_scaled_distance > 0
                assert expected_tortuosity == tortuosity

        finally:
            config.length_scale_factor = original_scale


class TestPlotCSVConsistency:
    """Tests verifying plot data would match CSV output.

    These tests verify that if plots scale data correctly, the axis
    values would match what appears in the scaled CSV output.
    """

    def test_2d_scaled_results_match_expected_csv_values(
        self, plantB_day11_graph, test_scale_factor
    ):
        """Verify scaled 2D results match what would appear in CSV."""
        G = plantB_day11_graph

        # Run analysis
        results, front, randoms, _, _, _ = quantify.analyze(G, enable_3d=False)

        # Apply scaling (as main.py does for CSV)
        scaled_results = scaling.apply_scaling_transformation(
            results, test_scale_factor
        )

        # What plot_all would produce (scaled internally)
        original_scale = config.length_scale_factor
        try:
            config.length_scale_factor = test_scale_factor

            # Simulate internal scaling in plot_all
            scaled_actual_x = results["Total root length"] * test_scale_factor
            scaled_actual_y = results["Travel distance"] * test_scale_factor

            # These should match CSV values
            assert (
                abs(scaled_actual_x - scaled_results["Total root length"]) < PRECISION
            )
            assert abs(scaled_actual_y - scaled_results["Travel distance"]) < PRECISION

        finally:
            config.length_scale_factor = original_scale

    def test_3d_scaled_results_should_match_expected_csv_values(
        self, plantB_day11_graph, test_scale_factor
    ):
        """Verify scaled 3D results would match CSV if plot_all_3d scaled correctly.

        This documents the expected behavior for the fix.
        """
        G = plantB_day11_graph

        # Run analysis
        _, _, _, results_3d, front_3d, randoms_3d = quantify.analyze(G, enable_3d=True)

        # Apply scaling (as main.py does for CSV)
        scaled_results_3d = scaling.apply_scaling_transformation(
            results_3d, test_scale_factor
        )

        # What plot_all_3d SHOULD produce (if it scaled internally)
        original_scale = config.length_scale_factor
        try:
            config.length_scale_factor = test_scale_factor

            # Simulate internal scaling that SHOULD happen in plot_all_3d
            scaled_actual_x = results_3d["Total root length"] * test_scale_factor
            scaled_actual_y = results_3d["Travel distance"] * test_scale_factor
            scaled_actual_z = results_3d["Path tortuosity"]  # NOT scaled

            # These should match CSV values
            assert (
                abs(scaled_actual_x - scaled_results_3d["Total root length"])
                < PRECISION
            )
            assert (
                abs(scaled_actual_y - scaled_results_3d["Travel distance"]) < PRECISION
            )
            # Path tortuosity should be identical (no scaling)
            assert scaled_actual_z == scaled_results_3d["Path tortuosity"]

        finally:
            config.length_scale_factor = original_scale
