# Improve CI Workflow with Best Practices

## Why

The current CI workflow is functional but missing several best practices that would improve reliability, performance, and code quality. Key issues:

1. **No lockfile committed**: The `uv.lock` file exists locally but is not committed, meaning CI regenerates it on every run, leading to non-reproducible builds and potential dependency drift between local dev and CI
2. **Missing quality checks**: Ruff linter is installed but never run in CI, despite being configured in pyproject.toml with docstring enforcement (Google style)
3. **No Python version pinning**: No `.python-version` file to ensure consistent Python version between local development and CI
4. **Incomplete uv best practices**: Not leveraging uv's full project management capabilities with proper `uv sync --frozen` workflow
5. **Coverage workflow issue**: Current branch's coverage requirement will fail until comprehensive tests are added (prerequisite: `add-comprehensive-test-coverage` change)
6. **Legacy pip usage in package testing**: The `package` job uses `pip install` instead of testing the actual uv-based installation workflow users will experience
7. **No dependency security scanning**: Missing vulnerability checks for dependencies
8. **Workflow optimization opportunities**: Redundant `uv lock` step, missing parallelization, and inefficient caching

These gaps reduce CI reliability, waste compute resources, and miss opportunities to catch quality issues early.

## What Changes

**uv Best Practices:**
- Commit `uv.lock` to repository for reproducible builds across all environments
- Add `.python-version` file to pin Python version for uv auto-detection (e.g., `3.12`)
- Optimize CI caching by explicitly setting `cache-dependency-glob: "**/uv.lock"`
- Use `uv sync --frozen` in CI to prevent lockfile modification and ensure reproducibility
- Remove redundant `uv lock` step (use committed lockfile directly)
- Add lockfile validation to detect uncommitted changes

**Quality Checks:**
- Add Ruff linting step with `uv run ruff check .` to enforce code quality and docstring standards
- Configure Ruff to fail on errors, warning on fixable issues
- Add `uv run ruff format --check .` for format consistency (complement to Black)

**Package Testing Improvements:**
- Replace legacy `pip install dist/*.whl` with proper uv workflow testing
- Test actual user installation experience: `uv init`, `uv add ariadne-roots`, `uv run ariadne-trace`
- Verify both wheel and sdist installation paths using uv (not pip)
- Test that built package works in fresh uv-managed environment

**Security & Dependency Management:**
- Add dependency compatibility check (implicit in `uv sync --frozen`)
- Document approach for vulnerability scanning (uv doesn't have built-in scanning yet, suggest manual `pip-audit` or similar)

**Workflow Optimizations:**
- Add concurrency controls to cancel outdated CI runs on force-push
- Improve job names and step descriptions for clarity
- Ensure coverage threshold handling (document prerequisite)
- Optimize caching with proper lockfile glob pattern

**Documentation:**
- Add inline comments explaining uv project management patterns
- Update README.md with correct uv workflow (emphasize `uv sync`, not `pip install`)
- Document Python version requirements and uv version compatibility

## Impact

- **Affected specs**: `ci-cd` (new capability)
- **Affected code**:
  - `.github/workflows/test-dev.yml` - major refactor to use uv best practices, add quality checks
  - `uv.lock` - commit to repository (currently exists but uncommitted)
  - `.python-version` - new file for Python version pinning
  - `.gitignore` - ensure uv.lock is NOT ignored
  - `README.md` - update developer instructions to emphasize uv project workflow
- **Dependencies**:
  - Prerequisite: `add-comprehensive-test-coverage` must complete first, OR coverage threshold must be temporarily adjusted
  - Blocks: None, but enables more robust CI for future changes
- **Breaking changes**: None (CI improvements don't affect code functionality)
- **Performance impact**:
  - Faster CI runs due to lockfile reuse and better caching (estimated 15-25% speedup)
  - More reliable builds due to frozen dependency resolution