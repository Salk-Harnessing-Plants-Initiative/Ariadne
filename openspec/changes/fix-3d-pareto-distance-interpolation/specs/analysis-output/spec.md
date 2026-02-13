## ADDED Requirements

### Requirement: 3D Pareto Distance Interpolation

The `distance_from_front_3d()` function SHALL use barycentric interpolation with the 3 nearest (α, β) points to compute interpolated parameter values, matching the precision of the 2D `distance_from_front()` function.

The function MUST skip front points where any cost dimension (total_root_length, total_travel_distance, or path_coverage) is zero to prevent division-by-zero errors.

#### Scenario: Interpolation between 3 nearest points
- **GIVEN** a 3D Pareto front with multiple (α, β) points
- **AND** an actual tree position not exactly on any front point
- **WHEN** `distance_from_front_3d()` is called
- **THEN** the returned alpha, beta, gamma values are interpolated using inverse-distance weighting
- **AND** the interpolated values satisfy α + β + γ = 1

#### Scenario: Division by zero protection
- **GIVEN** a 3D Pareto front where some points have zero values in cost dimensions
- **WHEN** `distance_from_front_3d()` is called
- **THEN** front points with any zero cost dimension are skipped
- **AND** no ZeroDivisionError is raised

#### Scenario: Actual tree on front returns epsilon ≈ 1.0
- **GIVEN** a 3D Pareto front
- **AND** an actual tree exactly on a front point
- **WHEN** `distance_from_front_3d()` is called
- **THEN** the returned epsilon is approximately 1.0 (within tolerance)

### Requirement: 3D Pareto Distance Return Format

The `distance_from_front_3d()` function SHALL return a dictionary containing all three Pareto weight parameters (α, β, γ) and the epsilon scaling factor, instead of a tuple with only (α, β).

This addresses issue #54: users should not need to manually compute γ = 1 - α - β.

The return format SHALL be:
```python
{
    "epsilon": float,  # multiplicative ε-indicator (scaling factor)
    "alpha": float,    # interpolated alpha parameter
    "beta": float,     # interpolated beta parameter
    "gamma": float,    # computed as 1 - alpha - beta
    "epsilon_components": {
        "material": float,   # actual[0] / front[0]
        "transport": float,  # actual[1] / front[1]
        "coverage": float,   # actual[2] / front[2]
    },
    "corner_costs": {
        "steiner": (length, distance, tortuosity),    # α=1, β=0, γ=0
        "satellite": (length, distance, tortuosity),  # α=0, β=1, γ=0
        "coverage": (length, distance, tortuosity),   # α=0, β=0, γ=1
    }
}
```

The epsilon value is the multiplicative ε-indicator from multi-objective optimization literature (Zitzler et al. 2003, Chandrasekhar & Navlakha 2019).

#### Scenario: Return dict with all three parameters
- **GIVEN** a 3D Pareto front and an actual tree
- **WHEN** `distance_from_front_3d()` is called
- **THEN** the return value is a dict with keys "epsilon", "alpha", "beta", "gamma"
- **AND** all values are Python native `float` types (not numpy)
- **AND** `alpha + beta + gamma` equals 1.0 (within floating point tolerance)

#### Scenario: Gamma computed automatically
- **GIVEN** an actual tree with interpolated (α=0.3, β=0.5)
- **WHEN** `distance_from_front_3d()` is called
- **THEN** the returned dict includes `"gamma": 0.2`
- **AND** users do not need to compute gamma manually

### Requirement: 3D Pareto Epsilon for Random Trees

The `distance_from_front_3d()` function SHALL return scientifically meaningful epsilon values for random trees, even when the closest (α, β) point is (0, 0).

The epsilon value represents how far the tree is from the Pareto front (>1.0 means dominated by front). This is the primary metric for random trees, not the (α, β) coordinates.

#### Scenario: Random tree returns meaningful epsilon
- **GIVEN** a random tree that is inefficient in all dimensions
- **WHEN** `distance_from_front_3d()` is called
- **THEN** the returned epsilon is greater than 1.0 (dominated by front)
- **AND** the epsilon accurately reflects how much worse the random tree is than optimal

#### Scenario: Random tree closest to (0, 0, 1) corner is valid
- **GIVEN** a random tree closest to the (α=0, β=0, γ=1) corner of the front
- **WHEN** `distance_from_front_3d()` is called
- **THEN** the returned (α, β) ≈ (0, 0) is mathematically correct
- **AND** the epsilon value is the meaningful metric (not the α, β coordinates)

### Requirement: 3D Results Field Naming Convention

The `pareto_calcs_3d_path_tortuosity()` function SHALL use field names with `_3d` suffix for 3D-specific metrics to avoid conflicts with 2D field names.

This naming follows the multiplicative ε-indicator terminology from multi-objective optimization literature.

**Required field names:**

| Field Name | Description |
|------------|-------------|
| `Total root length` | Material cost (same as 2D) |
| `Travel distance` | Transport cost (same as 2D) |
| `Path tortuosity` | Third dimension (3D only) |
| `alpha_3d` | Interpolated α weight |
| `beta_3d` | Interpolated β weight |
| `gamma_3d` | Computed γ = 1 - α - β |
| `epsilon_3d` | Multiplicative ε-indicator |
| `epsilon_3d_material` | Length ratio: actual/optimal |
| `epsilon_3d_transport` | Distance ratio: actual/optimal |
| `epsilon_3d_coverage` | Tortuosity ratio: actual/optimal |
| `alpha_3d (random)` | Interpolated α weight for random tree |
| `beta_3d (random)` | Interpolated β weight for random tree |
| `gamma_3d (random)` | Computed γ = 1 - α - β for random tree |
| `epsilon_3d (random)` | Multiplicative ε-indicator for random tree |
| `epsilon_3d_material (random)` | Length ratio for random tree |
| `epsilon_3d_transport (random)` | Distance ratio for random tree |
| `epsilon_3d_coverage (random)` | Tortuosity ratio for random tree |
| `Steiner_length_3d` | Corner cost (α=1) |
| `Steiner_distance_3d` | Corner cost (α=1) |
| `Steiner_tortuosity_3d` | Corner cost (α=1) |
| `Satellite_length_3d` | Corner cost (β=1) |
| `Satellite_distance_3d` | Corner cost (β=1) |
| `Satellite_tortuosity_3d` | Corner cost (β=1) |
| `Coverage_length_3d` | Corner cost (γ=1) |
| `Coverage_distance_3d` | Corner cost (γ=1) |
| `Coverage_tortuosity_3d` | Corner cost (γ=1) |

#### Scenario: 3D fields use _3d suffix
- **GIVEN** 3D Pareto analysis is performed
- **WHEN** results are returned
- **THEN** epsilon and weight fields use `_3d` suffix
- **AND** shared measurement fields (Total root length, etc.) use same names as 2D

#### Scenario: No field name conflicts with 2D
- **GIVEN** both 2D and 3D analysis results
- **WHEN** results are compared or merged
- **THEN** `epsilon_3d` does not conflict with 2D `scaling distance to front`
- **AND** field provenance is unambiguous