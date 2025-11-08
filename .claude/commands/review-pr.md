---
description: Systematic PR review workflow
---

# Review Pull Request

Systematic workflow for reviewing PRs and responding to comments.

## Quick Review Commands

```bash
# List open PRs
gh pr list

# View specific PR
gh pr view <number>

# View PR diff
gh pr diff <number>

# Checkout PR locally
gh pr checkout <number>

# View PR checks
gh pr checks <number>

# Add review comment
gh pr review <number> --comment --body "Great work!"

# Approve PR
gh pr review <number> --approve

# Request changes
gh pr review <number> --request-changes --body "Please address..."
```

## Review Checklist

### 1. Code Quality

- [ ] Code follows PEP 8 conventions
- [ ] Functions have clear, single responsibilities
- [ ] Variable/function names are descriptive (full words, not abbreviations)
- [ ] No commented-out code or debug statements
- [ ] Error handling is appropriate
- [ ] No hardcoded values that should be configurable

### 2. Type Safety & Documentation

- [ ] Type hints used where helpful
- [ ] Google-style docstrings on all public functions
- [ ] Complex algorithms have explanatory comments
- [ ] Docstrings explain "why" not just "what"

### 3. Testing

- [ ] New features have test coverage
- [ ] Tests are clear and descriptive
- [ ] Edge cases are tested
- [ ] Integration test passes (if modifying analysis algorithms)
- [ ] Coverage meets 90% threshold

### 4. Scientific Accuracy (if applicable)

- [ ] Algorithm references credible sources (papers, textbooks)
- [ ] Pareto optimization calculations are correct
- [ ] Graph analysis preserves mathematical properties
- [ ] Integration test validates against real root data
- [ ] Results are reproducible across platforms

### 5. Package Structure

- [ ] Changes are in the correct module
- [ ] Dependencies are properly declared in pyproject.toml
- [ ] No circular imports introduced
- [ ] Source layout (src/ariadne_roots/) maintained

## Review Workflow

### As a Reviewer

1. **Read the PR description** - Understand the purpose and scope
2. **Check CI status** - Don't review if CI is failing
3. **Review diff file by file** - Start with test files to understand intent
4. **Test locally** - Checkout the branch and run tests
5. **Leave specific comments** - Reference line numbers and suggest alternatives
6. **Approve or request changes** - Be clear and constructive

### As a PR Author

1. **Address all comments** - Don't ignore any feedback
2. **Respond to each comment** - Explain your reasoning or agree to change
3. **Push fixes** - Make requested changes in new commits
4. **Mark resolved** - Resolve conversations after addressing them
5. **Request re-review** - Notify reviewers when ready

## Example Review Comments

### Good Comments

```markdown
**Line 42**: Consider using `Dict[int, List[float]]` type hint for better clarity
on what this function returns.

**Line 87**: This Pareto calculation looks incorrect. According to the design doc,
alpha should weight wiring cost, but here it's weighting delay. Should this be
`alpha * wiring + (1 - alpha) * delay`?

**test_quantify.py**: Excellent test coverage! Could you add a test case for
graphs with no lateral roots to ensure the edge case is handled?

**General**: Great work on the gravitropic angle implementation! The code is
clean and well-tested. Just a few minor suggestions above.
```

### Less Helpful Comments

```markdown
This doesn't look right. ❌
Why did you do it this way? ❌
Use type hints. ❌
```

## Common Review Patterns

### Pattern 1: Algorithm Changes

When reviewing changes to Pareto or graph analysis:

1. **Check algorithm source** - Verify it matches cited reference
2. **Review mathematical correctness** - Check formulas and edge cases
3. **Validate with integration test** - Ensure real root data still works
4. **Check reproducibility** - Results should match across platforms

### Pattern 2: Test Coverage

When reviewing test changes:

1. **Check coverage** - Run `uv run pytest --cov` locally
2. **Review test fixtures** - Ensure they represent realistic scenarios
3. **Validate assertions** - Check that tests actually verify behavior
4. **Check integration test** - Ensure plantB_day11 fixture still validates

### Pattern 3: Performance Changes

When reviewing performance optimizations:

1. **Benchmark** - Measure actual performance impact
2. **Check accuracy** - Ensure optimization doesn't reduce precision
3. **Review complexity** - Document Big-O if relevant
4. **Test edge cases** - Large graphs, empty graphs, pathological cases

## GitHub CLI Review Examples

```bash
# Start a review
gh pr review 42 --comment --body "Starting review..."

# Approve with message
gh pr review 42 --approve --body "LGTM! Excellent test coverage on the Pareto calculations."

# Request changes
gh pr review 42 --request-changes --body "Please address the comments about algorithm correctness in pareto_functions.py"

# View review comments
gh pr view 42 --comments
```

## Responding to Review Comments

```bash
# View PR with comments
gh pr view 42 --comments

# Checkout PR to make fixes
gh pr checkout 42

# Make changes, commit, push
git add .
git commit -m "fix: address review comments on type hints"
git push

# Notify reviewer
gh pr comment 42 --body "✅ Addressed all review comments. Ready for re-review!"
```

## When to Request Changes vs Comment

- **Request Changes**: Test failures, incorrect algorithms, missing tests, broken functionality
- **Comment**: Style suggestions, performance optimizations, nice-to-haves, questions

## Tips for Effective Reviews

1. **Be timely** - Review within 24-48 hours if possible
2. **Be specific** - Reference line numbers and suggest concrete alternatives
3. **Be kind** - Assume positive intent, use constructive language
4. **Test locally** - Don't just read code, run it
5. **Focus on substance** - Don't nitpick style (that's what Black/Ruff are for)
6. **Explain why** - Help the author learn, don't just point out issues
7. **Approve quickly** - If it's good, say so and approve