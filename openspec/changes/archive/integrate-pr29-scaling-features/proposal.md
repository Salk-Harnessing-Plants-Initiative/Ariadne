# Proposal: Integrate PR #29 Scaling Features

## Why

PR #29 by @mplatre introduces two valuable features:
1. **User-tunable scaling**: Allows users to set a conversion factor from pixels to real-world units (mm, cm, etc.)
2. **Improved Pareto front visualization**: Better graph centering focused on the Pareto front

However, PR #29 is based on old code (pre-test-coverage, pre-CI improvements) and:
- Deletes all recent work (test suite, OpenSpec, CI improvements, issue #26 fix)
- Removes tkinter mocking from `conftest.py`, causing CI failures
- Adds binary files (.DS_Store, .png) and test data to `src/` instead of `tests/data/`
- Breaks the lockfile-based workflow
- Needs rebasing onto current `main`

## What Changes

### Code Integration
- Rebase PR #29 features onto current `main` branch
- Add `config.py` for global scaling configuration
- Modify `main.py` to add scale input dialog
- Update `quantify.py` to apply scaling to analysis results
- Improve Pareto front visualization in `pareto_functions.py`

### Test Infrastructure
- Restore tkinter mocking in `conftest.py`
- Add tests for scaling functionality
- Add tests for config module
- Ensure all existing tests still pass

### Repository Hygiene
- Remove binary files (.DS_Store, .png)
- Move test data from `src/` to `tests/data/`
- Maintain .gitignore patterns
- Preserve uv.lock

## Impact

- **Affected specs**: Will create `user-interface` spec for scaling dialog and `output-formatting` spec for scaled results
- **Affected code**:
  - `src/ariadne_roots/config.py` (new file)
  - `src/ariadne_roots/main.py` (scaling dialog, AnalyzerUI changes)
  - `src/ariadne_roots/quantify.py` (apply scaling to results)
  - `src/ariadne_roots/pareto_functions.py` (visualization improvements)
  - `tests/conftest.py` (preserve tkinter mocking)
  - `tests/test_main.py` (add scaling tests)
  - `tests/test_quantify.py` (add scaling tests)
- **Dependencies**: Supersedes PR #29, will create new PR with rebased changes
- **Coverage impact**: Must maintain 98%+ coverage with new feature tests

## Non-Goals

- This proposal does NOT change the underlying analysis algorithms
- This proposal does NOT modify the tree tracing UI
- This proposal does NOT change the file format for saved trees

## Success Criteria

1. All CI checks pass (tests, coverage, build)
2. Coverage remains ≥98%
3. Users can set custom scaling before analysis
4. Output CSV files contain properly scaled measurements
5. Pareto front visualizations are well-centered
6. No regression in existing functionality
