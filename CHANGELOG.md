# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Fixed `np.float64` serialization in CSV output for LR angles, lengths, and other numeric fields
- Fixed double-scaling bug in Pareto front graph visualization where data was scaled twice
- Updated test fixtures to use Python native floats instead of numpy types

### Added

- Comprehensive CSV output validation tests (`tests/test_csv_output.py`)
  - Field type validation (Python native types, not numpy)
  - Field range validation (angles 0-180°, lengths ≥ 0, etc.)
  - CSV serialization validation (no numpy type strings)

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

[Unreleased]: https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/compare/v0.1.0a1...HEAD
[0.1.0a1]: https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/compare/v0.0.3...v0.1.0a1
[0.0.3]: https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/releases/tag/v0.0.2
