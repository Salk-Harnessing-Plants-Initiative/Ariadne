# Tasks: Add Tests for Scaling Logic

## 1. Config Module Tests

- [x] 1.1 Create `tests/test_config.py`
- [x] 1.2 Add test for default values (length_scale_factor=1.0, length_scale_unit="px")
- [x] 1.3 Add test for setting custom scale factor
- [x] 1.4 Add test for setting custom unit
- [x] 1.5 Add test for module-level state persistence

## 2. Scaling Transformation Tests

- [x] 2.1 Extract scaling logic to testable function (or test in-place with mocks)
- [x] 2.2 Add test for excluded fields NOT being scaled:
  - "LR density", "alpha", "Mean LR angles", "Median LR angles"
  - "LR count", "Branched Zone density", "scaling distance to front"
  - "Tortuosity", "scaling (random)"
- [x] 2.3 Add test for numeric fields being scaled correctly
- [x] 2.4 Add test for array fields scaled element-wise:
  - "LR lengths" → each element multiplied by scale_factor
  - "LR minimal lengths" → each element multiplied by scale_factor
- [x] 2.5 Add test for non-numeric fields preserved unchanged
- [x] 2.6 Add test for edge cases:
  - Scale factor of 0
  - Scale factor of 2.5 (non-integer)
  - None values in results
  - Empty arrays

## 3. Integration Tests (Optional)

- [x] 3.1 Add mock-based test for AnalyzerUI.import_file workflow
- [x] 3.2 Verify scaled_results dictionary structure
- [x] 3.3 Verify filename field is preserved

## 4. Validation

- [x] 4.1 Run test suite and verify all tests pass
- [x] 4.2 Check coverage report for scaling logic
- [x] 4.3 Verify overall coverage remains ≥98%
- [x] 4.4 Update OpenSpec specs with test requirements
