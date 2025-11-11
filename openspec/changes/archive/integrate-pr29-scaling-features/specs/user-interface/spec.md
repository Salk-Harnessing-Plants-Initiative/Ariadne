# Spec: User Interface

This spec defines the user interface requirements for Ariadne's root analysis application.

## ADDED Requirements

### Requirement: Scaling Configuration Dialog

Users SHALL be able to configure measurement scaling before performing analysis, allowing conversion from pixel measurements to real-world units.

#### Scenario: Scaling dialog appears at analyzer startup

- **GIVEN** user launches the Analyzer UI
- **WHEN** the AnalyzerUI initializes
- **THEN** a modal dialog SHALL prompt for scaling configuration
- **AND** the dialog SHALL block further interaction until scale is set

#### Scenario: User provides valid scaling parameters

- **GIVEN** the scaling dialog is displayed
- **WHEN** user enters:
  - Distance in pixels (positive number)
  - Distance in real units (positive number)
  - Unit of length (e.g., "mm", "cm")
- **THEN** the system SHALL calculate scale factor as `real_dist / pixels`
- **AND** SHALL store the scale factor and unit for analysis
- **AND** SHALL display confirmation message showing "1 pixel = X.XXXX [unit]"

#### Scenario: Live scale calculation feedback

- **GIVEN** the scaling dialog is displayed
- **WHEN** user types values in any field
- **THEN** the calculated scale SHALL update in real-time
- **AND** SHALL display as "Result: 1 pixel = X.XXXX [unit]"

#### Scenario: Invalid scaling parameters rejected

- **GIVEN** the scaling dialog is displayed
- **WHEN** user enters zero, negative, or non-numeric values
- **THEN** the system SHALL show an error message
- **AND** SHALL NOT close the dialog
- **AND** SHALL require valid input before proceeding

#### Scenario: Default scaling values

- **GIVEN** no user input has been provided
- **WHEN** AnalyzerUI initializes
- **THEN** default scale factor SHALL be 1.0
- **AND** default unit SHALL be "px" (pixels)
