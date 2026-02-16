## 1. Write Failing Integration Tests (TDD: Red)

Tests use real fixtures, no mocking. Pattern follows `test_scientific_integration.py`.

- [x] 1.1 Create `tests/test_plot_scaling_integration.py` with test class structure
- [x] 1.2 Write `test_2d_plot_values_match_csv_scaling()` using `plantB_day11_json` fixture
- [x] 1.3 Write `test_3d_plot_xy_values_match_csv_scaling()` - this FAILED before fix
- [x] 1.4 Write `test_3d_plot_z_values_not_scaled()` - verifies path tortuosity unchanged
- [x] 1.5 Run tests to confirm 3D tests fail with current implementation

## 2. Implement Fix (TDD: Green)

- [x] 2.1 Add `scale_data()` helper function inside `plot_all_3d()` at quantify.py:635
- [x] 2.2 Scale `x_values` (front_3d length) using `scale_data()`
- [x] 2.3 Scale `y_values` (front_3d distance) using `scale_data()`
- [x] 2.4 Keep `z_values` (path tortuosity) unscaled - dimensionless
- [x] 2.5 Scale `actual_3d[0]` and `actual_3d[1]` for actual plant marker
- [x] 2.6 Scale random trees x,y coordinates in `randoms_3d`
- [x] 2.7 Scale `mrand` and `srand` (random centroid x,y)
- [x] 2.8 Keep `prand` unscaled (path tortuosity is dimensionless)
- [x] 2.9 Run tests to confirm they pass

## 3. Validation

- [x] 3.1 Run full test suite - 240 passed, 2 skipped
- [x] 3.2 Verify no regressions in existing tests
- [x] 3.3 Format code with black (using Python 3.13)
- [ ] 3.4 Run lint checks

## 4. Documentation

- [x] 4.1 Add docstring update to `plot_all_3d()` noting internal scaling behavior