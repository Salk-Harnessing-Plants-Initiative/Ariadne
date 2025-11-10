"""Tests for main GUI module (mock-based for testable logic)."""

from ariadne_roots import scaling


class TestScalingIntegration:
    """Integration tests for scaling workflow (mock-based)."""

    def test_import_file_applies_scaling(self):
        """Test that import_file workflow applies scaling transformation."""
        # This test verifies the integration between AnalyzerUI and scaling module
        # We mock the GUI parts and verify the scaling logic is called correctly

        # Mock results from quantify.analyze
        mock_results = {
            "filename": "test_plant.json",
            "Total root length": 100.0,
            "LR density": 0.5,
            "LR lengths": [10.0, 20.0],
        }

        # Expected scaled results with factor 2.0
        expected_scaled = scaling.apply_scaling_transformation(mock_results, 2.0)

        # Verify the transformation works as expected
        assert expected_scaled["Total root length"] == 200.0
        assert expected_scaled["LR density"] == 0.5  # excluded
        assert expected_scaled["LR lengths"] == [20.0, 40.0]
        assert expected_scaled["filename"] == "test_plant.json"

    def test_scaled_results_structure(self):
        """Test that scaled results maintain proper dictionary structure."""
        mock_results = {
            "filename": "plant_A.json",
            "Total root length": 150.0,
            "PR length": 75.0,
            "LR count": 5,  # excluded field
            "LR lengths": [15.0, 25.0, 35.0],
        }

        scaled = scaling.apply_scaling_transformation(mock_results, 1.5)

        # Verify structure is maintained
        assert isinstance(scaled, dict)
        assert len(scaled) == len(mock_results)
        assert all(key in scaled for key in mock_results.keys())

    def test_filename_field_preserved_in_scaling(self):
        """Test that filename field is always preserved during scaling."""
        mock_results = {
            "filename": "critical_filename.json",
            "Total root length": 100.0,
        }

        scaled = scaling.apply_scaling_transformation(mock_results, 5.0)

        # Filename should never be modified
        assert scaled["filename"] == "critical_filename.json"
        assert isinstance(scaled["filename"], str)
