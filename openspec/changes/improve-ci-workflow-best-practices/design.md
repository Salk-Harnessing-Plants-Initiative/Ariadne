# CI Workflow Best Practices Design

## Context

Ariadne's CI workflow was recently updated (commit a69cf33) to use uv for dependency management, replacing the previous conda/pip-based approach. This was a significant improvement, but the migration is incomplete and missing several modern best practices for uv-based CI/CD.

Current state:
- uv is properly installed and configured in CI (astral-sh/setup-uv@v5)
- Dependency resolution works (`uv lock` + `uv sync`)
- Tests run with coverage enforcement (80% threshold)
- Package building and installation testing exists
- Cross-platform testing (Ubuntu, Windows, macOS) with Python 3.12 and 3.13

Gaps:
- Lockfile not committed → non-reproducible builds
- `uv lock` runs on every CI build → unnecessary computation
- No linting enforcement despite Ruff configuration
- Package testing uses legacy pip instead of uv workflow
- No Python version pinning for local dev consistency
- Missing modern CI optimizations (concurrency controls, cache tuning)

## Goals / Non-Goals

**Goals:**
- Achieve reproducible builds across local development and CI environments
- Enforce code quality standards (linting, formatting) automatically in CI
- Test the actual user installation experience (uv-based workflow)
- Optimize CI performance (faster runs, better caching)
- Align with uv project management best practices (not legacy pip patterns)
- Maintain cross-platform compatibility (Linux, Windows, macOS)

**Non-Goals:**
- Type checking with mypy/pyright (can be added later, not required now)
- Dependency vulnerability scanning automation (document approach, don't implement)
- Performance benchmarking or profiling in CI
- Integration testing beyond smoke tests (out of scope)
- Changing the build backend (setuptools is fine for now)

## Decisions

### 1. Commit uv.lock for Reproducible Builds

**Decision:** Commit `uv.lock` to the repository and use `uv sync --frozen` in CI.

**Rationale:**
- **Reproducibility**: Lockfile ensures identical dependency versions across all environments (local dev, CI, production)
- **Speed**: CI skips dependency resolution (just reads lockfile), saving 5-10 seconds per run
- **Reliability**: Eliminates "works on my machine" issues caused by dependency drift
- **uv best practice**: Official uv documentation recommends committing lockfile for libraries and applications

**Implementation:**
- Create/update `uv.lock` locally with `uv lock`
- Commit lockfile to repo (ensure not gitignored)
- Change CI command from `uv sync` to `uv sync --frozen`
- Add validation step to detect unexpected lockfile modifications

**Alternatives considered:**
- **Generate lockfile in CI**: Current approach, but wastes compute and causes drift
- **Use requirements.txt**: Legacy approach, uv.lock is superior (platform-specific resolution, faster, more reliable)

### 2. Python Version Pinning with .python-version

**Decision:** Create `.python-version` file with single Python version (e.g., `3.12`) for local development consistency.

**Rationale:**
- **uv auto-detection**: uv automatically uses Python version from `.python-version` file
- **Developer consistency**: All developers use same Python version by default
- **Clear documentation**: Version pinning is self-documenting in repo root
- **CI alignment**: Local dev environment matches CI matrix (developers test what CI tests)

**Version choice:** Use `3.12` (latest stable supported in CI matrix, balances modern features with compatibility)

**Implementation:**
```bash
echo "3.12" > .python-version
git add .python-version
```

**Note:** CI still tests multiple Python versions (3.12, 3.13) via matrix, but local dev defaults to 3.12.

### 3. Ruff for Linting (Complement to Black)

**Decision:** Add `uv run ruff check .` to CI, keep Black for formatting.

**Rationale:**
- **Existing configuration**: Ruff is already configured in pyproject.toml (enforce docstrings)
- **Fast**: Ruff is 10-100x faster than traditional linters (flake8, pylint)
- **Comprehensive**: Catches code quality issues, not just formatting
- **Non-overlapping**: Ruff linting + Black formatting are complementary
- **Already installed**: Ruff is in dev dependencies, no new tooling overhead

**Configuration strategy:**
- Ruff checks code quality (unused imports, undefined names, docstring presence)
- Black checks formatting (line length, quote style, trailing commas)
- Both fail CI on violations (zero tolerance for quality issues)

**Alternatives considered:**
- **Replace Black with Ruff format**: Possible, but Black is established and working fine
- **Add mypy/pyright**: Defer to future (type checking is more invasive, requires annotations)
- **No linting**: Unacceptable for scientific code (quality and documentation are critical)

### 4. uv-Based Package Testing (Not pip)

**Decision:** Replace `pip install dist/*.whl` with proper uv workflow testing in package job.

**Rationale:**
- **Test real user experience**: Users will install with `uv add ariadne-roots`, not pip
- **Modern Python tooling**: pip is legacy, uv is the future (faster, more reliable)
- **Cross-platform consistency**: uv handles platform differences better than bash scripts
- **Simplicity**: Fewer manual venv activation steps, cleaner scripts

**Implementation approach:**
```yaml
- name: Test wheel installation with uv
  run: |
    uv init test-install
    cd test-install
    uv add ../dist/ariadne_roots-*.whl
    uv run python -c "import ariadne_roots; print(ariadne_roots.__version__)"

- name: Test sdist with dev extras
  run: |
    uv init test-sdist
    cd test-sdist
    uv add ../dist/ariadne-roots-*.tar.gz --extra dev
    uv run black --version  # verify dev tools installed
```

**Alternatives considered:**
- **Keep pip testing**: Doesn't test actual uv workflow, misses uv-specific issues
- **Test both pip and uv**: Redundant, uv is sufficient (and what we recommend to users)
- **Use uvx for CLI testing**: Could work, but `uv run` is more standard

### 5. Coverage Threshold Sequencing

**Decision:** Keep 80% threshold in workflow, but document dependency on comprehensive test coverage change.

**Rationale:**
- **Correctness**: Threshold reflects actual target (80% coverage for scientific code)
- **Transparency**: CI failure makes lack of tests visible (motivates completion)
- **Clean separation**: CI workflow change is independent of test implementation
- **No technical debt**: Don't lower threshold temporarily (creates forgotten work)

**Sequencing strategy:**
1. This change (`improve-ci-workflow-best-practices`) updates CI configuration
2. Tests are added via `add-comprehensive-test-coverage` change
3. CI passes once tests achieve 80% coverage

**Alternative considered:**
- **Lower threshold temporarily**: Creates risk of forgetting to raise it later, introduces inconsistency

### 6. Concurrency Controls for CI Efficiency

**Decision:** Add concurrency group to cancel outdated CI runs on force-push.

**Rationale:**
- **Resource efficiency**: Don't waste CI minutes on superseded commits
- **Faster feedback**: Focus compute on latest code, not stale pushes
- **Standard practice**: Most modern repos use this pattern

**Implementation:**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Scope:** Only cancel in-progress runs for same branch (don't interfere with other branches)

## Risks / Trade-offs

### Risk: Lockfile Merge Conflicts
**Risk:** Multiple developers updating dependencies simultaneously causes lockfile conflicts
**Mitigation:**
- Lockfile merges are usually clean (uv handles deterministic ordering)
- If conflict occurs: regenerate locally with `uv lock`, test, commit
- Educate team: update lockfile in separate commits, not mixed with feature work

### Risk: Python Version Pinning Limits Testing
**Risk:** Developers only test on pinned version (3.12), miss version-specific bugs
**Mitigation:**
- CI still tests multiple versions (3.12, 3.13) - version-specific bugs are caught
- `.python-version` is a default, developers can override with `uv run --python 3.13`
- Document in README: "CI tests multiple versions, local dev uses 3.12 by default"

### Trade-off: Ruff + Black Overlap
**Trade-off:** Some formatting rules overlap between Ruff and Black
**Acceptance:**
- Overlap is minimal (mostly compatible)
- Black is authoritative for formatting (Ruff defers to Black's style)
- Future: Could migrate fully to Ruff format, but not urgent

### Trade-off: uv-Only Package Testing
**Trade-off:** Don't test pip installation workflow (some users might still use pip)
**Acceptance:**
- README recommends uv (primary supported workflow)
- PyPI packages work with pip anyway (uv generates standard wheels)
- Testing pip explicitly is redundant (wheel format is pip-compatible by design)

## Migration Plan

### Phase 1: Lockfile and Version Pinning (Tasks 1.1-1.5)
1. Create `.python-version` with `3.12`
2. Regenerate lockfile with `uv lock`
3. Commit both files
4. Test locally that `uv sync --frozen` works
5. **No CI changes yet** (deferred to Phase 2)

### Phase 2: CI Quality Checks (Tasks 2.1-2.7, 4.1-4.4)
1. Update workflow to use `uv sync --frozen`
2. Remove `uv lock` step
3. Add Ruff linting step before tests
4. Add concurrency controls
5. Update cache configuration
6. **Dependencies**: Requires Phase 1 completed (lockfile committed)

### Phase 3: Package Testing Refactor (Tasks 3.1-3.5)
1. Replace pip-based wheel testing with uv workflow
2. Replace pip-based sdist testing with uv workflow
3. Simplify cross-platform scripts (remove bash conditionals)
4. **Dependencies**: None (independent of Phase 1-2)

### Phase 4: Documentation and Finalization (Tasks 6.1-6.4, 7.1-7.3, 8.1-8.6)
1. Update README.md with uv workflow emphasis
2. Add inline workflow comments
3. Document security scanning approach
4. Test on all platforms
5. **Dependencies**: Requires Phase 1-3 completed

### Rollback Strategy
- **Phase 1 rollback**: Delete `.python-version` and uv.lock, regenerate in CI (revert to old approach)
- **Phase 2 rollback**: Revert workflow file changes (git revert)
- **Phase 3 rollback**: Revert package testing changes (git revert)
- **No data loss risk**: All changes are configuration/workflow (no code changes)

## Open Questions

1. **Ruff format vs Black**: Should we migrate fully to `ruff format` (drop Black)? Or keep both?
   - **Recommendation**: Keep both for now (Black is working, migration is low priority)

2. **Type checking timeline**: When should we add mypy/pyright to CI?
   - **Recommendation**: Defer until codebase has significant type annotations (not urgent)

3. **Dependency vulnerability scanning tool**: Which tool should we recommend?
   - **Options**: pip-audit, safety, snyk, GitHub Dependabot
   - **Recommendation**: Document pip-audit in README, don't automate yet (manual quarterly scans)

4. **Python 3.13 as default**: Should `.python-version` use 3.13 instead of 3.12?
   - **Consideration**: 3.13 is newer, but 3.12 is more widely adopted
   - **Recommendation**: Use 3.12 (balance modernity with stability)

5. **Coverage threshold adjustment**: Lower to 70% temporarily while tests are added?
   - **Recommendation**: Keep at 80%, document CI will fail until tests are complete

**Resolution approach:** Address questions 1-2 in future changes. Questions 3-5 should be decided before implementation (clarify with team).