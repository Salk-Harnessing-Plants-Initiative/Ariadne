# Add Development Commands

**Status**: 🟡 Proposed
**Created**: 2024-11-11
**Owner**: Elizabeth Berrigan
**Effort**: 1-2 hours (reduced from initial estimate since pr-description and review-pr already exist)

## Problem Statement

The Ariadne repository currently has minimal Claude commands (only `/pre-merge-check`, `/release`, `/coverage`, `/lint`, `/cleanup-merged`, and OpenSpec commands). Other projects in the organization have comprehensive command sets that streamline development workflows.

**Current pain points:**
- No `/test` command for running pytest with common options
- No `/changelog` command for maintaining CHANGELOG.md
- No `/pr-description` command for creating comprehensive PRs
- No `/review-pr` command for systematic PR reviews
- Inconsistent workflow practices across projects
- `/release` command doesn't reference other commands for pre-release checks

**Observed in other repos:**
- **sleap-roots**: 15 commands including test, debug-test, docs-update, fix-formatting, validate-env, new-pipeline, run-ci-locally
- **bloom**: 10 commands including test, changelog, pr-description, review-pr, docs-review
- **cosmos-azul**: 9 commands including coverage, lint, changelog, pr-description, review-pr, docs-review, cleanup-merged

## Proposed Solution

Add essential development commands to `.claude/commands/` that are relevant for Python package development:

### Core Commands to Add

1. **`test.md`** - Run pytest with common configurations
2. **`changelog.md`** - Maintain CHANGELOG.md following Keep a Changelog format
3. **`release.md`** - Complete PyPI release workflow with command integrations

### Commands to Keep (Already Exist)

- ✅ `pr-description.md` - Template for comprehensive PR descriptions
- ✅ `review-pr.md` - Systematic PR review checklist
- ✅ `coverage.md` - Test coverage analysis
- ✅ `lint.md` - Linting and formatting
- ✅ `pre-merge-check.md` - Pre-merge validation
- ✅ `cleanup-merged.md` - Branch cleanup workflow
- ✅ OpenSpec commands (proposal, apply, archive)

### Commands NOT to Add (Not Relevant)

- ❌ `debug-test.md` - Not needed (sleap-roots specific for debugging failures)
- ❌ `docs-update.md` - README is straightforward, doesn't need specialized command
- ❌ `docs-review.md` - Docs are simpler than Bloom/Cosmos Azul projects
- ❌ `fix-formatting.md` - Covered by `/lint`
- ❌ `validate-env.md` - Not needed (uses `uv` for environment management)
- ❌ `new-pipeline.md` - Not relevant (sleap-roots specific)
- ❌ `run-ci-locally.md` - CI is simple, not needed

## Success Criteria

1. 3 new commands created and working:
   - `test.md` - pytest with common options
   - `changelog.md` - Keep a Changelog format
   - `release.md` - Complete PyPI release workflow
2. Commands adapted for Ariadne's Python/pytest/uv context
3. Commands follow existing style and format (matching pr-description, review-pr)
4. Commands reference appropriate tools and configurations
5. Release command integrates with all other commands
6. All commands tested with actual usage

## Implementation Plan

See [tasks.md](tasks.md) for detailed breakdown.

**Estimated effort**: 3-4 hours

## Design Decisions

### 1. Command Selection Criteria

**Include if:**
- Commonly used in development workflow
- Reduces friction or errors
- Provides templates/checklists
- Enforces best practices
- Relevant for Python package development

**Exclude if:**
- Project-specific to other repos
- Redundant with existing commands
- Overly simple (can be done in one command)
- Not part of Ariadne's workflow

### 2. Adaptation Strategy

Commands will be adapted from sleap-roots/bloom/cosmos-azul with:
- Python 3.12/3.13 context (not TypeScript/Flask)
- `uv` package manager (not pip/poetry)
- pytest testing framework
- Coverage threshold of 90% (from pyproject.toml)
- Black + Ruff linting (existing config)
- GitHub Actions CI (existing workflow)
- PyPI publishing workflow (existing)

### 3. Integration with `/release`

The `/release` command will be updated to reference other commands:
- Use `/coverage` before releasing
- Use `/lint` before releasing
- Use `/test` to verify functionality
- Use `/changelog` to update CHANGELOG.md
- Use `/pr-description` for version bump PR

## Out of Scope

- Creating a CHANGELOG.md file (will be added if command is used)
- Modifying existing CI workflows
- Adding new testing infrastructure
- Changing linting configuration
- Creating documentation beyond command files

## Non-Goals

- Port all commands from other repos (only relevant ones)
- Create project-specific commands (keep generic)
- Replace existing workflows (only enhance them)
- Add commands for every possible task (keep focused)

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Commands become outdated | Medium | Low | Include references to source files (pyproject.toml, CI configs) |
| Commands don't match actual workflow | Low | Medium | Test all commands with actual usage scenarios |
| Too many commands clutter `.claude/commands/` | Low | Low | Only add 4 essential commands, skip 7+ optional ones |
| Commands conflict with existing tools | Low | Low | Review existing commands first, ensure consistency |

## Alternatives Considered

### Alternative 1: Don't Add Commands
**Pros**: No maintenance burden
**Cons**: Missing helpful workflows, inconsistent with other repos
**Decision**: Rejected - commands provide value

### Alternative 2: Add All Commands from Other Repos
**Pros**: Complete coverage
**Cons**: Many irrelevant commands, maintenance burden
**Decision**: Rejected - only add relevant commands

### Alternative 3: Create Ariadne-Specific Commands
**Pros**: Tailored to this project
**Cons**: Doesn't leverage existing work
**Decision**: Rejected - adapt existing commands instead

## Dependencies

- Existing commands: `/coverage`, `/lint`, `/pre-merge-check`, `/cleanup-merged`, `/release`
- pyproject.toml configuration (coverage threshold, linting rules)
- GitHub Actions workflows (.github/workflows/)
- Package manager: `uv`
- Testing: pytest with coverage plugin

## Timeline

- **Planning**: 30 minutes (this proposal)
- **Implementation**: 1 hour (2 commands: test.md and changelog.md)
- **Testing**: 15 minutes (verify commands work)
- **Documentation**: Included in implementation

**Total**: 1-2 hours (revised from 3-4 hours since pr-description and review-pr already exist)

## Acceptance Criteria

- [x] `/test` command created with common pytest options
- [x] `/changelog` command created following Keep a Changelog format
- [x] `/release` command created with complete PyPI workflow
- [x] All commands adapted for Python/pytest/uv context
- [x] Commands follow existing style (match pr-description, review-pr format)
- [x] `/release` integrates with `/test`, `/coverage`, `/lint`, `/changelog`, `/pr-description`, `/cleanup-merged`
- [ ] Commands tested with actual usage scenarios
- [ ] Proposal approved and OpenSpec change archived

## Related Issues

- GitHub issue #35: Add custom Claude commands to improve development workflow

## References

- sleap-roots commands: `/Users/elizabethberrigan/repos/sleap-roots/.claude/commands/`
- bloom commands: `/Users/elizabethberrigan/repos/bloom/.claude/commands/`
- cosmos-azul commands: `/Users/elizabethberrigan/repos/cosmos-azul/.claude/commands/`
- Current Ariadne commands: `.claude/commands/`
- pyproject.toml: Coverage and linting configuration
- README.md: Current release process documentation
