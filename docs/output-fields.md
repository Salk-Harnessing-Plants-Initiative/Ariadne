# Output Fields Reference

This document provides a complete reference for all fields in the Ariadne CSV output.

## Table of Contents

1. [Basic Root Measurements](#basic-root-measurements)
2. [Primary Root Metrics](#primary-root-metrics)
3. [Lateral Root Metrics](#lateral-root-metrics)
4. [Zone Measurements](#zone-measurements)
5. [2D Pareto Analysis Fields](#2d-pareto-analysis-fields)
6. [3D Pareto Analysis Fields](#3d-pareto-analysis-fields)
7. [Other Metrics](#other-metrics)

---

## Units

All length measurements are in the units you specified during analysis:
- If scaling was configured (e.g., "mm"), measurements are in those units
- If no scaling was configured, measurements are in pixels

---

## Basic Root Measurements

| Field | Description | Units | Range |
|-------|-------------|-------|-------|
| `Total root length` | Sum of all edge lengths in the root network | length | > 0 |
| `Travel distance` | Sum of path lengths from base to each root tip | length | > 0 |
| `Total minimal Distance` | Sum of Euclidean distances (straight-line) to all tips | length | > 0 |
| `Tortuosity` | Total root length divided by Total minimal Distance | ratio | ≥ 1.0 |

---

## Primary Root Metrics

| Field | Description | Units | Range |
|-------|-------------|-------|-------|
| `PR length` | Length of the primary root | length | > 0 |
| `PR_minimal_length` | Euclidean distance from hypocotyl to primary root tip | length | > 0 |

---

## Lateral Root Metrics

| Field | Description | Units | Range |
|-------|-------------|-------|-------|
| `LR count` | Number of lateral roots | count | ≥ 0 |
| `LR density` | Number of lateral roots divided by PR length | 1/length | ≥ 0 |
| `Mean LR lengths` | Average length of all lateral roots | length | > 0 |
| `Median LR lengths` | Median length of all lateral roots | length | > 0 |
| `Mean LR minimal lengths` | Average Euclidean distance from LR tip to insertion point | length | ≥ 0 |
| `Median LR minimal lengths` | Median Euclidean distance from LR tip to insertion point | length | ≥ 0 |
| `sum LR minimal lengths` | Sum of Euclidean distances for all LRs | length | ≥ 0 |
| `Mean LR angles` | Average lateral root set point angle | degrees | 0-180 |
| `Median LR angles` | Median lateral root set point angle | degrees | 0-180 |
| `LR lengths` | Array of individual lateral root lengths | length[] | > 0 |
| `LR angles` | Array of individual lateral root angles | degrees[] | 0-180 |
| `LR minimal lengths` | Array of Euclidean distances for each LR | length[] | ≥ 0 |

---

## Zone Measurements

| Field | Description | Units | Range |
|-------|-------------|-------|-------|
| `Basal Zone length` | Length from hypocotyl to first lateral root insertion | length | ≥ 0 |
| `Branched Zone length` | Length from first to last lateral root insertion | length | ≥ 0 |
| `Apical Zone length` | Length from last lateral root to primary root tip | length | ≥ 0 |
| `Branched Zone density` | LR count divided by Branched Zone length | 1/length | ≥ 0 |

---

## 2D Pareto Analysis Fields

These fields describe the trade-off between material cost and transport cost.

| Field | Description | Units | Range |
|-------|-------------|-------|-------|
| `alpha` | Interpolated α parameter on the Pareto front | ratio | [0, 1] |
| `scaling distance to front` | Multiplicative ε-indicator (distance from Pareto front) | ratio | ≥ 1.0 |

### 2D Random Tree Comparison

| Field | Description | Units | Range |
|-------|-------------|-------|-------|
| `Total root length (random)` | Mean total root length of 1000 random trees | length | > 0 |
| `Travel distance (random)` | Mean travel distance of 1000 random trees | length | > 0 |
| `alpha (random)` | α parameter for the mean random tree | ratio | [0, 1] |
| `scaling (random)` | ε-indicator for the mean random tree | ratio | ≥ 1.0 |

### Interpretation

- alpha = 0: Tree prioritizes minimizing transport cost (Satellite-like)
- alpha = 1: Tree prioritizes minimizing material cost (Steiner-like)
- scaling ≈ 1.0: Tree is near Pareto optimal
- scaling >> 1.0: Tree is far from optimal (inefficient)

---

## 3D Pareto Analysis Fields

These fields are only present when "Add path tortuosity to Pareto (3D, slower)" is enabled. They extend the 2D analysis to include path coverage as a third objective.

### Actual Tree Metrics

| Field | Description | Units | Range |
|-------|-------------|-------|-------|
| `Path tortuosity` | Sum of tortuosity values for all root paths | ratio | ≥ number of paths |
| `alpha_3d` | Interpolated α weight (material cost) | ratio | [0, 1] |
| `beta_3d` | Interpolated β weight (transport cost) | ratio | [0, 1] |
| `gamma_3d` | Computed γ weight (path coverage) = 1 - α - β | ratio | [0, 1] |
| `epsilon_3d` | Multiplicative ε-indicator (3D distance from front) | ratio | ≥ 1.0 |

Constraint: alpha_3d + beta_3d + gamma_3d = 1

### Epsilon Components

These break down which objective most constrains optimality:

| Field | Description | Units | Range |
|-------|-------------|-------|-------|
| `epsilon_3d_material` | actual_length / optimal_length | ratio | > 0 |
| `epsilon_3d_transport` | actual_distance / optimal_distance | ratio | > 0 |
| `epsilon_3d_coverage` | actual_coverage / optimal_coverage | ratio | > 0 |

The overall epsilon_3d equals the maximum of these three components, indicating which objective most constrains the tree's optimality.

### Random Tree Metrics (3D)

| Field | Description | Units | Range |
|-------|-------------|-------|-------|
| `Total root length (random)` | Mean material cost of random trees | length | > 0 |
| `Travel distance (random)` | Mean transport cost of random trees | length | > 0 |
| `Path tortuosity (random)` | Mean path coverage of random trees | ratio | ≥ 1.0 |
| `alpha_3d (random)` | α for mean random tree | ratio | [0, 1] |
| `beta_3d (random)` | β for mean random tree | ratio | [0, 1] |
| `gamma_3d (random)` | γ for mean random tree | ratio | [0, 1] |
| `epsilon_3d (random)` | ε-indicator for mean random tree | ratio | ≥ 1.0 |
| `epsilon_3d_material (random)` | Material ratio for random tree | ratio | > 0 |
| `epsilon_3d_transport (random)` | Transport ratio for random tree | ratio | > 0 |
| `epsilon_3d_coverage (random)` | Coverage ratio for random tree | ratio | > 0 |

### Corner Cost Reference Points

These represent the optimal architectures at each corner of the Pareto surface:

| Field | Description | Weight Configuration |
|-------|-------------|---------------------|
| `Steiner_length_3d` | Total root length of Steiner tree | α=1, β=0, γ=0 |
| `Steiner_distance_3d` | Travel distance of Steiner tree | α=1, β=0, γ=0 |
| `Steiner_tortuosity_3d` | Path coverage of Steiner tree | α=1, β=0, γ=0 |
| `Satellite_length_3d` | Total root length of Satellite tree | α=0, β=1, γ=0 |
| `Satellite_distance_3d` | Travel distance of Satellite tree | α=0, β=1, γ=0 |
| `Satellite_tortuosity_3d` | Path coverage of Satellite tree | α=0, β=1, γ=0 |
| `Coverage_length_3d` | Total root length of Coverage tree | α=0, β=0, γ=1 |
| `Coverage_distance_3d` | Travel distance of Coverage tree | α=0, β=0, γ=1 |
| `Coverage_tortuosity_3d` | Path coverage of Coverage tree | α=0, β=0, γ=1 |

### Corner Architecture Interpretation

| Architecture | Optimizes | Characteristics |
|--------------|-----------|-----------------|
| Steiner (α=1) | Minimal total root length | Short connections, efficient material use |
| Satellite (β=1) | Minimal travel distance | Direct paths from base to tips |
| Coverage (γ=1) | Maximal path coverage | Extensive soil exploration |

---

## Other Metrics

| Field | Description | Units | Range |
|-------|-------------|-------|-------|
| `Barycenter x displacement` | Horizontal distance from hypocotyl to convex hull center | length | any |
| `Barycenter y displacement` | Vertical distance from hypocotyl to convex hull center | length | any |
| `Convex Hull Area` | Area of the convex hull enclosing all root nodes | area | > 0 |

---

## Example Values

From test data analysis:

```
epsilon_3d: 1.078 (tree is 7.8% worse than optimal)
alpha_3d: 0.0
beta_3d: 0.02
gamma_3d: 0.98 (tree is closest to Coverage-optimizing strategy)

epsilon_3d (random): 3.15 (random trees are ~3x worse than optimal)
epsilon_3d_material (random): 3.15 (material cost is the limiting factor)
```

---

## See Also

- [Scientific Methods](scientific-methods.md) - Mathematical foundations and references
- [README](../README.md) - Installation and usage instructions