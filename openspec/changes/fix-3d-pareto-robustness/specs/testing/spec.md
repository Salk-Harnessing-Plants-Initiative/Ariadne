## ADDED Requirements

### Requirement: 3D Pareto Function Unit Tests

The test suite SHALL include comprehensive unit tests for all 3D Pareto path tortuosity functions, written following TDD principles.

#### Scenario: Tests exist for graph_costs_3d_path_tortuosity
- **WHEN** `pytest tests/test_pareto_3d.py -k graph_costs` is run
- **THEN** at least 5 test cases execute:
  - Test with valid simple graph (3 nodes)
  - Test with valid complex graph (10+ nodes)
  - Test with graph containing cycle
  - Test with coincident node (same position as base)
  - Test with critical_nodes parameter

#### Scenario: Tests exist for pareto_cost_3d_path_tortuosity
- **WHEN** `pytest tests/test_pareto_3d.py -k pareto_cost` is run
- **THEN** at least 4 test cases execute:
  - Test with alpha=1, beta=0, gamma=0 (pure length minimization)
  - Test with alpha=0, beta=1, gamma=0 (pure distance minimization)
  - Test with alpha=0, beta=0, gamma=1 (pure coverage maximization)
  - Test with invalid alpha+beta > 1

#### Scenario: Tests exist for pareto_steiner_fast_3d_path_tortuosity
- **WHEN** `pytest tests/test_pareto_3d.py -k steiner` is run
- **THEN** at least 3 test cases execute:
  - Test produces connected tree
  - Test respects alpha/beta trade-off
  - Test handles edge case graphs

#### Scenario: Tests exist for pareto_front_3d_path_tortuosity
- **WHEN** `pytest tests/test_pareto_3d.py -k pareto_front` is run
- **THEN** at least 2 test cases execute:
  - Test returns expected structure (front, actual point)
  - Test front contains valid 3D coordinates

#### Scenario: Tests exist for random_tree_3d_path_tortuosity
- **WHEN** `pytest tests/test_pareto_3d.py -k random_tree` is run
- **THEN** at least 2 test cases execute:
  - Test produces connected tree
  - Test returns three cost values

### Requirement: TDD Red-Green Verification

Test development SHALL follow TDD methodology where tests are written before fixes and verified to fail initially.

#### Scenario: Tests fail before fixes applied
- **GIVEN** the test file `tests/test_pareto_3d.py` is created
- **AND** the bug fixes have NOT been applied
- **WHEN** `pytest tests/test_pareto_3d.py` is run
- **THEN** tests for cycle detection (3 values) SHALL fail
- **AND** tests for alpha+beta validation SHALL fail

#### Scenario: Tests pass after fixes applied
- **GIVEN** all fixes from this change have been applied
- **WHEN** `pytest tests/test_pareto_3d.py` is run
- **THEN** all tests SHALL pass
- **AND** code coverage for 3D functions exceeds 80%

### Requirement: 3D Scaling Integration Tests

The test suite SHALL verify that 3D results are scaled consistently with 2D results.

#### Scenario: Integration test for 3D scaling
- **GIVEN** a test fixture with known root data
- **AND** a non-unity scale factor (e.g., 0.5 mm/pixel)
- **WHEN** `quantify.analyze()` is called
- **AND** results are processed through `scaling.apply_scaling_transformation()`
- **THEN** 3D "Total root length" equals 2D "Total root length"
- **AND** both values reflect the scaled measurement

### Requirement: Edge Case Test Fixtures

The test suite SHALL include fixtures that exercise edge cases in 3D Pareto calculations.

#### Scenario: Fixture for coincident nodes
- **WHEN** test fixture `graph_with_coincident_node()` is used
- **THEN** it provides a graph where one critical node has position equal to base node
- **AND** the graph is otherwise valid (connected, acyclic)

#### Scenario: Fixture for cyclic graph
- **WHEN** test fixture `graph_with_cycle()` is used
- **THEN** it provides a graph containing at least one cycle
- **AND** the function under test detects and handles the cycle

#### Scenario: Fixture for boundary alpha/beta values
- **WHEN** parametrized tests run with alpha/beta combinations
- **THEN** combinations include: (0,0), (1,0), (0,1), (0.5,0.5), (0.3,0.7)
- **AND** invalid combination (0.6,0.6) is tested separately

### Requirement: 3D Toggle Config Tests

The test suite SHALL verify that the 3D analysis toggle correctly controls execution flow.

#### Scenario: Config flag controls 3D execution
- **GIVEN** `config.enable_3d_analysis` is set to False
- **WHEN** analysis workflow runs
- **THEN** 3D Pareto functions SHALL NOT be called
- **AND** no 3D output files are generated

#### Scenario: Config flag enables 3D execution
- **GIVEN** `config.enable_3d_analysis` is set to True
- **WHEN** analysis workflow runs
- **THEN** 3D Pareto functions SHALL be called
- **AND** 3D output files are generated

### Requirement: 3D Surface Plot Tests

The test suite SHALL verify that 3D visualization produces valid surface plots.

#### Scenario: Surface plot function creates valid figure
- **GIVEN** valid 3D front data with multiple (alpha, beta) points
- **WHEN** `plot_all_3d()` is called
- **THEN** the function SHALL complete without error
- **AND** the saved file SHALL be a valid image (PNG or SVG)

#### Scenario: Surface plot handles edge cases
- **GIVEN** 3D front data with collinear points (degenerate surface)
- **WHEN** `plot_all_3d()` is called
- **THEN** the function SHALL handle gracefully (no crash)
- **AND** a warning MAY be logged about visualization quality