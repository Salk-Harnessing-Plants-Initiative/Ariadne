## 1. Write Failing Tests (TDD)

- [x] 1.1 Write unit test that verifies `beta_3d` is in excluded_fields
- [x] 1.2 Write unit test that verifies `gamma_3d` is in excluded_fields
- [x] 1.3 Write unit test that verifies `epsilon_3d` is in excluded_fields
- [x] 1.4 Write unit test that verifies `epsilon_3d_material`, `epsilon_3d_transport`, `epsilon_3d_coverage` are excluded
- [x] 1.5 Write unit test that verifies all `(random)` variants of 3D fields are excluded
- [x] 1.6 Write integration test that applies scaling to 3D results and verifies dimensionless fields are unchanged
- [x] 1.7 Run tests to confirm they fail with current implementation

## 2. Implement Bug Fix

- [x] 2.1 Add `beta` to excluded_fields (catches `beta_3d` via substring matching)
- [x] 2.2 Add `gamma` to excluded_fields (catches `gamma_3d` via substring matching)
- [x] 2.3 Add `epsilon` to excluded_fields (catches all epsilon variants via substring matching)
- [x] 2.4 Run tests to confirm they pass

## 3. Validation

- [x] 3.1 Run full test suite (208 tests passed)
- [x] 3.2 Verify scaled CSV output contains correct dimensionless values
- [x] 3.3 Add inline documentation explaining why these fields are excluded