# Add Alpha Interpolation

## Why

Currently, the `distance_from_front()` function returns the closest discrete alpha value from the Pareto front (e.g., 0.00, 0.01, 0.02, ..., 1.00). This limits precision to 2 decimal places.

Matt Platre's research requires higher precision alpha values to better characterize where actual root architectures fall on the Pareto front. By interpolating between the two closest discrete alpha values, we can achieve 6 decimal place precision.

## What Changes

### Modified Function: `distance_from_front()` in `quantify.py`

Instead of returning the closest discrete alpha:
```python
characteristic_alpha, scaling_distance = closest
return characteristic_alpha, scaling_distance
```

The function will interpolate between the two closest alphas using distance-weighted linear interpolation:
```python
# Find two closest alpha values
sorted_alphas = sorted(distances.items(), key=lambda x: x[1])
closest = sorted_alphas[0]
second_closest = sorted_alphas[1] if len(sorted_alphas) > 1 else closest

alpha1, dist1 = closest
alpha2, dist2 = second_closest

# Linear interpolation (closer distance gets higher weight)
if dist1 == dist2:
    interpolated_alpha = alpha1
else:
    total_dist = dist1 + dist2
    weight1 = dist2 / total_dist
    weight2 = dist1 / total_dist
    interpolated_alpha = alpha1 * weight1 + alpha2 * weight2

return float(interpolated_alpha), float(dist1)
```

### Output Changes

- `alpha` field changes from discrete (e.g., `0.05`) to interpolated (e.g., `0.052847`)
- `alpha (random)` field similarly changes to interpolated value
- Precision: 6 decimal places (stored as Python float, not string)

## Impact

- **CSV Output**: Alpha values will have higher precision
- **Backward Compatibility**: Values are still floats, just more precise
- **Performance**: Negligible (one additional sort/interpolation per analysis)
