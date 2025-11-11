---
description: Maintain CHANGELOG.md following Keep a Changelog format
---

# Update Changelog

Maintain CHANGELOG.md following [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format for the ariadne-roots package.

## Quick Commands

```bash
# View recent changes
git log --oneline --decorate -10

# View changes since last tag
git log $(git describe --tags --abbrev=0)..HEAD --oneline

# View all tags
git tag -l | sort -V

# View changes by author
git log --author="<name>" --oneline

# View changes to specific module
git log --oneline -- src/ariadne_roots/quantify.py

# View current version
grep '^version = ' pyproject.toml
```

## Changelog Format

The CHANGELOG.md follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) principles:

- **Guiding Principle**: Changelogs are for humans, not machines
- **Latest First**: Most recent version at the top
- **One Version Per Release**: Each release gets a section
- **Same Date Format**: YYYY-MM-DD
- **Semantic Versioning**: Version numbers follow [SemVer](https://semver.org/)

### Change Categories

- **Added**: New features (new analysis capabilities, new GUI features, new CLI options)
- **Changed**: Changes to existing functionality (algorithm improvements, performance enhancements)
- **Deprecated**: Soon-to-be removed features (warn users)
- **Removed**: Removed features (breaking change)
- **Fixed**: Bug fixes (calculation errors, crashes, edge cases)
- **Security**: Security vulnerability fixes

## Template

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- New feature description

### Changed

- Change description

### Fixed

- Bug fix description

## [0.0.3] - 2024-11-15

### Added

- Scaling features for converting pixel measurements to real-world units
- Custom scaling dialog in GUI for setting conversion factors
- Automated scaling transformation applied to all output measurements
- Unit selection (mm, cm, µm) for scaled results

### Changed

- Output CSV files now include properly scaled measurements
- Pareto front visualizations are better centered with improved buffer calculation

### Fixed

- Fixed buffer calculation for negative coordinates and zero values (#26)
- Fixed matplotlib errors when plotting degenerate coordinate ranges

## [0.0.2] - 2024-06-27

### Added

- Initial release with core root system architecture analysis
- Pareto front analysis for optimal root networks
- Comprehensive trait calculations (lengths, angles, density, tortuosity)
- Tkinter GUI for interactive analysis
- CSV export of analysis results
- Multi-file batch processing

[Unreleased]: https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/compare/v0.0.3...HEAD
[0.0.3]: https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/releases/tag/v0.0.2
```

## Workflow: Adding Changes to Changelog

### Step 1: Identify Changes Since Last Release

```bash
# Find last version tag
git tag -l | sort -V | tail -1

# List commits since last tag (e.g., v0.0.3)
git log v0.0.3..HEAD --oneline

# Or view detailed diff
git log v0.0.3..HEAD --pretty=format:"%h %s" --reverse
```

### Step 2: Categorize Each Change

Group commits by category:

- **Added**: New pipelines, new traits, new GUI features, new CLI commands
- **Changed**: Refactors, performance improvements, algorithm updates
- **Fixed**: Bug fixes in calculations, error handling improvements, GUI fixes
- **Security**: Security patches, data handling fixes

### Step 3: Update CHANGELOG.md

Add changes to the `[Unreleased]` section:

```markdown
## [Unreleased]

### Added

- Custom scaling dialog for setting pixel-to-unit conversion factors (#29)
- Support for mm, cm, and µm unit selection
- Automated scaling transformation for all measurements

### Fixed

- Fixed buffer calculation for negative coordinates (#26)
- Fixed matplotlib errors for degenerate coordinate ranges
```

### Step 4: When Releasing a Version

Move `[Unreleased]` to a versioned section:

```markdown
## [Unreleased]

## [0.0.4] - 2024-11-15

### Added

- Custom scaling dialog for setting pixel-to-unit conversion factors (#29)
- Support for mm, cm, and µm unit selection
```

Update the version in `pyproject.toml`:

```toml
version = "0.0.4"
```

Update the links at the bottom:

```markdown
[Unreleased]: https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/compare/v0.0.4...HEAD
[0.0.4]: https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/releases/tag/v0.0.3
```

## Writing Good Changelog Entries

### Good Examples

```markdown
### Added

- Custom scaling dialog for converting pixel measurements to real-world units
- Convex hull calculation for root system spread analysis
- Batch processing support for analyzing multiple root systems

### Fixed

- Buffer calculation no longer fails for negative coordinates
- Pareto front visualization correctly handles degenerate cases
- CSV export properly escapes special characters in filenames
```

### Bad Examples

```markdown
### Added

- New stuff ❌ (too vague)
- Fix bug ❌ (belongs in "Fixed", not "Added")
- Updated dependencies ❌ (unless breaking change, don't include routine updates)
- Refactored code ❌ (internal change, not user-facing)
```

## Tips

1. **Update continuously**: Add to `[Unreleased]` as you merge PRs, don't batch at release time
2. **Link to PRs**: Include `(#42)` references for traceability
3. **Be user-focused**: Write for users, not developers
   - Good: "Added scaling features for pixel-to-unit conversion"
   - Bad: "Implemented ScalingDialog class with apply_scaling_transformation method"
4. **Note breaking changes**: Clearly mark with `**BREAKING:**`
5. **Skip internal changes**: Don't include CI config, test refactors, or minor internal changes
6. **Group related changes**: If a feature required multiple commits, summarize as one entry

## Breaking Changes

If a change is breaking, mark it clearly:

```markdown
### Changed

- **BREAKING**: `analyze()` now requires `scale_factor` parameter (previously optional)
  - Migration: Pass explicit `scale_factor=1.0` to maintain previous behavior
  - Example: `analyze(graph, scale_factor=1.0, unit="pixels")`
```

## Release Checklist

Before cutting a release:

- [ ] All changes moved from `[Unreleased]` to versioned section
- [ ] Version number follows SemVer (major.minor.patch)
- [ ] Version updated in `pyproject.toml`
- [ ] Date is today's date in YYYY-MM-DD format
- [ ] Links at bottom are updated
- [ ] Breaking changes are clearly marked
- [ ] Notable changes are user-friendly and descriptive

## Semantic Versioning Quick Reference

Given a version number `MAJOR.MINOR.PATCH`:

- **MAJOR**: Breaking changes (0.x.x → 1.0.0)
  - Changed trait calculation algorithms
  - Removed deprecated GUI features
  - Changed CSV output format
- **MINOR**: New features, backwards-compatible (0.0.x → 0.1.0)
  - New analysis capabilities
  - New GUI features
  - New trait calculations
- **PATCH**: Bug fixes, backwards-compatible (0.0.3 → 0.0.4)
  - Fixed calculation errors
  - Fixed GUI crashes
  - Fixed edge case handling

## Examples for ariadne-roots

### Version 0.0.3 (Minor Release)

```markdown
## [0.0.3] - 2024-11-15

### Added

- Custom scaling dialog for converting pixel measurements to real-world units (#29)
- Support for mm, cm, and µm unit selection
- Automated scaling transformation applied to all measurements in CSV output
- Pareto front visualizations with improved buffer calculation

### Fixed

- Fixed buffer calculation for negative coordinates and zero values (#26)
- Fixed matplotlib errors when plotting degenerate coordinate ranges
- Added comprehensive test coverage for buffer calculation edge cases
```

### Version 0.0.4 (Patch Release)

```markdown
## [0.0.4] - 2024-11-20

### Fixed

- Fixed convex hull calculation failing on single-point arrays
- Fixed CSV export error when filename contains special characters
- Corrected trait names in scaled output CSV
```

### Version 1.0.0 (Breaking Change)

```markdown
## [1.0.0] - 2025-01-15

### Changed

- **BREAKING**: Trait calculation results now use different normalization
  - All length measurements are now normalized by primary root length
  - Migration: Multiply length traits by primary root length to match previous values
  - This affects: LR lengths, PR length, Branched Zone length

### Added

- Comprehensive validation against published Arabidopsis root data
- Detailed documentation for all trait calculation algorithms

### Fixed

- Corrected lateral root angle calculation for branching patterns
```

## Project-Specific Notes

### Version Location

Version is defined in `pyproject.toml`:

```toml
[project]
name = "ariadne-roots"
version = "0.0.3"
```

### Scientific Accuracy

Be extra careful with changes to trait calculations:

- Note if calculations change in any way
- Provide validation data showing accuracy
- Consider impact on reproducibility of published papers
- Document any algorithm changes thoroughly

### PyPI Releases

When releasing (see `/release` command for full workflow):

```bash
# Update version in pyproject.toml
# Update CHANGELOG.md (move [Unreleased] to versioned section)
# Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 0.0.4"

# Create version bump PR
gh pr create --title "Release v0.0.4" --body "..."

# After PR merge, create GitHub release (triggers PyPI upload)
gh release create v0.0.4 --generate-notes
```

## Integration with Release Workflow

The changelog is a critical part of the release process:

1. **Before release**: Review `git log` and update `[Unreleased]` section
2. **During release**: Move `[Unreleased]` to versioned section with today's date
3. **After release**: Start new `[Unreleased]` section for next version

See `/release` command for complete release workflow.

## Related Commands

- `/release` - Complete release process guide
- `/test` - Run test suite before releasing
- `/coverage` - Verify test coverage
- `/lint` - Check code style
