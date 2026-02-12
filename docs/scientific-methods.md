# Scientific Methods

This document describes the scientific calculations implemented in Ariadne, with mathematical formulas and academic references.

## Table of Contents

1. [Pareto Optimality in Root Systems](#pareto-optimality-in-root-systems)
2. [2D Pareto Analysis](#2d-pareto-analysis)
3. [3D Pareto Analysis](#3d-pareto-analysis)
4. [Multiplicative ε-Indicator](#multiplicative-ε-indicator)
5. [Barycentric Interpolation](#barycentric-interpolation)
6. [Random Tree Baseline](#random-tree-baseline)
7. [References](#references)

---

## Pareto Optimality in Root Systems

Root systems face fundamental trade-offs between competing objectives. Ariadne quantifies these trade-offs using Pareto optimality analysis, following the framework established by Chandrasekhar & Navlakha (2019).

### Core Concepts

- **Material Cost (Wiring Cost)**: Total root length - the metabolic investment in building the root network
- **Transport Cost (Conduction Delay)**: Sum of path lengths from each lateral root tip to the base - represents resource transport efficiency
- **Path Coverage**: Sum of tortuosity values across all root paths - measures how thoroughly the root explores soil volume

A root system is **Pareto optimal** if no other configuration can improve one objective without worsening another.

---

## 2D Pareto Analysis

The 2D analysis considers the trade-off between material cost and transport cost.

### Cost Function

```
Cost(α) = α × TotalRootLength + (1 - α) × TravelDistance
```

Where:
- `α` (alpha): Weight parameter in range [0, 1]
- `α = 0`: Minimize transport cost only (Satellite tree)
- `α = 1`: Minimize material cost only (Steiner tree)

**Implementation**: `pareto_functions.py:262-276` (`pareto_cost`)

### Pareto Front Construction

The Pareto front is computed by:
1. Discretizing α from 0 to 1 in steps of 0.01
2. For each α, finding the minimum-cost spanning tree
3. Recording the (TotalRootLength, TravelDistance) for each optimal tree

**Implementation**: `pareto_functions.py` (`pareto_front`)

### Distance to Front (Scaling Factor)

The distance from an actual tree to the Pareto front uses the multiplicative ε-indicator:

```
ε = min_{r ∈ Front} max(actual_length/front_length, actual_distance/front_distance)
```

**Implementation**: `quantify.py:757-799` (`distance_from_front`)

---

## 3D Pareto Analysis

The 3D analysis extends the framework to include path coverage as a third objective.

### Cost Function

```
Cost(α, β) = α × TotalRootLength + β × TravelDistance - γ × PathCoverage
```

Where:
- `α` (alpha): Weight for material cost
- `β` (beta): Weight for transport cost
- `γ` (gamma): Weight for path coverage, computed as `γ = 1 - α - β`
- Constraint: `α + β + γ = 1` and `α, β, γ ≥ 0`

**Corner cases**:
- `(α=1, β=0, γ=0)`: Steiner tree - minimizes material cost
- `(α=0, β=1, γ=0)`: Satellite tree - minimizes transport cost
- `(α=0, β=0, γ=1)`: Coverage tree - maximizes path coverage

**Implementation**: `pareto_functions.py:279-314` (`pareto_cost_3d_path_tortuosity`)

### Path Coverage (Tortuosity)

Path coverage is the sum of tortuosity values for all root paths:

```
PathCoverage = Σ (PathLength_i / EuclideanDistance_i)
```

Where for each path `i` from base to tip:
- `PathLength_i`: Actual length along the root
- `EuclideanDistance_i`: Straight-line distance from base to tip
- Tortuosity ≥ 1.0 (equals 1.0 for a straight path)

---

## Multiplicative ε-Indicator

The multiplicative ε-indicator (epsilon) measures how far a solution is from Pareto optimality. This is a standard metric in multi-objective optimization (Zitzler et al., 2003).

### Definition

```
ε = min_{r ∈ Front} max_i (actual_i / front_i)
```

For 3D analysis with three objectives:
```
ε = min_{(α,β) ∈ Front} max(
    actual_length / front_length,
    actual_distance / front_distance,
    actual_coverage / front_coverage
)
```

### Interpretation

| ε Value | Meaning |
|---------|---------|
| ε = 1.0 | Tree is exactly on the Pareto front (optimal) |
| ε > 1.0 | Tree is suboptimal; ε is the scaling factor by which it's worse |
| ε < 1.0 | Tree dominates the front (theoretically impossible for valid fronts) |

### Epsilon Components

The implementation also returns individual ratio components:
- `epsilon_material`: `actual_length / optimal_length`
- `epsilon_transport`: `actual_distance / optimal_distance`
- `epsilon_coverage`: `actual_coverage / optimal_coverage`

The overall ε is the maximum of these three components, indicating which objective most constrains the tree's optimality.

**Implementation**: `quantify.py:903-1050` (`distance_from_front_3d`)

**Reference**: Zitzler et al. (2003), "Performance Assessment of Multiobjective Optimizers: An Analysis and Review", IEEE Transactions on Evolutionary Computation, 7(2), 117-132. https://doi.org/10.1109/TEVC.2003.810758

---

## Barycentric Interpolation

To improve precision beyond discrete sampling, Ariadne interpolates (α, β) coordinates using the k-nearest neighbors on the Pareto front.

### Method

1. Find the k=3 closest points on the Pareto front (by ε distance)
2. Compute inverse-distance weights for each point
3. Interpolate α and β using weighted averaging

### Formula

```
weight_i = 1 / (ε_i + guard)
α_interp = Σ(weight_i × α_i) / Σ(weight_i)
β_interp = Σ(weight_i × β_i) / Σ(weight_i)
γ_interp = 1 - α_interp - β_interp
```

Where `guard = 1e-10` prevents division by zero.

### Clamping

Results are clamped to ensure valid coordinates:
- `α ≥ 0`, `β ≥ 0`
- `α + β ≤ 1`

**Implementation**: `quantify.py:990-1025` (within `distance_from_front_3d`)

---

## Random Tree Baseline

Random trees provide a null model for comparison, representing architectures without optimization pressure.

### Generation Method (Conn et al., 2017)

For each of 1000 iterations:
1. Start with critical nodes (base node + all lateral root tips)
2. Initialize empty tree R
3. Randomly select a node from remaining critical nodes
4. If R is non-empty, connect to a random existing node in R
5. Repeat until all critical nodes are connected
6. Compute costs for the resulting random spanning tree

### Output

The random tree baseline is the **mean** of the 1000 random trees:
- `Total root length (random)`: Mean material cost
- `Travel distance (random)`: Mean transport cost
- `Path tortuosity (random)`: Mean path coverage (3D only)

The epsilon indicator is computed for this mean random tree position.

**Implementation**:
- 2D: `pareto_functions.py:917-962` (`random_tree`)
- 3D: `pareto_functions.py:965-1015` (`random_tree_3d_path_tortuosity`)

**Reference**: Conn et al. (2017), Section "Random null model"

---

## References

### Primary References

1. **Chandrasekhar, A., & Navlakha, S. (2019)**. "Neural arbors are Pareto optimal." *Proceedings of the Royal Society B*, 286(1902), 20182727.
   - DOI: https://doi.org/10.1098/rspb.2018.2727
   - Establishes the Pareto optimality framework for biological networks
   - Defines the multiplicative ε-indicator for measuring distance to front

2. **Conn, A., Pedmale, U. V., Chory, J., & Navlakha, S. (2017)**. "High-resolution laser scanning reveals plant architectures that reflect universal network design principles." *Cell Systems*, 5(1), 53-62.
   - DOI: https://doi.org/10.1016/j.cels.2017.06.017
   - Network design principles in plant root systems
   - Random tree null model methodology

### Additional References

3. **Zitzler, E., Thiele, L., Laumanns, M., Fonseca, C. M., & da Fonseca, V. G. (2003)**. "Performance Assessment of Multiobjective Optimizers: An Analysis and Review." *IEEE Transactions on Evolutionary Computation*, 7(2), 117-132.
   - DOI: https://doi.org/10.1109/TEVC.2003.810758
   - Defines the multiplicative ε-indicator metric

4. **Conn, A., Pedmale, U. V., Chory, J., Stevens, C. F., & Bhattacharjee, S., & Bhattacharjee, S., & Navlakha, S. (2019)**. "A connectomic approach to quantifying root system architecture." *PLOS Computational Biology*, 15(12), e1007325.
   - DOI: https://doi.org/10.1371/journal.pcbi.1007325
   - Tradeoff metric definitions

---

## Code References

| Calculation | File | Function | Lines |
|-------------|------|----------|-------|
| 2D Pareto cost | `pareto_functions.py` | `pareto_cost` | 262-276 |
| 3D Pareto cost | `pareto_functions.py` | `pareto_cost_3d_path_tortuosity` | 279-314 |
| 2D distance to front | `quantify.py` | `distance_from_front` | 757-799 |
| 3D distance to front | `quantify.py` | `distance_from_front_3d` | 903-1050 |
| Random tree (2D) | `pareto_functions.py` | `random_tree` | 917-962 |
| Random tree (3D) | `pareto_functions.py` | `random_tree_3d_path_tortuosity` | 965-1015 |