# Proposal: Add Edge Case Tests for PR #27 Bug Fix

## Why

PR #27 fixes a critical bug where `calc_len_LRs()` and `calc_len_LRs_with_distances()` crash with `UnboundLocalError` when lateral root indices don't start at 0. The PR includes a real root system test file (`test_issue26_230629PN005_0.json`) that reproduces the bug, but doesn't include explicit unit tests that:

1. Exercise the bug fix code path (non-zero starting LR index)
2. Verify the fix prevents the crash
3. Achieve 100% coverage on the diff lines

This change ensures PR #27's bug fix is comprehensively tested before merging.

## What Changes

- Add test fixture using the `test_issue26_230629PN005_0.json` file provided in PR #27
- Add unit test for `calc_len_LRs()` with non-zero starting LR index (reproduces issue #26)
- Add unit test for `calc_len_LRs_with_distances()` with non-zero starting LR index
- Add test to verify the `min_num_LRs` calculation works correctly
- Ensure 100% coverage on PR #27's diff lines (lines 254, 255, 260 and 532, 536 in quantify.py)

## Impact

- **Affected specs**: root-analysis (new spec for root trait calculation testing requirements)
- **Affected code**:
  - `tests/test_quantify.py` - Add new tests
  - `tests/conftest.py` - Add fixture for issue #26 test data
  - `.gitignore` - Update to allow test fixture data while excluding temporary analysis files
  - No changes to production code (only tests)
- **Dependencies**: Blocks merging PR #27 until tests are added
- **Coverage impact**: Ensures PR #27 maintains 98%+ coverage and covers all new lines

## Optional Follow-up Work

After PR #27 is merged, consider:
- Creating regression test fixtures from existing analysis outputs (CSV reports, Pareto plots)
- Adding a marimo notebook for API demonstrations (excluded from git via .gitignore)
- Evaluating whether current untracked files should be preserved as test fixtures
