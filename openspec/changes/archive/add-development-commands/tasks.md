# Tasks: Add Development Commands

**Status**: 🟡 In Progress
**Tracking**: This file tracks implementation tasks for the add-development-commands OpenSpec change

## Task Breakdown

### Phase 1: Create Test Command ✅ DONE
**Estimated**: 30 minutes
**Status**: ✅ Completed

- [x] Review sleap-roots `/test` command
- [x] Adapt for Ariadne context (pytest, uv, 115 tests)
- [x] Add common pytest options (-v, -x, -s, -k, --lf)
- [x] Document test organization and fixtures
- [x] Include cross-platform notes (if applicable)
- [x] Test command with actual usage

### Phase 2: Create Changelog Command
**Estimated**: 45 minutes
**Status**: 🔄 In Progress

- [x] Review sleap-roots `/changelog` command
- [ ] Adapt for Ariadne context (PyPI package, semantic versioning)
- [ ] Include Keep a Changelog format guide
- [ ] Add versioning examples (MAJOR.MINOR.PATCH)
- [ ] Document git commands for reviewing changes
- [ ] Include release workflow integration
- [ ] Test command with actual usage

### Phase 3: Create PR Description Command
**Estimated**: 30 minutes
**Status**: ⏳ Pending

- [ ] Review bloom `/pr-description` command
- [ ] Adapt for Ariadne context (Python package, not full-stack)
- [ ] Customize checklist sections:
  - [ ] Testing (pytest, coverage ≥90%)
  - [ ] Linting (Black, Ruff)
  - [ ] Type checking (if applicable)
  - [ ] Breaking changes
  - [ ] Related issues
- [ ] Remove irrelevant sections (TypeScript, Docker, database migrations)
- [ ] Add scientific accuracy validation (for trait calculations)
- [ ] Test template with example PR

### Phase 4: Create Review PR Command
**Estimated**: 45 minutes
**Status**: ⏳ Pending

- [ ] Review sleap-roots and bloom `/review-pr` commands
- [ ] Adapt for Ariadne context
- [ ] Create checklist sections:
  - [ ] Code review (logic, edge cases, performance)
  - [ ] Testing (coverage, test quality, edge cases)
  - [ ] Scientific accuracy (trait calculations validated)
  - [ ] Documentation (docstrings, README updates)
  - [ ] Style (Black, Ruff, type hints)
  - [ ] Breaking changes (API compatibility)
- [ ] Include `gh pr` commands for viewing changes
- [ ] Add examples of good vs. bad patterns
- [ ] Test command with actual PR review

### Phase 5: Update Release Command
**Estimated**: 30 minutes
**Status**: ⏳ Pending

- [ ] Read current `/release` command
- [ ] Update Step 1 (Pre-Release Validation) to reference:
  - [ ] `/test` - Run full test suite
  - [ ] `/coverage` - Verify 90%+ coverage
  - [ ] `/lint` - Check formatting and style
- [ ] Update Step 2 (Determine Version) to reference:
  - [ ] `/changelog` - Review changes and update CHANGELOG.md
- [ ] Update Step 8 (Create Version Bump PR) to reference:
  - [ ] `/pr-description` - Use template for PR
- [ ] Add cross-references in "Integration with Other Commands" section
- [ ] Update "Best Practices" with changelog maintenance
- [ ] Test release workflow with new commands

### Phase 6: Testing and Validation
**Estimated**: 30 minutes
**Status**: ⏳ Pending

- [ ] Test `/test` command with various options
- [ ] Test `/changelog` command with git log
- [ ] Test `/pr-description` command by creating example PR body
- [ ] Test `/review-pr` command with actual PR
- [ ] Verify `/release` command references are accurate
- [ ] Ensure all commands work with `uv` tooling
- [ ] Check that commands follow existing style

## Progress Tracking

- **Total Tasks**: 32
- **Completed**: 6
- **In Progress**: 0
- **Pending**: 26
- **Blocked**: 0

**Overall Progress**: 19% (6/32 tasks)

## Notes

- Commands adapted from sleap-roots are most relevant (similar Python/pytest setup)
- Bloom commands have full-stack context (Flask + TypeScript) - need more adaptation
- Cosmos-azul commands are similar to Bloom
- All commands should use `uv` instead of pip/poetry/npm
- Coverage threshold is 90% (configured in pyproject.toml)
- Scientific accuracy is critical for Ariadne (root trait calculations)

## Dependencies

- [x] Existing `/coverage` command
- [x] Existing `/lint` command
- [x] Existing `/pre-merge-check` command
- [x] Existing `/cleanup-merged` command
- [x] Existing `/release` command
- [ ] pyproject.toml (for configuration references)
- [ ] .github/workflows/ (for CI references)

## Blocked Items

None currently.

## Timeline

**Start**: 2024-11-11
**Target Completion**: 2024-11-11 (same day)
**Actual Completion**: TBD

## Acceptance Criteria Checklist

- [ ] All 4 new commands created
- [ ] All commands tested with actual usage
- [ ] Commands follow existing style and conventions
- [ ] `/release` command updated with cross-references
- [ ] All tasks marked complete
- [ ] OpenSpec change ready for archiving
