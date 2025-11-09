"""Scaling utilities for converting pixel measurements to real-world units."""


def apply_scaling_transformation(results, scale_factor, excluded_fields=None):
    """Apply scaling transformation to results dictionary.

    Args:
        results: Dictionary of analysis results
        scale_factor: Multiplicative scaling factor (e.g., 2.5 for 1 px = 2.5 mm)
        excluded_fields: Set of field name patterns to exclude from scaling
                        (dimensionless or already scaled fields)

    Returns:
        Dictionary with scaled numeric values, unchanged excluded/non-numeric values

    Examples:
        >>> results = {"Length": 100, "LR density": 0.5, "filename": "test.json"}
        >>> excluded = {"LR density"}
        >>> apply_scaling_transformation(results, 2.0, excluded)
        {"Length": 200.0, "LR density": 0.5, "filename": "test.json"}
    """
    if excluded_fields is None:
        excluded_fields = {
            "LR density",
            "alpha",
            "Mean LR angles",
            "Median LR angles",
            "LR count",
            "Branched Zone density",
            "scaling distance to front",
            "Tortuosity",
            "scaling (random)",
        }

    scaled_results = {}
    for key, value in results.items():
        if any(excl in key for excl in excluded_fields):
            # Do not scale excluded fields
            scaled_results[key] = value
        elif key in ["LR lengths", "LR minimal lengths"]:
            # Special handling for array fields - scale each element
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
