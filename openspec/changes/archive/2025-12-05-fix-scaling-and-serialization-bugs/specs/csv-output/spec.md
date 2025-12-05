# CSV Output Specification

## ADDED Requirements

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
