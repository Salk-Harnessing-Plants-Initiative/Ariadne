---
description: Guide through complete release process for ariadne-roots package
---

# Release Process for ariadne-roots

Comprehensive workflow for releasing a new version of the Ariadne package to PyPI.

## Purpose

This command guides you through the complete release process, ensuring:

1. All pre-release checks pass (tests, coverage, linting, CI)
2. Version is bumped correctly following semantic versioning
3. Changes are documented and committed properly
4. GitHub release is created with appropriate notes
5. Package is published to PyPI automatically
6. Release is verified and documented

## Prerequisites

Before starting a release, ensure:

- You are on the `main` branch with latest changes
- All PRs intended for this release are merged
- CI is passing on main branch
- You have maintainer permissions for the repository
- `gh` CLI is authenticated

## Usage

```bash
# Interactive release workflow
/release

# Or specify version type
/release patch   # 0.0.3 → 0.0.4
/release minor   # 0.0.3 → 0.1.0
/release major   # 0.0.3 → 1.0.0
```

## Release Workflow

### Step 1: Pre-Release Validation

Verify the project is ready for release using the validation commands:

```bash
# Check we're on main branch
git branch --show-current  # Should be 'main'

# Ensure working directory is clean
git status

# Pull latest changes
git pull origin main

# Verify CI is passing on main
gh run list --branch main --limit 5
```

**Run validation commands** (see respective commands for details):

```bash
# Run full test suite (see /test command)
uv run pytest

# Run with coverage (see /coverage command)
uv run pytest --cov=ariadne_roots --cov-report=term-missing --cov-fail-under=90

# Run linting checks (see /lint command)
uv run black --check .
uv run ruff check .
```

**Build and validate package:**

```bash
# Build and verify package metadata
uv build
uvx twine check dist/*

# Security audit
uvx pip-audit
```

**Stop if any checks fail.** Fix issues before proceeding.

**Tip**: Use `/test`, `/coverage`, and `/lint` commands for detailed guidance on these checks.

### Step 2: Determine Version Number and Update Changelog

Follow semantic versioning (https://semver.org):

**MAJOR.MINOR.PATCH** (e.g., 0.0.3)

- **PATCH** (0.0.3 → 0.0.4): Bug fixes, documentation updates, minor improvements
- **MINOR** (0.0.3 → 0.1.0): New features, backward-compatible changes
- **MAJOR** (0.0.3 → 1.0.0): Breaking changes, incompatible API changes

Current version: Read from pyproject.toml line 7

**Review changes and update CHANGELOG.md** (see `/changelog` command for details):

```bash
# Review changes since last release
LAST_TAG=$(gh release list --limit 1 --json tagName --jq '.[0].tagName')
echo "Last release: $LAST_TAG"
git log $LAST_TAG..HEAD --oneline --no-merges
```

**Update CHANGELOG.md**:
1. Move items from `[Unreleased]` section to new versioned section
2. Add today's date in YYYY-MM-DD format
3. Update comparison links at bottom
4. Save and commit with version bump

**Tip**: Use `/changelog` command for Keep a Changelog format guidelines.

**Decision Matrix:**

- New scaling features (PR #33)? → MINOR bump
- Just bug fixes? → PATCH bump
- Breaking API changes? → MAJOR bump

### Step 3: Create Release Branch

```bash
# Determine new version
CURRENT_VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "Current version: $CURRENT_VERSION"

# Get new version (example: 0.0.4 for patch bump)
NEW_VERSION="0.0.4"  # Replace based on Step 2 decision

# Create release branch
git checkout -b release/v$NEW_VERSION
```

### Step 4: Update Version Number

Edit `pyproject.toml` line 7:

```toml
version = "0.0.4"  # Update this line
```

### Step 5: Update Documentation (if needed)

Check if README or other docs need updates:

- Installation instructions
- Version-specific examples
- Breaking changes documentation
- Migration guides (for MAJOR versions)

### Step 6: Build and Test Release Artifacts

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build new distribution
uv build

# Verify build artifacts
ls -lh dist/
# Should see: ariadne_roots-0.0.4-py3-none-any.whl
#             ariadne_roots-0.0.4.tar.gz

# Validate package metadata
uvx twine check dist/*

# Test wheel installation in clean environment
mkdir -p /tmp/test-release-$NEW_VERSION
cd /tmp/test-release-$NEW_VERSION
uv init --no-readme --no-workspace test-install
cd test-install
uv add /Users/elizabethberrigan/repos/Ariadne/dist/ariadne_roots-$NEW_VERSION-py3-none-any.whl
uv run python -c "import ariadne_roots; print('Import successful')"
uv run ariadne-trace --help || echo "CLI test complete"

# Return to repo
cd /Users/elizabethberrigan/repos/Ariadne
```

### Step 7: Commit Version Bump and Changelog

```bash
# Stage changes (version and changelog)
git add pyproject.toml CHANGELOG.md

# Commit with standard message format
git commit -m "chore: bump version to v$NEW_VERSION

- Update version in pyproject.toml
- Update CHANGELOG.md with release notes"

# Push release branch
git push origin release/v$NEW_VERSION
```

### Step 8: Create and Merge Version Bump PR

**Tip**: Use `/pr-description` command for the full PR template.

```bash
# Create PR with detailed description
gh pr create \
  --title "Release v$NEW_VERSION" \
  --body "$(cat <<EOF
## Release v$NEW_VERSION

### Version Bump
- Bumps version from $CURRENT_VERSION to $NEW_VERSION

### Changes Since Last Release
$(git log v$CURRENT_VERSION..HEAD --oneline --no-merges | head -20)

### Pre-Release Checklist
- [x] All tests pass locally
- [x] Coverage meets 90% threshold
- [x] Linting checks pass
- [x] Build artifacts verified with twine
- [x] Security audit clean (pip-audit)
- [x] Package installs correctly from wheel
- [x] CI passing on main branch
- [x] CHANGELOG.md updated

### Release Type
- [ ] PATCH - Bug fixes and minor improvements
- [ ] MINOR - New features, backward-compatible
- [ ] MAJOR - Breaking changes

### Post-Merge Steps
1. Create GitHub release with tag v$NEW_VERSION
2. Verify PyPI upload via GitHub Actions
3. Test installation from PyPI
4. Announce release

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"

# Wait for review and CI checks
gh pr checks --watch

# After approval, merge (or request review first)
echo "Request review from maintainers, then merge when approved"
gh pr merge --squash --delete-branch
```

### Step 9: Create GitHub Release

After PR is merged to main:

```bash
# Switch to main and pull
git checkout main
git pull origin main

# Create GitHub release (this triggers PyPI upload)
gh release create v$NEW_VERSION \
  --title "ariadne-roots v$NEW_VERSION" \
  --generate-notes \
  --notes "$(cat <<EOF
## Installation

\`\`\`bash
pip install ariadne-roots==$NEW_VERSION
\`\`\`

Or with uv:

\`\`\`bash
uvx ariadne-trace
# or
uv add ariadne-roots
\`\`\`

## What's Changed

$(gh pr list --search "is:merged is:pr merged:>$(date -v-30d +%Y-%m-%d)" --limit 10 --json title,number --jq '.[] | "- #\(.number): \(.title)"')

**Full Changelog**: https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/compare/v$CURRENT_VERSION...v$NEW_VERSION

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

The GitHub Actions workflow `.github/workflows/python-publish.yml` will automatically:
1. Build the wheel
2. Run twine check
3. Upload to PyPI using stored token

### Step 10: Verify Release

Monitor the release process:

```bash
# Watch GitHub Actions workflow
gh run watch

# Once complete, verify PyPI upload (wait 1-2 minutes)
echo "Checking PyPI..."
sleep 60
curl -s https://pypi.org/pypi/ariadne-roots/json | \
  jq -r '.releases | keys | .[]' | grep $NEW_VERSION

# Test installation from PyPI
mkdir -p /tmp/verify-pypi-$NEW_VERSION
cd /tmp/verify-pypi-$NEW_VERSION
uv init --no-readme --no-workspace verify-install
cd verify-install
uv add ariadne-roots==$NEW_VERSION
uv run python -c "import ariadne_roots; print(f'Successfully installed from PyPI')"

# Return to repo
cd /Users/elizabethberrigan/repos/Ariadne
```

### Step 11: Post-Release Tasks

```bash
# Update any version badges or links if needed
# Announce release in relevant channels
# Close any resolved issues
# Update project board if used

echo "✅ Release v$NEW_VERSION complete!"
echo "📦 PyPI: https://pypi.org/project/ariadne-roots/$NEW_VERSION/"
echo "🐙 GitHub: https://github.com/Salk-Harnessing-Plants-Initiative/Ariadne/releases/tag/v$NEW_VERSION"
```

## Rollback Procedures

### If Release Fails Before PyPI Upload

```bash
# Delete GitHub release
gh release delete v$NEW_VERSION --yes

# Delete tag
git tag -d v$NEW_VERSION
git push origin :refs/tags/v$NEW_VERSION

# Revert version bump on main
git revert HEAD
git push origin main
```

### If Release Fails After PyPI Upload

**Note:** You cannot delete releases from PyPI, only "yank" them.

```bash
# Yank the bad release (makes it unavailable for new installs)
uvx twine yank ariadne-roots -v $NEW_VERSION -r pypi

# Release a patch version with fixes
# Follow normal release process with incremented version
```

### If Package is Broken on PyPI

```bash
# Immediately yank the broken version
uvx twine yank ariadne-roots -v $NEW_VERSION -r pypi \
  --reason "Critical bug in version $NEW_VERSION, use $NEXT_VERSION instead"

# Fix issues and release patch version ASAP
# Document the issue in GitHub release notes
```

## Safety Checks and Validation

### Critical Validations

Before each release, verify:

1. **Test Coverage**: Minimum 90% coverage required
   ```bash
   uv run pytest --cov=ariadne_roots --cov-fail-under=90
   ```

2. **All Tests Pass**: No failures across all platforms
   ```bash
   gh run list --branch main --workflow=CI --limit 1 --json conclusion --jq '.[0].conclusion'
   # Should output: "success"
   ```

3. **No Security Issues**: Clean pip-audit scan
   ```bash
   uvx pip-audit
   ```

4. **Package Builds**: Wheel and sdist build successfully
   ```bash
   uv build && uvx twine check dist/*
   ```

5. **Clean Working Tree**: No uncommitted changes
   ```bash
   git status --porcelain
   # Should be empty
   ```

### Release Checklist

Copy this checklist for each release:

```
## Release v{VERSION} Checklist

### Pre-Release
- [ ] All intended PRs merged to main
- [ ] CI passing on main branch
- [ ] Local tests pass with 90%+ coverage
- [ ] Linting checks pass (black, ruff)
- [ ] Security audit clean (pip-audit)
- [ ] Version number determined (MAJOR.MINOR.PATCH)
- [ ] CHANGELOG reviewed (git log since last release)
- [ ] CHANGELOG.md updated

### Version Bump
- [ ] Release branch created
- [ ] pyproject.toml updated with new version
- [ ] CHANGELOG.md updated with release date and version
- [ ] Documentation updated (if needed)
- [ ] Build artifacts tested locally
- [ ] Package installs from wheel successfully

### PR and Review
- [ ] Version bump PR created
- [ ] PR description includes changes since last release
- [ ] CI checks pass on PR
- [ ] Code review approved
- [ ] PR merged to main

### GitHub Release
- [ ] Switched to main branch
- [ ] Pulled latest changes
- [ ] GitHub release created with tag
- [ ] Release notes generated and reviewed
- [ ] Release published

### PyPI Verification
- [ ] GitHub Actions workflow completed successfully
- [ ] Package appears on PyPI
- [ ] Package version correct on PyPI
- [ ] Package installs from PyPI successfully
- [ ] CLI works: `uvx ariadne-trace`

### Post-Release
- [ ] Release announced (if applicable)
- [ ] Related issues closed
- [ ] Project board updated
- [ ] README badges updated (if needed)
```

## Versioning Examples

### Patch Release (0.0.3 → 0.0.4)

**When to use:**
- Bug fixes
- Documentation improvements
- Test additions
- Code refactoring without API changes
- Performance improvements (non-breaking)

**Example changes:**
- Fix calculation error in lateral root angle
- Update README installation instructions
- Add missing test cases
- Optimize graph traversal algorithm

### Minor Release (0.0.3 → 0.1.0)

**When to use:**
- New features
- New analysis capabilities
- Backward-compatible API additions
- Significant improvements

**Example changes:**
- Add scaling features (like PR #33)
- New trait calculations
- Enhanced GUI features
- Additional export formats

### Major Release (0.0.3 → 1.0.0)

**When to use:**
- Breaking API changes
- Incompatible file format changes
- Major architecture rewrites
- Removal of deprecated features

**Example changes:**
- Change JSON structure (breaks compatibility)
- Remove or rename public functions
- Change CLI interface
- Require new Python version

## Common Issues and Solutions

### Issue: CI Fails on Release PR

**Solution:**
```bash
# Pull latest changes from main
git checkout release/v$NEW_VERSION
git merge origin/main

# Fix any conflicts
# Run tests locally
uv run pytest

# Push updates
git push origin release/v$NEW_VERSION
```

### Issue: PyPI Upload Fails

**Solution:**
```bash
# Check GitHub Actions logs
gh run view --log-failed

# Common causes:
# 1. Version already exists on PyPI (increment version)
# 2. Token expired (update repository secret)
# 3. Package metadata invalid (check pyproject.toml)

# If metadata issue, fix and create new patch release
```

### Issue: Package Import Fails After Release

**Solution:**
```bash
# Test in clean environment
cd /tmp
uv init --no-readme test-debug
cd test-debug
uv add ariadne-roots==$NEW_VERSION
uv run python -c "import ariadne_roots; import ariadne_roots.pareto_functions"

# Check for:
# - Missing dependencies in pyproject.toml
# - Import errors in __init__.py
# - Missing package files in build

# If broken, yank release and issue patch
uvx twine yank ariadne-roots -v $NEW_VERSION -r pypi
```

### Issue: Version Mismatch Between Git and PyPI

**Prevention:**
```bash
# Always verify version in pyproject.toml matches tag
grep 'version = ' pyproject.toml
# Should output: version = "X.Y.Z"

# Tag should match: vX.Y.Z
git describe --tags
```

## Integration with Other Commands

### Before Releasing (Step 1: Pre-Release Validation)

```bash
/test              # Run full test suite with various options
/coverage          # Detailed coverage analysis (ensure 90%+)
/lint              # Check code style (Black + Ruff)
/pre-merge-check   # Comprehensive validation (if releasing from PR)
```

### During Release (Step 2: Changelog)

```bash
/changelog         # Update CHANGELOG.md with Keep a Changelog format
```

### Creating Version Bump PR (Step 8)

```bash
/pr-description    # Use comprehensive PR template
```

### After Merging (Step 9)

```bash
# Continue with GitHub release creation
# PyPI upload happens automatically via GitHub Actions
```

### Post-Release Cleanup

```bash
/cleanup-merged    # Clean up release branch after merge
```

## Example Release Session

```
User: /release minor

Claude: Starting release process for ariadne-roots
        Current version: 0.0.3
        Target version: 0.1.0 (minor bump)

Claude: Running pre-release checks...
        ✓ On main branch
        ✓ Working directory clean
        ✓ CI passing on main
        ✓ Tests pass with 98% coverage
        ✓ Linting checks pass
        ✓ Security audit clean

Claude: Changes since v0.0.3:
        - PR #33: Add scaling features for pixel-to-unit conversion
        - PR #30: Improve CI workflow with uv best practices
        [12 more commits]

Claude: This looks like a MINOR release (new features, backward-compatible)
        Proceeding with version 0.1.0

Claude: Creating release branch...
        [Creates branch, updates version, builds package]

Claude: Package built successfully. Creating version bump PR...
        PR #41: https://github.com/.../pull/41

Claude: Please review and merge PR #41. After merge, I'll create the GitHub release.

User: PR merged

Claude: Creating GitHub release v0.1.0...
        Release created: https://github.com/.../releases/tag/v0.1.0
        
        Monitoring PyPI upload... ⏳
        ✓ Package published to PyPI
        ✓ Installation verified

        Release v0.1.0 complete! 🎉
        PyPI: https://pypi.org/project/ariadne-roots/0.1.0/
```

## Best Practices

1. **Release Often**: Small, frequent releases are easier to manage than large ones
2. **Test Thoroughly**: Always run full test suite before releasing
3. **Document Changes**: Use git log and PR descriptions to generate release notes
4. **Verify Installation**: Test package installation from PyPI before announcing
5. **Communicate**: Announce releases to users and contributors
6. **Tag Consistently**: Always use `v` prefix for tags (v0.0.4)
7. **Never Force Push**: Release tags should be immutable
8. **Keep Changelog**: Maintain CHANGELOG.md using Keep a Changelog format

## Related Documentation

- [Semantic Versioning](https://semver.org)
- [PyPI Publishing](https://packaging.python.org/tutorials/packaging-projects/)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Keep a Changelog](https://keepachangelog.com/)
- Project README: Release section

## Related Commands

- `/test` - Run pytest with various options and filters
- `/coverage` - Run test coverage analysis with HTML reports
- `/lint` - Run code style checks (Black + Ruff)
- `/changelog` - Maintain CHANGELOG.md following Keep a Changelog format
- `/pr-description` - Template for creating comprehensive PRs
- `/review-pr` - Systematic PR review checklist
- `/pre-merge-check` - Comprehensive pre-merge validation
- `/cleanup-merged` - Clean up merged branch and archive OpenSpec changes
