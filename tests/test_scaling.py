"""Tests for the scaling module."""

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

    def test_tradeoff_fields_scaling(self):
        """Test that tradeoff fields are handled correctly during scaling.

        Tradeoff, Actual_ratio, and Optimal_ratio are dimensionless ratios
        and should NOT be scaled. Steiner/Satellite lengths and distances
        should be scaled.
        """
        results = {
            # Dimensionless ratios - should NOT be scaled
            "Tradeoff": 2.5,
            "Actual_ratio": 0.38,
            "Optimal_ratio": 0.15,
            # Length/distance metrics - SHOULD be scaled
            "Steiner_length": 4920.75,
            "Steiner_distance": 39266.99,
            "Satellite_length": 32523.42,
            "Satellite_distance": 32523.42,
            # Other metric for comparison
            "Total root length": 100.0,
        }

        scaled = apply_scaling_transformation(results, 2.0)

        # Dimensionless ratios should NOT be scaled
        assert scaled["Tradeoff"] == 2.5
        assert scaled["Actual_ratio"] == 0.38
        assert scaled["Optimal_ratio"] == 0.15

        # Length/distance metrics should be scaled
        assert scaled["Steiner_length"] == 4920.75 * 2.0
        assert scaled["Steiner_distance"] == 39266.99 * 2.0
        assert scaled["Satellite_length"] == 32523.42 * 2.0
        assert scaled["Satellite_distance"] == 32523.42 * 2.0
        assert scaled["Total root length"] == 200.0

    def test_3d_weight_fields_not_scaled(self):
        """Test that 3D Pareto weight fields (beta_3d, gamma_3d) are NOT scaled.

        These are dimensionless weights in range [0, 1] representing the
        trade-off position on the Pareto surface. Scaling them would produce
        scientifically meaningless values.
        """
        results = {
            "beta_3d": 0.02,
            "gamma_3d": 0.98,
            "beta_3d (random)": 0.15,
            "gamma_3d (random)": 0.45,
            "Total root length": 100.0,  # Should be scaled
        }

        scaled = apply_scaling_transformation(
            results, 0.01
        )  # Small factor to make bug obvious

        # Weight fields should NOT be scaled (remain unchanged)
        assert (
            scaled["beta_3d"] == 0.02
        ), "beta_3d should not be scaled (dimensionless weight)"
        assert (
            scaled["gamma_3d"] == 0.98
        ), "gamma_3d should not be scaled (dimensionless weight)"
        assert (
            scaled["beta_3d (random)"] == 0.15
        ), "beta_3d (random) should not be scaled"
        assert (
            scaled["gamma_3d (random)"] == 0.45
        ), "gamma_3d (random) should not be scaled"
        # Verify length fields ARE scaled
        assert scaled["Total root length"] == 1.0

    def test_3d_epsilon_fields_not_scaled(self):
        """Test that 3D epsilon indicator fields are NOT scaled.

        Epsilon is the multiplicative distance from the Pareto front (ratio >= 1.0).
        Scaling it would produce scientifically meaningless values.
        """
        results = {
            "epsilon_3d": 1.078,
            "epsilon_3d_material": 1.02,
            "epsilon_3d_transport": 1.05,
            "epsilon_3d_coverage": 1.078,
            "epsilon_3d (random)": 3.15,
            "epsilon_3d_material (random)": 3.15,
            "epsilon_3d_transport (random)": 1.8,
            "epsilon_3d_coverage (random)": 2.1,
            "Total root length": 100.0,
        }

        scaled = apply_scaling_transformation(results, 0.01)

        # Epsilon fields should NOT be scaled
        assert scaled["epsilon_3d"] == 1.078, "epsilon_3d should not be scaled (ratio)"
        assert scaled["epsilon_3d_material"] == 1.02
        assert scaled["epsilon_3d_transport"] == 1.05
        assert scaled["epsilon_3d_coverage"] == 1.078
        assert scaled["epsilon_3d (random)"] == 3.15
        assert scaled["epsilon_3d_material (random)"] == 3.15
        assert scaled["epsilon_3d_transport (random)"] == 1.8
        assert scaled["epsilon_3d_coverage (random)"] == 2.1

    def test_3d_scaling_preserves_dimensionless_fields_integration(self):
        """Integration test: verify all 3D dimensionless fields are preserved after scaling.

        This simulates a real 3D analysis output and verifies that scaling
        for length conversion (e.g., pixels to mm) preserves all dimensionless
        ratio and weight fields while correctly scaling length fields.
        """
        # Simulated 3D analysis output (realistic values)
        results_3d = {
            # Dimensionless fields - SHOULD NOT be scaled
            "alpha_3d": 0.0,
            "beta_3d": 0.02,
            "gamma_3d": 0.98,
            "epsilon_3d": 1.078,
            "epsilon_3d_material": 1.02,
            "epsilon_3d_transport": 1.05,
            "epsilon_3d_coverage": 1.078,
            "alpha_3d (random)": 0.0,
            "beta_3d (random)": 0.15,
            "gamma_3d (random)": 0.45,
            "epsilon_3d (random)": 3.15,
            "epsilon_3d_material (random)": 3.15,
            "epsilon_3d_transport (random)": 1.8,
            "epsilon_3d_coverage (random)": 2.1,
            "Path tortuosity": 15.5,
            "Path tortuosity (random)": 12.3,
            # Length fields - SHOULD be scaled
            "Total root length": 5000.0,
            "Travel distance": 8000.0,
            "Total root length (random)": 6500.0,
            "Travel distance (random)": 9200.0,
        }

        scale_factor = 0.0254  # Example: pixels to mm

        scaled = apply_scaling_transformation(results_3d, scale_factor)

        # Verify all dimensionless fields are unchanged
        dimensionless_fields = [
            "alpha_3d",
            "beta_3d",
            "gamma_3d",
            "epsilon_3d",
            "epsilon_3d_material",
            "epsilon_3d_transport",
            "epsilon_3d_coverage",
            "alpha_3d (random)",
            "beta_3d (random)",
            "gamma_3d (random)",
            "epsilon_3d (random)",
            "epsilon_3d_material (random)",
            "epsilon_3d_transport (random)",
            "epsilon_3d_coverage (random)",
            "Path tortuosity",
            "Path tortuosity (random)",
        ]

        for field in dimensionless_fields:
            assert scaled[field] == results_3d[field], (
                f"{field} should not be scaled (dimensionless). "
                f"Expected {results_3d[field]}, got {scaled[field]}"
            )

        # Verify length fields ARE scaled
        assert (
            scaled["Total root length"]
            == results_3d["Total root length"] * scale_factor
        )
        assert scaled["Travel distance"] == results_3d["Travel distance"] * scale_factor
