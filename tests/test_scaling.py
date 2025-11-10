"""Tests for the scaling module."""

import pytest
from ariadne_roots.scaling import apply_scaling_transformation


class TestScalingTransformation:
    """Test scaling transformation logic."""

    def test_excluded_fields_not_scaled(self):
        """Test that excluded fields are NOT scaled."""
        results = {
            "LR density": 0.5,
            "alpha": 1.2,
            "Mean LR angles": 45.0,
            "Median LR angles": 42.0,
            "LR count": 10,
            "Branched Zone density": 0.3,
            "scaling distance to front": 0.8,
            "Tortuosity": 1.1,
            "scaling (random)": 0.9,
        }

        scaled = apply_scaling_transformation(results, 2.0)

        # All excluded fields should remain unchanged
        assert scaled["LR density"] == 0.5
        assert scaled["alpha"] == 1.2
        assert scaled["Mean LR angles"] == 45.0
        assert scaled["Median LR angles"] == 42.0
        assert scaled["LR count"] == 10
        assert scaled["Branched Zone density"] == 0.3
        assert scaled["scaling distance to front"] == 0.8
        assert scaled["Tortuosity"] == 1.1
        assert scaled["scaling (random)"] == 0.9

    def test_numeric_fields_scaled_correctly(self):
        """Test that numeric fields are scaled by the factor."""
        results = {
            "Total root length": 100.0,
            "PR length": 50.0,
            "Travel distance": 75.0,
        }

        scaled = apply_scaling_transformation(results, 2.5)

        # Numeric fields should be multiplied by scale_factor
        assert scaled["Total root length"] == 250.0
        assert scaled["PR length"] == 125.0
        assert scaled["Travel distance"] == 187.5

    def test_array_fields_scaled_element_wise(self):
        """Test that array fields are scaled element-wise."""
        results = {
            "LR lengths": [10.0, 20.0, 30.0],
            "LR minimal lengths": [5.0, 15.0, 25.0],
        }

        scaled = apply_scaling_transformation(results, 2.0)

        # Each element should be scaled
        assert scaled["LR lengths"] == [20.0, 40.0, 60.0]
        assert scaled["LR minimal lengths"] == [10.0, 30.0, 50.0]

    def test_non_numeric_fields_preserved(self):
        """Test that non-numeric fields are preserved unchanged."""
        results = {
            "filename": "test.json",
            "some_string": "hello world",
        }

        scaled = apply_scaling_transformation(results, 3.0)

        # Non-numeric fields should remain unchanged
        assert scaled["filename"] == "test.json"
        assert scaled["some_string"] == "hello world"

    def test_scale_factor_zero(self):
        """Test edge case: scale factor of 0."""
        results = {
            "Total root length": 100.0,
            "PR length": 50.0,
        }

        scaled = apply_scaling_transformation(results, 0)

        # Should scale to 0 without error
        assert scaled["Total root length"] == 0.0
        assert scaled["PR length"] == 0.0

    def test_scale_factor_non_integer(self):
        """Test edge case: non-integer scale factor."""
        results = {
            "Total root length": 10,
        }

        scaled = apply_scaling_transformation(results, 2.54)

        # Should maintain precision
        assert scaled["Total root length"] == 25.4

    def test_none_values_preserved(self):
        """Test edge case: None values in results."""
        results = {
            "some_field": None,
            "LR density": 0.5,  # excluded field
        }

        scaled = apply_scaling_transformation(results, 2.0)

        # None should be preserved
        assert scaled["some_field"] is None
        assert scaled["LR density"] == 0.5

    def test_empty_arrays(self):
        """Test edge case: empty arrays."""
        results = {
            "LR lengths": [],
            "LR minimal lengths": [],
        }

        scaled = apply_scaling_transformation(results, 2.0)

        # Empty arrays should remain empty
        assert scaled["LR lengths"] == []
        assert scaled["LR minimal lengths"] == []

    def test_mixed_types_in_results(self):
        """Test realistic scenario with mixed field types."""
        results = {
            "filename": "plant_A.json",
            "Total root length": 150.0,
            "LR density": 0.45,  # excluded
            "LR lengths": [10.0, 20.0],
            "alpha": 1.5,  # excluded
            "PR length": 75.0,
        }

        scaled = apply_scaling_transformation(results, 2.0)

        # Check each field is handled correctly
        assert scaled["filename"] == "plant_A.json"  # string preserved
        assert scaled["Total root length"] == 300.0  # numeric scaled
        assert scaled["LR density"] == 0.45  # excluded not scaled
        assert scaled["LR lengths"] == [20.0, 40.0]  # array scaled
        assert scaled["alpha"] == 1.5  # excluded not scaled
        assert scaled["PR length"] == 150.0  # numeric scaled

    def test_custom_excluded_fields(self):
        """Test using custom excluded fields set."""
        results = {
            "field_A": 100.0,
            "field_B": 50.0,
        }

        # Exclude field_B from scaling
        scaled = apply_scaling_transformation(results, 2.0, excluded_fields={"field_B"})

        assert scaled["field_A"] == 200.0  # scaled
        assert scaled["field_B"] == 50.0  # not scaled (excluded)

    def test_negative_scale_factor(self):
        """Test edge case: negative scale factor."""
        results = {
            "Total root length": 100.0,
        }

        scaled = apply_scaling_transformation(results, -2.0)

        # Should apply negative scaling
        assert scaled["Total root length"] == -200.0

    def test_integer_to_float_conversion(self):
        """Test that integer values are converted to float after scaling."""
        results = {
            "Total root length": 100,  # integer
        }

        scaled = apply_scaling_transformation(results, 2.5)

        # Should be float
        assert scaled["Total root length"] == 250.0
        assert isinstance(scaled["Total root length"], float)

    def test_invalid_array_values_preserved(self):
        """Test that arrays with non-numeric values are preserved unchanged."""
        results = {
            "LR lengths": ["invalid", "data", None],
        }

        scaled = apply_scaling_transformation(results, 2.0)

        # Should preserve invalid array unchanged
        assert scaled["LR lengths"] == ["invalid", "data", None]

    def test_substring_matching_excludes_related_fields(self):
        """Verify substring matching excludes fields containing patterns."""
        results = {
            "LR density": 0.5,
            "Branched Zone density": 0.3,
            "alpha": 1.2,
            "Mean LR angles": 45.0,
            "Total root length": 100.0,
        }

        scaled = apply_scaling_transformation(results, 2.0)

        # Fields containing excluded patterns should NOT be scaled
        assert scaled["LR density"] == 0.5
        assert scaled["Branched Zone density"] == 0.3
        assert scaled["alpha"] == 1.2
        assert scaled["Mean LR angles"] == 45.0

        # Other fields should be scaled
        assert scaled["Total root length"] == 200.0

    def test_lr_angles_field_not_scaled(self):
        """Verify LR angles field is excluded (angles are dimensionless).

        This tests that substring matching correctly excludes "LR angles"
        because it contains "angles" pattern from "Mean LR angles" exclusion.
        """
        results = {
            "LR angles": [30.0, 45.0, 60.0],
            "LR lengths": [10.0, 20.0, 30.0],  # Should be scaled
            "Total root length": 100.0,
        }

        scaled = apply_scaling_transformation(results, 2.0)

        # Angles are dimensionless - should NOT be scaled (due to "angles" pattern)
        assert scaled["LR angles"] == [30.0, 45.0, 60.0]
        # Lengths should be scaled
        assert scaled["LR lengths"] == [20.0, 40.0, 60.0]
        assert scaled["Total root length"] == 200.0
