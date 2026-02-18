# analysis-output Specification

## Purpose
TBD - created by archiving change fix-scaling-and-serialization-bugs. Update Purpose after archive.
## Requirements
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

### Requirement: 3D Plot Data Consistency

The 3D visualization pipeline SHALL pass consistent data between CSV output and plot generation.

When `main.py` calls `plot_all_3d()`, the random tree metrics passed MUST match the values written to CSV output.

#### Scenario: Random path tortuosity matches CSV output
- **GIVEN** 3D Pareto analysis results from `distance_from_front_3d()`
- **WHEN** `main.py` calls `plot_all_3d()`
- **THEN** the `prand` parameter equals `results_3d["Path tortuosity (random)"]`
- **AND** the `mrand` parameter equals `results_3d["Total root length (random)"]`
- **AND** the `srand` parameter equals `results_3d["Travel distance (random)"]`

#### Scenario: Random centroid position is correct
- **GIVEN** a 3D Pareto front plot
- **WHEN** the "Random Centroid" marker is rendered
- **THEN** the z-coordinate equals the mean path tortuosity of 1000 random trees
- **AND** the z-coordinate does NOT equal the actual plant's path tortuosity

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

