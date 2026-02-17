## Why

The documentation created in `update-documentation-dry` contains field name discrepancies, missing fields, stale line number references, and excessive formatting emphasis that reduces readability. Scientific documentation must precisely match the code to be useful for researchers.

## What Changes

- Fix 12+ field name discrepancies in `docs/output-fields.md` to match actual code output
- Add missing `Convex Hull Area` field documentation
- Replace brittle line number references with stable function name references in `docs/scientific-methods.md`
- Reduce excessive underlining/emphasis to improve readability
- Fix duplicate author name in reference section
- Correct line number ranges in code reference table

## Impact

- Affected specs: documentation
- Affected files: `docs/output-fields.md`, `docs/scientific-methods.md`
- No breaking changes - documentation corrections only
- Critical for scientific accuracy - researchers rely on exact field names