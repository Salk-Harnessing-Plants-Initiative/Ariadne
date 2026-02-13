## ADDED Requirements

### Requirement: 3D Plot Argument Validation Tests

The test suite SHALL include tests that verify plot_all_3d receives correct random tree metrics.

#### Scenario: Integration test verifies prand argument
- **WHEN** `test_3d_plot_receives_random_path_tortuosity()` runs
- **THEN** the test executes the full 3D analysis pipeline
- **AND** captures the arguments passed to `plot_all_3d()`
- **AND** verifies `prand` equals the CSV field `Path tortuosity (random)`
- **AND** the test fails if `prand` equals the actual plant's `Path tortuosity`

#### Scenario: Test detects the bug before fix
- **WHEN** tests are run against code with the bug (passing wrong value)
- **THEN** the validation test SHALL fail
- **AND** the failure message indicates which argument was incorrect

### Requirement: CSV-Plot Data Consistency Tests

The test suite SHALL include tests that verify CSV output matches plot data for 3D analysis.

#### Scenario: All random metrics are consistent
- **WHEN** `test_3d_csv_plot_consistency()` runs
- **THEN** `Total root length (random)` in CSV equals `mrand` in plot
- **AND** `Travel distance (random)` in CSV equals `srand` in plot
- **AND** `Path tortuosity (random)` in CSV equals `prand` in plot