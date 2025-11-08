# Archived OpenSpec Changes

This directory contains completed OpenSpec changes that have been implemented and merged.

---

## add-comprehensive-test-coverage (November 2025)
**Status**: ✅ Completed - Merged in PR #30

Implemented comprehensive test coverage for Ariadne's core analysis modules, achieving 98.31% coverage.

- **Proposal**: [proposal.md](add-comprehensive-test-coverage/proposal.md)
- **Design**: [design.md](add-comprehensive-test-coverage/design.md)
- **Tasks**: [tasks.md](add-comprehensive-test-coverage/tasks.md)
- **Spec**: [spec.md](add-comprehensive-test-coverage/specs/test-framework/spec.md)
- **Related PR**: #30

**Key Deliverables**:
- 73 new tests across pareto_functions.py and quantify.py
- Three-tier fixture approach: minimal synthetic graphs, edge cases, real root data
- Enhanced test infrastructure with helper functions and documented fixtures
- Coverage raised from ~40% to 98.31% (exceeds 90% threshold)
- Integration test validates against real Arabidopsis thaliana root data

**Timeline**: 2 days (vs. 1 week estimate)

---

## add-claude-commands (November 2025)
**Status**: ✅ Completed - Merged in PR #30

Added Claude Code development workflow commands adapted from cosmos-azul and tailored to Ariadne's Python/pytest stack.

- **Proposal**: [proposal.md](add-claude-commands/proposal.md)
- **Design**: [design.md](add-claude-commands/design.md)
- **Tasks**: [tasks.md](add-claude-commands/tasks.md)
- **Spec**: [spec.md](add-claude-commands/specs/development-commands/spec.md)
- **Related PR**: #30

**Key Deliverables**:
- 5 Claude commands: `/coverage`, `/lint`, `/pr-description`, `/review-pr`, `/cleanup-merged`
- All commands use Ariadne-specific tools (uv, pytest, black, ruff)
- 90% coverage threshold integration
- Domain-specific examples for root phenotyping
- GitHub CLI workflow automation

**Timeline**: 1 day (vs. 4 hours estimate - included extra testing and refinement)

---

## improve-ci-workflow-best-practices (November 2025)
**Status**: ✅ Completed - Merged in PR #30

Modernized CI/CD pipeline with uv best practices, lockfile-based workflow, and comprehensive security documentation.

- **Proposal**: [proposal.md](improve-ci-workflow-best-practices/proposal.md)
- **Design**: [design.md](improve-ci-workflow-best-practices/design.md)
- **Tasks**: [tasks.md](improve-ci-workflow-best-practices/tasks.md)
- **Spec**: [spec.md](improve-ci-workflow-best-practices/specs/ci-cd/spec.md)
- **Related PR**: #30

**Key Deliverables**:
- Lockfile-based workflow with `uv sync --frozen` for reproducible builds
- Python version pinning via `.python-version` file (3.12)
- Improved caching with `cache-dependency-glob: "**/uv.lock"`
- Concurrency groups to cancel outdated CI runs
- Lockfile validation step to catch uncommitted changes
- Comprehensive package installation testing (wheel + sdist with dev extras)
- Security documentation with `pip-audit` guidance
- Updated developer documentation emphasizing uv workflow

**Timeline**: Implemented alongside test coverage work in PR #30 (37 of 38 tasks complete, 1 optional)

---

## Archive Management

When archiving a new OpenSpec change:

1. Move the change directory: `git mv openspec/changes/<change-name> openspec/changes/archive/`
2. Update this README with:
   - Change name and completion date
   - Status and PR reference
   - Key deliverables summary
   - Actual vs. estimated timeline
3. Commit with message: `chore: archive <change-name> OpenSpec change`
