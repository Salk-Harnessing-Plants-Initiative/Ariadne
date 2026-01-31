"""Scaling utilities for converting pixel measurements to real-world units."""


def apply_scaling_transformation(results, scale_factor, excluded_fields=None):
    """Apply scaling transformation to results dictionary.

    Scales numeric fields by scale_factor while preserving dimensionless metrics,
    non-numeric values, and array structures.

    Uses substring matching for excluded_fields to catch related metrics:
    - "LR density" excludes any field containing "LR density"
    - "angles" excludes "Mean LR angles", "Median LR angles", "LR angles"

    This approach reduces maintenance burden when adding new dimensionless
    metrics while maintaining scientific correctness.

    Args:
        results: Dictionary of analysis results
        scale_factor: Multiplicative scaling factor (e.g., 2.5 for 1 px = 2.5 mm)
        excluded_fields: Set of substring patterns to exclude from scaling.
                        Uses substring matching (not exact matching).
                        Defaults to 13 dimensionless patterns:
                        - "LR density", "Branched Zone density" (densities)
                        - "alpha" (shape parameter)
                        - "Mean LR angles", "Median LR angles", "LR angles" (angles)
                        - "LR count" (count)
                        - "scaling distance to front", "scaling (random)" (normalized)
                        - "Tortuosity" (ratio)
                        - "Tradeoff", "Actual_ratio", "Optimal_ratio" (dimensionless ratios)

    Returns:
        Dictionary with scaled numeric values, unchanged excluded/non-numeric values

    Examples:
        >>> results = {
        ...     "Total root length": 100,
        ...     "LR density": 0.5,
        ...     "Mean LR angles": 45.0,
        ...     "filename": "test.json"
        ... }
        >>> scaled = apply_scaling_transformation(results, 2.0)
        >>> scaled["Total root length"]  # Scaled
        200.0
        >>> scaled["LR density"]  # Excluded (contains "LR density" pattern)
        0.5
        >>> scaled["Mean LR angles"]  # Excluded (contains "angles" pattern)
        45.0
        >>> scaled["filename"]  # Non-numeric preserved
        'test.json'

        Custom exclusion patterns (substring matching):
        >>> excluded = {"ratio", "count"}
        >>> results = {"Length ratio": 1.5, "Root count": 10, "Length": 100}
        >>> scaled = apply_scaling_transformation(results, 2.0, excluded)
        >>> scaled["Length ratio"]  # Excluded (contains "ratio")
        1.5
        >>> scaled["Root count"]  # Excluded (contains "count")
        10
        >>> scaled["Length"]  # Scaled
        200.0
    """
    if excluded_fields is None:
        excluded_fields = {
            "LR density",
            "alpha",
            "Mean LR angles",
            "Median LR angles",
            "LR angles",  # Array of angles (dimensionless) - explicit exclusion
            "LR count",
            "Branched Zone density",
            "scaling distance to front",
            "Tortuosity",
            "scaling (random)",
            # Tradeoff metrics (dimensionless ratios)
            "Tradeoff",
            "Actual_ratio",
            "Optimal_ratio",
            # 3D Pareto analysis fields (ratios and parameter tuples)
            "Path tortuosity",  # Ratio: sum of (travel_dist / straight_dist)
            "alpha_beta",  # Parameter tuple, not a length
        }

    scaled_results = {}
    for key, value in results.items():
        if any(excl in key for excl in excluded_fields):
            # Do not scale excluded fields
            scaled_results[key] = value
        elif key in ["LR lengths", "LR minimal lengths"]:
            # Special handling for array fields - scale each element
            # Currently only LR lengths and LR minimal lengths are array-valued metrics
            # If new array fields are added to quantify.py, update this list
            try:
                scaled_results[key] = [float(v) * scale_factor for v in value]
            except (ValueError, TypeError):
                scaled_results[key] = value
        else:
            # Scale all other numeric fields
            try:
                scaled_results[key] = float(value) * scale_factor
            except (ValueError, TypeError):
                # Leave non-numeric values as-is
                scaled_results[key] = value

    return scaled_results
