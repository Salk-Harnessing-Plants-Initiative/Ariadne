# CI/CD Specification

## ADDED Requirements

### Requirement: Committed Lockfile for Reproducible Builds

The CI/CD pipeline SHALL use a committed `uv.lock` file to ensure reproducible dependency resolution across all environments.

#### Scenario: Lockfile committed to repository
- **WHEN** the repository is checked out
- **THEN** `uv.lock` file exists in repository root
- **AND** lockfile is tracked by git (not gitignored)

#### Scenario: CI uses frozen lockfile
- **WHEN** CI runs dependency installation
- **THEN** CI uses `uv sync --frozen` command
- **AND** lockfile is not modified during CI execution
- **AND** validation step confirms lockfile unchanged

#### Scenario: Lockfile changes detected
- **WHEN** lockfile is modified locally and not committed
- **THEN** CI validation step detects the change
- **AND** CI fails with informative message about uncommitted lockfile

### Requirement: Python Version Pinning

The project SHALL maintain a `.python-version` file to pin the default Python version for local development consistency.

#### Scenario: Python version file exists
- **WHEN** developers clone the repository
- **THEN** `.python-version` file exists in repository root
- **AND** file contains single Python version (e.g., `3.12`)

#### Scenario: uv uses pinned Python version
- **WHEN** developers run `uv sync` without specifying Python version
- **THEN** uv automatically uses version from `.python-version`
- **AND** virtual environment is created with pinned version

#### Scenario: CI tests multiple Python versions
- **WHEN** CI runs test matrix
- **THEN** CI tests multiple Python versions (3.12, 3.13) regardless of `.python-version`
- **AND** all matrix versions pass validation

### Requirement: Code Quality Enforcement

The CI/CD pipeline SHALL enforce code quality standards using Ruff linter before running tests.

#### Scenario: Ruff linting runs in CI
- **WHEN** CI executes quality checks
- **THEN** `uv run ruff check .` is executed before tests
- **AND** CI fails if Ruff reports errors
- **AND** Ruff checks enforce docstring presence (Google style)

#### Scenario: Ruff catches quality issues
- **WHEN** code violates Ruff rules (undefined names, unused imports, missing docstrings)
- **THEN** Ruff linting step fails
- **AND** error message identifies specific violations with file and line number

#### Scenario: Formatting consistency check
- **WHEN** CI runs formatting checks
- **THEN** Black format check runs with `uv run black --check .`
- **AND** CI fails if code is not formatted according to Black rules

### Requirement: uv-Based Package Testing

The CI/CD pipeline SHALL test package installation using uv project workflow, not legacy pip commands.

#### Scenario: Wheel installation with uv
- **WHEN** testing built wheel package
- **THEN** CI uses `uv init` to create test project
- **AND** CI uses `uv add <path-to-wheel>` to install package
- **AND** CI uses `uv run python -c "import ariadne_roots"` to verify import
- **AND** test succeeds on all platforms (Linux, Windows, macOS)

#### Scenario: Source distribution with dev extras
- **WHEN** testing built sdist package
- **THEN** CI uses `uv add <path-to-sdist> --extra dev` to install with dev dependencies
- **AND** CI verifies dev tools are available (e.g., `uv run black --version`)
- **AND** test succeeds on all platforms

#### Scenario: CLI tool smoke test
- **WHEN** package is installed via wheel or sdist
- **THEN** CI verifies CLI entry point works (e.g., `uv run ariadne-trace --help`)
- **AND** command exits successfully

### Requirement: Optimized CI Caching

The CI/CD pipeline SHALL optimize caching for uv dependencies using lockfile-based cache invalidation.

#### Scenario: Cache keyed on lockfile
- **WHEN** CI sets up uv caching
- **THEN** cache configuration uses `cache-dependency-glob: "**/uv.lock"`
- **AND** cache is invalidated when lockfile changes
- **AND** cache is preserved when lockfile unchanged

#### Scenario: Cache reuse across runs
- **WHEN** CI runs with unchanged lockfile
- **THEN** cached dependencies are restored
- **AND** CI logs show cache hit
- **AND** dependency installation is skipped (faster execution)

### Requirement: Concurrency Control for Resource Efficiency

The CI/CD pipeline SHALL cancel outdated workflow runs when new commits are pushed to the same branch.

#### Scenario: Outdated runs cancelled on force-push
- **WHEN** developer pushes new commit to branch
- **AND** previous CI run is still in progress for same branch
- **THEN** previous run is automatically cancelled
- **AND** new run starts immediately

#### Scenario: Concurrency scoped to branch
- **WHEN** multiple branches have concurrent CI runs
- **THEN** runs on different branches do not interfere with each other
- **AND** only runs on same branch are subject to cancellation

### Requirement: Lockfile Validation

The CI/CD pipeline SHALL validate that the lockfile is not modified during CI execution.

#### Scenario: Lockfile unchanged after sync
- **WHEN** CI runs `uv sync --frozen`
- **THEN** lockfile content is identical to committed version
- **AND** validation step passes

#### Scenario: Lockfile modification detected
- **WHEN** lockfile is unexpectedly modified during CI
- **THEN** validation step detects changes with `git diff --exit-code uv.lock`
- **AND** CI fails with error message
- **AND** error message instructs developer to commit lockfile locally

### Requirement: Cross-Platform Compatibility

The CI/CD pipeline SHALL test on multiple operating systems and Python versions to ensure cross-platform compatibility.

#### Scenario: OS matrix testing
- **WHEN** CI runs test job
- **THEN** tests execute on Ubuntu 22.04, Windows 2022, and macOS 14
- **AND** all platforms must pass for CI to succeed

#### Scenario: Python version matrix testing
- **WHEN** CI runs test job
- **THEN** tests execute on Python 3.12 and 3.13
- **AND** all versions must pass for CI to succeed

#### Scenario: Matrix combination coverage
- **WHEN** CI completes successfully
- **THEN** all OS×Python combinations have passed (6 total: 3 OS × 2 Python versions)

### Requirement: Test Coverage Enforcement

The CI/CD pipeline SHALL enforce minimum test coverage threshold and fail if coverage is below target.

#### Scenario: Coverage threshold set at 80%
- **WHEN** CI runs tests with coverage
- **THEN** pytest runs with `--cov-fail-under=80`
- **AND** CI fails if total coverage is below 80%

#### Scenario: Coverage report generated
- **WHEN** tests complete
- **THEN** coverage report is generated in XML format
- **AND** coverage report is uploaded as CI artifact
- **AND** artifact name includes OS and Python version (e.g., `coverage-ubuntu-22.04-py3.12`)

#### Scenario: Missing coverage identified
- **WHEN** coverage report is generated
- **THEN** report includes `--cov-report=term-missing` output
- **AND** uncovered lines are identified by file and line number

### Requirement: CI Workflow Documentation

The CI/CD workflow SHALL include inline comments explaining uv-specific patterns and decisions.

#### Scenario: Key steps documented
- **WHEN** developers read workflow file
- **THEN** comments explain purpose of `uv sync --frozen`
- **AND** comments explain lockfile validation step
- **AND** comments explain cache dependency glob pattern

#### Scenario: README documents uv workflow
- **WHEN** developers read contribution guide
- **THEN** README emphasizes `uv sync` workflow (not pip install)
- **AND** README explains `.python-version` file purpose
- **AND** README documents how to update lockfile (`uv lock`)

### Requirement: Security and Dependency Management

The project SHALL document approach for dependency vulnerability scanning and updates.

#### Scenario: Vulnerability scanning documented
- **WHEN** security concerns arise
- **THEN** README or contributing guide documents recommended tools (pip-audit, safety)
- **AND** documentation explains manual scanning process

#### Scenario: Dependency updates via lockfile
- **WHEN** dependencies need updating
- **THEN** developers run `uv lock --upgrade` locally
- **AND** commit updated lockfile
- **AND** CI validates updated lockfile with frozen sync