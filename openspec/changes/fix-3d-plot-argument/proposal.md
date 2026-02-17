## Why

The `plot_all_3d()` function receives incorrect data for the random tree path tortuosity parameter. At main.py:1329, the call passes `results_3d["Path tortuosity"]` (the actual plant's path coverage) instead of `results_3d["Path tortuosity (random)"]` (the mean of 1000 random trees). This causes the "Random Centroid" marker on 3D Pareto plots to display at the wrong z-coordinate, producing scientifically inaccurate visualizations.

Additionally, this proposal addresses minor code quality issues identified during review.

## What Changes

- **CRITICAL**: Fix `plot_all_3d()` call in main.py to pass `Path tortuosity (random)` instead of `Path tortuosity`
- Add integration tests that verify plot_all_3d receives correct random tree metrics
- Add unit tests that mock plot_all_3d and verify argument values
- Remove commented debug print statement in quantify.py:1054
- Move logging configuration from module level to function level in quantify.py
- Improve checkbox label clarity in main.py:1090

## Impact

- Affected specs: analysis-output, testing
- Affected files: `src/ariadne_roots/main.py`, `src/ariadne_roots/quantify.py`, `tests/test_main.py`
- No breaking changes to API
- **Scientific accuracy**: Random centroid marker will now display at correct position on 3D Pareto plots