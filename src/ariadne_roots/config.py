"""Global configuration for scaling factors.

This module stores scaling configuration that allows converting pixel measurements
to real-world units (e.g., mm, cm). The scaling factor is set by the user through
the AnalyzerUI dialog and applied during analysis output.
"""

length_scale_factor = 1.0  # Default: 1 pixel = 1.0 unit
length_scale_unit = "px"  # Default unit
