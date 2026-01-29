# Test Data Documentation

This directory contains test fixtures for validating Ariadne's root system architecture (RSA) analysis algorithms.

## Test Data Sources

### Real Root System Data

**`_set1_day1_20230509-125420_014_plantB_day11.json`**
- **Source**: Real Arabidopsis thaliana root system
- **Date**: May 9, 2023
- **Plant ID**: Plant B, Day 11
- **Validation**: Expected values in `tests/fixtures.py` were calculated using the production analyze() function and validated against manual measurements
- **Structure**: NetworkX adjacency graph format with:
  - Primary root (PR) nodes with `LR_index: null`
  - Lateral root (LR) nodes with `LR_index: 0-23` (24 lateral roots total)
  - Node positions as (x, y) coordinates
  - Edge weights representing Euclidean distances

### Expected Output Values

All expected values in `tests/fixtures.py` are derived from:
1. Running the production `analyze()` function on known-good data
2. Visual verification of root system structure
3. Comparison with published algorithms (Chandrasekhar & Navlakha 2019, Conn et al. 2017)

**Tolerance**: Tests use `rel_tol=1e-8` (relative tolerance) for floating-point comparisons to account for numerical precision variations across platforms.

## Adding New Test Data

When adding new test fixtures:

1. **Document provenance**:
   - Source experiment/dataset
   - Date collected
   - Plant ID and growth conditions
   - Any preprocessing applied

2. **Generate expected values**:
   ```python
   from ariadne_roots.quantify import analyze
   import json
   from networkx.readwrite import json_graph

   # Load fixture
   with open('tests/data/new_fixture.json') as f:
       data = json.load(f)
       graph = json_graph.adjacency_graph(data)

   # Calculate expected values
   results, front, randoms = analyze(graph)
   print(results)  # Copy to fixtures.py
   ```

3. **Add fixture functions** to `tests/fixtures.py`:
   ```python
   @pytest.fixture
   def new_fixture_json():
       return "tests/data/new_fixture.json"

   @pytest.fixture
   def new_fixture_expected_lr_lengths():
       return [...]  # From analyze() output
   ```

4. **Document in this README**: Add entry above with source and validation method

## Fixture Types

### Real Datasets
- Complete root systems from actual experiments
- Used for integration testing and end-to-end validation
- Ensure scientific accuracy of algorithms

### Synthetic Graphs (Programmatic)
- Minimal graphs (3-5 nodes) for unit testing
- Edge-case graphs (single root, highly branched, disconnected)
- Fast execution, hand-verifiable outputs
- Generated in `tests/fixtures.py` using helper functions

## Reproducibility

All tests must be reproducible:
- Fixed random seeds for any randomized operations
- Committed test data files (no generated data at test time)
- Platform-independent expected values (use relative tolerance)
- Documented floating-point precision assumptions

## File Naming Convention

- Real data: `<experiment>_<plant_id>_<timepoint>.json`
- Synthetic data: Generated programmatically in fixtures.py (not committed as files)

## References

Expected values are validated against these published algorithms:
1. Chandrasekhar, A., & Navlakha, S. (2019). Neural arbors are Pareto optimal. *Proceedings of the Royal Society B*, 286(1902), 20182727.
2. Conn, A., et al. (2017). High-resolution laser scanning reveals plant architectures that reflect universal network design principles. *Cell Systems*, 5(1), 53-62.
