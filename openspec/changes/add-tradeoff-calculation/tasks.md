# Tasks

## Phase 1: Implementation

- [ ] Add `calculate_tradeoff()` function to `quantify.py`
  - [ ] Find Steiner point (min total root length)
  - [ ] Find Satellite point (min travel distance)
  - [ ] Calculate Actual_ratio and Optimal_ratio
  - [ ] Calculate Tradeoff metric
  - [ ] Handle division by zero edge cases
  - [ ] Return dict with all 7 fields

- [ ] Integrate into `analyze()` function
  - [ ] Call `calculate_tradeoff()` with front and actual tree
  - [ ] Merge tradeoff results into main results dict

## Phase 2: Testing

- [ ] Add test for Steiner point identification
- [ ] Add test for Satellite point identification
- [ ] Add test for Tradeoff calculation
- [ ] Add test for division by zero handling
- [ ] Add test that all 7 fields are present in results
- [ ] Verify existing tests still pass

## Phase 3: Documentation

- [ ] Add docstring to `calculate_tradeoff()`
- [ ] Update CHANGELOG.md
