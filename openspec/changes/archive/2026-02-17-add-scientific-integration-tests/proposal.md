## Why

The current test suite lacks integration tests that verify end-to-end scientific accuracy of the 2D and 3D Pareto analysis pipelines. Recent bugs (wrong plot arguments, missing scaling exclusions) were not caught because:

1. No tests verify that computed values match expected results for known inputs
2. No tests trace data flow from analysis functions through to CSV/plot outputs
3. No reproducible test fixtures with pre-computed expected values

Scientific software requires tests that verify numerical correctness, not just that code runs without errors.

## What Changes

- Add synthetic test data generator that creates controlled NetworkX graphs with known exact expected outputs
- Add integration tests for 2D Pareto pipeline (`pareto_calcs`, `distance_from_front`, `random_tree`)
- Add integration tests for 3D Pareto pipeline (`pareto_calcs_3d_path_tortuosity`, `distance_from_front_3d`)
- Generate and save test fixtures with pre-computed expected values
- Verify all computed values against expected values with 1e-6 precision tolerance
- Ensure reproducibility by seeding random number generators in tests
- Create separate test classes for core functions vs full pipeline integration

## Impact

- Affected specs: testing
- Affected files: `tests/test_scientific_integration.py`, `tests/fixtures/`, `tests/conftest.py`
- No breaking changes - adds new tests only
- **Scientific rigor**: Catches numerical errors before they affect research outputs