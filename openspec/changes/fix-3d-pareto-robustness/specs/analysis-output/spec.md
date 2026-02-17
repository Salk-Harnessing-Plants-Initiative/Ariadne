## ADDED Requirements

### Requirement: 3D Pareto Graph Costs Robustness

The `graph_costs_3d_path_tortuosity()` function SHALL handle edge cases robustly without raising runtime errors.

#### Scenario: Cycle detection returns three values
- **GIVEN** a graph G containing a cycle
- **WHEN** `graph_costs_3d_path_tortuosity(G)` is called
- **THEN** it SHALL return `(float("inf"), float("inf"), float("inf"))`
- **AND** no unpacking errors occur in calling code

#### Scenario: Coincident node does not cause division by zero
- **GIVEN** a graph G where a critical node has the same position as the base node
- **WHEN** `graph_costs_3d_path_tortuosity(G)` is called
- **THEN** the function SHALL return valid finite values
- **AND** the tortuosity contribution for the coincident node SHALL be 1.0

#### Scenario: Valid graph returns three costs
- **GIVEN** a valid connected acyclic graph G
- **WHEN** `graph_costs_3d_path_tortuosity(G)` is called
- **THEN** it SHALL return `(total_root_length, total_travel_distance, total_path_coverage)`
- **AND** all three values are non-negative finite floats

### Requirement: 3D Pareto Cost Function Validation

The `pareto_cost_3d_path_tortuosity()` function SHALL validate that alpha and beta parameters produce a valid gamma.

#### Scenario: Alpha plus beta exceeds one
- **GIVEN** alpha = 0.6 and beta = 0.6
- **WHEN** `pareto_cost_3d_path_tortuosity(length, distance, coverage, alpha, beta)` is called
- **THEN** an AssertionError SHALL be raised
- **AND** the error message indicates the constraint violation

#### Scenario: Valid boundary parameters
- **GIVEN** alpha = 0.5 and beta = 0.5 (gamma = 0)
- **WHEN** `pareto_cost_3d_path_tortuosity(length, distance, coverage, alpha, beta)` is called
- **THEN** the function SHALL return a valid cost
- **AND** the cost equals `0.5 * length + 0.5 * distance - 0 * coverage`

#### Scenario: Pure path coverage optimization
- **GIVEN** alpha = 0 and beta = 0 (gamma = 1)
- **WHEN** `pareto_cost_3d_path_tortuosity(length, distance, coverage, alpha, beta)` is called
- **THEN** the cost equals `-coverage`
- **AND** minimizing this cost maximizes path coverage

### Requirement: 3D Results Scaling Consistency

The 3D analysis results SHALL be scaled using the same transformation as 2D results before CSV output.

#### Scenario: 3D results scaled before CSV write
- **GIVEN** analysis produces `results_3d` with pixel-based measurements
- **AND** a length scale factor is configured
- **WHEN** results are written to the 3D CSV file
- **THEN** `scaling.apply_scaling_transformation()` SHALL be applied to `results_3d`
- **AND** the CSV contains scaled values, not raw pixel values

#### Scenario: 3D scaling matches 2D scaling
- **GIVEN** the same root graph is analyzed
- **WHEN** both 2D and 3D results are written to CSV
- **THEN** common fields (like "Total root length") SHALL have the same scaled values
- **AND** the scaling factor is applied consistently to length-based metrics

### Requirement: Optional 3D Analysis Toggle

The analysis workflow SHALL provide a GUI checkbox to enable or disable 3D Pareto analysis, allowing users to skip the slower computation when not needed.

#### Scenario: 3D analysis checkbox in scale dialog
- **GIVEN** the user opens the Analyze mode
- **WHEN** the scale configuration dialog appears
- **THEN** a checkbox labeled "Include 3D Pareto analysis (slower)" SHALL be visible
- **AND** the checkbox SHALL be unchecked by default

#### Scenario: 3D analysis skipped when disabled
- **GIVEN** the 3D analysis checkbox is unchecked
- **WHEN** the user runs analysis on selected files
- **THEN** the 3D Pareto front computation SHALL be skipped
- **AND** no `*_3d.csv` file SHALL be created
- **AND** no 3D Pareto plot SHALL be generated

#### Scenario: 3D analysis runs when enabled
- **GIVEN** the 3D analysis checkbox is checked
- **WHEN** the user runs analysis on selected files
- **THEN** the 3D Pareto front computation SHALL run
- **AND** a `*_3d.csv` file SHALL be created with 3D results
- **AND** a 3D Pareto surface plot SHALL be generated

### Requirement: 3D Pareto Surface Visualization

The 3D Pareto front SHALL be visualized as a surface plot, accurately representing the trade-off space in three dimensions.

#### Scenario: Surface plot for Pareto front
- **GIVEN** 3D analysis is enabled and complete
- **WHEN** the 3D Pareto plot is generated
- **THEN** the Pareto front SHALL be rendered as a triangulated surface using `plot_trisurf`
- **AND** the surface SHALL have a colormap indicating cost gradient
- **AND** axis labels SHALL show "Total Root Length", "Travel Distance", and "Path Coverage"

#### Scenario: Actual plant marker on surface plot
- **GIVEN** a 3D surface plot is generated
- **WHEN** the actual plant's costs are plotted
- **THEN** a distinct marker (e.g., orange "X") SHALL indicate the plant's position
- **AND** the marker SHALL be visible above/on the surface

#### Scenario: Random trees on surface plot
- **GIVEN** a 3D surface plot is generated
- **WHEN** random tree costs are plotted
- **THEN** scatter points SHALL show random tree positions
- **AND** the points SHALL be distinguishable from the surface (e.g., green "+")

### Requirement: Separate 3D CSV Output File

The 3D analysis results SHALL be written to a separate CSV file from 2D results.

#### Scenario: 3D results in separate file
- **GIVEN** both 2D and 3D analysis are enabled
- **WHEN** analysis completes
- **THEN** 2D results SHALL be written to `results.csv`
- **AND** 3D results SHALL be written to `results_3d.csv`
- **AND** both files SHALL be in the same output directory

#### Scenario: 3D file not created when disabled
- **GIVEN** 3D analysis is disabled (checkbox unchecked)
- **WHEN** analysis completes
- **THEN** only the 2D `results.csv` file SHALL be created
- **AND** no `results_3d.csv` file SHALL exist