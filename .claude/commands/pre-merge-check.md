---
description: Automated pre-merge review with GitHub Copilot feedback analysis
---

# Pre-Merge Check

Automated workflow for analyzing GitHub Copilot review comments and preparing PR for merge.

## Purpose

This command performs a comprehensive pre-merge check by:

1. Fetching all GitHub Copilot review comments from the PR
2. Using Planning mode to analyze and categorize issues
3. Prioritizing fixes by severity (CRITICAL → HIGH → MEDIUM → LOW)
4. Creating an actionable implementation plan
5. Identifying already-fixed issues vs new work needed

## Usage

```bash
# From a checked-out PR branch, run:
/pre-merge-check
```

## What This Command Does

### Step 1: Fetch Copilot Comments

Retrieve all review comments from GitHub Copilot on the current PR:

```bash
gh pr view --json number --jq .number | \
  xargs -I {} gh api repos/{owner}/{repo}/pulls/{}/comments
```

### Step 2: Planning Mode Analysis

Use the Task tool with subagent_type=Plan to:

- Review all Copilot comments
- Categorize by priority:
  - **CRITICAL**: Data consistency issues, security vulnerabilities, broken functionality
  - **HIGH**: Type safety violations, missing tests, significant bugs
  - **MEDIUM**: Code quality issues, performance concerns, style inconsistencies
  - **LOW**: Nice-to-haves, documentation improvements, minor refactoring
  - **NO ACTION**: Working as designed, false positives
- Identify already-fixed issues from previous commits
- Create phased implementation plan

### Step 3: Generate Action Plan

Output a prioritized task list with:

- Issue description and location (file:line)
- Priority level and reasoning
- Estimated effort
- Dependencies between fixes
- Implementation phases

### Step 4: Execution

Based on the analysis:

1. Implement CRITICAL and HIGH priority fixes immediately
2. Run tests after each fix
3. Commit changes with clear descriptions
4. Mark MEDIUM and LOW priority items for future work or accept as-is

## Expected Output Format

```
## Pre-Merge Analysis

### Summary
- Total comments: X
- Already fixed: Y
- Requiring action: Z

### CRITICAL Issues (Must Fix)
1. [main.py:1208] CSV/plot data inconsistency - plots use unscaled data
   - Impact: Scientific accuracy problem
   - Effort: 15 min
   - Fix: Pass scaled_results to plot_all()

### HIGH Issues (Should Fix)
...

### MEDIUM Issues (Consider)
...

### LOW Issues (Optional)
...

### NO ACTION (Working as Designed)
...

## Recommended Action Plan

Phase 1 (Blocking): Fix CRITICAL issues → Run tests → Commit
Phase 2 (Pre-merge): Fix HIGH issues → Run tests → Commit
Phase 3 (Future work): Create issues for MEDIUM/LOW items
```

## Best Practices

### When to Use This Command

- Before creating a pull request
- After receiving Copilot review comments
- Before requesting final review from maintainers
- When preparing to merge to main

### What Makes a Good Pre-Merge Check

1. **Thoroughness**: Review ALL comments, don't skip any
2. **Prioritization**: Focus on correctness and functionality first
3. **Testing**: Run full test suite after each fix
4. **Documentation**: Update README/docs if behavior changed
5. **Commit hygiene**: Separate commits for different types of fixes

### Common Patterns

#### Pattern 1: Data Consistency Issues (CRITICAL)

```python
# BAD: CSV has scaled data, plot has unscaled
csv_writer.writerow(scaled_results)
plot_all(results)  # ❌ inconsistent!

# GOOD: Both use scaled data
csv_writer.writerow(scaled_results)
plot_all(scaled_results)  # ✅ consistent
```

#### Pattern 2: Missing User Controls (CRITICAL)

```python
# BAD: No cancel button, users forced to enter values
def ask_scale():
    tk.Button(win, text="OK", command=submit).pack()
    # ❌ No way to cancel

# GOOD: Cancel button with defaults
def ask_scale():
    tk.Button(win, text="OK", command=submit).pack()
    tk.Button(win, text="Cancel", command=use_defaults).pack()
    # ✅ User can skip
```

#### Pattern 3: Test Isolation (HIGH)

```python
# BAD: Manual cleanup that won't run on failure
def test_something():
    config.value = 5
    assert config.value == 5
    config.value = 1  # ❌ Won't run if assertion fails

# GOOD: pytest fixture guarantees cleanup
@pytest.fixture(autouse=True)
def reset_config():
    config.value = 1
    yield  # ✅ Cleanup always runs
    config.value = 1
```

## Command Implementation

This command should:

1. Check that we're on a PR branch (not main)
2. Verify PR exists for current branch
3. Fetch Copilot comments using gh CLI
4. Launch Planning agent with analysis prompt
5. Present results and ask user to proceed
6. Implement fixes based on priorities
7. Commit and push when ready

## Integration with Other Commands

After running this command:

```bash
# If tests pass and fixes are committed
/coverage          # Verify test coverage still meets threshold
/lint              # Check code style
gh pr checks       # Verify CI passes
/review-pr         # Final self-review checklist
gh pr review --approve  # Request merge if ready
```

## Example Session

```
User: /pre-merge-check
Claude: Fetching PR comments from GitHub Copilot...
Claude: Found 21 review comments. Analyzing with Planning mode...
Claude: Analysis complete. Found 3 CRITICAL, 1 HIGH, 3 MEDIUM, 1 LOW issues.
        6 issues already fixed in previous commits.
Claude: Starting Phase 1 (CRITICAL fixes)...
Claude: [Implements fixes, runs tests, commits]
Claude: All critical issues resolved. PR ready for final review.
```

## Tips

- Run this command early and often during PR development
- Don't wait for Copilot to comment - be proactive about code review
- Use Planning mode to think through changes before implementing
- Keep commits focused - one fix per commit when possible
- Update documentation if behavior changes
- Always run full test suite before pushing

## Related Commands

- `/review-pr` - Manual review checklist
- `/coverage` - Check test coverage
- `/lint` - Run code style checks
- `/pr-description` - Generate PR description