# Test Framework Specification

## ADDED Requirements

### Requirement: Centralized Real Data Fixtures

The test framework SHALL provide centralized fixtures in `tests/fixtures.py` and `tests/conftest.py` containing real root system data with independently validated expected outputs for scientific accuracy verification.

#### Scenario: Loading real root system JSON data
- **WHEN** a test requests the `plantB_day11_json` fixture
- **THEN** the fixture returns the file path to a valid JSON file containing real root system graph data

#### Scenario: Accessing validated expected values
- **WHEN** a test requests expected value fixtures (e.g., `plantB_day11_lr_lengths`)
- **THEN** the fixture returns pre-calculated values derived from independent validation
- **AND** values are documented with provenance in `tests/data/README.md`

#### Scenario: Using multiple real datasets
- **WHEN** tests require diverse root system architectures
- **THEN** at least 3 distinct real root JSON files are available in `tests/data/`
- **AND** each has corresponding expected value fixtures for all calculated traits

### Requirement: Synthetic Minimal Graph Fixtures

The test framework SHALL provide minimal synthetic graph fixtures (3-5 nodes) for fast unit testing of mathematical functions with hand-verifiable outputs.

#### Scenario: Testing with minimal graphs
- **WHEN** a unit test needs to verify a mathematical function in isolation
- **THEN** fixtures provide simple graphs (e.g., 3-node linear, 4-node branched)
- **AND** expected outputs can be manually verified without computation

#### Scenario: Constructing synthetic graphs
- **WHEN** tests need programmatically generated graphs
- **THEN** fixture helper functions construct NetworkX graphs with specified topology
- **AND** edge weights are Euclidean distances based on node positions

### Requirement: Edge Case Fixtures

The test framework SHALL provide fixtures representing edge cases and boundary conditions in root system architecture.

#### Scenario: Single primary root (no laterals)
- **WHEN** analyzing roots without lateral branching
- **THEN** fixture provides graph with only primary root nodes (degree 1 or 2)
- **AND** LR count is 0, LR-related metrics are empty or zero

#### Scenario: Highly branched root system
- **WHEN** testing complex branching scenarios
- **THEN** fixture provides graph with >50 lateral roots
- **AND** expected outputs include all trait calculations

#### Scenario: Disconnected graph components
- **WHEN** testing graph validation
- **THEN** fixture provides invalid graph with disconnected components
- **AND** functions handle errors gracefully (return inf or raise appropriate exception)

### Requirement: Pareto Functions Test Coverage

Tests SHALL achieve ≥90% code coverage for `src/ariadne_roots/pareto_functions.py` by verifying all graph cost calculations, Pareto front generation, and randomized operations.

#### Scenario: Critical node identification
- **WHEN** `get_critical_nodes()` is called with various graph topologies
- **THEN** tests verify base node (id=0) and all degree-1 nodes are identified
- **AND** edge cases include single-node graphs and fully connected graphs

#### Scenario: Graph cost calculation accuracy
- **WHEN** `graph_costs()` computes wiring cost and conduction delay
- **THEN** tests compare outputs to hand-calculated or published reference values
- **AND** tests use real fixture data with validated expected costs

#### Scenario: Graph cost edge cases
- **WHEN** `graph_costs()` receives invalid graphs (cycles, disconnected)
- **THEN** function returns (inf, inf) for cycles
- **AND** raises assertion error for disconnected graphs

#### Scenario: Pareto cost interpolation
- **WHEN** `pareto_cost()` is called with various alpha values (0, 0.5, 1.0)
- **THEN** tests verify cost = (1-alpha)*wiring + alpha*conduction
- **AND** alpha=0 minimizes conduction, alpha=1 minimizes wiring

#### Scenario: Pareto front properties
- **WHEN** `pareto_front()` generates optimal trade-off curve
- **THEN** tests verify front has 101 points (alpha 0.00 to 1.00)
- **AND** front is monotonic (wiring decreases as conduction increases)
- **AND** alpha=0 endpoint has maximal wiring, minimal conduction
- **AND** alpha=1 endpoint has minimal wiring, maximal conduction

#### Scenario: Random tree reproducibility
- **WHEN** `random_tree()` generates randomized graphs with fixed seed
- **THEN** identical seeds produce identical graphs across runs
- **AND** tests verify graph properties (node count, edge weights) are preserved

### Requirement: Quantify Module Test Coverage

Tests SHALL achieve ≥90% code coverage for `src/ariadne_roots/quantify.py` by verifying all distance calculations, graph parsing, trait extraction, and error handling.

#### Scenario: Euclidean distance calculation
- **WHEN** `distance()` is called with known point pairs
- **THEN** output matches hand-calculated Euclidean distance
- **AND** tests include zero distance (same point) and large coordinates

#### Scenario: Graph construction from file
- **WHEN** `make_graph()` parses valid .xyz format files
- **THEN** resulting NetworkX graph has correct node count and edges
- **AND** node positions match input coordinates
- **AND** edge lengths are Euclidean distances between connected nodes

#### Scenario: Primary root trait extraction
- **WHEN** `analyze()` calculates PR-related traits
- **THEN** PR length, minimal length, basal/branched/apical zone lengths match validated values
- **AND** tests use real fixture data with pre-calculated expected outputs

#### Scenario: Lateral root trait extraction
- **WHEN** `analyze()` calculates LR-related traits
- **THEN** LR count, mean/median lengths, angles, densities match validated values
- **AND** tests verify individual LR arrays (lengths, angles, minimal lengths)

#### Scenario: Convex hull calculations
- **WHEN** `analyze()` computes convex hull area and barycenter displacement
- **THEN** outputs match expected values for known geometries
- **AND** tests include edge cases (collinear points, minimal point sets)

#### Scenario: Tortuosity and efficiency metrics
- **WHEN** `analyze()` calculates tortuosity (material/total distance ratio)
- **THEN** tortuosity = total_root_length / total_minimal_distance
- **AND** tests verify values with hand-calculated examples

#### Scenario: Invalid input handling
- **WHEN** functions receive malformed inputs (empty graphs, missing attributes)
- **THEN** appropriate exceptions are raised or error values returned
- **AND** tests verify error messages are informative

### Requirement: End-to-End Integration Tests

Tests SHALL include end-to-end integration tests validating the complete `analyze()` workflow with multiple real datasets.

#### Scenario: Full analyze workflow with real data
- **WHEN** `analyze()` is called with complete root system JSON
- **THEN** all 31 output features are returned with expected types
- **AND** scalar values match pre-validated outputs within tolerance (rtol=1e-8)
- **AND** array values match pre-validated outputs element-wise

#### Scenario: Reproducibility across runs
- **WHEN** `analyze()` is called multiple times with identical input
- **THEN** outputs are bitwise identical across all runs
- **AND** random operations use fixed seeds for deterministic behavior

#### Scenario: Edge case integration
- **WHEN** `analyze()` processes edge-case fixtures (single root, no laterals)
- **THEN** workflow completes without errors
- **AND** outputs reflect expected boundary values (e.g., LR count = 0)

### Requirement: Test Execution Performance

The test suite SHALL execute in <30 seconds total on standard CI hardware to maintain fast feedback loops.

#### Scenario: Fast unit tests
- **WHEN** unit tests run with minimal synthetic fixtures
- **THEN** individual tests complete in <100ms
- **AND** total unit test time is <10 seconds

#### Scenario: Integration test performance
- **WHEN** integration tests run with real datasets
- **THEN** each integration test completes in <5 seconds
- **AND** total integration test time is <20 seconds

### Requirement: Fixture Documentation

Test fixtures SHALL be documented with provenance, validation methodology, and usage examples to ensure scientific credibility and maintainability.

#### Scenario: Fixture provenance documentation
- **WHEN** developers add new test fixtures
- **THEN** `tests/data/README.md` documents data source (experiment ID, date, researcher)
- **AND** expected value derivation method is documented (manual calculation, reference implementation, published result)

#### Scenario: Fixture usage examples
- **WHEN** developers write new tests
- **THEN** `tests/README.md` provides examples of using centralized fixtures
- **AND** inline test comments explain scientific validation approach

#### Scenario: Expected value tolerance justification
- **WHEN** tests use tolerance-based assertions (rtol, atol)
- **THEN** comments explain tolerance choice (numerical precision, platform variance)
- **AND** scientific validity is documented (e.g., "within measurement precision")

### Requirement: Coverage Reporting and Enforcement

The test suite SHALL generate coverage reports and enforce ≥80% minimum coverage for scientific computation modules in CI.

#### Scenario: Coverage report generation
- **WHEN** tests run with coverage enabled
- **THEN** coverage report shows line and branch coverage per module
- **AND** report identifies uncovered lines (--cov-report=term-missing)
- **AND** XML coverage artifact is uploaded for CI analysis

#### Scenario: Coverage threshold enforcement
- **WHEN** coverage falls below 80% threshold
- **THEN** pytest exits with error code
- **AND** CI build fails with informative message

#### Scenario: Module-specific coverage targets
- **WHEN** evaluating test coverage
- **THEN** `pareto_functions.py` achieves ≥90% coverage
- **AND** `quantify.py` achieves ≥90% coverage
- **AND** `main.py` (GUI) is excluded from coverage requirements

### Requirement: Assertion Strategy for Scientific Accuracy

Tests SHALL use tolerance-based floating-point comparisons appropriate for scientific computing precision.

#### Scenario: Scalar floating-point assertions
- **WHEN** comparing scalar float values
- **THEN** tests use `math.isclose()` with relative tolerance (default rtol=1e-8)
- **AND** tolerance is justified based on numerical precision needs

#### Scenario: Array floating-point assertions
- **WHEN** comparing NumPy arrays
- **THEN** tests use `numpy.testing.assert_allclose()` with appropriate tolerances
- **AND** element-wise comparison reports first mismatch for debugging

#### Scenario: Integer and exact comparisons
- **WHEN** comparing counts or discrete values
- **THEN** tests use exact equality (`==`)
- **AND** no tolerance is applied to integer comparisons