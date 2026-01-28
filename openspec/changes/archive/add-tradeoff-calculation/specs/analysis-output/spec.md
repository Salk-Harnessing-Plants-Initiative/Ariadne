# Analysis Output Specification

## ADDED Requirements

### Requirement: Tradeoff Calculation

The system SHALL calculate a Tradeoff metric comparing the actual root architecture to theoretically optimal Steiner and Satellite architectures.

#### Scenario: Calculate Steiner architecture
- **GIVEN** a Pareto front with multiple points
- **WHEN** `calculate_tradeoff()` is called
- **THEN** Steiner point is identified as the point with minimum total root length
- **AND** `Steiner_length` equals the minimum total root length
- **AND** `Steiner_distance` equals the travel distance at that point

#### Scenario: Calculate Satellite architecture
- **GIVEN** a Pareto front with multiple points
- **WHEN** `calculate_tradeoff()` is called
- **THEN** Satellite point is identified as the point with minimum travel distance
- **AND** `Satellite_distance` equals the minimum travel distance
- **AND** `Satellite_length` equals the total root length at that point

#### Scenario: Calculate Tradeoff ratio
- **GIVEN** valid Steiner, Satellite, and actual tree values
- **WHEN** `calculate_tradeoff()` is called
- **THEN** `Actual_ratio` = actual_length / actual_distance
- **AND** `Optimal_ratio` = steiner_length / satellite_distance
- **AND** `Tradeoff` = Actual_ratio / Optimal_ratio

#### Scenario: Handle division by zero
- **GIVEN** actual_distance or satellite_distance is zero
- **WHEN** `calculate_tradeoff()` is called
- **THEN** the function returns `None` for affected ratios
- **AND** logs a warning message

### Requirement: Tradeoff Output Fields

The results dictionary SHALL include all tradeoff-related fields.

#### Scenario: All tradeoff fields present
- **WHEN** `quantify.analyze()` returns results with a valid Pareto front
- **THEN** results contains "Tradeoff" (float or None)
- **AND** results contains "Steiner_length" (float)
- **AND** results contains "Steiner_distance" (float)
- **AND** results contains "Satellite_length" (float)
- **AND** results contains "Satellite_distance" (float)
- **AND** results contains "Actual_ratio" (float or inf)
- **AND** results contains "Optimal_ratio" (float or inf)
