## ADDED Requirements

### Requirement: Synthetic Test Data Generation

The test suite SHALL include a generator for creating controlled test graphs with known expected outputs.

#### Scenario: Generate simple linear graph
- **GIVEN** a request for a simple linear root graph
- **WHEN** `create_simple_linear_graph()` is called
- **THEN** returns a NetworkX graph with node 0 at origin
- **AND** nodes connected in a straight line
- **AND** edge weights equal to Euclidean distances between nodes
- **AND** expected `Total root length` can be computed as sum of edge weights

#### Scenario: Generate branching graph with known tortuosity
- **GIVEN** a request for a Y-shaped branching graph
- **WHEN** `create_branching_graph()` is called
- **THEN** returns a graph with one primary root and two lateral roots
- **AND** path tortuosity can be manually computed as sum of (path_length / straight_distance)
- **AND** expected values are documented in fixture file

### Requirement: 2D Pareto Integration Tests

The test suite SHALL include integration tests that verify 2D Pareto analysis produces correct numerical values.

#### Scenario: graph_costs returns exact expected values
- **WHEN** `test_graph_costs_exact_values()` runs on synthetic graph
- **THEN** returned `total_root_length` matches expected value within 1e-6
- **AND** returned `total_travel_distance` matches expected value within 1e-6

#### Scenario: pareto_front corner costs are correct
- **WHEN** `test_pareto_front_corners()` runs
- **THEN** front[0.0] (Satellite) matches expected [length, distance] within 1e-6
- **AND** front[1.0] (Steiner) matches expected [length, distance] within 1e-6

#### Scenario: distance_from_front interpolation is accurate
- **WHEN** `test_distance_from_front_known_position()` runs with tree at known alpha
- **THEN** returned alpha matches expected value within 1e-6
- **AND** returned epsilon matches expected value within 1e-6

### Requirement: 3D Pareto Integration Tests

The test suite SHALL include integration tests that verify 3D Pareto analysis produces correct numerical values.

#### Scenario: graph_costs_3d returns correct path tortuosity
- **WHEN** `test_graph_costs_3d_path_tortuosity()` runs on synthetic graph
- **THEN** returned `total_root_length` matches expected within 1e-6
- **AND** returned `total_travel_distance` matches expected within 1e-6
- **AND** returned `total_path_coverage` matches manually computed tortuosity sum within 1e-6

#### Scenario: distance_from_front_3d returns correct weights
- **WHEN** `test_distance_from_front_3d_known_position()` runs
- **THEN** returned alpha, beta, gamma sum to 1.0 within 1e-9
- **AND** returned epsilon matches expected value within 1e-6
- **AND** epsilon_components match expected ratios within 1e-6

### Requirement: Full Pipeline Consistency Tests

The test suite SHALL include tests that verify the full analysis pipeline produces consistent results.

#### Scenario: analyze() produces identical results across runs
- **WHEN** `quantify.analyze()` is called twice with same input
- **THEN** all numeric fields in results are identical within 1e-10
- **AND** all fields in results_3d are identical within 1e-10

#### Scenario: CSV output matches computed values
- **WHEN** analysis results are written to CSV
- **THEN** CSV field values parse to same numeric values as results dict
- **AND** no precision loss occurs during serialization

### Requirement: Reproducibility with Fixed Seeds

The test suite SHALL include tests that verify random operations are reproducible when seeded.

#### Scenario: random_tree with fixed seed is reproducible
- **WHEN** `random_tree()` is called with fixed seed
- **THEN** returned costs are identical across multiple calls
- **AND** mean values (mrand, srand) are reproducible

#### Scenario: random_tree_3d with fixed seed is reproducible
- **WHEN** `random_tree_3d_path_tortuosity()` is called with fixed seed
- **THEN** returned costs are identical across multiple calls
- **AND** mean values (mrand, srand, prand) are reproducible

### Requirement: Real Data Regression Tests

The test suite SHALL include regression tests using saved expected outputs from real analysis runs.

#### Scenario: Real data regression test
- **GIVEN** pre-computed expected values from Matt's test data
- **WHEN** analysis is run on the same input files
- **THEN** all numeric fields match saved expected values within 1e-6
- **AND** any precision differences are documented and justified