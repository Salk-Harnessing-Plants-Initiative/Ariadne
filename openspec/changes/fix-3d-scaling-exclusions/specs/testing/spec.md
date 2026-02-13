## ADDED Requirements

### Requirement: 3D Scaling Exclusion Tests

The test suite SHALL include comprehensive tests for 3D dimensionless field scaling exclusion.

#### Scenario: Unit tests verify 3D weight field exclusions
- **WHEN** `test_3d_weight_fields_excluded()` runs
- **THEN** the test verifies `beta_3d` matches exclusion patterns
- **AND** the test verifies `gamma_3d` matches exclusion patterns
- **AND** the test verifies `beta_3d (random)` matches exclusion patterns
- **AND** the test verifies `gamma_3d (random)` matches exclusion patterns

#### Scenario: Unit tests verify 3D epsilon field exclusions
- **WHEN** `test_3d_epsilon_fields_excluded()` runs
- **THEN** the test verifies `epsilon_3d` matches exclusion patterns
- **AND** the test verifies `epsilon_3d_material` matches exclusion patterns
- **AND** the test verifies `epsilon_3d_transport` matches exclusion patterns
- **AND** the test verifies `epsilon_3d_coverage` matches exclusion patterns
- **AND** the test verifies all `(random)` variants match exclusion patterns

#### Scenario: Integration test verifies 3D scaling behavior
- **WHEN** `test_3d_scaling_preserves_dimensionless_fields()` runs
- **THEN** the test applies a scale factor to 3D results
- **AND** verifies all dimensionless fields are unchanged
- **AND** verifies length fields are correctly scaled

#### Scenario: Tests fail before fix is applied
- **WHEN** tests are run against code without the 3D exclusion fix
- **THEN** the exclusion tests SHALL fail
- **AND** the integration test SHALL show incorrect scaled values for dimensionless fields