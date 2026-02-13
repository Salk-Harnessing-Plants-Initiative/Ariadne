## ADDED Requirements

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