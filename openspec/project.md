# Project Context

## Purpose
Ariadne is a specialized software package for analyzing images of _Arabidopsis thaliana_ root systems. The project aims to:
- Provide a GUI for semi-automated image segmentation of plant root systems
- Create dynamic 2D skeleton graphs of root system architecture (RSA)
- Handle complex, messy, and highly-branched root systems where current methods fail
- Support time-series analysis via GIF processing
- Measure cost-performance trade-offs and Pareto optimality in RSA networks
- Calculate comprehensive root traits for plant phenotyping research

This is an active research tool developed for the Salk Harnessing Plants Initiative, designed to advance plant biology research through accurate root system analysis.

## Tech Stack
- **Language**: Python 3.8+ (tested on 3.11, 3.12, 3.13)
- **Build System**: setuptools
- **Package Manager**: uv (primary), conda/mamba (alternative)
- **Core Dependencies**:
  - pillow (image processing)
  - networkx (graph analysis for skeleton structures)
  - numpy (numerical computations)
  - scipy (scientific algorithms)
  - matplotlib (visualization and GUI)
- **Dev Tools**:
  - pytest & pytest-cov (testing and coverage)
  - black (code formatting, 88 char line length)
  - ruff (linting with pydocstyle)
  - pydocstyle (Google-style docstrings)
- **CI/CD**: GitHub Actions
- **Distribution**: PyPI (ariadne-roots package)

## Project Conventions

### Code Style
- **Formatter**: Black with 88-character line length
- **Linter**: Ruff configured to enforce docstring standards (select = ["D"])
- **Docstring Style**: Google style convention (required for all functions)
- **Naming Conventions**:
  - Use full words, not single letters, for variable names (readability priority)
  - Follow Python PEP 8 conventions
- **Type Annotations**: Preferred and encouraged
- **Comments**: Required for calculation steps and algorithm explanations
- **Consistency**: Variable names should be consistent across the codebase

### Architecture Patterns
- **Package Structure**: Source layout with `src/ariadne_roots/` directory
- **Entry Point**: CLI tool via `ariadne-trace` command (defined in pyproject.toml scripts)
- **Core Modules**:
  - `main.py`: GUI entry point
  - `quantify.py`: Root trait calculations
  - `pareto_functions.py`: Pareto optimality algorithms
- **Data Format**: JSON files for traced root data
- **GUI Framework**: Matplotlib-based interactive GUI with custom keybindings

### Testing Strategy
- **Framework**: pytest
- **Coverage Requirements**: Minimum 80% code coverage (enforced in CI)
- **Coverage Tools**: pytest-cov with branch coverage enabled
- **Test Location**: `tests/` directory
- **CI Matrix Testing**:
  - OS: Ubuntu 22.04, Windows 2022, macOS 14
  - Python versions: 3.12, 3.13
- **Additional CI Checks**:
  - Black formatting verification
  - Package building (sdist & wheel)
  - Installation testing (both wheel and sdist with dev extras)
  - Twine metadata validation

### Git Workflow
- **Main Branch**: `main`
- **Branching Strategy**: Feature branches with descriptive names
  - Pattern for personal branches: `<name>/<descriptive-feature-name>`
  - Example: `elizabeth/add-coverage-requirement`
- **Commit Messages**: Short, descriptive messages that explain the "why"
- **Pull Request Process**:
  1. Create feature branch
  2. Make changes with frequent commits
  3. Push and open PR with clear description
  4. Request review from team members
  5. Merge after approval
  6. Delete remote branch post-merge
- **CI Triggers**: All pushes and pull requests run full test suite

### Release Process
- **Versioning**: Semantic versioning (MAJOR.MINOR.PATCH)
- **Release Workflow**:
  1. Create bump version branch
  2. Update version in pyproject.toml
  3. Open PR and get review
  4. Merge to main
  5. Create GitHub release with tag
  6. Automated PyPI publishing via GitHub Actions

## Domain Context

### Plant Biology & Phenotyping
- **Target Organism**: _Arabidopsis thaliana_ (model plant organism)
- **Root System Architecture (RSA)**: The spatial configuration of a plant's root system
- **Primary Root (PR)**: The main root growing downward from the hypocotyl
- **Lateral Roots (LR)**: Branches emerging from the primary root
- **Hypocotyl**: The stem-like portion between roots and cotyledons

### Root Traits Measured
The software calculates 30+ RSA traits including:
- **Length metrics**: Total root length, PR length, mean/median LR lengths
- **Spatial metrics**: Basal/branched/apical zone lengths, barycentre displacement
- **Architectural metrics**: LR count, LR density, branched zone density
- **Angle metrics**: Mean/median LR set point angles
- **Efficiency metrics**: Tortuosity, minimal distances, travel distances
- **Pareto-related traits**: Alpha (growth vs transport efficiency trade-off), scaling distance to front

### Scientific Background
The project implements algorithms from published research:
1. Chandrasekhar & Navlakha (2019): Neural arbors are Pareto optimal (Proc. Royal Soc. B)
2. Conn et al. (2017): Universal network design principles in plant architectures (Cell Systems)

### GUI Workflow
1. **Trace Mode**: Users manually trace roots by clicking to place nodes
2. **Save**: Each traced root saved as JSON with plant ID
3. **Analyze Mode**: Batch processing of JSON files to calculate all RSA traits
4. **Output**: CSV file with traits + Pareto optimality graphs

## Important Constraints
- **Research Code**: This is a work-in-progress research tool, provided as-is
- **License**: GPL-3.0-or-later (open source with copyleft)
- **Python Version**: Requires Python 3.8+ (actively tested on 3.11-3.13)
- **Platform Support**: Cross-platform (Linux, Windows, macOS)
- **Development Stage**: Beta (Development Status :: 4 - Beta)
- **GUI Dependency**: Requires display for interactive tracing interface
- **Manual Input**: Semi-automated - requires human input for initial root tracing

## External Dependencies
- **PyPI**: Package distribution via https://pypi.org/project/ariadne-roots/
- **GitHub**:
  - Source repository: https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne
  - Issue tracking
  - GitHub Actions for CI/CD
  - Release management
- **No External APIs**: All processing done locally
- **No External Services**: Standalone desktop application
