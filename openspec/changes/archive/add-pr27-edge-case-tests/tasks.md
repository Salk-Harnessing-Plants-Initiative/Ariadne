# Tasks: Add Edge Case Tests for PR #27

## 1. Test Infrastructure

- [x] 1.1 Add fixture `issue26_root_json` in `fixtures.py` that loads `test_issue26_230629PN005_0.json`
- [x] 1.2 Use `json_graph.tree_graph()` to convert tree-formatted JSON to NetworkX DiGraph

## 2. Unit Tests for Bug Fix

- [x] 2.1 Add `test_calc_len_LRs_nonzero_start_index()` that verifies the function works when LR indices start at 1 (not 0)
- [x] 2.2 Add `test_calc_len_LRs_with_distances_nonzero_start_index()` for the same edge case
- [x] 2.3 Verified tests work with PR #27 fix (both tests pass)
- [x] 2.4 Tests include comprehensive docstrings explaining issue #26 bug scenario

## 3. Coverage Validation

- [x] 3.1 Verified 100% coverage on executable diff lines:
  - Line 271: `min_num_LRs = min(idxs.values())` ✓
  - Line 274: `for i in range(min_num_LRs, num_LRs):` ✓
  - Line 532: `min_num_LRs = min(idxs.values())` ✓
  - Line 536: `for i in range(min_num_LRs, num_LRs):` ✓
  - (Line 270 is a comment, not tracked by coverage)
- [x] 3.2 Overall coverage maintained at 98.31% (exceeds 98% threshold)
- [x] 3.3 Full test suite passes: 80 passed, 1 skipped, 0 failures

## 4. Documentation

- [x] 4.1 Added comprehensive docstrings to both test functions
- [x] 4.2 Both tests reference issue #26 and explain the UnboundLocalError bug

## 5. Repository Hygiene

- [x] 5.1 Verified `.gitignore` excludes temporary files (`*.ipynb`, `*.png`, `*.csv`) ✓
- [x] 5.2 Added `coverage.json` to gitignore (line 48)
- [x] 5.3 Test fixtures use specific filenames (`test_issue26_*.json`) not matching wildcard patterns
