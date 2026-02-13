## MODIFIED Requirements

### Requirement: Output Field Documentation

The system SHALL provide documentation of all CSV output fields with exact field names matching the code.

Field names MUST exactly match the strings used in `quantify.py` including:
- Capitalization (e.g., `Basal Zone length` not `Basal zone length`)
- Spacing vs underscores (e.g., `PR_minimal_length` not `PR minimal length`)
- Word choice (e.g., `lengths` not `distances` for LR minimal fields)
- Spelling (e.g., `Barycenter` not `Barycentre`)

#### Scenario: Field name accuracy verification
- WHEN a user reads the documentation for a field
- THEN the documented field name exactly matches the CSV column header produced by the code

#### Scenario: Complete field coverage
- WHEN documentation lists output fields
- THEN all fields produced by `quantify.analyze()` are documented including `Convex Hull Area`

### Requirement: Scientific Methods Documentation

The system SHALL provide documentation of scientific methods with stable code references.

Code references SHOULD use function names rather than line numbers to avoid becoming stale when code changes.

#### Scenario: Stable code references
- WHEN documentation references implementation code
- THEN references use function names (e.g., `distance_from_front_3d()`) rather than line numbers alone

#### Scenario: Readable formatting
- WHEN documentation uses emphasis (bold, backticks)
- THEN emphasis is used sparingly for key concepts, not on every field name in prose