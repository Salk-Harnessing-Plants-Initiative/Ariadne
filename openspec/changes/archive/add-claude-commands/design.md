# Design: Add Claude Commands

## Overview

This design outlines how to adapt cosmos-azul's Claude commands to Ariadne's Python/pytest ecosystem while maintaining the same structured workflow patterns.

## Command Adaptations

### 1. Coverage Command

**Source**: cosmos-azul `/coverage`
**Adaptations**:
- Replace `pnpm test:coverage` → `uv run pytest --cov=ariadne_roots --cov-report=term-missing --cov-branch`
- Replace "golden test" → "integration test with real root system data (plantB_day11)"
- Replace astrology accuracy concerns → root phenotyping accuracy
- Update coverage goals from 50%/70%/100% → 90% overall (per current pyproject.toml)
- Reference `coverage/` directory for HTML reports

**Key Differences**:
- Single package (not monorepo), so no `--filter` needed
- Coverage configured in pyproject.toml `[tool.coverage.report]`
- Focus on pareto_functions.py and quantify.py as core modules

### 2. Lint Command

**Source**: cosmos-azul `/lint`
**Adaptations**:
- Replace `pnpm format` → `uv run black .`
- Replace `pnpm format:check` → `uv run black --check .`
- Replace `pnpm type-check` → `uv run mypy src/` (if mypy is added) OR skip type-check section
- Replace `pnpm lint` → `uv run ruff check .`
- Add pydocstyle checking: `uv run ruff check . --select D`

**Key Differences**:
- Python uses black (opinionated) vs Prettier (configurable)
- Ruff combines linting + docstring checking
- Type checking is optional (not enforced in current project)
- Single package, no monorepo concerns

### 3. PR Description Command

**Source**: cosmos-azul `/pr-description`
**Adaptations**:
- Replace testing checklist: `pnpm test` → `uv run pytest`
- Replace "golden test" → "integration test with real root data"
- Remove "Type Checking & Linting" section (combine into "Code Quality")
- Update coverage threshold: 50%→90%
- Replace package list (apps/packages) → single package context
- Update examples to use root phenotyping domain

**Template Structure**:
```markdown
## Summary
[Brief description]

## Changes
- [Bullet list]

## Testing
- [ ] All tests pass (`uv run pytest`)
- [ ] New tests added for new functionality
- [ ] Integration test passes (if modifying analysis algorithms)
- [ ] Coverage meets 90% threshold

## Code Quality
- [ ] Black formatting applied (`uv run black .`)
- [ ] Ruff linting passes (`uv run ruff check .`)
- [ ] Docstrings follow Google style

## Domain Accuracy (if applicable)
- [ ] Algorithm references credible sources
- [ ] Pareto calculations validated
- [ ] Graph analysis correctness verified
```

### 4. Review PR Command

**Source**: cosmos-azul `/review-pr`
**Adaptations**:
- Replace TypeScript concerns → Python concerns (type hints, naming conventions)
- Replace "Monorepo Structure" → "Package Structure" (src layout)
- Replace "Astrology Accuracy" → "Scientific Accuracy" (Pareto, graph algorithms)
- Update security/privacy concerns (no user data, focus on scientific reproducibility)
- Replace "Performance" checks with Python-specific concerns (numpy efficiency, graph algorithms)

**Review Checklist Sections**:
1. Code Quality (Python conventions, PEP 8)
2. Type Safety (type hints, docstrings)
3. Testing (coverage, integration tests)
4. Documentation (comments for algorithms, Google-style docstrings)
5. Scientific Accuracy (algorithm sources, reproducibility)
6. Package Structure (src layout, dependencies)

### 5. Cleanup Merged Command

**Source**: cosmos-azul `/cleanup-merged`
**Adaptations**:
- Minimal changes needed (git workflow is language-agnostic)
- Update OpenSpec archive path to match Ariadne structure
- Simplify examples (no monorepo packages to list)
- Add reminder about `main` vs `master` branch naming

**Workflow**:
1. Verify merge with `gh pr list --state merged`
2. Switch to main and pull
3. Delete branch with `git branch -d` (safety check)
4. Archive OpenSpec if applicable
5. Commit archive changes

## File Organization

```
.claude/
├── commands/
│   ├── openspec/          # Existing
│   │   ├── proposal.md
│   │   ├── apply.md
│   │   └── archive.md
│   ├── coverage.md        # NEW
│   ├── lint.md            # NEW
│   ├── pr-description.md  # NEW
│   ├── review-pr.md       # NEW
│   └── cleanup-merged.md  # NEW
└── settings.local.json    # Existing
```

## Command Metadata

Each command file includes YAML frontmatter:

```yaml
---
description: [Short description for command list]
---
```

Examples:
- `coverage.md`: "Run tests with coverage analysis"
- `lint.md`: "Run linting and formatting checks"
- `pr-description.md`: "Template for creating comprehensive PRs"
- `review-pr.md`: "Systematic PR review workflow"
- `cleanup-merged.md`: "Clean up merged branches and archive OpenSpec"

## Integration with Existing Commands

These commands complement the existing OpenSpec commands:
- `/openspec:proposal` - Create new change proposal
- `/openspec:apply` - Implement approved change
- `/openspec:archive` - Archive completed change

New commands don't overlap:
- `/coverage`, `/lint` - Development quality checks
- `/pr-description`, `/review-pr` - PR workflow
- `/cleanup-merged` - Post-merge cleanup (uses `/openspec:archive` internally)

## Testing Strategy

Each command will be tested by:
1. Running actual commands on command line
2. Verifying GitHub CLI commands work
3. Testing with Claude Code to ensure proper execution
4. Validating file paths and tool references

## Future Enhancements (Out of Scope)

- Add `/test` command for common test invocations
- Add `/build` command for building and publishing packages
- Create domain-specific commands (e.g., `/analyze-roots` for common analysis workflows)
- Integration with pre-commit hooks

## References

- Cosmos-azul commands: `~/.../cosmos-azul/.claude/commands/`
- Ariadne pyproject.toml: `pyproject.toml` (tool configurations)
- Test coverage implementation: `openspec/changes/add-comprehensive-test-coverage/`
- CI workflow: `.github/workflows/tests.yml`
