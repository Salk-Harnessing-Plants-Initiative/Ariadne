# Tasks: Fix Scaling and Serialization Bugs

## Overview

Fix two bugs reported by Matt Platre in v0.1.0a1:
1. `np.float64` appearing in CSV LR_angles field
2. Graph barycenter/RSA not scaled properly

Using **TDD approach**: Write failing tests first, then implement fixes.

## Phase 1: Test-Driven Bug Fixes

### 1.1 Bug #1: LR_angles serialization

#### Write failing tests

- [ ] Create test `test_lr_angles_are_python_floats`
  - Load real root data fixture
  - Call `quantify.analyze()`
  - Assert each angle in `results["LR angles"]` is `isinstance(angle, (int, float))`
  - Assert each angle is NOT `isinstance(angle, np.floating)`

- [ ] Create test `test_lr_angles_csv_serialization`
  - Verify angles serialize to clean numbers in CSV format
  - No `np.float64(...)` in string representation

- [ ] Run tests - confirm they FAIL (demonstrating the bug exists)

#### Implement fix

- [ ] Modify `quantify.py` line ~816
  - Change: `results["LR angles"] = angles_LRs`
  - To: `results["LR angles"] = [float(angle) for angle in angles_LRs] if angles_LRs else []`

- [ ] Run tests - confirm they PASS

- [ ] Run full test suite - confirm no regressions

### 1.2 Bug #2: Graph double-scaling

#### Investigate current behavior

- [ ] Trace the data flow:
  1. `quantify.analyze()` returns unscaled `results`
  2. `main.py` applies `apply_scaling_transformation()` → `scaled_results`
  3. `main.py` passes `scaled_results` values to `plot_all()`
  4. `plot_all()` scales again via `config.length_scale_factor`

- [ ] Confirm this is the root cause of misaligned graphs

#### Write failing tests

- [ ] Create test `test_plot_data_scaling_consistency`
  - Use mock/patch to capture what values are plotted
  - Verify data is scaled exactly once, not twice

- [ ] Create test `test_analyze_returns_unscaled_values`
  - Verify `quantify.analyze()` returns pixel values (unscaled)
  - This is the expected contract

- [ ] Run tests - confirm they reveal the issue

#### Implement fix

**Option A (Recommended)**: Pass unscaled data to `plot_all`

- [ ] Modify `main.py` `import_file()` method:
  - Change plot_all call to pass `results` instead of `scaled_results`
  - Keep CSV writing using `scaled_results`

- [ ] Verify `plot_all()` continues to scale internally via `config`

**Option B** (Alternative): Make `plot_all` accept pre-scaled data

- [ ] Add parameter to `plot_all()` to indicate if data is pre-scaled
- [ ] Skip internal scaling if data is already scaled

- [ ] Run tests - confirm they PASS

- [ ] Run full test suite - confirm no regressions

## Phase 1.5: CSV Output Validation Tests

### 1.5.1 Create comprehensive CSV field validation tests

- [ ] Create `tests/test_csv_output.py` for CSV output validation
  - Test each field has correct type
  - Test each field has expected range
  - Test array fields contain correct element types

- [ ] Test field types:
  ```python
  def test_csv_field_types():
      """Verify each CSV field has correct Python type."""
      results, _, _ = quantify.analyze(test_graph)

      # Numeric fields (should be float or int)
      numeric_fields = [
          "Total root length", "Travel distance", "PR length",
          "PR_minimal_length", "Basal Zone length", "Branched Zone length",
          "Apical Zone length", "Mean LR lengths", "Mean LR minimal lengths",
          "Median LR lengths", "Median LR minimal lengths", "sum LR minimal lengths",
          "Mean LR angles", "Median LR angles", "LR count", "LR density",
          "Branched Zone density", "Barycenter x displacement",
          "Barycenter y displacement", "Total minimal Distance",
          "Tortuosity", "Convex Hull Area"
      ]
      for field in numeric_fields:
          assert isinstance(results[field], (int, float)), f"{field} should be numeric"
          assert not isinstance(results[field], np.floating), f"{field} should not be np.floating"

      # Array fields (should be lists of Python floats)
      array_fields = ["LR lengths", "LR angles", "LR minimal lengths"]
      for field in array_fields:
          assert isinstance(results[field], list), f"{field} should be a list"
          for i, val in enumerate(results[field]):
              assert isinstance(val, (int, float)), f"{field}[{i}] should be numeric"
              assert not isinstance(val, np.floating), f"{field}[{i}] should not be np.floating"
  ```

- [ ] Test field ranges:
  ```python
  def test_csv_field_ranges():
      """Verify each CSV field has expected range."""
      results, _, _ = quantify.analyze(test_graph)

      # Positive fields (lengths, distances, counts)
      positive_fields = [
          "Total root length", "Travel distance", "PR length",
          "LR count", "Total minimal Distance"
      ]
      for field in positive_fields:
          assert results[field] >= 0, f"{field} should be non-negative"

      # Angle fields (should be in degrees, 0-180)
      if results.get("LR angles"):
          for angle in results["LR angles"]:
              assert 0 <= angle <= 180, f"LR angle {angle} out of range"
          assert 0 <= results["Mean LR angles"] <= 180
          assert 0 <= results["Median LR angles"] <= 180

      # Density fields (should be positive)
      if results.get("LR density"):
          assert results["LR density"] >= 0

      # Alpha (should be 0-1)
      if results.get("alpha"):
          assert 0 <= results["alpha"] <= 1, f"alpha should be 0-1"
  ```

- [ ] Test CSV serialization:
  ```python
  def test_csv_serialization_no_numpy():
      """Verify CSV output contains no numpy type representations."""
      results, _, _ = quantify.analyze(test_graph)

      # Convert to CSV-like string representation
      import csv
      import io
      output = io.StringIO()
      writer = csv.DictWriter(output, fieldnames=results.keys())
      writer.writeheader()
      writer.writerow(results)

      csv_content = output.getvalue()
      assert "np.float64" not in csv_content, "CSV contains np.float64"
      assert "np.int64" not in csv_content, "CSV contains np.int64"
      assert "numpy" not in csv_content.lower(), "CSV contains numpy reference"
  ```

### 1.5.2 Test with multiple fixtures

- [ ] Run validation tests on all available fixtures:
  - `_set1_day1_20230509-125420_014_plantB_day11.json`
  - `test_issue26_230629PN005_0.json`
  - New fixtures from Matt's data

- [ ] Create parametrized tests to run on all fixtures

## Phase 2: Add Test Fixtures

### 2.1 Select test data from Matt's samples

- [ ] Review available data in `/Users/elizabethberrigan/Downloads/Re__Ref (1)/EtOH_OUTPUT/`
- [ ] Select representative samples:
  - One with many lateral roots (complex)
  - One with few lateral roots (simple)
  - One with edge case structure

- [ ] Copy selected JSON files to `tests/data/`
  - Rename to follow convention: `test_<description>.json`
  - Remove parentheses and special chars from filenames

### 2.2 Create fixture functions

- [ ] Add to `tests/fixtures.py`:
  ```python
  @pytest.fixture
  def etoh_plantb_json():
      return "tests/data/test_etoh_plantB_day10.json"
  ```

- [ ] Generate expected values for new fixtures:
  ```python
  results, front, randoms = analyze(graph)
  # Document key expected values
  ```

### 2.3 Document test data

- [ ] Update `tests/data/README.md` with:
  - Source and provenance of new fixtures
  - Expected value derivation method
  - Matt Platre as data contributor

## Phase 3: Validation with Matt

### 3.1 Generate test outputs

- [ ] Create sample CSV output with fixed code
- [ ] Generate sample Pareto graph with fixed code
- [ ] Use same input data Matt used in his report

### 3.2 Send to Matt for validation

- [ ] Email Matt with:
  - Sample CSV showing correct LR_angles format
  - Sample Pareto graph showing correct scaling
  - Request confirmation that outputs match expectations

### 3.3 Iterate if needed

- [ ] If Matt reports issues, investigate and fix
- [ ] Re-validate until Matt confirms correct behavior

## Phase 4: Documentation and Release

### 4.1 Update CHANGELOG

- [ ] Add entry for bug fixes:
  ```markdown
  ### Fixed
  - Fixed `np.float64` serialization in CSV LR_angles field
  - Fixed double-scaling bug in Pareto front graph visualization
  ```

### 4.2 Bump version

- [ ] Update `pyproject.toml` version to `0.1.0a2` or `0.1.0`
- [ ] Decision: pre-release for more testing, or stable release?

### 4.3 Create PR

- [ ] Create branch `fix-scaling-serialization-bugs`
- [ ] Commit changes with descriptive messages
- [ ] Open PR with test results and Matt's validation

### 4.4 Release

- [ ] After PR merge, create GitHub release
- [ ] Publish to PyPI
- [ ] Notify Matt of fix availability

## Test Commands

```bash
# Run specific tests
uv run pytest tests/test_quantify.py -k "lr_angles" -v

# Run all tests with coverage
uv run pytest --cov=ariadne_roots --cov-report=term-missing

# Run tests and verify no regressions
uv run pytest -q
```

## Files to Create/Modify

### New files:
- `tests/data/test_etoh_plantB_day10.json` (new fixture)

### Modified files:
- `tests/test_quantify.py` (add type tests)
- `tests/fixtures.py` (add fixture functions)
- `tests/data/README.md` (document new fixtures)
- `src/ariadne_roots/quantify.py` (fix angle conversion)
- `src/ariadne_roots/main.py` (fix plot_all call)
- `CHANGELOG.md` (document fixes)
- `pyproject.toml` (bump version)

## Success Checklist

### Bug #1 (LR_angles)
- [ ] Test exists that verifies angles are Python floats
- [ ] Test fails before fix
- [ ] Test passes after fix
- [ ] CSV output shows clean numbers (no `np.float64`)

### Bug #2 (Graph scaling)
- [ ] Root cause confirmed via code tracing
- [ ] Test exists that verifies scaling consistency
- [ ] Test fails before fix (or demonstrates issue)
- [ ] Test passes after fix
- [ ] Graph barycenter positioned correctly

### Overall
- [ ] All 115+ existing tests pass
- [ ] Coverage remains ≥90%
- [ ] Matt validates outputs are correct
- [ ] No regressions in existing functionality

## Decision Points

1. **Alpha interpolation**: Include in this fix or defer?
   - Recommendation: **Defer** to separate proposal (it's an enhancement, not a bug)

2. **Tradeoff calculation**: Include or defer?
   - Recommendation: **Defer** (new feature, not a bug)

3. **Release version**: 0.1.0a2 (another pre-release) or 0.1.0 (stable)?
   - Recommendation: **0.1.0a2** until Matt confirms fix, then **0.1.0** stable

4. **Test fixture selection**: Which of Matt's files to include?
   - Recommendation: 1-2 files that exercise the bug (have LR_angles)
