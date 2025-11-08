# Spec: Development Commands

## ADDED Requirements

### Requirement: Coverage Analysis Command

The system SHALL provide a `/coverage` command that enables AI assistants and developers to run comprehensive test coverage analysis with standardized instructions and interpretation guidance.

#### Scenario: Run coverage and view results

**GIVEN** a developer wants to check test coverage
**WHEN** they run `/coverage`
**THEN** the command provides:
- Instructions to run `uv run pytest --cov=ariadne_roots --cov-report=term-missing --cov-branch`
- Guidance on interpreting coverage percentages (statements, branches, functions, lines)
- Reference to the 90% coverage threshold from pyproject.toml
- Instructions to view HTML coverage report in `coverage/index.html`
- Explanation of what to test (core analysis functions vs GUI)

#### Scenario: Understand coverage gaps

**GIVEN** coverage results show missing lines
**WHEN** a developer needs to understand what to test
**THEN** the command explains:
- High priority: Pareto optimization and graph analysis functions
- Medium priority: Root trait calculations
- Lower priority: GUI functions (marked with pragma: no cover)
- How to identify critical gaps using the term-missing report

---

### Requirement: Code Quality Commands

The system SHALL provide a `/lint` command that enables AI assistants and developers to run linting and formatting checks with Black and Ruff using standardized instructions.

#### Scenario: Format code with Black

**GIVEN** a developer has made changes to Python files
**WHEN** they run `/lint`
**THEN** the command provides instructions to:
- Run `uv run black .` to format all Python files
- Run `uv run black --check .` to preview changes without applying
- Verify 88-character line length is enforced
- Commit formatting changes separately from logic changes

#### Scenario: Check code quality with Ruff

**GIVEN** a developer wants to verify code quality
**WHEN** they run `/lint`
**THEN** the command provides instructions to:
- Run `uv run ruff check .` for general linting
- Run `uv run ruff check . --select D` for docstring checks
- Fix or suppress warnings as appropriate
- Ensure Google-style docstrings are present on public functions

---

### Requirement: PR Description Template

The system SHALL provide a `/pr-description` command that gives developers access to a comprehensive PR description template adapted to Ariadne's Python/pytest conventions and scientific computing context.

#### Scenario: Create a new pull request

**GIVEN** a developer has completed feature development
**WHEN** they run `/pr-description`
**THEN** the command provides:
- A complete PR description template in Markdown
- Checklist for testing (pytest, integration tests, coverage)
- Checklist for code quality (Black, Ruff, docstrings)
- Section for domain accuracy (algorithm sources, Pareto validation)
- Section for breaking changes and migration notes
- Instructions to create PR with `gh pr create`

#### Scenario: Describe changes in root phenotyping domain

**GIVEN** a PR modifies root analysis algorithms
**WHEN** the developer fills out the template
**THEN** the template includes sections for:
- Summary of changes to Pareto functions or trait calculations
- Validation against real root data (plantB_day11 fixture)
- Algorithm sources and accuracy trade-offs
- Impact on existing analyses and reproducibility

---

### Requirement: PR Review Workflow

The system SHALL provide a `/review-pr` command that gives reviewers access to a systematic PR review checklist adapted to Python conventions and scientific computing validation requirements.

#### Scenario: Review a pull request systematically

**GIVEN** a reviewer is assigned to review a PR
**WHEN** they run `/review-pr`
**THEN** the command provides:
- GitHub CLI commands for viewing and checking out PRs
- Comprehensive review checklist covering:
  - Code quality (PEP 8, naming, error handling)
  - Type safety (type hints, docstrings)
  - Testing (coverage, integration tests, fixtures)
  - Documentation (algorithm comments, Google-style docstrings)
  - Scientific accuracy (algorithm sources, Pareto validation)
  - Package structure (src layout, dependencies)

#### Scenario: Validate scientific accuracy

**GIVEN** a PR changes Pareto optimization or graph analysis
**WHEN** the reviewer checks scientific accuracy
**THEN** the command provides guidance to:
- Verify algorithm references credible sources
- Check integration tests pass with real root data
- Ensure Pareto front calculations are correct
- Validate graph analysis preserves mathematical properties
- Review reproducibility considerations

---

### Requirement: Post-Merge Cleanup

The system SHALL provide a `/cleanup-merged` command that enables developers to systematically clean up after PR merges, including branch deletion and OpenSpec change archival with safety checks.

#### Scenario: Clean up after merging a simple PR

**GIVEN** a PR without OpenSpec documentation has been merged
**WHEN** a developer runs `/cleanup-merged`
**THEN** the command guides them to:
1. Verify the merge with `gh pr list --state merged`
2. Switch to main branch with `git checkout main && git pull`
3. Delete local branch with `git branch -d <branch-name>`
4. Prune remote tracking with `git remote prune origin`
5. Verify cleanup with `git branch -a | grep <branch-name>`

#### Scenario: Archive OpenSpec change after merge

**GIVEN** a PR with OpenSpec documentation has been merged
**WHEN** a developer runs `/cleanup-merged`
**THEN** the command additionally guides them to:
1. Identify the change directory in `openspec/changes/`
2. Move to archive with `git mv openspec/changes/<id> openspec/changes/archive/<id>`
3. Update `openspec/changes/archive/README.md` with summary
4. Commit archive changes with descriptive message
5. Push to remote

#### Scenario: Safety check prevents premature deletion

**GIVEN** a branch has not been fully merged
**WHEN** a developer tries to delete with `git branch -d`
**THEN** the command:
- Explains that `-d` (not `-D`) is used for safety
- Shows that git will prevent deletion if not merged
- Instructs to check merge status with `gh pr view <number>`
- Warns never to force delete with `-D` without verification
