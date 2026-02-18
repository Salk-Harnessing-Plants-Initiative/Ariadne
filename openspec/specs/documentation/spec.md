# documentation Specification

## Purpose
TBD - created by archiving change fix-documentation-accuracy. Update Purpose after archive.
## Requirements
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

The project SHALL provide a `docs/scientific-methods.md` file that documents all scientific calculations with full academic references.

The documentation MUST include:
- Pareto optimality calculations (2D and 3D)
- Multiplicative ε-indicator definition and interpretation
- Barycentric interpolation methodology
- Random tree baseline generation
- Complete bibliographic references with DOIs

#### Scenario: Researcher finds calculation reference
- **GIVEN** a researcher using Ariadne for plant phenotyping
- **WHEN** they need to understand or cite the Pareto calculations
- **THEN** they can find complete scientific references in `docs/scientific-methods.md`
- **AND** the references include DOIs for direct access to source papers

#### Scenario: Developer understands algorithm
- **GIVEN** a developer modifying the Pareto analysis code
- **WHEN** they need to understand the mathematical basis
- **THEN** they can find formulas and explanations in `docs/scientific-methods.md`
- **AND** the documentation cross-references relevant code locations

### Requirement: Output Fields Documentation

The project SHALL provide a `docs/output-fields.md` file that documents all CSV output fields with descriptions, units, and expected value ranges.

The documentation MUST include:
- All 2D Pareto fields (alpha, scaling distance to front)
- All 3D Pareto fields (alpha_3d, beta_3d, gamma_3d, epsilon_3d, epsilon components)
- Corner cost reference fields (Steiner, Satellite, Coverage)
- Random tree comparison fields
- Units for each field
- Expected value ranges and interpretation guidance

#### Scenario: User interprets CSV output
- **GIVEN** a user analyzing Ariadne CSV output
- **WHEN** they encounter an unfamiliar field name
- **THEN** they can find the field in `docs/output-fields.md`
- **AND** the documentation explains what the field measures and how to interpret it

#### Scenario: 3D analysis fields documented
- **GIVEN** a user with 3D Pareto analysis enabled
- **WHEN** they view the output CSV
- **THEN** all 3D fields (epsilon_3d, alpha_3d, beta_3d, gamma_3d, epsilon components) are documented
- **AND** the relationship between α + β + γ = 1 is explained

### Requirement: Documentation Discoverability

The README SHALL prominently link to detailed documentation to ensure discoverability.

The README MUST include:
- A "Documentation" section visible without excessive scrolling
- Direct links to `docs/scientific-methods.md` and `docs/output-fields.md`
- Brief descriptions of what each documentation file contains

#### Scenario: New user finds documentation
- **GIVEN** a new user visiting the GitHub repository
- **WHEN** they read the README
- **THEN** they find links to detailed documentation within the first few sections
- **AND** the links have clear descriptions of their content

#### Scenario: PyPI user finds documentation
- **GIVEN** a user who installed from PyPI
- **WHEN** they visit the PyPI page or GitHub repository
- **THEN** documentation links in the README work correctly
- **AND** relative links resolve to the correct files

### Requirement: Scientific Accuracy Verification

All documentation MUST be verified for scientific accuracy before publication since this serves as the authoritative reference for scientific code and results.

The verification process MUST include:
- Cross-referencing all formulas against source code implementation
- Verifying definitions match cited academic papers
- Confirming field descriptions match actual code output
- Domain expert review before merge

#### Scenario: Formula matches implementation
- **GIVEN** a formula documented in `docs/scientific-methods.md`
- **WHEN** compared against the source code
- **THEN** the documented formula exactly matches the implementation
- **AND** any approximations or simplifications are explicitly noted

#### Scenario: Field description matches output
- **GIVEN** a field description in `docs/output-fields.md`
- **WHEN** analysis is run on test data
- **THEN** the actual CSV output matches the documented description
- **AND** value ranges fall within documented expectations

#### Scenario: Citation accuracy
- **GIVEN** an academic reference cited for a calculation
- **WHEN** the original paper is consulted
- **THEN** the documented formula matches the paper's definition
- **AND** any adaptations for this implementation are clearly noted

