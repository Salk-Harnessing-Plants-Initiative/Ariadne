# Tasks: Modernize PyPI Publish Workflow

## Overview

Update `.github/workflows/python-publish.yml` to use modern uv toolchain with pre-publish validation.

## Task Breakdown

### 1. Analysis and Planning (15 min)

- [x] Review current python-publish.yml workflow
- [x] Review test-dev.yml for uv usage patterns
- [x] Identify validation checks needed
- [x] Draft proposal document
- [ ] Review proposal with team

### 2. Implement Validate-Release Job (15 min)

- [x] Create `validate-release` job
  - [x] Set up uv with lockfile caching
  - [x] Extract version from git tag (GITHUB_REF_NAME)
  - [x] Read version from pyproject.toml
  - [x] Compare versions (handle pre-release suffixes)
  - [x] Verify CHANGELOG.md has entry for this version
  - [x] Run full test suite with coverage
  - [x] Ensure coverage meets 90% threshold

**Implementation notes:**
```yaml
validate-release:
  steps:
    - name: Extract version from tag
      run: |
        TAG_VERSION="${GITHUB_REF_NAME#v}"  # Strip 'v' prefix
        echo "TAG_VERSION=$TAG_VERSION" >> $GITHUB_ENV

    - name: Verify version matches pyproject.toml
      run: |
        TOML_VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
        if [ "$TAG_VERSION" != "$TOML_VERSION" ]; then
          echo "ERROR: Tag version ($TAG_VERSION) != pyproject.toml version ($TOML_VERSION)"
          exit 1
        fi

    - name: Verify CHANGELOG.md updated
      run: |
        if ! grep -q "## \[$TAG_VERSION\]" CHANGELOG.md; then
          echo "ERROR: CHANGELOG.md missing entry for version $TAG_VERSION"
          exit 1
        fi
```

### 3. Update Build-and-Publish Job (15 min)

- [x] Add `needs: validate-release` dependency
- [x] Replace pip setup with uv setup
  - [x] Use `astral-sh/setup-uv@v5` action
  - [x] Enable cache with lockfile dependency glob
  - [x] Install Python 3.12
- [x] Replace build steps
  - [x] Replace `pip install` with `uv sync --frozen`
  - [x] Replace `python -m build` with `uv build`
  - [x] Keep `uvx twine check dist/*` (already correct in spirit)
- [x] Add pre-upload validation
  - [x] Test wheel installation in clean environment
  - [x] Run security audit with `uvx pip-audit`
- [x] Update upload step
  - [x] Replace `twine upload` with `uvx twine upload`

**Implementation notes:**
```yaml
build-and-publish:
  needs: validate-release
  steps:
    - name: Set up uv
      uses: astral-sh/setup-uv@v5
      with:
        enable-cache: true
        github-token: ${{ secrets.GITHUB_TOKEN }}
        cache-dependency-glob: "**/uv.lock"

    - name: Install Python 3.12
      run: uv python install 3.12

    - name: Sync dependencies
      run: uv sync --frozen

    - name: Build package
      run: uv build

    - name: Check metadata
      run: uvx twine check dist/*

    - name: Test wheel installation
      run: |
        mkdir test-install && cd test-install
        uv init --no-readme --no-workspace test-project
        cd test-project
        uv add ../../dist/*.whl
        uv run python -c "import ariadne_roots; print('Install OK')"

    - name: Security audit
      run: uvx pip-audit
      continue-on-error: true  # Informational for now

    - name: Upload to PyPI
      env:
        PYPI_TOKEN: ${{ secrets.EBERRIGAN_PYPI_TOKEN }}
      run: |
        uvx twine upload -u __token__ -p "$PYPI_TOKEN" dist/* \
          --non-interactive --skip-existing --disable-progress-bar
```

### 4. Testing and Validation (15 min)

- [ ] Commit workflow changes
- [ ] Create v0.1.0a1 pre-release tag (if not exists)
- [ ] Trigger workflow with pre-release
- [ ] Verify validate-release job succeeds
- [ ] Verify build-and-publish job succeeds
- [ ] Verify package appears on PyPI
- [ ] Test installation from PyPI: `pip install ariadne-roots==0.1.0a1`

### 5. Documentation (Included in above)

- [ ] Add comments to workflow explaining each step
- [ ] Update workflow name if needed
- [ ] Ensure secret references are correct

## Success Criteria Checklist

- [ ] Workflow uses uv exclusively (no pip install, no python -m build)
- [ ] Version validation catches mismatches
- [ ] CHANGELOG validation catches missing entries
- [ ] Tests run before publish
- [ ] Wheel installation tested before upload
- [ ] Security audit runs (even if informational)
- [ ] Package publishes successfully to PyPI
- [ ] Post-publish installation works

## Estimated Time

- Analysis: 15 minutes (completed)
- Implementation: 30 minutes (validate job + build job)
- Testing: 15 minutes (dry-run with v0.1.0a1)
- **Total**: 1 hour

## Dependencies

- Git tag must follow `vX.Y.Z` format
- pyproject.toml version must match tag (without 'v' prefix)
- CHANGELOG.md must have entry for version
- uv.lock must be committed and up-to-date
- CI must be passing on release commit

## Rollback Plan

If the new workflow fails:
1. Revert workflow file to previous version
2. Re-trigger release with old workflow
3. Debug issue in separate PR
4. Re-attempt with fixed workflow

## Notes

- First real test will be v0.1.0a1 pre-release
- May need iteration based on first run
- Security audit set to continue-on-error initially (can make blocking later)
- Version extraction handles pre-release suffixes (a1, b2, rc1, etc.)
