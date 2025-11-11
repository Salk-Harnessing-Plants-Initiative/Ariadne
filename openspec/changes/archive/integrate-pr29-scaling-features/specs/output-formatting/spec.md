# Spec: Output Formatting

This spec defines how analysis results are formatted and scaled for output.

## ADDED Requirements

### Requirement: Scaled Measurement Output

Analysis results SHALL be scaled according to user-configured conversion factors, converting pixel measurements to real-world units.

#### Scenario: Length measurements are scaled

- **GIVEN** user has set a scaling factor of X units per pixel
- **WHEN** analysis generates length measurements (Total wiring, PR length, LR lengths)
- **THEN** output SHALL multiply pixel values by X
- **AND** SHALL write scaled values to CSV output
- **AND** SHALL use the user-specified unit label

#### Scenario: Dimensionless metrics are NOT scaled

- **GIVEN** user has set a custom scaling factor
- **WHEN** analysis generates dimensionless metrics:
  - LR density (count/length)
  - Alpha (Pareto optimality metric)
  - Tortuosity (ratio)
  - LR count (integer)
  - Angles (degrees)
- **THEN** output SHALL NOT apply scaling to these values
- **AND** SHALL write them unchanged to CSV output

#### Scenario: Array fields are scaled element-wise

- **GIVEN** user has set a scaling factor of X
- **WHEN** analysis generates array fields (LR lengths, LR minimal lengths)
- **THEN** each element in the array SHALL be multiplied by X
- **AND** the scaled array SHALL be written to CSV output

#### Scenario: Scaling preserves field exclusions

- **GIVEN** the following fields must not be scaled:
  - "LR density"
  - "alpha"
  - "Mean LR angles"
  - "Median LR angles"
  - "LR count"
  - "Branched Zone density"
  - "scaling distance to front"
  - "Tortuosity"
  - "scaling (random)"
- **WHEN** scaling is applied to results
- **THEN** these fields SHALL remain unscaled
- **AND** all other numeric fields SHALL be scaled

### Requirement: Configuration Module

A global configuration module SHALL store scaling parameters accessible across the application.

#### Scenario: Config module provides defaults

- **GIVEN** the config module is imported
- **WHEN** no scaling has been set
- **THEN** `length_scale_factor` SHALL default to 1.0
- **AND** `length_scale_unit` SHALL default to "px"

#### Scenario: Config module stores user scaling

- **GIVEN** user has configured scaling in the UI
- **WHEN** scaling values are set
- **THEN** config.length_scale_factor SHALL store the numeric factor
- **AND** config.length_scale_unit SHALL store the unit string
- **AND** these values SHALL persist for the analysis session

#### Scenario: Analysis functions access config

- **GIVEN** config module has scaling values set
- **WHEN** analysis functions (quantify.analyze, pareto front generation) run
- **THEN** they SHALL import and read config.length_scale_factor
- **AND** SHALL import and read config.length_scale_unit
- **AND** SHALL apply scaling to appropriate output fields
