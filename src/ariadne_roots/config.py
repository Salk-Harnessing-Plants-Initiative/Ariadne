"""Global configuration for scaling factors and analysis options.

This module stores configuration settings for:
- Scaling: converting pixel measurements to real-world units (e.g., mm, cm)
- Analysis options: enabling/disabling optional analysis features

Settings are typically configured through the AnalyzerUI dialog.
"""

length_scale_factor = 1.0  # Default: 1 pixel = 1.0 unit
length_scale_unit = "px"  # Default unit

# 3D Pareto analysis is optional (slower: 10,201 iterations vs 101 for 2D)
enable_3d_analysis = False  # Default: disabled
