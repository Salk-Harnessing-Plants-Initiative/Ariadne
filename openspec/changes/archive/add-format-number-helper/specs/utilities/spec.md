# Utilities Specification

## ADDED Requirements

### Requirement: Format Number Helper

The system SHALL provide a utility function for consistent decimal formatting of numeric values.

#### Scenario: Format float value
- **GIVEN** a float value like `3.14159265359`
- **WHEN** `format_number(value, decimals=2)` is called
- **THEN** the function returns `"3.14"`

#### Scenario: Format with default precision
- **GIVEN** a float value
- **WHEN** `format_number(value)` is called without decimals parameter
- **THEN** the function returns the value formatted to 6 decimal places

#### Scenario: Non-float value passthrough
- **GIVEN** a non-float value (int, string, None)
- **WHEN** `format_number(value)` is called
- **THEN** the function returns the original value unchanged

#### Scenario: Integer input
- **GIVEN** an integer value like `42`
- **WHEN** `format_number(value)` is called
- **THEN** the function returns `42` (not `"42.000000"`)
