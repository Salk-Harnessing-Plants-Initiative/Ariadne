# testing Specification

## Purpose
TBD - created by archiving change fix-scaling-and-serialization-bugs. Update Purpose after archive.
## Requirements
### Requirement: CSV Field Type Validation Tests

The test suite SHALL include comprehensive tests that verify all CSV output fields have correct Python native types.

#### Scenario: Numeric fields are validated for type
- **WHEN** `test_csv_field_types()` runs
- **THEN** all numeric fields in results are verified to be `int` or `float`
- **AND** array fields (like "LR lengths", "LR angles") are verified to be lists of native Python types
- **AND** no numpy scalar types are present in the results

#### Scenario: Tests fail before fix is applied
- **WHEN** tests are run against code without the numpy conversion fix
- **THEN** the type validation tests SHALL fail
- **AND** the failure message indicates numpy types were found

### Requirement: CSV Field Range Validation Tests

The test suite SHALL include tests that verify CSV output fields have expected value ranges.

#### Scenario: Positive fields are validated
- **WHEN** `test_csv_field_ranges()` runs
- **THEN** length fields (Total root length, PR length, etc.) are verified to be non-negative
- **AND** count fields (LR count) are verified to be non-negative integers
- **AND** density fields are verified to be non-negative

#### Scenario: Angle fields are in valid range
- **WHEN** results contain LR angles
- **THEN** each angle is verified to be between 0 and 180 degrees
- **AND** Mean LR angles and Median LR angles are between 0 and 180

### Requirement: CSV Serialization Validation Tests

The test suite SHALL include tests that verify CSV output can be serialized without numpy type representations.

#### Scenario: CSV output contains no numpy strings
- **WHEN** `test_csv_serialization_no_numpy()` runs
- **THEN** the serialized CSV content is checked for "np.float64"
- **AND** the serialized CSV content is checked for "np.int64"
- **AND** the test fails if any numpy type representations are found

### Requirement: Test Fixtures from Real Data

The test suite SHALL include test fixtures derived from real Arabidopsis root data to validate the fixes work on production data.

#### Scenario: Tests run on real data fixtures
- **WHEN** CSV validation tests are run
- **THEN** the tests use at least one real data fixture from Matt's samples
- **AND** the tests verify the fix works on real-world root structures

