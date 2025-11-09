# Proposal: Add Tests for Scaling Logic

## Why

PR #33 adds user-tunable scaling functionality that converts pixel measurements to real-world units. While the overall test coverage remains at 98.32%, the new scaling logic in `main.py` is NOT covered by automated tests because:

1. `main.py` is a Tkinter GUI module that is never imported during test runs (tkinter is mocked)
2. The scaling dialog (`ask_scale` method) requires user interaction
3. The scaling logic in `import_file` method executes only during GUI workflow

**Current Coverage Gap**:
- Config module:  100% covered (2/2 statements)
- Scaling dialog (ask_scale): L 0% covered (~80 lines)
- CSV scaling logic (import_file): L 0% covered (~40 lines)
- plot_all improvements:  Marked `# pragma: no cover` (GUI visualization)

## What Changes

Add unit tests for the **data transformation logic** (the parts that can be tested without GUI):

### 1. Config Module Tests
- Test default values (1.0, "px")
- Test setting custom values
- Test module-level state persistence

### 2. Scaling Logic Tests
Extract and test the core scaling transformation:
- Test excluded fields are NOT scaled (LR density, alpha, angles, etc.)
- Test numeric fields ARE scaled by factor
- Test array fields are scaled element-wise (LR lengths, minimal lengths)
- Test non-numeric fields are preserved unchanged
- Test edge cases (zero, negative, None values)

### 3. Integration Test (Optional)
- Mock the AnalyzerUI workflow
- Verify scaled results end-to-end

## Impact

- **Affected specs**: Add `test-coverage` spec with scaling test requirements
- **Affected code**:
  - `tests/test_main.py` - Add scaling logic unit tests
  - `tests/test_config.py` (new) - Add config module tests
  - NO changes to production code
- **Coverage impact**: Increase testable scaling logic coverage from 0% to 100%
- **Note**: GUI interactions (dialog, buttons) will remain untested and verified manually

## Non-Goals

- This proposal does NOT test GUI interactions (tkinter dialogs, user input)
- This proposal does NOT test visualization rendering
- This proposal does NOT change any production code

## Success Criteria

1. All new tests pass
2. Coverage of scaling transformation logic: 100%
3. Overall project coverage remains e98%
4. No false positives (tests actually verify behavior)
5. Tests are fast (no GUI rendering, no file I/O where possible)
