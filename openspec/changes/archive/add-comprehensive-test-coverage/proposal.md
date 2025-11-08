# Add Comprehensive Test Coverage

## Why

The project currently has only 40.48% test coverage, failing to meet the newly established 80% minimum coverage requirement enforced in CI. Scientific computing requires rigorous testing to ensure accuracy, precision, and reproducibility of root system architecture (RSA) trait calculations. The existing test infrastructure (pytest with centralized fixtures) is well-designed but incomplete, covering only basic quantify module functionality. To maintain scientific credibility and catch regressions in Pareto optimality algorithms and trait measurements, comprehensive test coverage is essential.

## What Changes

- Add comprehensive unit tests for `pareto_functions.py` covering all graph cost calculations, Pareto front generation, Steiner tree operations, and random tree generation
- Add comprehensive unit tests for `quantify.py` covering distance calculations, graph parsing, trait extraction (PR/LR metrics, angles, zones, convex hull), and edge cases
- Expand centralized test fixtures in `tests/fixtures.py` to include:
  - Additional real root system JSON test data with known-correct output values
  - Graph fixtures representing edge cases (single root, no lateral roots, complex branching)
  - Minimal synthetic graphs for isolated unit testing of mathematical functions
- Add integration tests validating end-to-end analyze() workflow with multiple real datasets
- Document fixture generation methodology to ensure reproducibility and scientific validity
- Exclude GUI module (`main.py`) from coverage requirements due to matplotlib interaction complexity (focus on scientific computation accuracy)

## Impact

- **Affected specs**: `test-framework` (new capability)
- **Affected code**:
  - `tests/test_pareto_functions.py` - expand from stub to comprehensive coverage
  - `tests/test_quantify.py` - expand beyond single integration test
  - `tests/fixtures.py` - add new fixture data and helper functions
  - `tests/conftest.py` - enhance fixture configuration
  - `tests/data/` - add additional JSON test files with validated outputs
- **Coverage target**: Achieve 80%+ coverage for `pareto_functions.py` and `quantify.py` (excluding `main.py`)
- **No breaking changes**: Tests verify existing behavior without modifying implementation