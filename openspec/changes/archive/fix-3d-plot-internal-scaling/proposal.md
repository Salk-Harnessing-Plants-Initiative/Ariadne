## Why

The `plot_all_3d()` function does not scale data internally like `plot_all()` does. This causes 3D Pareto plots to display pixel values while labeling axes with scaled units (e.g., "mm"), producing scientifically incorrect visualizations.

The existing spec `analysis-output` requires "Single-Pass Plot Scaling" for 2D plots (lines 23-39), where `plot_all()` receives unscaled data and scales internally using `config.length_scale_factor`. However, `plot_all_3d()` was implemented without this internal scaling, creating an inconsistency:

| Output | 2D | 3D |
|--------|----|----|
| CSV | Scaled | Scaled |
| Plot | Scaled (internal) | **UNSCALED** |

This bug causes:
- 3D plot axis values showing pixels while labeled as "mm"
- Inconsistency between 3D CSV data and 3D plot visualizations
- Scientific publications using these plots would have incorrect axis values

## What Changes

- **CRITICAL**: Add internal `scale_data()` helper to `plot_all_3d()` matching the 2D pattern
- Scale x (total root length) and y (travel distance) values before plotting
- Do NOT scale z (path tortuosity) - it is dimensionless
- Add integration tests using real fixtures (no mocking) that verify 3D plot data matches CSV scaling
- Add tests for 2D plot consistency as well (to prevent regressions)

## Impact

- Affected specs: analysis-output
- Affected files: `src/ariadne_roots/quantify.py`, `tests/test_plot_scaling_integration.py`
- No breaking changes to API (main.py already passes unscaled data to both plots)
- **Scientific accuracy**: 3D plots will show correct scaled values matching CSV output