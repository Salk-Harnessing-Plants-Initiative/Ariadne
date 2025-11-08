# Test Coverage Design

## Context

Ariadne performs scientific calculations for plant root system architecture analysis, implementing published Pareto optimality algorithms. The codebase currently has 40.48% coverage with only one integration test. Scientific computing demands high test coverage to ensure:

1. **Accuracy**: Calculations match published algorithms and validated outputs
2. **Precision**: Numerical stability across different input ranges
3. **Reproducibility**: Identical inputs always produce identical outputs (critical for scientific validity)

The existing test infrastructure uses pytest with centralized fixtures (`tests/fixtures.py`, `tests/conftest.py`), which is well-suited for expansion. The main constraint is that mocking is insufficient—tests must use real plant data with independently validated expected outputs.

## Goals / Non-Goals

**Goals:**
- Achieve ≥80% code coverage for scientific computation modules (`pareto_functions.py`, `quantify.py`)
- Validate calculation accuracy using real root system data with known-correct outputs
- Ensure reproducibility with deterministic fixtures and seeded random operations
- Maintain fast test execution (< 30 seconds total)
- Provide clear fixture documentation for future scientific validation

**Non-Goals:**
- GUI testing (`main.py` is excluded from coverage requirements due to matplotlib complexity)
- Performance benchmarking (covered separately if needed)
- Property-based testing (hypothesis) - use explicit fixtures for scientific reproducibility
- Mocking scientific calculations (defeats accuracy validation purpose)

## Decisions

### 1. Fixture Strategy: Real Data with Validated Outputs

**Decision:** Use real root system JSON files with pre-calculated expected values derived from independent validation (manual calculation, published results, or reference implementations).

**Rationale:**
- Scientific credibility requires testing against ground truth, not synthetic/mocked data
- Existing fixture pattern (`plantB_day11_json` with separate expected value fixtures) is proven and maintainable
- Enables regression detection if algorithm implementations drift

**Implementation:**
- Store JSON files in `tests/data/` with descriptive names
- Create parallel fixture functions returning expected values (lengths, angles, costs)
- Document validation methodology in `tests/data/README.md` (how expected values were derived)

### 2. Fixture Scope: Layered Approach

**Decision:** Provide three fixture tiers:
1. **Minimal synthetic graphs** (3-5 nodes) for unit testing mathematical functions
2. **Edge-case graphs** (single root, no laterals, extreme branching) for boundary testing
3. **Real datasets** (complete root systems) for integration and accuracy validation

**Rationale:**
- Minimal graphs enable fast, focused unit tests with hand-verifiable outputs
- Edge cases catch boundary conditions without complex fixture construction
- Real datasets validate end-to-end accuracy and scientific correctness

**Alternatives considered:**
- Only real datasets: Too slow, hard to isolate failures in specific functions
- Only synthetic: Insufficient confidence in scientific accuracy
- Generative fixtures: Not reproducible, defeats scientific validation purpose

### 3. Coverage Exclusion: GUI Module

**Decision:** Exclude `main.py` (GUI) from coverage requirements by adjusting `pyproject.toml` if needed, or accept lower overall coverage with commentary.

**Rationale:**
- GUI testing requires complex matplotlib interaction simulation
- Scientific accuracy depends on computation modules, not GUI
- Current coverage failure driven by 8.73% coverage in `main.py` (606/538 lines missed)
- Effort better spent on computation coverage than GUI mocking

**Implementation:**
- Focus tests on `pareto_functions.py` (68.23% → 90%+) and `quantify.py` (67.46% → 90%+)
- Document GUI testing strategy separately if interactive testing becomes priority
- Overall coverage will reach ~80% when computation modules achieve 90%+ (weighted by line count)

### 4. Reproducibility: Seeded Random Operations

**Decision:** All tests involving randomness (e.g., `random_tree()`) must use fixed seeds set in fixtures or test setup.

**Rationale:**
- Scientific reproducibility requires deterministic test outcomes
- Enables debugging (failures can be reliably reproduced)
- Aligns with scientific computing best practices

**Implementation:**
```python
@pytest.fixture
def random_seed():
    return 42

def test_random_tree(plantB_day11_json, random_seed):
    random.seed(random_seed)
    np.random.seed(random_seed)
    # test randomized operations
```

### 5. Assertion Strategy: Tolerance-Based Comparison

**Decision:** Use `math.isclose()` or `numpy.testing.assert_allclose()` with appropriate tolerances for floating-point comparisons, not exact equality.

**Rationale:**
- Floating-point arithmetic is non-deterministic across platforms
- Existing test pattern (`rel_tol=1e-8`) is appropriate for scientific precision
- Aligns with IEEE 754 best practices

**Already implemented correctly in `test_quantify.py:31-60`**

## Risks / Trade-offs

### Risk: Test Data Availability
**Risk:** Limited real root system datasets may constrain test coverage breadth
**Mitigation:**
- Start with existing `plantB_day11.json` (proven fixture)
- Generate 2-3 minimal synthetic datasets for edge cases
- Document process for adding new validated fixtures as data becomes available

### Risk: Test Execution Time
**Risk:** Multiple integration tests with Pareto front generation could slow CI
**Mitigation:**
- Target < 30 seconds total test time
- Use minimal graphs for unit tests (fast)
- Limit integration tests to 3-5 representative datasets
- Consider pytest markers (`@pytest.mark.slow`) for optional extended tests

### Trade-off: Coverage vs. Maintenance
**Trade-off:** High coverage requires many tests, increasing maintenance burden
**Acceptance:**
- Scientific software benefits justify maintenance cost
- Centralized fixtures reduce duplication
- Focus on critical computation paths, not every line (80% is sufficient, not 100%)

## Migration Plan

### Phase 1: Foundation (Tasks 1.1-1.5)
1. Add 2 new real root JSON fixtures with validated expected values
2. Create minimal synthetic graph fixtures
3. Document fixture validation methodology
4. No code changes to implementation

### Phase 2: Unit Tests (Tasks 2.1-3.8)
1. Expand `test_pareto_functions.py` with 15-20 unit tests
2. Expand `test_quantify.py` with 15-20 unit tests
3. No code changes to implementation (tests verify existing behavior)

### Phase 3: Integration & Validation (Tasks 4.1-6.4)
1. Add 2-3 end-to-end integration tests
2. Run coverage analysis and add targeted tests for gaps
3. Verify ≥80% coverage achieved
4. Confirm CI passes on all platforms

### Rollback
- If coverage target cannot be reached: Adjust threshold in `pyproject.toml` temporarily and document gap closure plan
- If tests reveal bugs: Fix bugs in separate PRs (not in this change)
- No implementation changes in this proposal = no rollback risk to production behavior

## Open Questions

1. **Expected value validation**: How were the existing expected values in `fixtures.py` (LR lengths, angles) originally calculated? Document methodology.
2. **Edge case priority**: Which edge cases are most scientifically relevant? (e.g., roots with no laterals, extremely tortuous roots)
3. **Performance baseline**: What is acceptable test execution time? (Proposed: < 30 seconds)
4. **Coverage adjustment**: Should `main.py` be explicitly excluded from coverage via omit directive, or accept overall ~75-80% with commentary?

**Recommendation:** Address questions 1-2 before implementing fixtures (affects test validity). Questions 3-4 can be resolved during implementation.