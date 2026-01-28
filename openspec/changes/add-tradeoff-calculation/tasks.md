# Tasks

## Phase 1: Implementation

- [x] Add `calculate_tradeoff()` function to `quantify.py`
  - [x] Find Steiner point (min total root length)
  - [x] Find Satellite point (min travel distance)
  - [x] Calculate Actual_ratio and Optimal_ratio
  - [x] Calculate Tradeoff metric
  - [x] Handle division by zero edge cases
  - [x] Return dict with all 7 fields

- [x] Integrate into `pareto_calcs()` function
  - [x] Call `calculate_tradeoff()` with front and actual tree
  - [x] Merge tradeoff results into main results dict

## Phase 2: Testing

- [x] Add test for Steiner point identification
- [x] Add test for Satellite point identification
- [x] Add test for Tradeoff calculation
- [x] Add test for division by zero handling
- [x] Add test that all 7 fields are present in results
- [x] Add test for Python float return types
- [x] Add test for scaling transformation of tradeoff fields
- [x] Verify existing tests still pass

## Phase 3: Documentation

- [x] Add docstring to `calculate_tradeoff()`
- [x] Update CHANGELOG.md
