# Add Tradeoff Calculation

## Why

Researchers need to quantify how close an actual root architecture is to theoretically optimal architectures. The Pareto front contains two extreme points:

1. **Steiner architecture** - Minimizes total root length (material cost)
2. **Satellite architecture** - Minimizes travel distance (transport efficiency)

A "Tradeoff" metric comparing the actual root to these optima provides insight into the evolutionary/developmental strategy of the plant.

## What Changes

### New Function: `calculate_tradeoff()` in `quantify.py`

```python
def calculate_tradeoff(front, actual_tree):
    """
    Calculate Tradeoff metric comparing actual root to optimal architectures.

    Tradeoff = (actual_length / actual_distance) / (steiner_length / satellite_distance)

    Args:
        front: Dict of {alpha: [total_length, travel_distance]} Pareto front points
        actual_tree: Tuple of (total_root_length, travel_distance)

    Returns:
        Dict with Tradeoff and component values
    """
```

### New Output Fields

The function adds 7 new fields to the results dictionary:

| Field | Description |
|-------|-------------|
| `Tradeoff` | Ratio of actual to optimal efficiency |
| `Steiner_length` | Min total root length on Pareto front |
| `Steiner_distance` | Travel distance at Steiner point |
| `Satellite_length` | Total root length at Satellite point |
| `Satellite_distance` | Min travel distance on Pareto front |
| `Actual_ratio` | actual_length / actual_distance |
| `Optimal_ratio` | steiner_length / satellite_distance |

### Integration

The function is called from `pareto_calcs()` or `analyze()` and the results are merged into the output dictionary.

## Impact

- **CSV Output**: 7 new columns in analysis results
- **Backward Compatibility**: New fields only, no existing fields modified
- **Performance**: Minimal (two min() operations on Pareto front)
