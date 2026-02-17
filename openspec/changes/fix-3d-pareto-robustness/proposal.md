## Why

The 3D Pareto path tortuosity analysis (PR #19) has several robustness issues that could cause runtime errors, produce incorrect results, or lead to irreproducible outputs. As a scientific computing tool, Ariadne must provide accurate, validated, and traceable results.

## What Changes

### Critical Fixes
- **BREAKING**: Fix `graph_costs_3d_path_tortuosity()` to return 3 values on cycle detection (currently returns 2, causing unpacking errors)
- Add division-by-zero protection when computing path tortuosity (when critical node is at same position as base)
- Add validation that `alpha + beta <= 1` in `pareto_cost_3d_path_tortuosity()` (gamma could be negative otherwise)

### Consistency Fixes
- Apply scaling transformation to 3D results in `main.py` (2D results are scaled, but 3D are not)

### UX Enhancements
- Add GUI checkbox in scale dialog: "Include 3D Pareto analysis (slower)" - unchecked by default
- Replace 3D line plot with surface plot (`plot_trisurf`) for better visualization of the Pareto front
- Keep 3D results in separate CSV file (`*_3d.csv`) for clarity

### Testing (TDD Approach)
- Add comprehensive unit tests for all 3D Pareto functions
- Tests written BEFORE fixes to verify they fail, then pass after fixes
- Test edge cases: cycles, coincident nodes, boundary alpha/beta values

## Impact

- Affected specs: `analysis-output`, `testing`
- Affected code:
  - `src/ariadne_roots/pareto_functions.py:103-197` (graph_costs_3d_path_tortuosity)
  - `src/ariadne_roots/pareto_functions.py:274-308` (pareto_cost_3d_path_tortuosity)
  - `src/ariadne_roots/main.py:1054-1150` (scale dialog - add 3D checkbox)
  - `src/ariadne_roots/main.py:1237-1291` (3D analysis - conditional execution)
  - `src/ariadne_roots/quantify.py:612-680` (plot_all_3d - surface plot)
  - `tests/` (new test file for 3D functions)