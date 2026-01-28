# Analysis Output Specification

## MODIFIED Requirements

### Requirement: Alpha Value Precision

The `alpha` value returned by `distance_from_front()` SHALL be interpolated between the two closest discrete Pareto front alpha values for higher precision.

#### Scenario: Interpolated alpha calculation
- **GIVEN** a Pareto front with discrete alpha values (0.00, 0.01, ..., 1.00)
- **AND** an actual tree position
- **WHEN** `distance_from_front()` is called
- **THEN** the function identifies the two closest discrete alpha values
- **AND** calculates a distance-weighted interpolated alpha
- **AND** returns the interpolated alpha as a Python float

#### Scenario: Equal distance edge case
- **GIVEN** an actual tree equidistant from two Pareto front points
- **WHEN** `distance_from_front()` is called
- **THEN** the function returns the first (lower) alpha value

#### Scenario: Single Pareto point edge case
- **GIVEN** a Pareto front with only one point
- **WHEN** `distance_from_front()` is called
- **THEN** the function returns that single alpha value

### Requirement: Alpha Return Type

The `alpha` and `alpha (random)` values in the results dictionary SHALL be Python native `float` types (not strings).

#### Scenario: Alpha is Python float
- **WHEN** `quantify.analyze()` returns results
- **THEN** `results["alpha"]` is a Python `float`
- **AND** `results["alpha (random)"]` is a Python `float`
- **AND** neither value is a string representation
