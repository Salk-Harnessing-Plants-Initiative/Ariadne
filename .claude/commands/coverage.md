---
description: Run tests with coverage analysis
---

# Test Coverage Analysis

Run tests with coverage analysis to identify untested code and ensure quality.

## Commands

```bash
# Run all tests with coverage
uv run pytest --cov=ariadne_roots --cov-report=term-missing --cov-branch

# Run tests with HTML coverage report
uv run pytest --cov=ariadne_roots --cov-report=html --cov-branch

# Check coverage threshold (90%)
uv run pytest --cov=ariadne_roots --cov-report=term-missing --cov-branch --cov-fail-under=90
```

## Understanding Results

After running coverage, you'll see a table like:

```
Name                                    Stmts   Miss Branch BrPart   Cover   Missing
------------------------------------------------------------------------------------
src/ariadne_roots/pareto_functions.py     355      1     92      3  99.11%   659
src/ariadne_roots/quantify.py             256      5     70      4  97.24%   30, 305, 444
------------------------------------------------------------------------------------
TOTAL                                     615      6    162      7  98.33%
```

### Coverage Goals

- **Core calculation logic** (pareto_functions, quantify): Target 90%+
- **Overall project**: Current threshold 90%
- **GUI module** (main.py): Excluded from coverage (not suitable for automated testing)

### What to Test

1. **High priority**: Pareto optimization and graph analysis algorithms
2. **Medium priority**: Root trait calculations (length, angle, zones)
3. **Lower priority**: Legacy functions marked with `pragma: no cover`

## Coverage Files

- `coverage/` - HTML coverage report (open `coverage/index.html` in browser)
- `.coverage` - Raw coverage data (machine-readable)

## Integration Test

The integration test validates accuracy using real Arabidopsis root system data:

```bash
# Run the integration test specifically
uv run pytest tests/test_quantify.py::test_analyze -v
```

This test uses `plantB_day11.json` fixture to validate:
- All root trait calculations (24 lateral roots)
- Pareto front computation
- Graph structure preservation
- Reproducible results across platforms

Run this test before any changes to analysis algorithms to ensure scientific accuracy.

## Identifying Coverage Gaps

Use the `term-missing` report to see exactly which lines aren't covered:

```bash
uv run pytest --cov=ariadne_roots --cov-report=term-missing --cov-branch
```

Missing lines are shown in the rightmost column (e.g., `30, 305, 444`).

Focus on:
- Uncovered branches in core algorithms
- Edge cases in graph analysis
- Error handling paths

Avoid testing:
- GUI interaction code (use manual testing)
- Legacy text file parsers (marked `pragma: no cover`)
- Stub functions not yet implemented