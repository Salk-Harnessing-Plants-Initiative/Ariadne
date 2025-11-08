# Proposal: Add Claude Commands for Development Workflows

## Problem Statement

The Ariadne repository currently lacks standardized slash commands for common development tasks, making it harder for AI assistants and developers to efficiently execute routine workflows like running tests with coverage, formatting code, creating PRs, and cleaning up merged branches.

Cosmos-azul has a well-structured set of Claude commands that provide clear, step-by-step guidance for these workflows. Adapting these commands to Ariadne would improve development velocity and consistency.

## Proposed Solution

Add five Claude slash commands adapted from cosmos-azul to `.claude/commands/`:

1. **`/coverage`** - Run tests with coverage analysis and understand results
2. **`/lint`** - Run linting and formatting checks (black, ruff)
3. **`/pr-description`** - Template and guidelines for creating comprehensive PRs
4. **`/review-pr`** - Systematic workflow for reviewing PRs and responding to comments
5. **`/cleanup-merged`** - Post-merge cleanup process (branch deletion, OpenSpec archival)

These commands will be tailored to Ariadne's tech stack (Python/uv instead of TypeScript/pnpm), testing conventions (pytest instead of Vitest), and project-specific requirements (root phenotyping domain instead of astrology).

## Benefits

1. **Consistency**: Standardized workflows for common development tasks
2. **Efficiency**: Quick reference commands reduce context switching
3. **Onboarding**: New contributors and AI assistants can quickly understand project conventions
4. **Quality**: Built-in checklists ensure important steps aren't missed
5. **Documentation**: Commands serve as living documentation of project practices

## Scope

**In Scope:**
- Create 5 new command files in `.claude/commands/`
- Adapt cosmos-azul command content to Ariadne's Python/pytest stack
- Reference Ariadne-specific conventions (coverage thresholds, code style, domain context)
- Include examples relevant to root phenotyping and graph analysis

**Out of Scope:**
- Modifying existing OpenSpec commands (proposal, apply, archive)
- Changing project.md or other OpenSpec documentation
- Adding new CI/CD automation
- Creating additional tooling beyond command documentation

## Dependencies

- Existing `.claude/commands/openspec/` directory structure
- Current pyproject.toml configuration (coverage thresholds, formatting rules)
- GitHub CLI (`gh`) for PR-related commands

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Commands become outdated as project evolves | Include references to source files (pyproject.toml) so commands stay aligned |
| Commands too verbose for quick reference | Keep core commands concise, use expandable checklists |
| Stack-specific differences from cosmos-azul | Thoroughly adapt TypeScript→Python, pnpm→uv, astrology→plant biology |

## Success Criteria

1. All 5 commands are created and functional
2. Commands reference correct Ariadne-specific tools and conventions
3. Examples use Ariadne domain language (roots, phenotyping, Pareto optimization)
4. Commands work with both `gh` CLI and manual git workflows
5. OpenSpec validation passes for all related changes

## Timeline Estimate

- **Design & adaptation**: 1 hour
- **Implementation**: 2 hours
- **Testing & refinement**: 1 hour
- **Total**: ~4 hours

## Related Work

- Source commands from cosmos-azul: `~/.../cosmos-azul/.claude/commands/`
- Ariadne project conventions: `openspec/project.md`
- Existing test coverage implementation: OpenSpec change `add-comprehensive-test-coverage`
