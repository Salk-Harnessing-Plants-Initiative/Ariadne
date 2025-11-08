---
description: Run linting and formatting checks
---

# Lint & Format Code

Run linting and formatting checks to ensure code quality and consistent style.

## Commands

```bash
# Format code with Black
uv run black .

# Check formatting without making changes
uv run black --check .

# Run Ruff linting
uv run ruff check .

# Run Ruff with docstring checks
uv run ruff check . --select D

# Fix auto-fixable issues
uv run ruff check . --fix
```

## What to Do After Running

1. **Review formatting changes** - Check the diff to ensure Black changes look correct
2. **Fix lint errors** - Address any errors reported by Ruff
3. **Add/fix docstrings** - Ensure all public functions have Google-style docstrings
4. **Commit changes** - If formatting changed files, commit them separately from logic changes

## Code Style Rules

### Black Formatting
- **Line length**: 88 characters (configured in pyproject.toml)
- **Quote style**: Double quotes preferred
- **Trailing commas**: Added automatically for multi-line structures

### Ruff Linting
- **Select rules**: D (docstrings), E (errors), F (pyflakes), W (warnings)
- **Ignored rules**: D100, D104, D107 (module/package/init docstrings)
- **Docstring convention**: Google style

### Google-Style Docstrings

```python
def calculate_pareto_cost(wiring: float, delay: float, alpha: float = 0.5) -> float:
    """Calculate Pareto cost for root system architecture.

    The Pareto cost balances material cost (wiring) against conduction delay,
    parameterized by alpha. When alpha=0, only delay matters; when alpha=1,
    only wiring matters.

    Args:
        wiring: Total root length in pixels (material cost).
        delay: Sum of shortest paths from tips to base (conduction delay).
        alpha: Trade-off parameter between 0 and 1.

    Returns:
        Pareto cost as a weighted combination of wiring and delay.

    Raises:
        AssertionError: If alpha is not in range [0, 1].
    """
    assert 0 <= alpha <= 1
    return alpha * wiring + (1 - alpha) * delay
```

## Common Issues

### Missing Docstrings
```bash
# Identify functions missing docstrings
uv run ruff check . --select D
```

Fix by adding Google-style docstrings to all public functions.

### Line Too Long
Black will automatically fix most line-length issues, but complex expressions may need manual breaking:

```python
# Before (too long)
result = calculate_very_long_function_name(parameter1, parameter2, parameter3, parameter4)

# After (manually broken)
result = calculate_very_long_function_name(
    parameter1, parameter2, parameter3, parameter4
)
```

### Import Organization
Ruff will flag import issues. Organize imports as:
1. Standard library
2. Third-party packages
3. Local application imports

## Pre-Commit Workflow

Before committing:

```bash
# Format code
uv run black .

# Check linting
uv run ruff check . --fix

# Verify docstrings
uv run ruff check . --select D

# Run tests
uv run pytest
```

## Configuration

All linting and formatting rules are defined in `pyproject.toml`:

```toml
[tool.black]
line-length = 88

[tool.ruff]
line-length = 88
extend-exclude = ["*.ipynb"]

[tool.ruff.lint]
select = ["D", "E", "F", "W"]
ignore = ["D100", "D104", "D107"]

[tool.ruff.lint.pydocstyle]
convention = "google"
```