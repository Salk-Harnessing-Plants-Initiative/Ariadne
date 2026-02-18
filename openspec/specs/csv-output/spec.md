# csv-output Specification

## Purpose
TBD - created by archiving change fix-scaling-and-serialization-bugs. Update Purpose after archive.
## Requirements
### Requirement: Clean CSV Serialization

All analysis results written to CSV SHALL serialize cleanly without Python type wrapper representations.

#### Scenario: CSV contains no numpy type strings
- **WHEN** analysis results are written to CSV
- **THEN** the CSV content does NOT contain "np.float64"
- **AND** the CSV content does NOT contain "np.int64"
- **AND** the CSV content does NOT contain "numpy"

#### Scenario: Array fields serialize as readable lists
- **GIVEN** results with array fields like "LR angles", "LR lengths"
- **WHEN** the results are written to CSV
- **THEN** array values appear as `[1.23, 4.56, 7.89]` not `[np.float64(1.23), ...]`

### Requirement: Numeric Field Type Safety

All numeric fields in the results dictionary SHALL be Python native types suitable for JSON/CSV serialization.

#### Scenario: Scalar fields are native Python types
- **WHEN** `quantify.analyze()` returns results
- **THEN** numeric scalar fields are `int` or `float`, not `numpy.int64` or `numpy.float64`

#### Scenario: Array fields contain native Python types
- **WHEN** `quantify.analyze()` returns results with array fields
- **THEN** each element in "LR angles", "LR lengths", "LR minimal lengths" is a Python `float`
- **AND** no element is an instance of `numpy.floating` or `numpy.integer`

### Requirement: 3D Dimensionless Field Scaling Exclusion

The scaling module SHALL exclude all 3D Pareto dimensionless fields from length-based scaling transformations.

Dimensionless fields are ratios and weights that have no length unit and should remain unchanged when converting between pixel and physical length units.

#### Scenario: 3D weight fields are not scaled
- **GIVEN** results containing `beta_3d`, `gamma_3d` (Pareto weight parameters)
- **WHEN** `scale_results()` is called with a scale factor
- **THEN** `beta_3d` and `gamma_3d` retain their original values
- **AND** the values remain in the range [0, 1]

#### Scenario: 3D epsilon fields are not scaled
- **GIVEN** results containing `epsilon_3d`, `epsilon_3d_material`, `epsilon_3d_transport`, `epsilon_3d_coverage`
- **WHEN** `scale_results()` is called with a scale factor
- **THEN** all epsilon fields retain their original values
- **AND** the values remain >= 1.0 (multiplicative distance indicator)

#### Scenario: Random tree 3D dimensionless fields are not scaled
- **GIVEN** results containing `beta_3d (random)`, `gamma_3d (random)`, `epsilon_3d (random)`, and related fields
- **WHEN** `scale_results()` is called with a scale factor
- **THEN** all random tree dimensionless fields retain their original values

