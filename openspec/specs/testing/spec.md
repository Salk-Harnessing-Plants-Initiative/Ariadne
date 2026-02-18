# testing Specification

## Purpose
TBD - created by archiving change fix-scaling-and-serialization-bugs. Update Purpose after archive.
## Requirements
### Requirement: CSV Field Type Validation Tests

The test suite SHALL include comprehensive tests that verify all CSV output fields have correct Python native types.

#### Scenario: Numeric fields are validated for type
- **WHEN** `test_csv_field_types()` runs
- **THEN** all numeric fields in results are verified to be `int` or `float`
- **AND** array fields (like "LR lengths", "LR angles") are verified to be lists of native Python types
- **AND** no numpy scalar types are present in the results

#### Scenario: Tests fail before fix is applied
- **WHEN** tests are run against code without the numpy conversion fix
- **THEN** the type validation tests SHALL fail
- **AND** the failure message indicates numpy types were found

### Requirement: CSV Field Range Validation Tests

The test suite SHALL include tests that verify CSV output fields have expected value ranges.

#### Scenario: Positive fields are validated
- **WHEN** `test_csv_field_ranges()` runs
- **THEN** length fields (Total root length, PR length, etc.) are verified to be non-negative
- **AND** count fields (LR count) are verified to be non-negative integers
- **AND** density fields are verified to be non-negative

#### Scenario: Angle fields are in valid range
- **WHEN** results contain LR angles
- **THEN** each angle is verified to be between 0 and 180 degrees
- **AND** Mean LR angles and Median LR angles are between 0 and 180

### Requirement: CSV Serialization Validation Tests

The test suite SHALL include tests that verify CSV output can be serialized without numpy type representations.

#### Scenario: CSV output contains no numpy strings
- **WHEN** `test_csv_serialization_no_numpy()` runs
- **THEN** the serialized CSV content is checked for "np.float64"
- **AND** the serialized CSV content is checked for "np.int64"
- **AND** the test fails if any numpy type representations are found

### Requirement: Test Fixtures from Real Data

The test suite SHALL include test fixtures derived from real Arabidopsis root data to validate the fixes work on production data.

#### Scenario: Tests run on real data fixtures
- **WHEN** CSV validation tests are run
- **THEN** the tests use at least one real data fixture from Matt's samples
- **AND** the tests verify the fix works on real-world root structures

### Requirement: 3D Plot Argument Validation Tests

The test suite SHALL include tests that verify plot_all_3d receives correct random tree metrics.

#### Scenario: Integration test verifies prand argument
- **WHEN** `test_3d_plot_receives_random_path_tortuosity()` runs
- **THEN** the test executes the full 3D analysis pipeline
- **AND** captures the arguments passed to `plot_all_3d()`
- **AND** verifies `prand` equals the CSV field `Path tortuosity (random)`
- **AND** the test fails if `prand` equals the actual plant's `Path tortuosity`

#### Scenario: Test detects the bug before fix
- **WHEN** tests are run against code with the bug (passing wrong value)
- **THEN** the validation test SHALL fail
- **AND** the failure message indicates which argument was incorrect

### Requirement: CSV-Plot Data Consistency Tests

The test suite SHALL include tests that verify CSV output matches plot data for 3D analysis.

#### Scenario: All random metrics are consistent
- **WHEN** `test_3d_csv_plot_consistency()` runs
- **THEN** `Total root length (random)` in CSV equals `mrand` in plot
- **AND** `Travel distance (random)` in CSV equals `srand` in plot
- **AND** `Path tortuosity (random)` in CSV equals `prand` in plot

### Requirement: 3D Scaling Exclusion Tests

The test suite SHALL include comprehensive tests for 3D dimensionless field scaling exclusion.

#### Scenario: Unit tests verify 3D weight field exclusions
- **WHEN** `test_3d_weight_fields_excluded()` runs
- **THEN** the test verifies `beta_3d` matches exclusion patterns
- **AND** the test verifies `gamma_3d` matches exclusion patterns
- **AND** the test verifies `beta_3d (random)` matches exclusion patterns
- **AND** the test verifies `gamma_3d (random)` matches exclusion patterns

#### Scenario: Unit tests verify 3D epsilon field exclusions
- **WHEN** `test_3d_epsilon_fields_excluded()` runs
- **THEN** the test verifies `epsilon_3d` matches exclusion patterns
- **AND** the test verifies `epsilon_3d_material` matches exclusion patterns
- **AND** the test verifies `epsilon_3d_transport` matches exclusion patterns
- **AND** the test verifies `epsilon_3d_coverage` matches exclusion patterns
- **AND** the test verifies all `(random)` variants match exclusion patterns

#### Scenario: Integration test verifies 3D scaling behavior
- **WHEN** `test_3d_scaling_preserves_dimensionless_fields()` runs
- **THEN** the test applies a scale factor to 3D results
- **AND** verifies all dimensionless fields are unchanged
- **AND** verifies length fields are correctly scaled

#### Scenario: Tests fail before fix is applied
- **WHEN** tests are run against code without the 3D exclusion fix
- **THEN** the exclusion tests SHALL fail
- **AND** the integration test SHALL show incorrect scaled values for dimensionless fields

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

