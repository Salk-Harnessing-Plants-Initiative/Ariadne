## MODIFIED Requirements

### Requirement: Single-Pass Plot Scaling

**Modification**: Extend this requirement to cover 3D plots as well as 2D plots.

The visualization pipeline SHALL scale data exactly once for both 2D and 3D plots.

When `main.py` calls `plot_all()` or `plot_all_3d()`, the data passed MUST be unscaled (pixel values), and each plot function SHALL handle all scaling internally using `config.length_scale_factor`.

#### Scenario: Unscaled data passed to plot_all_3d
- **GIVEN** analysis results from `quantify.analyze()` with 3D analysis enabled
- **WHEN** `main.py` calls `plot_all_3d()`
- **THEN** the `front_3d` parameter contains unscaled length and distance values
- **AND** the `actual_3d` parameter contains unscaled values (from `results_3d`, not `scaled_results_3d`)
- **AND** the `mrand` and `srand` parameters contain unscaled random tree values
- **AND** the `prand` parameter contains the raw path tortuosity value (dimensionless, no scaling needed)

#### Scenario: 3D plot axis values match CSV values
- **GIVEN** a scale factor of 0.01 (pixels to mm)
- **WHEN** both 3D CSV and 3D plot are generated
- **THEN** the 3D plot x-axis values (Total Root Length) match the scaled CSV column
- **AND** the 3D plot y-axis values (Travel Distance) match the scaled CSV column
- **AND** the 3D plot z-axis values (Path Tortuosity) are NOT scaled (dimensionless)

#### Scenario: 3D plot internal scaling matches 2D pattern
- **GIVEN** `plot_all_3d()` receives unscaled data
- **WHEN** the function plots data
- **THEN** it SHALL use an internal `scale_data()` helper matching the 2D implementation
- **AND** x-values (length) SHALL be multiplied by `config.length_scale_factor`
- **AND** y-values (distance) SHALL be multiplied by `config.length_scale_factor`
- **AND** z-values (path tortuosity) SHALL NOT be scaled

## ADDED Requirements

### Requirement: Plot-CSV Scaling Consistency Tests

The test suite SHALL include integration tests that verify plot data matches CSV output scaling for both 2D and 3D visualizations.

#### Scenario: 2D plot scaling consistency test exists
- **GIVEN** the test suite
- **WHEN** `test_2d_plot_values_match_csv_scaling()` runs
- **THEN** it loads a real root data fixture
- **AND** runs analysis with a known scale factor
- **AND** verifies the 2D plot axis data matches scaled CSV output within precision tolerance

#### Scenario: 3D plot scaling consistency test exists
- **GIVEN** the test suite
- **WHEN** `test_3d_plot_xy_values_match_csv_scaling()` runs
- **THEN** it loads a real root data fixture
- **AND** runs analysis with a known scale factor
- **AND** verifies the 3D plot x,y axis data matches scaled CSV output within precision tolerance

#### Scenario: 3D path tortuosity not scaled
- **GIVEN** the test suite
- **WHEN** `test_3d_plot_z_values_not_scaled()` runs
- **THEN** it verifies the z-axis (path tortuosity) values are unchanged by scaling
- **AND** confirms path tortuosity is dimensionless