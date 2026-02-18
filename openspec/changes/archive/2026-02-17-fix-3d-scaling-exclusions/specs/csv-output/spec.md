## ADDED Requirements

### Requirement: 3D Dimensionless Field Scaling Exclusion

The scaling module SHALL exclude all 3D Pareto dimensionless fields from length-based scaling transformations.

Dimensionless fields are ratios and weights that have no length unit and should remain unchanged when converting between pixel and physical length units.

#### Scenario: 3D weight fields are not scaled
- **GIVEN** results containing `beta_3d`, `gamma_3d` (Pareto weight parameters)
- **WHEN** `scale_results()` is called with a scale factor
- **THEN** `beta_3d` and `gamma_3d` retain their original values
- **AND** the values remain in the range [0, 1]

#### Scenario: 3D epsilon fields are not scaled
- **GIVEN** results containing `epsilon_3d`, `epsilon_3d_material`, `epsilon_3d_transport`, `epsilon_3d_coverage`
- **WHEN** `scale_results()` is called with a scale factor
- **THEN** all epsilon fields retain their original values
- **AND** the values remain >= 1.0 (multiplicative distance indicator)

#### Scenario: Random tree 3D dimensionless fields are not scaled
- **GIVEN** results containing `beta_3d (random)`, `gamma_3d (random)`, `epsilon_3d (random)`, and related fields
- **WHEN** `scale_results()` is called with a scale factor
- **THEN** all random tree dimensionless fields retain their original values