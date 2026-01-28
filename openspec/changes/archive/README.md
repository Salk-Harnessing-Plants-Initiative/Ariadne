# Archived OpenSpec Changes

This directory contains completed OpenSpec changes that have been implemented and merged.

---

## add-format-number-helper (January 2026)
**Status**: ⏸️ Deferred - Tracked in issue #47

Utility function for formatting floats to a specified number of decimal places. Originated from Matt Platre's MATT_P branch (PR #29). Deferred as low priority — the function was never called in the original branch.

- **Proposal**: [proposal.md](add-format-number-helper/proposal.md)
- **Tasks**: [tasks.md](add-format-number-helper/tasks.md)
- **Related Issue**: #47
- **Original PR**: #29

**Recommendation**: Defer until a concrete use case arises (e.g., GUI display panel, formatted reporting).

---

## add-alpha-interpolation (January 2026)
**Status**: ✅ Completed - Merged in PR #43

Added distance-weighted linear interpolation for more precise characteristic alpha values in Pareto front analysis. Based on Matt Platre's implementation in the MATT_P branch.

- **Proposal**: [proposal.md](add-alpha-interpolation/proposal.md)
- **Tasks**: [tasks.md](add-alpha-interpolation/tasks.md)
- **Related PR**: #43
- **Original PR**: #29

**Key Deliverables**:
- `distance_from_front()` now interpolates between the two closest discrete alpha values
- Division-by-zero guard for zero-value Pareto front points
- `math.isclose()` for robust float comparison
- Returns Python floats (not strings) for clean CSV serialization
- 4 new tests for interpolation, edge cases, and type validation
- Comprehensive CSV output validation tests (`tests/test_csv_output.py`)

**Timeline**: 1 day (including Copilot review feedback)

---

## add-tradeoff-calculation (January 2026)
**Status**: ✅ Completed - Merged in PR #44

Added `calculate_tradeoff()` function to quantify how close an actual root architecture is to theoretically optimal Steiner/Satellite architectures. Inspired by Conn et al., 2019 (https://doi.org/10.1371/journal.pcbi.1007325).

- **Proposal**: [proposal.md](add-tradeoff-calculation/proposal.md)
- **Tasks**: [tasks.md](add-tradeoff-calculation/tasks.md)
- **Related PR**: #44
- **Original PR**: #29

**Key Deliverables**:
- New `calculate_tradeoff()` function with Conn et al. citation in docstring
- 7 new CSV output fields: Tradeoff, Steiner_length, Steiner_distance, Satellite_length, Satellite_distance, Actual_ratio, Optimal_ratio
- Dimensionless ratio fields excluded from scaling transformation
- 9 tradeoff tests + 1 scaling test covering all edge cases
- Integration test validates against real plant data (Tradeoff = 2.5128)
- 143 tests pass, 98.23% coverage

**Timeline**: 2 days (including two rounds of Copilot review feedback)

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

## add-pr27-edge-case-tests (November 2025)
**Status**: ✅ Completed - Merged in PR #32

Added comprehensive edge case tests for the UnboundLocalError bug fix (issue #26), ensuring 100% coverage on the diff and fixing previously skipped tests.

- **Proposal**: [proposal.md](add-pr27-edge-case-tests/proposal.md)
- **Tasks**: [tasks.md](add-pr27-edge-case-tests/tasks.md)
- **Spec**: [spec.md](add-pr27-edge-case-tests/specs/root-analysis/spec.md)
- **Related PR**: #32 (supersedes #27)
- **Related Issue**: #26

**Key Deliverables**:
- Added `issue26_root_json` fixture with real Arabidopsis root data (5559-line tree-formatted JSON)
- Added `test_calc_len_LRs_nonzero_start_index()` to test LR indices starting at 1
- Added `test_calc_len_LRs_with_distances_nonzero_start_index()` for the same edge case
- Fixed and unskipped `test_calc_len_LRs_simple()` using proper LR_index convention and `nx.bfs_tree()`
- Updated `.gitignore` to exclude `coverage.json`
- 100% coverage on PR #27 diff lines (4 executable lines)
- Test suite: 81 passed (previously 80 passed, 1 skipped)
- Overall coverage: 98.31% (maintained above 98% threshold)

**Bug Fix Context**:
Original fix by @pradal addressed `UnboundLocalError` when lateral root indices don't start at 0. The fix calculates `min_num_LRs = min(idxs.values())` and uses `range(min_num_LRs, num_LRs)` instead of `range(num_LRs)` in both `calc_len_LRs()` and `calc_len_LRs_with_distances()`.

**Timeline**: 1 day (including investigation of LR_index conventions and test fixture debugging)

---

## integrate-pr29-scaling-features (November 2024)
**Status**: ✅ Completed - Merged in PR #33

Integrated PR #29 scaling features onto current main branch with proper test coverage and CI compatibility.

- **Proposal**: [proposal.md](integrate-pr29-scaling-features/proposal.md)
- **Tasks**: [tasks.md](integrate-pr29-scaling-features/tasks.md)
- **Related PR**: #33
- **Original PR**: #29

**Key Deliverables**:
- Custom scaling dialog for converting pixel measurements to real-world units
- Support for mm, cm, and µm unit selection in GUI
- Automated scaling transformation applied to all measurements in CSV output
- Improved Pareto front visualization with better graph centering
- Config module (`config.py`) for global scaling configuration
- Preserved tkinter mocking and test infrastructure
- Maintained 98.38% coverage

**Timeline**: Rebased and integrated with full test coverage

---

## add-scaling-tests (November 2024)
**Status**: ✅ Completed - Merged in PR #33

Added comprehensive unit tests for the scaling logic introduced in PR #29.

- **Proposal**: [proposal.md](add-scaling-tests/proposal.md)
- **Tasks**: [tasks.md](add-scaling-tests/tasks.md)
- **Related PR**: #33

**Key Deliverables**:
- Unit tests for config module (default values, custom values, state persistence)
- Unit tests for scaling transformation logic (excluded fields, numeric fields, arrays, edge cases)
- Tests for buffer calculation edge cases (zero values, negative coordinates)
- 15 new tests covering scaling functionality
- Maintained 98.38% overall coverage

**Timeline**: Implemented alongside feature integration in PR #33

---

## add-development-commands (November 2024)
**Status**: ✅ Completed - Merged in PR #41

Added comprehensive development commands for managing the Ariadne project, including test, changelog, and release workflows.

- **Proposal**: [proposal.md](add-development-commands/proposal.md)
- **Tasks**: [tasks.md](add-development-commands/tasks.md)
- **Related PR**: #41
- **Related Issue**: #35

**Key Deliverables**:
- `/test` command for running pytest with common options and filters
- `/changelog` command for maintaining CHANGELOG.md following Keep a Changelog format
- `/release` command for complete PyPI release workflow with command integrations
- CHANGELOG.md file following Keep a Changelog format
- OpenSpec proposal system for managing development changes
- Comprehensive command integration (test, coverage, lint, changelog, pr-description, review-pr, release, cleanup-merged)

**Timeline**: 1-2 hours (as estimated)

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
