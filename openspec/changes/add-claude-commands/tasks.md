# Tasks: Add Claude Commands

## Phase 1: Setup & Foundation
- [x] Create `.claude/commands/` directory structure (if not exists)
- [x] Review cosmos-azul commands for adaptation patterns
- [x] Identify Ariadne-specific conventions to incorporate

## Phase 2: Coverage Command
- [x] Create `.claude/commands/coverage.md`
- [x] Adapt pytest/pytest-cov commands (replace pnpm with uv)
- [x] Reference 90% coverage threshold from pyproject.toml
- [x] Add examples for pareto_functions.py and quantify.py
- [x] Include guidance on understanding coverage reports
- [x] Document HTML coverage report location

## Phase 3: Lint Command
- [x] Create `.claude/commands/lint.md`
- [x] Document black formatting commands
- [x] Document ruff linting commands
- [x] Add pydocstyle/docstring checking guidance
- [x] Include pre-commit workflow recommendations
- [x] Add examples of fixing common lint issues

## Phase 4: PR Description Command
- [x] Create `.claude/commands/pr-description.md`
- [x] Adapt PR template to Python/pytest context
- [x] Include Ariadne-specific testing checklist
- [x] Add coverage threshold verification (90%)
- [x] Reference root phenotyping domain in examples
- [x] Include monorepo context (even though single package)
- [x] Add GitHub CLI examples for PR creation

## Phase 5: Review PR Command
- [x] Create `.claude/commands/review-pr.md`
- [x] Adapt review checklist to Python conventions
- [x] Add type safety checks (type annotations)
- [x] Include test coverage verification
- [x] Add algorithm accuracy review (Pareto, graph analysis)
- [x] Document scientific accuracy validation patterns
- [x] Include GitHub CLI review examples

## Phase 6: Cleanup Merged Command
- [x] Create `.claude/commands/cleanup-merged.md`
- [x] Adapt branch cleanup workflow
- [x] Document OpenSpec archival process
- [x] Add safety checks (git branch -d vs -D)
- [x] Include examples for both simple and OpenSpec PRs
- [x] Add verification steps

## Phase 7: Integration & Documentation
- [x] Test all commands with actual workflows
- [x] Verify GitHub CLI commands work correctly
- [x] Ensure commands reference correct file paths
- [x] Add command descriptions to metadata (YAML frontmatter)
- [x] Update CLAUDE.md if needed to reference new commands

## Phase 8: Validation & Refinement
- [x] Run `openspec validate add-claude-commands --strict`
- [x] Fix any validation errors
- [x] Test commands with Claude Code
- [x] Refine based on actual usage
- [x] Commit and push changes

## Validation Checklist
- [x] All commands use correct Ariadne-specific tools (uv, pytest, black, ruff)
- [x] Coverage thresholds match pyproject.toml (90%)
- [x] Domain examples use root phenotyping terminology
- [x] GitHub CLI commands tested and working
- [x] File paths are correct relative to repo root
- [x] YAML frontmatter includes descriptions
- [x] Commands are concise but comprehensive
