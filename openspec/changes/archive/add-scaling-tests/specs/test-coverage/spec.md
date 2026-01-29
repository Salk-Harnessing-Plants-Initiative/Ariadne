# Spec: Test Coverage

This spec defines test coverage requirements for Ariadne's scaling functionality.

## ADDED Requirements

### Requirement: Config Module Testing

The config module SHALL have comprehensive test coverage for its scaling configuration functionality.

#### Scenario: Default configuration values

- **GIVEN** the config module is imported
- **WHEN** no values have been set
- **THEN** `length_scale_factor` SHALL equal 1.0
- **AND** `length_scale_unit` SHALL equal "px"

#### Scenario: Setting custom scale factor

- **GIVEN** the config module is imported
- **WHEN** `config.length_scale_factor` is set to 2.5
- **THEN** subsequent reads SHALL return 2.5
- **AND** the value SHALL persist for the module's lifetime

#### Scenario: Setting custom unit

- **GIVEN** the config module is imported
- **WHEN** `config.length_scale_unit` is set to "mm"
- **THEN** subsequent reads SHALL return "mm"
- **AND** the value SHALL persist for the module's lifetime

### Requirement: Scaling Transformation Testing

The scaling transformation logic SHALL be tested to verify correct handling of all field types.

#### Scenario: Excluded fields not scaled

- **GIVEN** a results dictionary with excluded field names:
  - "LR density", "alpha", "Mean LR angles", "Median LR angles"
  - "LR count", "Branched Zone density", "scaling distance to front"
  - "Tortuosity", "scaling (random)"
- **WHEN** scaling transformation is applied with scale_factor = 2.0
- **THEN** these fields SHALL remain unchanged
- **AND** their values SHALL equal the original values

#### Scenario: Numeric fields scaled

- **GIVEN** a results dictionary with numeric fields (Total root length, PR length, etc.)
- **WHEN** scaling transformation is applied with scale_factor = 2.5
- **THEN** each numeric field SHALL be multiplied by 2.5
- **AND** the result SHALL be a float

#### Scenario: Array fields scaled element-wise

- **GIVEN** a results dictionary with array fields ["LR lengths", "LR minimal lengths"]
- **AND** "LR lengths" contains [10.0, 20.0, 30.0]
- **WHEN** scaling transformation is applied with scale_factor = 2.0
- **THEN** "LR lengths" SHALL contain [20.0, 40.0, 60.0]
- **AND** each element SHALL be scaled independently

#### Scenario: Non-numeric fields preserved

- **GIVEN** a results dictionary with non-numeric field "filename" = "test.json"
- **WHEN** scaling transformation is applied with any scale_factor
- **THEN** "filename" SHALL remain "test.json"
- **AND** no type conversion SHALL occur

#### Scenario: Edge case - zero scale factor

- **GIVEN** a results dictionary with numeric value 100.0
- **WHEN** scaling transformation is applied with scale_factor = 0
- **THEN** the result SHALL be 0.0
- **AND** no error SHALL be raised

#### Scenario: Edge case - non-integer scale factor

- **GIVEN** a results dictionary with numeric value 10
- **WHEN** scaling transformation is applied with scale_factor = 2.54
- **THEN** the result SHALL be 25.4
- **AND** precision SHALL be maintained

#### Scenario: Edge case - None values

- **GIVEN** a results dictionary with value None
- **WHEN** scaling transformation is applied
- **THEN** the value SHALL remain None
- **AND** no error SHALL be raised

### Requirement: Overall Coverage Maintenance

Test additions SHALL maintain the project's high test coverage standards.

#### Scenario: Coverage threshold maintained

- **GIVEN** current project coverage is 98.32%
- **WHEN** new scaling tests are added
- **THEN** overall coverage SHALL remain ≥98%
- **AND** no existing tests SHALL break

#### Scenario: Fast test execution

- **GIVEN** new scaling tests are added
- **WHEN** the test suite is run
- **THEN** scaling tests SHALL complete in <1 second total
- **AND** SHALL NOT require file I/O (except for config import)
- **AND** SHALL NOT render GUI elements
