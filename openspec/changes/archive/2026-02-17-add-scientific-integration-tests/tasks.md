## 1. Create Synthetic Test Data Generator

- [x] 1.1 Create test graph generator functions in `tests/test_scientific_integration.py`
- [x] 1.2 Implement `create_graph_with_attributes()` - generic helper for test graphs
- [x] 1.3 Implement `simple_straight_line` fixture - straight line root with known costs
- [x] 1.4 Implement `simple_y_branch` fixture - Y-shaped root with branching
- [x] 1.5 Implement `tortuous_path` fixture - zigzag path with known tortuosity > 1

## 2. Compute and Save Expected Values

- [x] 2.1 Create `ExpectedValues` class with pre-computed expected results
- [x] 2.2 Compute expected `Total root length` manually for each test graph
- [x] 2.3 Compute expected `Travel distance` manually for each test graph (with/without critical nodes)
- [x] 2.4 Compute expected `Path tortuosity` manually for each test graph
- [x] 2.5 Document calculation methodology in code comments
- [ ] 2.6 Compute expected Pareto front corner values (Steiner, Satellite) - deferred

## 3. Core Function Integration Tests (2D)

- [x] 3.1 Create `tests/test_scientific_integration.py` with `TestCore2DParetoGraphCosts` class
- [x] 3.2 Test `graph_costs()` returns exact expected values for synthetic graphs
- [x] 3.3 Test `pareto_front()` generates front with expected alpha range (0.0 to 1.0)
- [x] 3.4 Test `distance_from_front()` returns alpha in valid range and epsilon >= 1.0
- [x] 3.5 Document that `random_tree()` is NOT reproducible due to internal `random.seed(a=None)`
- [x] 3.6 Verify all values within 1e-6 tolerance

## 4. Core Function Integration Tests (3D)

- [x] 4.1 Create `TestCore3DParetoGraphCosts` and `TestCore3DDistanceFromFront` classes
- [x] 4.2 Test `graph_costs_3d_path_tortuosity()` returns exact expected values
- [x] 4.3 Test that 3D length/distance matches 2D version
- [x] 4.4 Test `distance_from_front_3d()` returns weights that sum to 1.0
- [x] 4.5 Document that `random_tree_3d_path_tortuosity()` is NOT reproducible
- [x] 4.6 Verify path tortuosity calculation matches manual computation

## 5. Full Pipeline Integration Tests

- [x] 5.1 Create `TestFullPipeline2D` class
- [x] 5.2 Test `pareto_calcs()` returns all required fields
- [x] 5.3 Create `TestFullPipeline3D` class
- [x] 5.4 Test `pareto_calcs_3d_path_tortuosity()` returns all required fields
- [x] 5.5 Verify 2D and 3D pipelines return consistent length/distance values
- [ ] 5.6 Save pipeline outputs as fixtures for regression testing - deferred

## 6. Real Data Fixture Tests

- [ ] 6.1 Create `TestRealDataFixtures` class using Matt's existing test data - deferred
- [ ] 6.2 Run analysis on existing fixtures and save expected outputs - deferred
- [ ] 6.3 Add regression tests that verify outputs match saved expectations - deferred
- [ ] 6.4 Document any precision considerations for real data - deferred

## 7. Reproducibility Tests

- [x] 7.1 Create `TestReproducibility` class
- [x] 7.2 Test that `random_tree()` generates 1000 trees (consistent count)
- [x] 7.3 Document limitation: external seeding does not work (skipped tests)
- [x] 7.4 Test that `random_tree_3d_path_tortuosity()` generates 1000 trees

**Known Issue**: `random_tree()` and `random_tree_3d_path_tortuosity()` call
`random.seed(a=None)` internally (pareto_functions.py:927, :976), which resets
the random state to system time. This makes external seeding ineffective and
results are not reproducible across runs. Tests for reproducibility are skipped
with documentation of this limitation.

## 8. Validation

- [x] 8.1 Run full test suite - 230 passed, 2 skipped
- [x] 8.2 Verify all new tests pass
- [ ] 8.3 Document test coverage additions - pending