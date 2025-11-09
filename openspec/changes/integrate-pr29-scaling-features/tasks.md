# Tasks: Integrate PR #29 Scaling Features

## 1. Investigation & Planning

- [ ] 1.1 Review PR #29 code changes in detail
- [ ] 1.2 Identify all features to extract (scaling dialog, config module, visualization improvements)
- [ ] 1.3 Identify all breaking changes to avoid (conftest.py deletion, binary files, etc.)
- [ ] 1.4 Create feature branch from current `main`

## 2. Core Scaling Infrastructure

- [ ] 2.1 Create `src/ariadne_roots/config.py` with scaling configuration
- [ ] 2.2 Add scaling dialog to `AnalyzerUI` in `main.py`
- [ ] 2.3 Integrate config module with analysis workflow
- [ ] 2.4 Add tests for config module

## 3. Analysis Integration

- [ ] 3.1 Update `quantify.py` to apply scaling to measurements
- [ ] 3.2 Identify which fields should/shouldn't be scaled
- [ ] 3.3 Handle array fields (LR lengths, minimal lengths) separately
- [ ] 3.4 Add tests for scaled vs unscaled outputs

## 4. Visualization Improvements

- [ ] 4.1 Extract Pareto front centering improvements from PR #29
- [ ] 4.2 Apply to `pareto_functions.py`
- [ ] 4.3 Test visualization outputs
- [ ] 4.4 Ensure plots are well-centered

## 5. Test Coverage

- [ ] 5.1 Add unit tests for scaling dialog logic
- [ ] 5.2 Add integration tests for end-to-end scaling workflow
- [ ] 5.3 Verify tkinter mocking is preserved in `conftest.py`
- [ ] 5.4 Run full test suite and ensure 98%+ coverage

## 6. Repository Hygiene

- [ ] 6.1 Ensure no .DS_Store files are committed
- [ ] 6.2 Ensure test data goes in `tests/data/`, not `src/`
- [ ] 6.3 Verify .gitignore patterns are correct
- [ ] 6.4 Run `uv lock` to update lockfile if dependencies changed

## 7. Documentation & Validation

- [ ] 7.1 Update README if scaling feature needs documentation
- [ ] 7.2 Create OpenSpec specs for new capabilities
- [ ] 7.3 Run `openspec validate --strict`
- [ ] 7.4 Verify all CI checks pass

## 8. PR Management

- [ ] 8.1 Create new PR with rebased features
- [ ] 8.2 Link to PR #29 and credit @mplatre
- [ ] 8.3 Add comment to PR #29 explaining superseding
- [ ] 8.4 Request review and merge
