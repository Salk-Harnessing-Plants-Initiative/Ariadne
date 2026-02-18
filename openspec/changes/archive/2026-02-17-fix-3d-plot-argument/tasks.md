## 1. Write Failing Tests (TDD)

- [x] 1.1 Write integration test that runs full 3D analysis pipeline and verifies plot data consistency
- [x] 1.2 Write test that captures plot_all_3d arguments and verifies `prand` equals the random tree mean (not the actual plant value)
- [x] 1.3 Write test that compares CSV output `Path tortuosity (random)` with the value passed to plot_all_3d
- [x] 1.4 Run tests to confirm they fail with current implementation

## 2. Implement Bug Fix

- [x] 2.1 Fix main.py:1329 to pass `results_3d["Path tortuosity (random)"]` instead of `results_3d["Path tortuosity"]`
- [x] 2.2 Run tests to confirm they pass

## 3. Address Code Quality Issues

- [x] 3.1 Remove commented debug print at quantify.py:1054
- [ ] 3.2 Move logging.basicConfig from module level to appropriate function scope (deferred - requires broader refactoring)
- [x] 3.3 Checkbox label at main.py:1090 already describes path tortuosity clearly (no change needed)

## 4. Validation

- [x] 4.1 Run full test suite (208 tests passed)
- [x] 4.2 Verify 3D Pareto plot displays correctly with test data
- [x] 4.3 Update documentation if needed (no changes required)