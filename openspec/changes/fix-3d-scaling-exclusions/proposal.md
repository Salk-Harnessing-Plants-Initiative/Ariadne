## Why

The `scaling.py` module's `excluded_fields` set is missing 3D Pareto analysis fields that are dimensionless (ratios and weights). Currently, `alpha` is excluded (which catches `alpha_3d` via substring matching), but `beta_3d`, `gamma_3d`, `epsilon_3d`, and related fields have no matching exclusion pattern.

When users apply length scaling (e.g., pixels to mm), these dimensionless fields would be incorrectly multiplied by the scale factor, producing scientifically meaningless values. For example, `gamma_3d=0.98` (a weight between 0-1) could become `gamma_3d=0.0098` with a 0.01 scale factor.

This bug was not caught because test_scaling.py only tests 2D fields.

## What Changes

- **CRITICAL**: Add missing 3D field exclusions: `beta_3d`, `gamma_3d`, `epsilon_3d`, `epsilon_3d_material`, `epsilon_3d_transport`, `epsilon_3d_coverage` (and their `(random)` variants)
- Add comprehensive unit tests for all 3D dimensionless fields
- Add integration tests that verify scaled CSV output preserves dimensionless field values
- Document which fields are dimensionless and why they should not be scaled

## Impact

- Affected specs: csv-output, testing
- Affected files: `src/ariadne_roots/scaling.py`, `tests/test_scaling.py`
- No breaking changes to API
- **Scientific accuracy**: Dimensionless ratios and weights will no longer be corrupted by scaling operations