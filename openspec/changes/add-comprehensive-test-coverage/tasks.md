# Implementation Tasks

## 1. Fixture Infrastructure
- [ ] 1.1 Add at least 2 additional real root system JSON files to `tests/data/` with documented expected outputs
- [ ] 1.2 Create synthetic minimal graph fixtures (3-5 node graphs) for unit testing mathematical functions
- [ ] 1.3 Add edge-case fixtures: single primary root (no laterals), highly branched system, disconnected components
- [ ] 1.4 Document fixture provenance and validation methodology in `tests/data/README.md`
- [ ] 1.5 Add fixture helper functions to `fixtures.py` for graph construction and expected value extraction

## 2. Pareto Functions Tests
- [ ] 2.1 Test `get_critical_nodes()` with various graph topologies (isolated nodes, all tips, base node)
- [ ] 2.2 Test `graph_costs()` with known graphs and validated outputs (wiring cost, conduction delay)
- [ ] 2.3 Test `graph_costs()` edge cases (cycles, disconnected graphs, single node)
- [ ] 2.4 Test `pareto_cost()` with multiple alpha values and verify cost interpolation
- [ ] 2.5 Test `pareto_front()` generation with real fixture data, verify front properties (monotonicity, alpha=0/1 endpoints)
- [ ] 2.6 Test `random_tree()` generation with seed for reproducibility, verify graph properties preserved
- [ ] 2.7 Test Steiner tree operations if exposed in public API

## 3. Quantify Module Tests
- [ ] 3.1 Test `distance()` function with known point pairs, verify Euclidean calculation
- [ ] 3.2 Test `make_graph()` with minimal valid .xyz format files, verify graph structure
- [ ] 3.3 Test `make_graph_alt()` error handling for malformed input
- [ ] 3.4 Test primary root trait extraction (PR length, minimal length, zones) with fixture data
- [ ] 3.5 Test lateral root trait extraction (LR counts, lengths, angles, densities) with fixture data
- [ ] 3.6 Test convex hull calculations (area, barycenter displacement) with known geometries
- [ ] 3.7 Test tortuosity and minimal distance calculations
- [ ] 3.8 Add negative tests for invalid inputs (empty graphs, missing attributes, malformed JSON)

## 4. Integration Tests
- [ ] 4.1 Add end-to-end test for `analyze()` with 2-3 different real datasets
- [ ] 4.2 Verify reproducibility: same input produces identical output across runs
- [ ] 4.3 Test analyze() with edge-case fixtures (single root, no branches)
- [ ] 4.4 Validate all 31 output features have expected types and ranges

## 5. Coverage and Documentation
- [ ] 5.1 Run coverage report and identify remaining gaps in `pareto_functions.py` and `quantify.py`
- [ ] 5.2 Add targeted tests for uncovered branches (error paths, edge cases)
- [ ] 5.3 Verify total coverage ≥80% with `uv run pytest --cov=ariadne_roots --cov-fail-under=80`
- [ ] 5.4 Update `tests/README.md` with testing strategy, fixture documentation, and how to add new tests
- [ ] 5.5 Add inline comments in test files explaining scientific validation approach

## 6. CI Validation
- [ ] 6.1 Verify all tests pass locally on current branch
- [ ] 6.2 Verify coverage threshold passes in local run
- [ ] 6.3 Push to feature branch and confirm CI passes on all platforms (Ubuntu, Windows, macOS)
- [ ] 6.4 Verify coverage artifacts are correctly uploaded in CI