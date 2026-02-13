## 1. Fix Field Names in output-fields.md

- [x] 1.1 Fix `Tortuosity (Material/Total Distance Ratio)` → `Tortuosity`
- [x] 1.2 Fix `PR minimal length` → `PR_minimal_length` (underscore)
- [x] 1.3 Fix `Total minimal distance` → `Total minimal Distance` (capital D)
- [x] 1.4 Fix zone field capitalization (Basal Zone, Branched Zone, Apical Zone)
- [x] 1.5 Fix `Mean LR minimal distances` → `Mean LR minimal lengths`
- [x] 1.6 Fix `Median LR minimal distances` → `Median LR minimal lengths`
- [x] 1.7 Fix `Sum LR minimal distances` → `sum LR minimal lengths` (lowercase, lengths)
- [x] 1.8 Fix `LR minimal distance` → `LR minimal lengths` (plural, lengths)
- [x] 1.9 Fix `Barycentre` → `Barycenter` (American spelling)
- [x] 1.10 Add missing `Convex Hull Area` field

## 2. Improve Formatting in output-fields.md

- [x] 2.1 Remove excessive backtick formatting on field names in prose (keep in tables)
- [x] 2.2 Reduce bold/emphasis to key concepts only
- [x] 2.3 Ensure consistent formatting throughout

## 3. Fix scientific-methods.md

- [x] 3.1 Replace line number references with function name references
- [x] 3.2 Remove stale line ranges entirely (use function names instead)
- [x] 3.3 Fix duplicate author "Bhattacharjee, S." in reference #4
- [x] 3.4 Reduce excessive emphasis/formatting

## 4. Fix Descriptions (Post-Verification)

- [x] 4.1 Fix `Travel distance` description: "lateral root tip" → "root tip" (includes PR tip)
- [x] 4.2 Fix Reference #4: wrong title and authors (was "A connectomic approach..." by Pedmale, Stevens; now "Network trade-offs and homeostasis in Arabidopsis shoot architectures" by Chandrasekhar, van Rongen, Leyser)
- [x] 4.3 Fix Random Tree description: "lateral root tips" → "root tips" (includes PR tip)

## 5. Validation

- [x] 5.1 Run `openspec validate fix-documentation-accuracy --strict`
- [x] 5.2 Verify all field names match code output exactly
- [x] 5.3 Test internal documentation links
- [x] 5.4 Verify all scientific references against DOIs