# Implementation Tasks

## 1. Lockfile and Version Pinning
- [ ] 1.1 Create `.python-version` file with pinned Python version (3.12 or 3.13)
- [ ] 1.2 Verify `uv.lock` is up-to-date locally with `uv lock`
- [ ] 1.3 Commit `uv.lock` to repository (ensure not gitignored)
- [ ] 1.4 Update `.gitignore` to explicitly NOT ignore uv.lock if currently ignored
- [ ] 1.5 Test that `uv sync --frozen` works locally with committed lockfile

## 2. CI Workflow - Test Job Improvements
- [ ] 2.1 Update `cache-dependency-glob` to `"**/uv.lock"` for proper cache invalidation
- [ ] 2.2 Remove redundant `uv lock` step (use committed lockfile instead)
- [ ] 2.3 Change `uv sync` to `uv sync --frozen` to prevent lockfile modification in CI
- [ ] 2.4 Add lockfile validation step after sync to detect any unexpected modifications
- [ ] 2.5 Add Ruff linting step: `uv run ruff check .` before tests
- [ ] 2.6 Add Ruff format check: `uv run ruff format --check .` (or decide to rely on Black only)
- [ ] 2.7 Add concurrency group to cancel outdated runs: `concurrency: group: ${{ github.workflow }}-${{ github.ref }}`

## 3. CI Workflow - Package Job Refactor
- [ ] 3.1 Replace manual venv + pip install with uv-based testing workflow
- [ ] 3.2 Test wheel installation: `uv init test-wheel-install && cd test-wheel-install && uv add ../dist/*.whl && uv run python -c "import ariadne_roots; ..."`
- [ ] 3.3 Test sdist installation with dev extras using uv: `uv add ../dist/*.tar.gz --extra dev`
- [ ] 3.4 Verify CLI tool works: `uv run ariadne-trace --help` (or similar smoke test if available)
- [ ] 3.5 Clean up shell script complexity (use uv's cross-platform compatibility instead of bash conditionals)

## 4. Quality Check Configuration
- [ ] 4.1 Verify Ruff configuration in pyproject.toml is appropriate for CI enforcement
- [ ] 4.2 Decide on Ruff vs Black for formatting (keep both, or migrate fully to Ruff format)
- [ ] 4.3 Add ruff configuration for maximum line length consistency with Black (88 chars)
- [ ] 4.4 Test that `uv run ruff check .` passes locally before CI changes

## 5. Coverage Threshold Handling
- [ ] 5.1 Document that coverage threshold (80%) will fail until comprehensive tests are added
- [ ] 5.2 Decision: Either lower threshold temporarily OR implement tests first
- [ ] 5.3 Add comment in workflow explaining coverage threshold and dependency on test coverage change
- [ ] 5.4 Coordinate with `add-comprehensive-test-coverage` change for sequencing

## 6. Documentation Updates
- [ ] 6.1 Update README.md developer section to emphasize `uv sync` workflow (not pip install)
- [ ] 6.2 Add inline comments in workflow file explaining uv patterns (--frozen, cache-dependency-glob)
- [ ] 6.3 Document Python version requirements (.python-version file purpose)
- [ ] 6.4 Update contributing guide if exists to mention lockfile workflow

## 7. Security and Dependency Management
- [ ] 7.1 Document approach for dependency vulnerability scanning (uv lacks built-in tool)
- [ ] 7.2 Add note in README about running `pip-audit` or similar tools manually
- [ ] 7.3 Consider adding GitHub Dependabot configuration for automated dependency updates

## 8. Testing and Validation
- [ ] 8.1 Test workflow changes locally with `act` (GitHub Actions local runner) if available
- [ ] 8.2 Push to feature branch and verify CI passes on all platforms (Ubuntu, Windows, macOS)
- [ ] 8.3 Verify cache reuse works correctly (check CI logs for cache hits)
- [ ] 8.4 Verify lockfile is not modified in CI (validation step should pass)
- [ ] 8.5 Verify Ruff linting catches intentional code quality issues (negative test)
- [ ] 8.6 Verify package installation tests work with built artifacts on all platforms