---
description: Clean up merged branch and archive OpenSpec change
---

# Clean Up Merged Branch

Clean up after a PR merge by deleting branches and archiving OpenSpec changes.

## 1. Verify Merge Status

First, confirm the PR has been merged:

```bash
# Show recent merged PRs
gh pr list --state merged --limit 5

# View specific PR status
gh pr view <number>
```

Verify the branch appears in the merged list before proceeding.

## 2. Switch to Main and Pull

```bash
git checkout main
git pull
```

Confirm you're on the latest main branch.

## 3. Delete Feature Branch

Delete both local and remote tracking references:

```bash
# Delete local branch (safety check with -d)
git branch -d <branch-name>

# Prune remote tracking references
git remote prune origin
```

**Important**: The `-d` flag (not `-D`) ensures the branch has been merged. Git will prevent deletion if the branch hasn't been fully merged.

## 4. Archive OpenSpec Change (if applicable)

If this was an OpenSpec-tracked change:

### Check for OpenSpec directory

```bash
ls openspec/changes/
```

### Move to archive

Identify the change directory (e.g., `add-claude-commands`, `improve-ci-workflow`):

```bash
# Move change to archive
git mv openspec/changes/<change-name> openspec/changes/archive/<change-name>
```

### Update Archive README

Edit `openspec/changes/archive/README.md` to add the new archived change:

```markdown
### <change-name> (Month Year)
**Status**: ✅ Completed - Merged in PR #<number>

Brief description of what was implemented.

- **Proposal**: [proposal.md](<change-name>/proposal.md)
- **Design**: [design.md](<change-name>/design.md)
- **Tasks**: [tasks.md](<change-name>/tasks.md)
- **Related Issue**: #<issue-number>

**Key Deliverables**:
- Bullet point summary
- Of main deliverables
- And outcomes

**Timeline**: <actual-time> (vs. <estimated-time> estimate)
```

## 5. Commit and Push

```bash
git add -A
git commit -m "chore: archive <change-name> OpenSpec change

Moved completed OpenSpec change to archive after PR #<number> merge.
Updated archive README with summary of deliverables.

Related: #<issue>, PR #<pr-number>"

git push
```

## 6. Verify Cleanup

Confirm cleanup is complete:

```bash
# Branch should not appear
git branch -a | grep <branch-name> || echo "✅ Branch deleted"

# OpenSpec should be in archive (if applicable)
ls openspec/changes/archive/<change-name>
```

## Summary Checklist

After cleanup, verify:

- ✅ Branch deleted (local + remote)
- ✅ OpenSpec change archived (if applicable)
- ✅ Archive README updated (if applicable)
- ✅ Main branch clean and up-to-date

## Common Scenarios

### Scenario 1: Simple bug fix (no OpenSpec)

1. Switch to main, pull
2. Delete branch
3. Done

### Scenario 2: Feature with OpenSpec documentation

1. Switch to main, pull
2. Delete branch
3. Archive OpenSpec change
4. Update archive README
5. Commit and push

### Scenario 3: Branch not yet merged

**Stop!** Do not force delete with `-D`.

1. Check merge status: `gh pr view <number>`
2. If PR is still open, ask user to merge first
3. If PR was closed without merging, confirm before force deletion

## Notes

- Only archive OpenSpec changes if they exist in `openspec/changes/`
- Not all PRs have OpenSpec documentation - that's okay
- If the branch can't be deleted with `-d`, it means it hasn't been merged
- Preserve git history with `git mv` instead of shell `mv`
- Use `gh pr view <number>` to verify merge status if unsure

## Safety Checks

### Before Deleting

```bash
# Verify branch is fully merged
git branch --merged main | grep <branch-name>

# If not in the list, the branch is NOT fully merged
```

### Force Delete Warning

**Never** use `git branch -D` unless you're absolutely certain:

- The branch was closed without merging (intentional)
- You've verified with the team this is the right action
- You understand the commits will be lost

## Troubleshooting

### Branch won't delete

```
error: The branch '<branch-name>' is not fully merged.
```

**Solution**: Check if PR was actually merged:

```bash
gh pr view <number>
```

If it shows "Merged", there may be a remote sync issue:

```bash
git fetch --all --prune
git checkout main
git pull
git branch -d <branch-name>
```

### Can't find OpenSpec change

Not all PRs have OpenSpec documentation. Check:

```bash
ls openspec/changes/
```

If the change isn't there, skip the archive step.