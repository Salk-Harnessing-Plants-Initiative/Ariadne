# Modernize PyPI Publish Workflow

**Status**: 🟡 Proposed
**Created**: 2024-11-11
**Owner**: Elizabeth Berrigan
**Effort**: 30 minutes - 1 hour

## Problem Statement

The `.github/workflows/python-publish.yml` workflow still uses legacy pip-based tooling instead of the modern uv toolchain used everywhere else in the project.

**Current issues:**

1. **Inconsistent tooling**: Uses `pip install` and `python -m build` instead of `uv`
2. **Missing dependency management**: Doesn't use `uv.lock` for reproducible builds
3. **Legacy approach**: Uses `twine` via pip instead of `uvx twine`
4. **No pre-publish validation**: Missing checks that should run before PyPI upload
5. **Missing security checks**: No validation that published version matches git tag
6. **Incomplete testing**: Doesn't verify package installation before publishing

**Observed in CI workflow (`test-dev.yml`):**
- Uses `uv sync --frozen` for reproducible builds
- Validates lockfile hasn't changed
- Builds with `uv build`
- Checks metadata with `uvx twine check`
- Tests wheel and sdist installation
- Runs full test suite with coverage

**Observed in other workflows:**
- sleap-roots: Uses `uv build` and `uvx twine upload`
- cosmos-azul: Pre-publish validation with version checks
- Standard practice: Match CI build tools with publish tools

## Proposed Solution

Modernize the PyPI publish workflow to:

1. **Use uv toolchain** consistently with CI
2. **Add pre-publish validation** checks
3. **Verify version consistency** between git tag and package
4. **Test package installation** before publishing
5. **Use locked dependencies** for reproducible builds
6. **Add security checks** (pip-audit on built package)

### Updated Workflow Structure

```yaml
name: Build

on:
  release:
    types:
      - published

jobs:
  validate-release:
    name: Validate Release
    runs-on: ubuntu-22.04
    steps:
      - Checkout code
      - Set up uv
      - Verify git tag matches pyproject.toml version
      - Verify CHANGELOG.md is updated for this version
      - Run full test suite (ensure passing before publish)
      - Run coverage check (ensure 90%+ threshold)

  build-and-publish:
    name: Build and Publish to PyPI
    needs: validate-release
    runs-on: ubuntu-22.04
    steps:
      - Checkout code
      - Set up uv with lockfile caching
      - Install Python (match CI version: 3.12)
      - Build package with `uv build`
      - Validate metadata with `uvx twine check`
      - Test wheel installation
      - Security audit with `uvx pip-audit`
      - Upload to PyPI with `uvx twine upload`
      - Verify package on PyPI (post-upload check)
```

## Success Criteria

1. Publish workflow uses `uv` toolchain exclusively
2. Pre-publish validation catches common issues (version mismatch, missing tests)
3. Package is tested before publishing
4. Security audit runs on built package
5. Version consistency enforced (git tag = pyproject.toml = CHANGELOG.md)
6. Build is reproducible (uses lockfile)
7. Workflow succeeds for v0.1.0a1 pre-release

## Implementation Plan

See [tasks.md](tasks.md) for detailed breakdown.

**Estimated effort**: 30 minutes - 1 hour

## Design Decisions

### 1. Split Into Two Jobs

**Decision**: Use `validate-release` job before `build-and-publish`

**Rationale**:
- Fail fast if version mismatch or tests fail
- Separates validation logic from build logic
- Clearer failure messages (know which stage failed)
- Follows CI best practices (validate → build → deploy)

### 2. Version Consistency Checks

**Include checks for**:
- Git tag (e.g., `v0.1.0`) matches `pyproject.toml` version (`0.1.0`)
- CHANGELOG.md has entry for this version
- No uncommitted changes (workflow triggers on published release, should be clean)

**Rationale**:
- Catches manual release process errors
- Ensures documentation is up-to-date
- Prevents accidental version mismatches on PyPI

### 3. Pre-Publish Testing

**Include**:
- Full test suite (same as CI)
- Coverage check (90%+ threshold)
- Wheel installation test
- Security audit with `pip-audit`

**Rationale**:
- CI passing ≠ tests passing on release tag (could be stale)
- Ensures we're publishing working code
- Security audit catches known vulnerabilities in dependencies
- Wheel test catches packaging issues

### 4. Use Locked Dependencies

**Decision**: Use `uv sync --frozen` for build environment

**Rationale**:
- Reproducible builds (same environment as CI)
- Prevents surprise dependency changes during release
- Matches CI workflow approach
- Build tooling versions are pinned

### 5. Python Version Selection

**Decision**: Use Python 3.12 (matches CI and .python-version)

**Rationale**:
- Consistency with CI workflow
- Matches `.python-version` file
- Tested in CI matrix (3.12 and 3.13)
- 3.12 is current stable

### 6. Security Audit Placement

**Decision**: Run `pip-audit` on built package before upload

**Rationale**:
- Catches vulnerabilities in dependencies bundled with package
- Fails before publishing to PyPI (not after)
- Audit only affects this specific package build
- Documentation in README.md recommends `pip-audit`

## Out of Scope

- Automatic version bumping (handled manually with `/release` command)
- Automated changelog generation (handled manually with `/changelog` command)
- Publishing to TestPyPI (can be added later if needed)
- Package signing (can be added later if needed)
- Multi-platform wheel builds (pure Python package, not needed)
- Conda package publishing (PyPI only for now)

## Non-Goals

- Change the release trigger (still on `release: published`)
- Modify package metadata or versioning scheme
- Change PyPI credentials handling
- Add automated release creation (handled manually)

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Workflow fails on first real release | Medium | High | Test with v0.1.0a1 pre-release first |
| Version check too strict (false positives) | Low | Medium | Use clear regex matching, handle pre-release suffixes |
| Security audit blocks valid release | Low | High | Allow `pip-audit` to be informational (continue-on-error) initially |
| Lockfile drift causes build issues | Low | Medium | Validate lockfile in CI, same as test workflow |

## Alternatives Considered

### Alternative 1: Keep pip-based workflow

**Pros**: No changes needed, currently working
**Cons**: Inconsistent with rest of project, missing modern tooling benefits
**Decision**: Rejected - should use uv everywhere

### Alternative 2: Minimal changes (just swap pip → uv)

**Pros**: Quick, low risk
**Cons**: Misses opportunity to add validation checks
**Decision**: Rejected - add validation while we're modernizing

### Alternative 3: Use PyPI Trusted Publishers (OIDC)

**Pros**: More secure than API tokens
**Cons**: Requires PyPI project configuration changes
**Decision**: Deferred - can migrate later without workflow changes

## Dependencies

- Existing workflow: `.github/workflows/python-publish.yml`
- CI workflow: `.github/workflows/test-dev.yml` (reference for uv usage)
- Package configuration: `pyproject.toml` (version source)
- Changelog: `CHANGELOG.md` (version documentation)
- PyPI credentials: `secrets.EBERRIGAN_PYPI_TOKEN`

## Timeline

- **Analysis**: 15 minutes (understand current workflow and requirements)
- **Implementation**: 30 minutes (update workflow YAML)
- **Testing**: 15 minutes (dry-run with v0.1.0a1 pre-release)
- **Documentation**: Included in implementation

**Total**: 30 minutes - 1 hour

## Acceptance Criteria

- [ ] Workflow uses `uv` toolchain exclusively (no pip, no python -m build)
- [ ] Pre-publish validation job checks:
  - [ ] Git tag matches pyproject.toml version
  - [ ] CHANGELOG.md has entry for version
  - [ ] Full test suite passes
  - [ ] Coverage meets 90% threshold
- [ ] Build job:
  - [ ] Uses `uv build` to create wheel and sdist
  - [ ] Validates metadata with `uvx twine check`
  - [ ] Tests wheel installation
  - [ ] Runs security audit with `uvx pip-audit`
  - [ ] Uploads to PyPI with `uvx twine upload`
- [ ] Workflow tested with v0.1.0a1 pre-release
- [ ] Documentation updated (if needed)

## Related Issues

- None currently, but follows from the uv migration in PR #30

## References

- Current publish workflow: `.github/workflows/python-publish.yml`
- CI workflow: `.github/workflows/test-dev.yml`
- uv documentation: https://docs.astral.sh/uv/
- PyPI publishing best practices: https://packaging.python.org/tutorials/packaging-projects/
- GitHub Actions security: https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions

## Questions for Review

1. Should `pip-audit` be blocking (fail) or informational (continue-on-error)?
   - **Recommendation**: Start with continue-on-error, make blocking after first successful release
2. Should we test pre-releases differently than stable releases?
   - **Recommendation**: Same validation for both, PyPI handles pre-release flag
3. Should we add TestPyPI upload for pre-releases?
   - **Recommendation**: Optional, can add later if useful for testing

## Implementation Notes

The validate-release job should:
1. Extract version from git tag (strip 'v' prefix)
2. Read version from pyproject.toml
3. Compare versions (handle pre-release suffixes like 'a1', 'b2', 'rc1')
4. Check CHANGELOG.md contains a heading with this version
5. Run same test suite as CI

The build-and-publish job should:
1. Depend on validate-release (needs: validate-release)
2. Use uv for all operations
3. Test wheel before uploading (catch issues early)
4. Upload with twine (same as current, but via uvx)
