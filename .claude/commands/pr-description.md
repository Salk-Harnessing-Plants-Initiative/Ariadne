---
description: Template for creating comprehensive PRs
---

# PR Description Template

Use this template when creating pull requests to ensure comprehensive documentation.

## Quick Commands

```bash
# View current PR
gh pr view

# View PR diff
gh pr diff

# List changed files
gh pr diff --name-only

# View specific file changes
gh pr diff <file-path>
```

## PR Description Template

```markdown
## Summary

[Brief 1-2 sentence description of what this PR does]

## Changes

- [Bullet point list of specific changes]
- [Group related changes together]
- [Use present tense: "Add X", "Fix Y", "Update Z"]

## Testing

- [ ] All existing tests pass (`uv run pytest`)
- [ ] Added new tests for new functionality
- [ ] Integration test passes (`test_analyze` with real root data)
- [ ] Coverage meets 90% threshold (`uv run pytest --cov`)

## Code Quality

- [ ] Black formatting applied (`uv run black .`)
- [ ] Ruff linting passes (`uv run ruff check .`)
- [ ] Google-style docstrings on all public functions

## Domain Accuracy (if applicable)

- [ ] Algorithm references credible sources
- [ ] Pareto calculations validated
- [ ] Graph analysis correctness verified
- [ ] Reproducibility ensured (same results across platforms)

## Breaking Changes

- [ ] No breaking changes
- [ ] Breaking changes documented below

[If breaking changes, describe migration path]

## Related Issues

Closes #[issue number]
Related to #[issue number]

## Reviewer Notes

[Specific areas you want reviewers to focus on]
[Any concerns or questions you have]
```

## Examples

### Feature PR Example

```markdown
## Summary

Add support for calculating lateral root emergence angles relative to gravity vector.

## Changes

- **src/ariadne_roots/quantify.py**: Add `calc_lr_gravitropic_angles()` function
- **tests/test_quantify.py**: Add 8 test cases for angle calculations
- **tests/fixtures.py**: Add `simple_angled_root_graph` fixture
- Update integration test to validate angles match expected values

## Testing

- [x] All existing tests pass
- [x] Added 8 new test cases for angle calculations
- [x] Integration test validates angles for all 24 lateral roots
- [x] Coverage: 98.5% (up from 98.33%)

## Domain Accuracy

- [x] Algorithm based on vector projection method from Voss et al. 2015
- [x] Validated angles match manual measurements within 0.5°
- [x] Tested with both upward and downward-growing roots
```

### Bug Fix PR Example

```markdown
## Summary

Fix Pareto front calculation returning duplicate points when costs are identical.

## Changes

- **src/ariadne_roots/pareto_functions.py**: Add deduplication in `pareto_front()`
- **tests/test_pareto_functions.py**: Add regression test for duplicate detection

## Testing

- [x] All tests pass
- [x] Added regression test that reproduces the bug
- [x] Integration test unaffected (no data changes)

## Related Issues

Closes #156
```

## GitHub CLI Tips

```bash
# Create PR with description from file
gh pr create --title "feat: add gravitropic angle calculation" --body-file pr-description.md

# Create PR interactively
gh pr create

# Add labels
gh pr edit --add-label "enhancement" --add-label "core-analysis"

# Request review
gh pr edit --add-reviewer @username

# Check CI status
gh pr checks
```

## Package Context

Ariadne is a single Python package for root system architecture analysis:

- **src/ariadne_roots/main.py**: GUI entry point (tkinter-based)
- **src/ariadne_roots/quantify.py**: Root trait calculations
- **src/ariadne_roots/pareto_functions.py**: Pareto optimization algorithms
- **tests/**: Unit and integration tests with real root data fixtures

When describing changes, specify which module is affected and whether it impacts:
- Core analysis algorithms (pareto_functions, quantify)
- GUI interface (main.py)
- Test fixtures or test infrastructure