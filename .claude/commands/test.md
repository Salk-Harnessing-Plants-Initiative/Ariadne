---
description: Run pytest test suite with various options and filters
---

# Run Tests

Execute the pytest test suite with common options for Ariadne root system analysis.

## Quick Commands

```bash
# Run all tests
uv run pytest

# Run all tests with verbose output
uv run pytest -v

# Run tests for a specific module
uv run pytest tests/test_quantify.py

# Run a specific test function
uv run pytest tests/test_quantify.py::test_analyze

# Run tests matching a pattern
uv run pytest -k "pareto" tests/

# Run tests with output (print statements visible)
uv run pytest -s tests/

# Run tests and stop on first failure
uv run pytest -x tests/

# Run previously failed tests
uv run pytest --lf tests/

# Run tests with coverage
uv run pytest --cov=ariadne_roots --cov-report=term-missing
```

## Understanding Test Output

### Successful test run:
```
================================ test session starts =================================
platform darwin -- Python 3.12.12, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/elizabethberrigan/repos/Ariadne
collected 115 items

tests/test_config.py ......                                                [  5%]
tests/test_main.py ...                                                     [  8%]
tests/test_pareto_functions.py ................................................ [ 50%]
tests/test_quantify.py .......................................... [ 84%]
tests/test_scaling.py ...............                                     [100%]

================================ 115 passed in 1.34s =================================
```

### Failed test:
```
================================== FAILURES ==========================================
____________________________ test_buffer_calculation __________________________________

    def test_buffer_calculation():
        min_val, max_val = calculate_plot_buffer(0, 10)
>       assert min_val == -2.0
E       AssertionError: assert -1.9999999 == -2.0

tests/test_quantify.py:615: AssertionError
========================== short test summary info ===================================
FAILED tests/test_quantify.py::test_buffer_calculation - AssertionError
========================== 1 failed, 114 passed in 1.34s =============================
```

## Test Organization

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── test_config.py           # Tests for config.py (scaling config)
├── test_main.py             # Tests for main.py (GUI integration)
├── test_pareto_functions.py # Tests for pareto_functions.py (61 tests)
├── test_quantify.py         # Tests for quantify.py (34 tests)
└── test_scaling.py          # Tests for scaling.py (15 tests)
```

**Total**: 115 tests across 5 test files

## Cross-Platform Testing

Tests run on multiple platforms in CI:
- **Ubuntu 22.04** (primary coverage platform)
- **Windows 2022**
- **macOS latest**

Ensure tests pass locally before pushing, especially if modifying:
- File path handling
- Line endings
- Platform-specific GUI code (Tkinter)

## Common Testing Workflows

### 1. Running tests during development
```bash
# Run tests for the module you're working on
uv run pytest tests/test_quantify.py -v

# Watch for changes and re-run (if pytest-watch installed)
uv run ptw tests/test_quantify.py
```

### 2. Testing a new feature
```bash
# Run tests with verbose output to see details
uv run pytest -v tests/test_new_feature.py

# Run with coverage to ensure new code is tested
uv run pytest --cov=ariadne_roots.new_module tests/test_new_feature.py
```

### 3. Debugging a failing test
```bash
# Run with output visible (print statements)
uv run pytest -s tests/test_failing.py

# Drop into debugger on failure
uv run pytest --pdb tests/test_failing.py

# Run only the failing test
uv run pytest tests/test_failing.py::test_specific_function
```

### 4. Before creating a PR
```bash
# Run all tests
uv run pytest

# Run with coverage (90% threshold required)
uv run pytest --cov=ariadne_roots --cov-report=term-missing --cov-fail-under=90

# Ensure linting passes
uv run black --check .
uv run ruff check .
```

## Pytest Fixtures

Common fixtures defined in `tests/conftest.py`:

```python
@pytest.fixture
def sample_graph():
    """Fixture providing a sample networkx graph."""
    # Returns a simple test graph for analysis

@pytest.fixture
def sample_results():
    """Fixture providing sample analysis results."""
    # Returns dict with typical trait values
```

Use fixtures in your tests:
```python
def test_with_fixture(sample_graph):
    critical_nodes = get_critical_nodes(sample_graph)
    assert len(critical_nodes) > 0
```

## Writing Good Tests

### 1. Test naming convention
```python
# Good: Descriptive test names
def test_buffer_calculation_with_zero_values():
    pass

def test_pareto_front_with_single_node():
    pass

# Bad: Vague test names
def test_buffer():
    pass

def test_case1():
    pass
```

### 2. Test structure (Arrange, Act, Assert)
```python
def test_calculate_plot_buffer():
    # Arrange: Set up test data
    base_min, base_max = 0, 10
    
    # Act: Execute the function
    min_limit, max_limit = calculate_plot_buffer(base_min, base_max)
    
    # Assert: Verify the result
    assert min_limit == -2.0
    assert max_limit == 12.0
```

### 3. Test edge cases
```python
def test_buffer_with_empty_range():
    """Test with degenerate case (all zeros)."""
    min_limit, max_limit = calculate_plot_buffer(0, 0)
    assert min_limit < max_limit  # Prevent matplotlib errors

def test_buffer_with_negative_range():
    """Test with negative coordinate range."""
    min_limit, max_limit = calculate_plot_buffer(-10, -2)
    assert min_limit < -10  # Buffer extends beyond range
    assert max_limit > -2
```

## CI Testing

GitHub Actions runs tests on:
- Multiple platforms (Ubuntu, Windows, macOS)
- Python 3.12 and 3.13
- With coverage reporting (Ubuntu only)

CI configuration: `.github/workflows/ci.yml`

```yaml
- name: Test with pytest (with coverage)
  run: |
    uv run pytest --cov=ariadne_roots --cov-report=xml tests/
```

## Coverage Goals

- **Target**: 90%+ coverage (enforced in CI)
- **Current**: Tracked via Codecov on each PR
- **Requirement**: Coverage must not decrease

### Priority Areas
1. **High priority**: Core analysis functions (`quantify.py`, `pareto_functions.py`)
2. **Medium priority**: Scaling transformations (`scaling.py`)
3. **Lower priority**: GUI code (has `# pragma: no cover` for display functions)

## Tips

1. **Run tests frequently**: Don't wait until the end to test
2. **Test one thing at a time**: Each test should verify one specific behavior
3. **Use descriptive assertions**: Include messages to help debug failures
4. **Keep tests fast**: All 115 tests run in ~1.3 seconds
5. **Test error cases**: Not just the happy path
6. **Use parametrize for similar tests**: Reduce code duplication
7. **Test scientific accuracy**: Validate trait calculations against expected values

## Pytest Configuration

Configuration in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]

[tool.coverage.run]
source = ["ariadne_roots"]
omit = ["tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
]
fail_under = 90
```

## Quick Reference

```bash
# Most common commands
uv run pytest                    # Run all tests
uv run pytest -v                 # Verbose output
uv run pytest -x                 # Stop on first failure
uv run pytest --lf               # Run last failed
uv run pytest -k "pattern"       # Run tests matching pattern
uv run pytest --cov              # With coverage
uv run pytest -s                 # Show print statements
uv run pytest tests/test_X.py    # Run specific file
```

## Integration with Other Commands

```bash
/coverage    # Detailed coverage analysis with HTML report
/lint        # Code style and formatting checks
/test        # This command (run tests)
```

## Related Documentation

- pytest documentation: https://docs.pytest.org/
- Coverage.py documentation: https://coverage.readthedocs.io/
- Project README: Test section
- CI workflow: `.github/workflows/ci.yml`
