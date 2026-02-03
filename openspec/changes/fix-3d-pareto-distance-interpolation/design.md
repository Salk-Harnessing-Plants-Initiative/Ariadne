## Context

The 3D Pareto front analysis (`fix-3d-pareto-robustness` change) introduced a third dimension (path tortuosity) to the existing 2D Pareto optimization. The `distance_from_front_3d()` function calculates how far an actual root system is from the optimal Pareto front.

**Current problem**: The function only returns the nearest discrete (α, β) point, while the 2D version interpolates between the two closest points for higher precision. This causes:
1. Random trees to return `((0.0, 0.0), scaling)` which is mathematically correct but scientifically uninformative
2. Loss of precision compared to 2D analysis
3. Missing division-by-zero guards present in 2D

## Goals / Non-Goals

**Goals:**
- Match 2D precision by implementing interpolation in the (α, β) parameter space
- Provide scientifically meaningful results for both actual plants and random trees
- Maintain numerical stability with division-by-zero guards
- Return results that clearly separate "how far" (epsilon) from "which direction" (α, β, γ)

**Non-Goals:**
- Changing the distance metric (keep `max()` epsilon indicator per Chandrasekhar 2019)
- Performance optimization (10,201 points is fine for brute force)
- Spatial indexing (KD-tree unnecessary at this scale)

## Decisions

### Decision 1: Barycentric Interpolation with 3 Nearest Points

**What:** Use barycentric interpolation with the 3 closest (α, β) points to interpolate the parameter values.

**Why:** This is the natural extension of linear interpolation from 1D to 2D. The 2D version interpolates between 2 closest alpha values; the 3D version should interpolate between 3 closest (α, β) points forming a triangle in parameter space.

**Algorithm:**
```python
# 1. Find 3 nearest (α, β) points by distance metric
sorted_points = sorted(distances.items(), key=lambda x: x[1])[:3]

# 2. Compute barycentric weights (inverse distance weighting)
p1, p2, p3 = sorted_points
d1, d2, d3 = p1[1], p2[1], p3[1]
total_inv = (1/d1 + 1/d2 + 1/d3)
w1, w2, w3 = (1/d1)/total_inv, (1/d2)/total_inv, (1/d3)/total_inv

# 3. Interpolate (α, β)
alpha = w1*p1[0][0] + w2*p2[0][0] + w3*p3[0][0]
beta = w1*p1[0][1] + w2*p2[0][1] + w3*p3[0][1]
gamma = 1 - alpha - beta
```

**Alternatives considered:**
- **2D parameter interpolation (2 points):** Rejected - "two closest" is ambiguous in 2D parameter space
- **Euclidean distance in cost space:** Rejected - different metric, normalization issues, not standard in literature
- **No interpolation (nearest neighbor only):** Rejected - loses precision, current bug

### Decision 2: Return Dict Instead of Tuple

**What:** Change return format from `((alpha, beta), scaling)` to:
```python
{
    "epsilon": float,      # scaling factor (how far from front)
    "alpha": float,        # interpolated alpha parameter
    "beta": float,         # interpolated beta parameter
    "gamma": float,        # computed: 1 - alpha - beta
    "epsilon_components": {
        "material": float,   # actual[0] / front[0]
        "transport": float,  # actual[1] / front[1]
        "coverage": float,   # actual[2] / front[2]
    },
    "corner_costs": {
        "steiner": (length, distance, coverage),    # α=1, β=0, γ=0
        "satellite": (length, distance, coverage),  # α=0, β=1, γ=0
        "coverage": (length, distance, coverage),   # α=0, β=0, γ=1
    }
}
```

**Why:**
- Separates "how far" (epsilon) from "which direction" (α, β, γ)
- For random trees, epsilon ≈ 2.75 is the meaningful number (2.75x worse than optimal)
- The (α, β) = (0, 0) for random trees is expected (closest to least-pruned corner) but not the primary metric
- Dict is self-documenting and allows future extension
- `epsilon_components` shows which dimension drives the epsilon value (useful for scientific interpretation)
- `corner_costs` provides reference points for normalization and publication

**Alternatives considered:**
- **Keep tuple format:** Rejected - conflates distance and direction
- **Omit epsilon_components:** Rejected - values are already computed, low cost to return
- **Omit corner_costs:** Rejected - essential reference points for scientific interpretation

### Decision 3: Division-by-Zero Guard (Skip Zero Values)

**What:** Skip front points where any cost dimension is zero:
```python
if any(v == 0 for v in alpha_beta_tree):
    continue
```

**Why:** Matches 2D behavior (`quantify.py:774-776`). Division by zero produces infinity which contaminates the distance calculation.

**Alternatives considered:**
- **Return infinity for that point:** Rejected - already handled by skipping
- **Warn on extreme ratios:** Deferred - can add if users request

### Decision 4: Keep Max() Distance Metric (Epsilon Indicator)

**What:** Continue using `max(material_ratio, transport_ratio, path_coverage_ratio)` as the distance metric.

**Why:** This is the standard epsilon-indicator metric in multi-objective optimization literature and what Chandrasekhar & Navlakha (2019) use. The problem isn't the metric—it's that only returning the nearest point's (α, β) loses information.

### Decision 5: Return Epsilon Components

**What:** Return the individual ratio components that determine epsilon:
```python
"epsilon_components": {
    "material": actual[0] / front[0],
    "transport": actual[1] / front[1],
    "coverage": actual[2] / front[2],
}
```

**Why:**
- Shows which dimension is driving the epsilon (the max of the three)
- Enables scientific interpretation: "tree is 1.5× suboptimal in transport but only 1.1× in wiring"
- Low implementation cost - values are already computed in the distance calculation
- Already part of the 2D logic but not exposed

### Decision 6: Return Corner Architecture Costs

**What:** Return the cost values at the three corner points of the Pareto front:
```python
"corner_costs": {
    "steiner": front[(1.0, 0.0)],    # Minimizes total root length
    "satellite": front[(0.0, 1.0)],  # Minimizes travel distance
    "coverage": front[(0.0, 0.0)],   # Minimizes path tortuosity (max coverage)
}
```

**Why:**
- Provides essential reference points for normalization
- Enables researchers to express results as percentages: "23% above Steiner minimum"
- Values are already in the front dictionary - just a lookup
- Analogous to 2D's Steiner/Satellite values in `calculate_tradeoff()`

### Decision 7: Skip 3D Tradeoff Calculation

**What:** Do not implement a 3D analog of `calculate_tradeoff()` in this proposal.

**Why:**
- In 2D, tradeoff expresses position between two extremes on a single axis
- In 3D, the (α, β, γ) weights already capture this as barycentric coordinates
- Pairwise ratios (e.g., α/(α+β)) can be computed post-hoc by researchers if needed
- Adding a 3D tradeoff metric requires scientific validation and is out of scope

**Future work:** If researchers request specific pairwise tradeoff metrics, can be added later.

### Decision 8: Field Naming Convention (Epsilon Terminology)

**What:** Use `epsilon_3d` for 3D distance-from-front metrics. Keep 2D field names unchanged for backwards compatibility. Future rename of 2D fields tracked in GitHub issue #56.

**Why:**
- "Epsilon indicator" (ε-indicator) is the standard term in multi-objective optimization literature
- The metric measures the minimum scaling factor needed for a Pareto-optimal point to dominate the actual point
- Renaming 3D fields to use `epsilon` aligns with literature (Zitzler et al. 2003, Chandrasekhar & Navlakha 2019)
- 2D rename deferred to avoid breaking existing user scripts (tracked in #56)

**Literature References:**
- Zitzler, E., et al. (2003). "Performance Assessment of Multiobjective Optimizers: An Analysis and Review." IEEE Transactions on Evolutionary Computation, 7(2), 117-132.
- Chandrasekhar, A., & Navlakha, S. (2019). "Neural arbors are Pareto optimal." Proc. Royal Society B, 286(1902). Supplementary Methods, Equation 2.

**Epsilon interpretation:**
| ε Value | Meaning |
|---------|---------|
| ε = 1.0 | Point is exactly ON the Pareto front |
| ε > 1.0 | Point is dominated (suboptimal); ε is the scaling factor needed |
| ε < 1.0 | Point dominates the front (indicates front computation error) |

**3D Field Names (this proposal):**

| Field Name | Description |
|------------|-------------|
| `Total root length` | Material cost (same as 2D) |
| `Travel distance` | Transport cost (same as 2D) |
| `Path tortuosity` | Third dimension (3D only) |
| `alpha_3d` | Interpolated α parameter (weight for length minimization) |
| `beta_3d` | Interpolated β parameter (weight for distance minimization) |
| `gamma_3d` | Computed γ = 1 - α - β (weight for coverage maximization) |
| `epsilon_3d` | Multiplicative ε-indicator distance from Pareto front |
| `epsilon_3d_material` | Length ratio component: actual[0] / front[0] |
| `epsilon_3d_transport` | Distance ratio component: actual[1] / front[1] |
| `epsilon_3d_coverage` | Tortuosity ratio component: actual[2] / front[2] |
| `*_3d (random)` | Same fields for random tree centroid |
| `Steiner_*_3d` | Corner costs at α=1, β=0, γ=0 |
| `Satellite_*_3d` | Corner costs at α=0, β=1, γ=0 |
| `Coverage_*_3d` | Corner costs at α=0, β=0, γ=1 |

**2D Field Names (UNCHANGED - backwards compatible):**

| Current Name | Future Name (per #56) |
|--------------|----------------------|
| `alpha` | (keep or `alpha_2d`) |
| `scaling distance to front` | `epsilon` or `epsilon_2d` |
| `scaling (random)` | `epsilon (random)` |

**Related Issues:**
- #56 - Document the epsilon indicator and consider renaming 2D fields
- #55 - Return (alpha, beta) instead of just alpha in 2D

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Barycentric interpolation may produce (α, β) outside valid triangle | Clamp to valid range: α ≥ 0, β ≥ 0, α + β ≤ 1 |
| Return format change breaks callers | Update all callers in same PR; no external consumers yet |
| Edge case with < 3 front points | Fall back to nearest-neighbor for degenerate cases |
| Equal distances cause division by zero in weighting | Add small epsilon: `1/(d + 1e-10)` |

## Migration Plan

1. Tests written first (TDD)
2. Tests initially fail (expected - function returns tuple not dict)
3. Implementation changes return format
4. Update callers to handle dict
5. All tests pass
6. Manual verification with real root data

**Rollback:** Revert commits if issues arise.

## Open Questions

1. Should we log a warning when all front points have zero values in some dimension?
   - **Proposed:** Yes, at WARNING level - indicates degenerate Pareto front

2. Should extreme epsilon values (> 10x) trigger a warning?
   - **Deferred:** Not in initial implementation; can add based on user feedback