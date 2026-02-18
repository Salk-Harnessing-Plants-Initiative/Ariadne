# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0a1] - 2026-02-18 (Pre-release)

### Added

- **3D Pareto path tortuosity analysis** (PR #19) - Major new capability for analyzing root system architecture in three dimensions
  - GUI checkbox "Add path tortuosity to Pareto (3D, slower)" in scale dialog for optional 3D analysis
  - 3D surface plot visualization using Delaunay triangulation for Pareto front
  - Surface colored by path coverage using viridis colormap with colorbar
  - Graceful fallback to scatter plot when triangulation fails (collinear points)
  - `enable_3d` parameter to `analyze()` function (default: True for backward compatibility)
- **Tradeoff calculation** for comparing actual root architecture to optimal Steiner/Satellite architectures (Conn et al., 2019)
  - New `calculate_tradeoff()` function computes Steiner (material-optimal) and Satellite (transport-optimal) points
  - 7 new CSV output fields: `Tradeoff`, `Steiner_length`, `Steiner_distance`, `Satellite_length`, `Satellite_distance`, `Actual_ratio`, `Optimal_ratio`
- **Alpha interpolation** for more precise characteristic alpha values in Pareto front analysis
  - `distance_from_front()` now interpolates between the two closest discrete alpha values
  - Returns Python floats (not strings) for clean CSV serialization
- Comprehensive test suite for 3D Pareto functions (`tests/test_pareto_3d.py`, `tests/test_scientific_integration.py`)
- Scientific documentation (`docs/scientific-methods.md`, `docs/output-fields.md`)
- Explicit exclusions in scaling.py for 3D ratio fields: "Path tortuosity", "alpha_beta"

### Fixed

- **3D Pareto robustness fixes:**
  - Cycle detection in `graph_costs_3d_path_tortuosity` now returns 3 inf values (was returning 2)
  - Division by zero protection for coincident nodes in path tortuosity calculation
  - Parameter validation: `alpha + beta <= 1` assertion in `pareto_cost_3d_path_tortuosity`
  - Invalid (alpha, beta) combinations now skipped in `pareto_front_3d_path_tortuosity`
- 3D results scaling now applied consistently with 2D results in main.py
- 3D plot internal scaling to match CSV output values
- Fixed `np.float64` serialization in CSV output for LR angles, lengths, and other numeric fields
- Fixed double-scaling bug in Pareto front graph visualization where data was scaled twice
- Restored "Tortuosity" key name in results dict (was incorrectly renamed during branch merge)

### Changed

- `plot_all_3d()` now uses triangulated surface instead of line plot for better visualization
- 3D analysis is optional via GUI checkbox (disabled by default for performance)
- Dimensionless ratio fields excluded from scaling transformation

**Note**: This is a pre-release version (alpha 1 of 0.2.0) for testing the new 3D Pareto analysis features.

## [0.1.0a1] - 2024-11-11 (Pre-release)

### Added

- `/test` command for running pytest with common options and filters
- `/changelog` command for maintaining CHANGELOG.md following Keep a Changelog format
- `/release` command for complete PyPI release workflow
- OpenSpec proposal system for managing development changes
- Comprehensive command integration (test, coverage, lint, changelog, pr-description, review-pr, release, cleanup-merged)
- CHANGELOG.md file following Keep a Changelog format

**Note**: This is a pre-release version (alpha 1) for testing the new command infrastructure.

## [0.0.3] - 2024-11-11

### Added

- Custom scaling dialog for converting pixel measurements to real-world units (#29)
- Support for mm, cm, and µm unit selection in GUI
- Automated scaling transformation applied to all measurements in CSV output
- Comprehensive test coverage for buffer calculation edge cases (#32)
- Security scanning documentation in README
- Claude commands for development workflow (`/coverage`, `/lint`, `/pre-merge-check`, `/pr-description`, `/review-pr`, `/cleanup-merged`)
- Improved CI workflow with uv best practices (#30)
- Coverage requirement enforcement in CI (90% threshold)

### Changed

- Pareto front visualizations now use improved buffer calculation
- Output CSV files include properly scaled measurements with units
- CI workflow migrated to use uv package manager
- Test framework with pytest and comprehensive fixtures

### Fixed

- Fixed buffer calculation for negative coordinates and zero values (#26)
- Fixed matplotlib errors when plotting degenerate coordinate ranges
- Fixed UnboundLocalError in buffer calculation with comprehensive test coverage

## [0.0.2] - 2024-06-27

### Added

- Initial release with core root system architecture analysis
- Pareto front analysis for optimal root networks
- Comprehensive trait calculations (lengths, angles, density, tortuosity)
- Tkinter GUI for interactive root analysis
- CSV export of analysis results
- Multi-file batch processing
- NetworkX-based graph algorithms for root networks

[Unreleased]: https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/compare/v0.2.0a1...HEAD
[0.2.0a1]: https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/compare/v0.1.0a1...v0.2.0a1
[0.1.0a1]: https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/compare/v0.0.3...v0.1.0a1
[0.0.3]: https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/releases/tag/v0.0.2