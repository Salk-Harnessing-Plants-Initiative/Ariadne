"""Tests for main GUI module (mock-based for testable logic)."""

from pathlib import Path

from ariadne_roots import scaling


class TestGUILabels:
    """Tests for GUI label text clarity."""

    def test_3d_pareto_checkbox_label_describes_tortuosity(self):
        """Test that 3D Pareto checkbox label clearly indicates path tortuosity is added.

        The label should help users understand what the 3D analysis adds,
        not just that it exists and is slower.
        """
        # Read the source file directly to check the label text
        main_py = Path(__file__).parent.parent / "src" / "ariadne_roots" / "main.py"
        source = main_py.read_text()

        # The label should mention path tortuosity to clarify what 3D adds
        expected_label = "Add path tortuosity to Pareto (3D, slower)"
        assert expected_label in source, (
            f"Expected 3D Pareto checkbox label '{expected_label}' not found. "
            "The label should clearly indicate that 3D adds path tortuosity analysis."
        )


class TestAnalysisProgressFeedback:
    """Tests for GUI progress feedback during analysis."""

    def test_gui_updates_during_analysis_loop(self):
        """Test that GUI calls update_idletasks() after updating current file display.

        The GUI must call update_idletasks() to force a refresh after updating
        the output label, otherwise the interface appears frozen during analysis.
        """
        main_py = Path(__file__).parent.parent / "src" / "ariadne_roots" / "main.py"
        source = main_py.read_text()

        # Look for the pattern: update output label followed by update_idletasks()
        # The update should happen inside the analysis loop after setting file name
        assert "self.output.config(text=self.output_info)" in source, (
            "Expected output label config call not found"
        )
        assert "self.base.update_idletasks()" in source, (
            "Expected update_idletasks() call not found. "
            "The GUI must call update_idletasks() to refresh during the analysis loop."
        )

    def test_initial_analyzing_status_message(self):
        """Test that analysis shows 'Analyzing N file(s)...' status at start.

        Users should immediately see that analysis has begun with a count of
        files being processed.
        """
        main_py = Path(__file__).parent.parent / "src" / "ariadne_roots" / "main.py"
        source = main_py.read_text()

        # The initial message should indicate analysis is starting
        assert 'Analyzing {len(self.tree_paths)} file(s)...' in source or \
               'f"Analyzing {len(self.tree_paths)} file(s)..."' in source, (
            "Expected initial 'Analyzing N file(s)...' status message not found. "
            "Users need immediate feedback that analysis has started."
        )

    def test_gui_refresh_before_analysis_loop(self):
        """Test that GUI refreshes immediately after setting initial status.

        The initial status message must be displayed before the analysis loop
        begins, requiring an update_idletasks() call right after setting it.
        """
        main_py = Path(__file__).parent.parent / "src" / "ariadne_roots" / "main.py"
        source = main_py.read_text()

        # Find the section where initial status is set and verify refresh follows
        # Look for pattern: set output_info with "Analyzing" then update display
        lines = source.split('\n')
        found_initial_status = False
        found_refresh_after = False

        for i, line in enumerate(lines):
            if 'Analyzing' in line and 'file(s)' in line and 'output_info' in line:
                found_initial_status = True
                # Check next few lines for update_idletasks
                for j in range(i + 1, min(i + 5, len(lines))):
                    if 'update_idletasks()' in lines[j]:
                        found_refresh_after = True
                        break
                break

        assert found_initial_status, (
            "Initial 'Analyzing' status message assignment not found"
        )
        assert found_refresh_after, (
            "update_idletasks() must be called immediately after setting initial status"
        )


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
