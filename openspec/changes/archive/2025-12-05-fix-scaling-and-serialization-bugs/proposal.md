# Proposal: Fix Scaling and Serialization Bugs

**Status**: 🟡 Proposed
**Created**: 2024-12-03
**Owner**: Elizabeth Berrigan
**Reporter**: Matthieu Platre (@mplatre)
**Effort**: 2-4 hours (TDD approach)

## Problem Statement

Matt Platre reported two bugs in v0.1.0a1 pre-release after testing:

### Bug 1: `np.float64` appearing in CSV output for LR_angles

**Symptom**: CSV files contain numpy float objects instead of Python floats:
```csv
"LR angles","[np.float64(57.86275101895822), np.float64(51.44160009933503), ...]"
```

**Expected**: Python float values that serialize cleanly:
```csv
"LR angles","[57.86275101895822, 51.44160009933503, ...]"
```

**Root Cause**: In `quantify.py`, the `angles_LRs` list contains numpy `float64` objects from `numpy.arctan2()` calculations. When these are stored in the results dict and later written to CSV, they serialize as `np.float64(...)` instead of plain numbers.

**Location**: `src/ariadne_roots/quantify.py` line 816:
```python
results["LR angles"] = angles_LRs  # Contains np.float64 objects
```

### Bug 2: Graph barycenter/RSA not scaled properly

**Symptom**: In the Pareto front graph, the random tree barycenter (red +) and/or RSA are not positioned correctly relative to the Pareto front.

**Root Cause**: Double-scaling bug in the visualization pipeline:

1. In `main.py`, we call `plot_all()` with **already-scaled** results:
   ```python
   quantify.plot_all(
       front,
       [scaled_results["Total root length"], scaled_results["Travel distance"]],
       randoms,
       scaled_results["Total root length (random)"],
       scaled_results["Travel distance (random)"],
       pareto_path,
   )
   ```

2. Inside `plot_all()`, the function scales the data **again** using `config.length_scale_factor`:
   ```python
   def scale_data(data):
       return data * config.length_scale_factor

   scaled_mrand = scale_data(mrand)  # Double-scaled!
   ```

3. Result: Some values are scaled twice, causing misalignment in the graph.

## Evidence from Matt's Branch

Matt's branch (`origin/MATT_P`) contains fixes for both issues:

### Fix 1: LR_angles serialization
```python
# Matt's fix in MATT_P:
results["LR angles"] = [angle.item() for angle in angles_LRs] if angles_LRs else []
```

The `.item()` method converts numpy scalars to Python native types.

### Fix 2: Graph scaling
Matt's approach passes scale parameters explicitly to `plot_all()`:
```python
# Matt's fix - pass unscaled values + explicit scale parameters:
quantify.plot_all(
    front,
    [results["Total root length"], results["Travel distance"]],  # Unscaled
    randoms,
    results["Total root length (random)"],
    results["Travel distance (random)"],
    pareto_path,
    scale_factor,   # Explicit parameter
    scale_unit      # Explicit parameter
)
```

## Additional Findings from Matt's Branch

Matt's branch (`origin/MATT_P`) includes these changes not yet in main:

### Bug Fixes (MUST incorporate)
1. **LR_angles type fix**: `[angle.item() for angle in angles_LRs]` - converts numpy to Python floats
2. **Graph scaling fix**: Passes unscaled data to `plot_all()` with explicit scale parameters

### Enhancements (Consider for this or future proposal)

1. **Alpha interpolation**: Higher precision alpha values (6 decimal places) via linear interpolation:
   ```python
   # Interpolate between two closest alphas
   weight1 = dist2 / total_dist  # Closer distance gets higher weight
   weight2 = dist1 / total_dist
   interpolated_alpha = alpha1 * weight1 + alpha2 * weight2
   interpolated_alpha = f"{interpolated_alpha:.6f}"
   ```

2. **Tradeoff calculation**: New `calculate_tradeoff()` function that computes:
   - Steiner architecture (minimizes total root length)
   - Satellite architecture (minimizes travel distance)
   - Tradeoff metric: `(actual_length/actual_distance) / (steiner_length/satellite_distance)`
   - Returns: Tradeoff, Steiner_length, Steiner_distance, Satellite_length, Satellite_distance, Actual_ratio, Optimal_ratio

3. **Format number helper**: `format_number()` for consistent decimal formatting

**Decision needed**:
- Bug fixes: **Must include** in this proposal
- Alpha interpolation: **Defer** or include? (affects alpha precision)
- Tradeoff calculation: **Defer** or include? (adds new output fields)

## Why We Can't Simply Merge Matt's Branch

Attempting to merge `origin/MATT_P` into `main` results in:
- Conflict in `config.py` (different implementations)
- Conflict in `main.py` (many conflicts in analysis workflow)
- Conflict in `quantify.py` (conflicts in core logic)
- Brings in `.DS_Store` and other binary artifacts
- Removes our `scaling.py` module
- Removes `# pragma: no cover` comments (breaks coverage)
- Different import patterns that would break tests

**Approach**: Cherry-pick the specific bug fixes using TDD.

## Proposed Solution

### Phase 1: Test-Driven Bug Fixes

#### Fix 1: LR_angles serialization

**Test first** (TDD):
```python
def test_lr_angles_are_python_floats():
    """Verify LR angles are Python floats, not numpy types."""
    results, _, _ = quantify.analyze(test_graph)
    for angle in results["LR angles"]:
        assert isinstance(angle, (int, float)), f"Expected Python float, got {type(angle)}"
        assert not isinstance(angle, np.floating), f"Should not be numpy float"
```

**Implementation**:
```python
# In quantify.py, line ~816
results["LR angles"] = [float(angle) for angle in angles_LRs] if angles_LRs else []
```

Note: Using `float()` instead of `.item()` for robustness - works with both numpy and Python floats.

#### Fix 2: Graph scaling

**Test first** (TDD):
```python
def test_plot_all_scaling_consistency():
    """Verify plot_all doesn't double-scale data."""
    # Create mock data
    front = {0.5: [100.0, 150.0]}
    actual = [120.0, 160.0]
    randoms = [(110.0, 155.0)]
    mrand, srand = 110.0, 155.0
    scale_factor = 2.0

    # The function should scale consistently
    # Verify via mocking matplotlib calls
    ...
```

**Implementation options**:

**Option A** (Recommended): Pass unscaled data to `plot_all`, let it handle scaling
- Matches Matt's approach
- More explicit and testable
- Requires changing `plot_all` signature

**Option B**: Don't scale inside `plot_all` if already scaled
- Less refactoring
- But harder to reason about

### Phase 2: Add New Test Fixtures

Add test data from Matt's samples to `tests/data/`:

1. `_set1_day1_20230206-153345_022_EtOH_EXP1(1)_plantB_day10.json`
   - 24 lateral roots
   - Complex branching structure
   - Good for edge case testing

2. Additional fixtures TBD based on Matt's data

### Phase 3: Validation with Matt

1. Generate outputs using fixed code
2. Send to Matt for visual comparison
3. Confirm graphs match his expectations
4. Confirm CSV values are correct

## Test Data Available

### Existing test data:
- `tests/data/_set1_day1_20230509-125420_014_plantB_day11.json` (24 LRs)
- `tests/data/test_issue26_230629PN005_0.json` (issue #26 data)

### New test data from Matt:
- `/Users/elizabethberrigan/Downloads/Re__Ref (1)/EtOH_OUTPUT/` (25 JSON files)
- Multiple experiments with varying root structures
- Can select representative samples for test fixtures

## Success Criteria

### Must Have
- [ ] `LR angles` in CSV contains Python floats, not `np.float64(...)`
- [ ] All existing tests pass
- [ ] New tests verify type conversion
- [ ] Graph barycenter correctly positioned
- [ ] Coverage remains ≥90%

### Should Have
- [ ] New test fixtures from Matt's data
- [ ] Matt confirms outputs are correct
- [ ] Documentation of the fix

### Could Have
- [ ] Alpha interpolation enhancement (may defer)
- [ ] Tradeoff calculation (may defer)

## Implementation Plan

### TDD Workflow

1. **Write failing tests first**
   - Test that LR_angles are Python floats
   - Test that plot scaling is consistent

2. **Run tests to confirm they fail**
   - Verify tests catch the actual bugs

3. **Implement minimal fixes**
   - Convert angles to Python floats
   - Fix plot_all scaling logic

4. **Run tests to confirm they pass**
   - All new tests green
   - All existing tests still green

5. **Refactor if needed**
   - Clean up code
   - Add documentation

### Task Breakdown

See [tasks.md](tasks.md) for detailed task breakdown.

## Files to Modify

| File | Changes |
|------|---------|
| `tests/test_quantify.py` | Add type verification tests for LR_angles |
| `tests/test_main.py` | Add plot scaling tests (if feasible with mocks) |
| `tests/data/` | Add new test fixtures |
| `tests/fixtures.py` | Add fixture functions for new data |
| `src/ariadne_roots/quantify.py` | Fix angle type conversion |
| `src/ariadne_roots/main.py` | Fix plot_all call (pass unscaled data) |
| `CHANGELOG.md` | Document fixes |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Fix breaks existing functionality | Low | High | Comprehensive test suite, TDD approach |
| Matt's expected outputs differ from ours | Medium | Medium | Validation phase with Matt |
| Missing edge cases in angle conversion | Low | Medium | Multiple test fixtures |
| Plot fix requires significant refactoring | Medium | Medium | Consider both implementation options |

## Questions for Elizabeth

1. **Should we include alpha interpolation in this fix?**
   - It's an enhancement, not a bug fix
   - Recommendation: Defer to separate proposal

2. **Which test fixtures should we add?**
   - Recommendation: Select 2-3 representative samples from Matt's data
   - One with many LRs, one with few, one edge case

3. **How should we validate with Matt?**
   - Option A: Send him the fixed package to test
   - Option B: Generate outputs and send for visual comparison
   - Recommendation: Option B first, then Option A for final confirmation

## Timeline

- **Phase 1** (Bug fixes with TDD): 1-2 hours
- **Phase 2** (Test fixtures): 30 minutes
- **Phase 3** (Validation with Matt): Async, depends on Matt's availability
- **Total**: 2-4 hours + validation time

## Related

- v0.1.0a1 pre-release
- Matt's branch: `origin/MATT_P`
- Original PR: #29
- Integration PR: #33

## References

- Matt's email (2024-12-03) reporting bugs
- Matt's CSV output showing `np.float64` issue
- Git diff between `main` and `origin/MATT_P`
