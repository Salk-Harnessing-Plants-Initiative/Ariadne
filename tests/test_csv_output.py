"""Tests for CSV output validation.

These tests verify that analysis results have correct types and ranges
for clean CSV serialization. They were created as part of the TDD approach
to fix the np.float64 serialization bug reported by Matt Platre.

Tests cover:
- Field type validation (Python native types, not numpy)
- Field range validation (angles 0-180, lengths >= 0, etc.)
- CSV serialization (no numpy type strings in output)
"""

import csv
import io
import json

import numpy as np
import pytest
from networkx.readwrite import json_graph

from ariadne_roots import quantify


class TestCSVFieldTypes:
    """Test that all CSV fields have correct Python native types."""

    def test_numeric_fields_are_python_types(self, plantB_day11_json):
        """Verify numeric fields are Python int/float, not numpy types."""
        with open(plantB_day11_json) as f:
            data = json.load(f)
            graph = json_graph.adjacency_graph(data)

        results, _, _ = quantify.analyze(graph)

        # Numeric fields that should be float or int
        numeric_fields = [
            "Total root length",
            "Travel distance",
            "PR length",
            "PR_minimal_length",
            "Basal Zone length",
            "Branched Zone length",
            "Apical Zone length",
            "Mean LR lengths",
            "Mean LR minimal lengths",
            "Median LR lengths",
            "Median LR minimal lengths",
            "sum LR minimal lengths",
            "Mean LR angles",
            "Median LR angles",
            "LR count",
            "LR density",
            "Branched Zone density",
            "Barycenter x displacement",
            "Barycenter y displacement",
            "Total minimal Distance",
            "Tortuosity",
            "Convex Hull Area",
        ]

        for field in numeric_fields:
            value = results.get(field)
            if value is not None:
                assert isinstance(
                    value, (int, float)
                ), f"{field} should be numeric, got {type(value)}"
                assert not isinstance(
                    value, (np.floating, np.integer)
                ), f"{field} should not be numpy type, got {type(value)}"

    def test_lr_angles_are_python_floats(self, plantB_day11_json):
        """Verify LR angles are Python floats, not numpy types.

        This is the specific bug reported by Matt Platre where CSV output
        contained np.float64(...) instead of plain numbers.
        """
        with open(plantB_day11_json) as f:
            data = json.load(f)
            graph = json_graph.adjacency_graph(data)

        results, _, _ = quantify.analyze(graph)

        lr_angles = results.get("LR angles", [])
        assert isinstance(lr_angles, list), "LR angles should be a list"

        for i, angle in enumerate(lr_angles):
            assert isinstance(
                angle, (int, float)
            ), f"LR angles[{i}] should be Python float, got {type(angle)}"
            assert not isinstance(
                angle, np.floating
            ), f"LR angles[{i}] should not be np.floating, got {type(angle)}"

    def test_lr_lengths_are_python_floats(self, plantB_day11_json):
        """Verify LR lengths are Python floats, not numpy types."""
        with open(plantB_day11_json) as f:
            data = json.load(f)
            graph = json_graph.adjacency_graph(data)

        results, _, _ = quantify.analyze(graph)

        lr_lengths = results.get("LR lengths", [])
        assert isinstance(lr_lengths, list), "LR lengths should be a list"

        for i, length in enumerate(lr_lengths):
            assert isinstance(
                length, (int, float)
            ), f"LR lengths[{i}] should be Python float, got {type(length)}"
            assert not isinstance(
                length, np.floating
            ), f"LR lengths[{i}] should not be np.floating, got {type(length)}"

    def test_lr_minimal_lengths_are_python_floats(self, plantB_day11_json):
        """Verify LR minimal lengths are Python floats, not numpy types."""
        with open(plantB_day11_json) as f:
            data = json.load(f)
            graph = json_graph.adjacency_graph(data)

        results, _, _ = quantify.analyze(graph)

        lr_minimal_lengths = results.get("LR minimal lengths", [])
        assert isinstance(
            lr_minimal_lengths, list
        ), "LR minimal lengths should be a list"

        for i, length in enumerate(lr_minimal_lengths):
            assert isinstance(
                length, (int, float)
            ), f"LR minimal lengths[{i}] should be Python float, got {type(length)}"
            assert not isinstance(
                length, np.floating
            ), f"LR minimal lengths[{i}] should not be np.floating, got {type(length)}"


class TestCSVFieldRanges:
    """Test that CSV fields have expected value ranges."""

    def test_positive_length_fields(self, plantB_day11_json):
        """Verify length fields are non-negative."""
        with open(plantB_day11_json) as f:
            data = json.load(f)
            graph = json_graph.adjacency_graph(data)

        results, _, _ = quantify.analyze(graph)

        positive_fields = [
            "Total root length",
            "Travel distance",
            "PR length",
            "LR count",
            "Total minimal Distance",
        ]

        for field in positive_fields:
            value = results.get(field)
            if value is not None:
                assert value >= 0, f"{field} should be non-negative, got {value}"

    def test_lr_angles_in_valid_range(self, plantB_day11_json):
        """Verify LR angles are between 0 and 180 degrees."""
        with open(plantB_day11_json) as f:
            data = json.load(f)
            graph = json_graph.adjacency_graph(data)

        results, _, _ = quantify.analyze(graph)

        lr_angles = results.get("LR angles", [])
        for i, angle in enumerate(lr_angles):
            assert 0 <= angle <= 180, f"LR angles[{i}] = {angle} out of range [0, 180]"

        mean_angle = results.get("Mean LR angles")
        if mean_angle is not None:
            assert 0 <= mean_angle <= 180, f"Mean LR angles = {mean_angle} out of range"

        median_angle = results.get("Median LR angles")
        if median_angle is not None:
            assert (
                0 <= median_angle <= 180
            ), f"Median LR angles = {median_angle} out of range"

    def test_density_fields_non_negative(self, plantB_day11_json):
        """Verify density fields are non-negative."""
        with open(plantB_day11_json) as f:
            data = json.load(f)
            graph = json_graph.adjacency_graph(data)

        results, _, _ = quantify.analyze(graph)

        if results.get("LR density") is not None:
            assert results["LR density"] >= 0, "LR density should be non-negative"

        if results.get("Branched Zone density") is not None:
            assert (
                results["Branched Zone density"] >= 0
            ), "Branched Zone density should be non-negative"

    def test_alpha_in_valid_range(self, plantB_day11_json):
        """Verify alpha is between 0 and 1."""
        with open(plantB_day11_json) as f:
            data = json.load(f)
            graph = json_graph.adjacency_graph(data)

        results, _, _ = quantify.analyze(graph)

        alpha = results.get("alpha")
        if alpha is not None:
            assert 0 <= alpha <= 1, f"alpha = {alpha} should be in range [0, 1]"


class TestCSVSerialization:
    """Test that CSV serialization produces clean output."""

    def test_csv_contains_no_numpy_types(self, plantB_day11_json):
        """Verify CSV output contains no numpy type representations.

        This is the core test for the bug Matt reported where CSV files
        contained 'np.float64(...)' instead of plain numbers.
        """
        with open(plantB_day11_json) as f:
            data = json.load(f)
            graph = json_graph.adjacency_graph(data)

        results, _, _ = quantify.analyze(graph)

        # Serialize to CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=results.keys())
        writer.writeheader()
        writer.writerow(results)

        csv_content = output.getvalue()

        assert "np.float64" not in csv_content, (
            f"CSV contains np.float64. "
            f"Found in: {[k for k, v in results.items() if 'np.float64' in str(v)]}"
        )
        assert "np.int64" not in csv_content, "CSV contains np.int64"
        assert "numpy" not in csv_content.lower(), "CSV contains numpy reference"

    def test_array_fields_serialize_cleanly(self, plantB_day11_json):
        """Verify array fields serialize as readable lists, not numpy arrays."""
        with open(plantB_day11_json) as f:
            data = json.load(f)
            graph = json_graph.adjacency_graph(data)

        results, _, _ = quantify.analyze(graph)

        # Check string representation of array fields
        for field in ["LR angles", "LR lengths", "LR minimal lengths"]:
            value = results.get(field, [])
            str_repr = str(value)

            assert "np.float64" not in str_repr, (
                f"{field} contains np.float64 in string representation: "
                f"{str_repr[:100]}..."
            )
            assert (
                "numpy" not in str_repr.lower()
            ), f"{field} contains numpy in string representation"


class TestMattPlatreData:
    """Tests using Matt Platre's data from v0.1.0a1 bug report.

    These tests verify the np.float64 serialization fix works on the
    actual data that exposed the bug.
    """

    def test_matt_exp1_no_numpy_types(self, matt_etoh_exp1_plantB_day10_json):
        """Verify EtOH EXP1 data has no numpy types in results."""
        with open(matt_etoh_exp1_plantB_day10_json) as f:
            data = json.load(f)
            graph = json_graph.adjacency_graph(data)

        results, _, _ = quantify.analyze(graph)

        # Check LR angles specifically (the field Matt reported)
        for i, angle in enumerate(results.get("LR angles", [])):
            assert isinstance(angle, float), f"LR angles[{i}] is {type(angle)}"
            assert not isinstance(angle, np.floating)

        # Check CSV serialization
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=results.keys())
        writer.writerow(results)
        assert "np.float64" not in output.getvalue()

    def test_matt_exp2_no_numpy_types(self, matt_etoh_exp2_plantB_day11_json):
        """Verify EtOH EXP2 data has no numpy types in results."""
        with open(matt_etoh_exp2_plantB_day11_json) as f:
            data = json.load(f)
            graph = json_graph.adjacency_graph(data)

        results, _, _ = quantify.analyze(graph)

        # Check LR angles specifically (the field Matt reported)
        for i, angle in enumerate(results.get("LR angles", [])):
            assert isinstance(angle, float), f"LR angles[{i}] is {type(angle)}"
            assert not isinstance(angle, np.floating)

        # Check CSV serialization
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=results.keys())
        writer.writerow(results)
        assert "np.float64" not in output.getvalue()

    def test_matt_exp3_no_numpy_types(self, matt_etoh_exp3_plantE_day11_json):
        """Verify EtOH EXP3 data (largest file) has no numpy types in results."""
        with open(matt_etoh_exp3_plantE_day11_json) as f:
            data = json.load(f)
            graph = json_graph.adjacency_graph(data)

        results, _, _ = quantify.analyze(graph)

        # Check LR angles specifically (the field Matt reported)
        for i, angle in enumerate(results.get("LR angles", [])):
            assert isinstance(angle, float), f"LR angles[{i}] is {type(angle)}"
            assert not isinstance(angle, np.floating)

        # Check CSV serialization
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=results.keys())
        writer.writerow(results)
        assert "np.float64" not in output.getvalue()

    def test_matt_data_valid_ranges(self, matt_etoh_exp1_plantB_day10_json):
        """Verify Matt's data produces valid ranges for all fields."""
        with open(matt_etoh_exp1_plantB_day10_json) as f:
            data = json.load(f)
            graph = json_graph.adjacency_graph(data)

        results, _, _ = quantify.analyze(graph)

        # LR angles should be 0-180
        for angle in results.get("LR angles", []):
            assert 0 <= angle <= 180

        # Lengths should be positive
        assert results["Total root length"] > 0
        assert results["PR length"] > 0

        # Alpha should be 0-1
        assert 0 <= results["alpha"] <= 1
