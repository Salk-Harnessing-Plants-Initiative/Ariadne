## Context

The 3D Pareto path tortuosity feature extends the existing 2D Pareto optimization to include a third dimension (path tortuosity). This analysis helps researchers understand root system architecture trade-offs between material cost, transport efficiency, and path coverage.

The implementation in PR #19 has several edge cases that are not handled robustly:
1. Cycle detection returns wrong number of values
2. Division by zero when nodes are coincident
3. Invalid parameter validation
4. Inconsistent scaling between 2D and 3D outputs

## Goals / Non-Goals

**Goals:**
- Ensure 3D Pareto functions handle all edge cases without runtime errors
- Maintain consistency with 2D Pareto function behavior
- Provide comprehensive test coverage for reproducibility
- Apply same scaling transformation to 3D results as 2D results

**Non-Goals:**
- Performance optimization (10,201 iterations is acceptable, but made optional via toggle)
- Refactoring 2D functions to share code with 3D

## Decisions

### Decision 1: Cycle Detection Return Value

**What:** Return `(float("inf"), float("inf"), float("inf"))` on cycle detection instead of `(float("inf"), float("inf"))`.

**Why:** The 3D cost function expects 3 return values (total_root_length, total_travel_distance, total_path_coverage). Returning 2 values causes unpacking errors.

**Alternatives considered:**
- Raise an exception: Rejected - callers expect numeric return values
- Return `(float("inf"), float("inf"), 0)`: Rejected - inconsistent with inf pattern

### Decision 2: Division by Zero Protection

**What:** When `straight_distance_to_base == 0`, set tortuosity contribution to 1.0 (path length equals straight line distance when coincident).

**Why:** A node at the same position as base has trivial tortuosity (ratio = 1). This is mathematically sound: `lim(x/x) = 1` as `x -> 0`.

**Alternatives considered:**
- Skip the node entirely: Rejected - changes total count, affects comparison
- Return infinity: Rejected - contaminates sum, not meaningful
- Raise exception: Rejected - coincident nodes are valid in traced data

### Decision 3: Alpha + Beta Validation

**What:** Add assertion `assert alpha + beta <= 1` in `pareto_cost_3d_path_tortuosity()`.

**Why:** The cost function uses `gamma = 1 - alpha - beta`. If `alpha + beta > 1`, gamma becomes negative, which inverts the path coverage term's effect on the cost function.

**Alternatives considered:**
- Clamp gamma to 0: Rejected - silently changes user intent
- Allow negative gamma: Rejected - produces nonsensical results

### Decision 4: 3D Results Scaling

**What:** Apply `scaling.apply_scaling_transformation()` to `results_3d` before writing to CSV.

**Why:** Consistency with 2D results. Users expect all measurements in the same units (scaled or unscaled) across output files.

**Note:** The scaling function may need to be extended if 3D results have fields not present in 2D results.

### Decision 5: GUI Checkbox for 3D Analysis

**What:** Add a checkbox in the scale dialog: "Include 3D Pareto analysis (slower)" - unchecked by default.

**Why:** 3D analysis runs 10,201 iterations vs 101 for 2D, making it significantly slower. Users should opt-in when they need the additional analysis dimension.

**Implementation:**
- Add `tk.Checkbutton` to `ask_scale()` dialog in `main.py:1054-1150`
- Store value in `self.enable_3d_analysis` and `config.enable_3d_analysis`
- Conditionally skip 3D analysis in the main loop when disabled
- Skip 3D CSV and plot generation when disabled

**Alternatives considered:**
- Config file setting: Rejected - user prefers GUI control
- Separate button: Rejected - adds complexity, checkbox is simpler
- Always run 3D: Rejected - too slow for routine analysis

### Decision 6: 3D Surface Plot Visualization

**What:** Replace the line plot with `ax.plot_trisurf()` for the 3D Pareto front visualization.

**Why:** The 3D Pareto front forms a surface in (length, distance, coverage) space, not a line. A surface plot accurately represents the trade-off space and helps researchers understand the relationship between all three dimensions.

**Implementation:**
- Use `matplotlib.tri.Triangulation` to create triangle mesh from front points
- Use `ax.plot_trisurf()` with colormap to show the surface
- Keep scatter points for actual plant and random trees
- Add colorbar showing cost gradient

**Alternatives considered:**
- Keep line plot: Rejected - misrepresents the data structure
- Scatter plot only: Rejected - doesn't show the front surface
- Wireframe plot: Considered - surface is more intuitive for researchers

### Decision 7: Separate 3D CSV Output

**What:** Keep 3D results in a separate CSV file (`*_3d.csv`) rather than merging with 2D results.

**Why:**
- 3D analysis is optional; separate file avoids empty columns when disabled
- Different metrics (path tortuosity) may confuse users if mixed with 2D
- Easier to compare 2D vs 3D results when in separate files
- Maintains backwards compatibility with existing analysis pipelines

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Tests may not cover all edge cases | Use property-based testing for boundary conditions |
| Scaling function may not handle 3D fields | Audit scaling.py and extend if needed |
| Existing results may differ after fix | Document in CHANGELOG that this fixes incorrect behavior |
| Surface plot may be slow for large fronts | 101x101 grid is fixed; matplotlib handles well |
| Users may not notice 3D checkbox | Add tooltip and brief label explaining trade-off |

## Migration Plan

1. Tests are written first (TDD)
2. Tests initially fail (expected - bugs exist)
3. Fixes applied incrementally
4. Tests pass after each fix
5. Manual verification with real root data

**Rollback:** Revert the fix commits if issues arise.

## Open Questions

1. Should we add a warning log when coincident nodes are detected?
   - Proposed: Yes, log at DEBUG level for traceability
2. ~~Should 3D CSV output go to a separate file or be merged with 2D results?~~
   - **Resolved**: Keep separate (Decision 7)

## Future Work

**GitHub Issue #48: Modular Cost Term Architecture**

The current implementation duplicates ~340 lines of code between 2D and 3D versions. A future refactor (tracked in [#48](https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/issues/48)) will:

- Create a `CostTerm` protocol for pluggable cost terms
- Unify `graph_costs()`, `pareto_steiner_fast()`, and `pareto_front()` functions
- Reduce effort to add new cost terms from ~380 lines to ~40 lines
- Delete ~340 lines of duplicated code

This refactor is out of scope for the current proposal but will enable future extensibility for cost terms like "root depth", "branching angle variance", etc.