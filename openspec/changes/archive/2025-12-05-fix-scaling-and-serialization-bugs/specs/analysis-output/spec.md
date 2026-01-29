# Analysis Output Specification

## ADDED Requirements

### Requirement: LR Angles Python Float Serialization

The `quantify.analyze()` function SHALL return lateral root angles as Python native `float` types, not numpy scalar types.

This fixes the bug where CSV output contained `np.float64(...)` instead of plain numbers.

#### Scenario: LR angles are Python floats after analysis
- **GIVEN** a root graph with lateral roots
- **WHEN** `quantify.analyze()` is called
- **THEN** `results["LR angles"]` is a list of Python `float` values
- **AND** no element is an instance of `numpy.floating`

#### Scenario: Empty LR angles list for roots without laterals
- **GIVEN** a root graph with no lateral roots
- **WHEN** `quantify.analyze()` is called
- **THEN** `results["LR angles"]` is an empty list `[]`

### Requirement: Single-Pass Plot Scaling

The visualization pipeline SHALL scale data exactly once, not twice.

When `main.py` calls `plot_all()`, the data passed MUST be unscaled (pixel values), and `plot_all()` SHALL handle all scaling internally using `config.length_scale_factor`.

#### Scenario: Unscaled data passed to plot_all
- **GIVEN** analysis results from `quantify.analyze()`
- **WHEN** `main.py` calls `plot_all()`
- **THEN** the `actual` parameter contains unscaled values (from `results`, not `scaled_results`)
- **AND** the `mrand` and `srand` parameters contain unscaled random tree values

#### Scenario: Barycenter position matches RSA
- **GIVEN** a root graph with known barycenter position
- **WHEN** the Pareto front graph is plotted
- **THEN** the RSA marker position matches the actual root's position on the scaled graph
- **AND** the RSA marker is NOT offset due to double-scaling

## ADDED Requirements (Deferred - Matt's Enhancements)

### Requirement: Alpha Interpolation (DEFERRED)

> **Status**: Deferred to future proposal. This is an enhancement, not a bug fix.

The system SHOULD compute alpha values with higher precision using linear interpolation between the two closest Pareto front points.

#### Scenario: High-precision alpha calculation
- **GIVEN** an actual root position near the Pareto front
- **WHEN** alpha is calculated
- **THEN** the alpha value is interpolated to 6 decimal places
- **AND** the interpolation uses distance-weighted averaging of the two nearest front points

### Requirement: Tradeoff Calculation (DEFERRED)

> **Status**: Deferred to future proposal. This is a new feature, not a bug fix.

The system SHOULD compute a tradeoff metric comparing the actual root architecture to optimal Steiner and Satellite architectures.

#### Scenario: Tradeoff metric calculation
- **GIVEN** a root graph with Pareto front computed
- **WHEN** tradeoff calculation is performed
- **THEN** the system returns: Tradeoff, Steiner_length, Steiner_distance, Satellite_length, Satellite_distance, Actual_ratio, Optimal_ratio

### Requirement: Format Number Helper (DEFERRED)

> **Status**: Deferred to future proposal. This is a utility enhancement.

The system SHOULD provide a `format_number()` helper for consistent decimal formatting in output.

#### Scenario: Consistent number formatting
- **WHEN** numeric values are formatted for output
- **THEN** the formatting is consistent across all output fields
