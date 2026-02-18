## Why

The new 3D Pareto analysis features (issues #53, #54) are not documented. Scientific references and calculation explanations are scattered, making them hard to find for researchers using this scientific software. The README's RSA traits list is incomplete and doesn't explain the underlying scientific methods.

## What Changes

- Create `docs/` directory with structured scientific documentation
- Add `docs/scientific-methods.md` explaining Pareto optimality calculations with full references
- Add `docs/output-fields.md` with complete field reference (2D and 3D)
- Update README.md with prominent links to new docs and add 3D fields to traits list
- Keep scientific references in docstrings for developer convenience (accessible duplication)
- Ensure new documentation is easily discoverable from README

## Impact

- Affected specs: documentation (new capability)
- Affected files: README.md, new `docs/` directory
- No breaking changes - documentation only
- Improves accessibility for scientists and developers