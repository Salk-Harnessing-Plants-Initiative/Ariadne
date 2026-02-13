<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# Package Management

**NEVER install packages to the base Python environment.** Always use uv:
- `uv run <command>` - Run commands within the project environment
- `uv tool run <tool>` - Run standalone tools without installing
- `uv add <package>` - Add dependencies to the project
- `uv pip install` - Install to project venv only

Never use `pip install` or `pip3 install` directly.