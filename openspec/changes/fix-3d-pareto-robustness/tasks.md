## 1. Test Infrastructure (TDD: Red Phase Setup)

- [ ] 1.1 Create `tests/test_pareto_3d.py` with test structure and fixtures
- [ ] 1.2 Create fixture `make_simple_graph()` - valid 3-node connected graph
- [ ] 1.3 Create fixture `make_complex_graph()` - valid 10+ node graph
- [ ] 1.4 Create fixture `make_cyclic_graph()` - graph with a cycle
- [ ] 1.5 Create fixture `make_coincident_node_graph()` - node at base position
- [ ] 1.6 Verify fixtures work: `pytest tests/test_pareto_3d.py -v --collect-only`

## 2. Tests for graph_costs_3d_path_tortuosity (TDD: Red)

- [ ] 2.1 Write `test_graph_costs_3d_valid_simple_graph()` - expects 3 finite values
- [ ] 2.2 Write `test_graph_costs_3d_valid_complex_graph()` - verifies costs are positive
- [ ] 2.3 Write `test_graph_costs_3d_cycle_returns_three_inf()` - expects 3 inf values (WILL FAIL - bug exists)
- [ ] 2.4 Write `test_graph_costs_3d_coincident_node_no_divide_by_zero()` - expects no error (WILL FAIL - bug exists)
- [ ] 2.5 Write `test_graph_costs_3d_with_critical_nodes()` - verifies critical_nodes parameter
- [ ] 2.6 Run tests, confirm 2.3 and 2.4 fail: `pytest tests/test_pareto_3d.py -v -k graph_costs`

## 3. Tests for pareto_cost_3d_path_tortuosity (TDD: Red)

- [ ] 3.1 Write `test_pareto_cost_3d_alpha_only()` - alpha=1, beta=0
- [ ] 3.2 Write `test_pareto_cost_3d_beta_only()` - alpha=0, beta=1
- [ ] 3.3 Write `test_pareto_cost_3d_gamma_only()` - alpha=0, beta=0
- [ ] 3.4 Write `test_pareto_cost_3d_boundary_valid()` - alpha=0.5, beta=0.5
- [ ] 3.5 Write `test_pareto_cost_3d_invalid_alpha_beta()` - alpha=0.6, beta=0.6 (WILL FAIL - validation missing)
- [ ] 3.6 Run tests, confirm 3.5 fails: `pytest tests/test_pareto_3d.py -v -k pareto_cost`

## 4. Tests for Other 3D Functions (TDD: Red)

- [ ] 4.1 Write `test_pareto_steiner_3d_produces_tree()` - result is connected tree
- [ ] 4.2 Write `test_pareto_steiner_3d_respects_alpha_beta()` - different params give different trees
- [ ] 4.3 Write `test_pareto_front_3d_structure()` - returns expected data shape
- [ ] 4.4 Write `test_random_tree_3d_produces_tree()` - result is connected tree
- [ ] 4.5 Write `test_random_tree_3d_returns_three_values()` - returns 3 costs
- [ ] 4.6 Run all tests: `pytest tests/test_pareto_3d.py -v`

## 5. Fix graph_costs_3d_path_tortuosity (TDD: Green)

- [ ] 5.1 Fix cycle detection: return 3 inf values at `pareto_functions.py:157`
- [ ] 5.2 Add division-by-zero protection at `pareto_functions.py:189-192`
- [ ] 5.3 Run tests 2.3 and 2.4, verify they now pass
- [ ] 5.4 Run full test suite to ensure no regressions: `pytest tests/test_pareto_3d.py -v`

## 6. Fix pareto_cost_3d_path_tortuosity (TDD: Green)

- [ ] 6.1 Add assertion `assert alpha + beta <= 1` at `pareto_functions.py:300`
- [ ] 6.2 Run test 3.5, verify it now passes
- [ ] 6.3 Run full test suite to ensure no regressions

## 7. Fix 3D Results Scaling (TDD: Green)

- [ ] 7.1 Write `test_3d_results_scaling_applied()` - integration test for scaling
- [ ] 7.2 Run test, verify it fails (3D results not scaled)
- [ ] 7.3 Apply `scaling.apply_scaling_transformation()` to `results_3d` in `main.py:1262-1269`
- [ ] 7.4 Run test, verify it now passes
- [ ] 7.5 Manual verification: compare scaled 2D and 3D CSV output values

## 8. Code Quality and Coverage (TDD: Refactor)

- [ ] 8.1 Run full test suite with coverage: `pytest tests/test_pareto_3d.py --cov=ariadne_roots.pareto_functions --cov-report=term-missing`
- [ ] 8.2 Verify 3D functions have >= 80% coverage
- [ ] 8.3 Run linter: `ruff check src/ariadne_roots/pareto_functions.py`
- [ ] 8.4 Run formatter: `black src/ariadne_roots/pareto_functions.py`
- [ ] 8.5 Ensure all docstrings are Google style

## 9. GUI Checkbox for 3D Analysis Toggle (TDD: Red)

- [ ] 9.1 Write `test_config_enable_3d_analysis_default()` - verify default is False
- [ ] 9.2 Write `test_3d_analysis_skipped_when_disabled()` - verify no 3D output when disabled
- [ ] 9.3 Write `test_3d_analysis_runs_when_enabled()` - verify 3D output when enabled
- [ ] 9.4 Run tests, confirm they fail (toggle not implemented)

## 10. Implement 3D Analysis Toggle (TDD: Green)

- [ ] 10.1 Add `enable_3d_analysis = False` to `config.py`
- [ ] 10.2 Add checkbox to `ask_scale()` in `main.py:1054-1150`:
  - Label: "Include 3D Pareto analysis (slower)"
  - Default: unchecked
  - Store in `self.enable_3d_analysis` and `config.enable_3d_analysis`
- [ ] 10.3 Wrap 3D analysis code in `main.py:1237-1291` with `if config.enable_3d_analysis:`
- [ ] 10.4 Skip 3D CSV file creation when disabled
- [ ] 10.5 Skip 3D plot generation when disabled
- [ ] 10.6 Run tests 9.1-9.3, verify they pass

## 11. 3D Surface Plot Visualization (TDD: Red)

- [ ] 11.1 Write `test_plot_all_3d_creates_surface()` - verify surface plot created
- [ ] 11.2 Write `test_plot_all_3d_has_colorbar()` - verify colorbar present
- [ ] 11.3 Write `test_plot_all_3d_handles_collinear()` - verify graceful handling
- [ ] 11.4 Run tests, confirm they fail (line plot, not surface)

## 12. Implement 3D Surface Plot (TDD: Green)

- [ ] 12.1 Import `matplotlib.tri` in `quantify.py`
- [ ] 12.2 Replace `ax.plot()` with `ax.plot_trisurf()` in `plot_all_3d()`:
  - Create `Triangulation` from front x, y points
  - Use colormap (e.g., 'viridis') for z values (path coverage)
  - Set alpha for transparency
- [ ] 12.3 Add colorbar showing path coverage gradient
- [ ] 12.4 Keep scatter plots for actual plant (orange X) and random trees (green +)
- [ ] 12.5 Update axis labels and title
- [ ] 12.6 Handle edge case: collinear points (log warning, fall back to scatter)
- [ ] 12.7 Run tests 11.1-11.3, verify they pass

## 13. Documentation and Cleanup

- [ ] 13.1 Update CHANGELOG.md with all changes:
  - Bug fixes (cycle detection, division by zero, alpha+beta validation)
  - 3D scaling consistency
  - GUI checkbox for optional 3D analysis
  - 3D surface plot visualization
- [ ] 13.2 Add inline comments explaining edge case handling
- [ ] 13.3 Update docstrings for modified functions
- [ ] 13.4 Run full project test suite: `pytest tests/ -v`
- [ ] 13.5 Run linter and formatter on all modified files
- [ ] 13.6 Verify CI passes on branch
- [ ] 13.7 Manual QA: test with real root data with 3D enabled/disabled