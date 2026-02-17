## ADDED Requirements

### Requirement: 3D Pareto Option Label Clarity

The Analyzer UI 3D Pareto checkbox SHALL clearly indicate that enabling 3D analysis adds path tortuosity as an additional optimization dimension.

The label text SHALL be: "Add path tortuosity to Pareto (3D, slower)"

#### Scenario: User sees descriptive 3D option label
- **GIVEN** the user opens the Analyzer scale configuration dialog
- **WHEN** the 3D Pareto checkbox is displayed
- **THEN** the checkbox label reads "Add path tortuosity to Pareto (3D, slower)"
- **AND** the user understands that 3D adds path tortuosity analysis