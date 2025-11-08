# Spec: Root Analysis Testing

## ADDED Requirements

### Requirement: Lateral Root Index Edge Cases

The test suite SHALL verify that lateral root calculations handle non-zero starting LR indices correctly.

#### Scenario: LR indices start at 1 (not 0)

- **GIVEN** a root system graph where lateral root indices start at 1 (primary root is None)
- **WHEN** `calc_len_LRs()` is called
- **THEN** the function SHALL NOT raise `UnboundLocalError`
- **AND** SHALL return valid length and angle data for all lateral roots

#### Scenario: calc_len_LRs_with_distances with non-zero start

- **GIVEN** a root system graph where lateral root indices start at 1
- **WHEN** `calc_len_LRs_with_distances()` is called
- **THEN** the function SHALL NOT raise `UnboundLocalError`
- **AND** SHALL return valid length and distance data for all lateral roots

#### Scenario: Reproduces issue #26 bug

- **GIVEN** test data from real Arabidopsis thaliana root (`test_issue26_230629PN005_0.json`)
- **WHEN** the data is processed through analyze() or individual calculation functions
- **THEN** calculations SHALL complete successfully without errors
- **AND** SHALL produce valid trait measurements

### Requirement: Bug Fix Coverage

Test coverage SHALL include all lines modified in PR #27.

#### Scenario: min_num_LRs calculation coverage

- **GIVEN** PR #27 adds `min_num_LRs = min(idxs.values())` on lines 254 and 532
- **WHEN** tests execute
- **THEN** these lines SHALL be covered by at least one test case
- **AND** coverage reports SHALL show 100% coverage on diff lines

#### Scenario: Modified loop range coverage

- **GIVEN** PR #27 changes loop from `range(num_LRs)` to `range(min_num_LRs, num_LRs)`
- **WHEN** tests execute
- **THEN** the modified loop ranges SHALL be exercised
- **AND** tests SHALL verify correct iteration behavior

### Requirement: Test Fixture Management

Test data SHALL be managed to distinguish between committed fixtures and temporary analysis outputs.

#### Scenario: Gitignore excludes temporary files

- **GIVEN** temporary analysis files (notebooks, CSVs, PNGs) may be generated during development
- **WHEN** developers run git status
- **THEN** `.gitignore` SHALL exclude wildcard patterns (`*.ipynb`, `*.png`, `*.csv`)
- **AND** SHALL NOT exclude committed test fixtures in `tests/data/`

#### Scenario: Test fixtures are version controlled

- **GIVEN** test fixtures like `test_issue26_230629PN005_0.json` in `tests/data/`
- **WHEN** these files are added to git
- **THEN** they SHALL be tracked despite wildcard exclusions
- **AND** SHALL use specific filenames (not matching temporary file patterns)
