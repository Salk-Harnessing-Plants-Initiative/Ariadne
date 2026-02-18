## Why

The `distance_from_front_3d()` function returns scientifically misleading results. It only identifies the nearest discrete point on the 3D Pareto front, whereas the 2D version (`distance_from_front()`) performs linear interpolation for higher precision. Additionally, the 3D version lacks division-by-zero protection and returns uninformative `(0.0, 0.0)` for random trees.

**GitHub Issues**:
- [#53](https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/issues/53) - 3D Pareto distance calculation lacks interpolation
- [#54](https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/issues/54) - Return (alpha, beta, gamma) instead of just (alpha, beta)

## What Changes

- Add barycentric interpolation using 3 nearest (α, β) points to `distance_from_front_3d()`
- Add division-by-zero guards (skip front points with zero values, matching 2D behavior)
- Change return format from `((alpha, beta), scaling)` to dict with epsilon and all three parameters
- Return gamma explicitly (γ = 1 - α - β) instead of requiring users to compute it (#54)
- Return epsilon components (material, transport, coverage ratios) showing which dimension drives epsilon
- Return corner architecture costs (Steiner, Satellite, Coverage) as reference points
- Add comprehensive unit tests mirroring the 2D test suite (10+ tests)

## Impact

- **Affected specs**: `analysis-output`
- **Affected code**: `quantify.py:903-934` (`distance_from_front_3d`), `quantify.py:985-1001` (callers)
- **Test files**: `tests/test_pareto_3d.py` (new test class), `tests/test_quantify.py` (integration)
- **No backwards compatibility concerns**: This is a new feature not yet merged to main