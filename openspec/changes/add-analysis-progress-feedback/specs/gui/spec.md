## ADDED Requirements

### Requirement: Analysis Progress Feedback

The Analyzer GUI SHALL provide visual feedback to users during the analysis process so they can see the application is actively working.

#### Scenario: Analysis status shown at start
- **WHEN** user initiates analysis of one or more files
- **THEN** the GUI SHALL immediately display "Analyzing N file(s)..." where N is the count of selected files
- **AND** the GUI SHALL remain responsive (not appear frozen)

#### Scenario: Current file list updates during analysis
- **WHEN** the analysis loop begins processing each file
- **THEN** the GUI SHALL update the "Current files" display to show each filename as it is processed
- **AND** the display SHALL update in real-time (not batch at the end)

#### Scenario: GUI remains responsive during long analysis
- **WHEN** analysis is running on multiple files
- **THEN** the GUI event loop SHALL be allowed to process updates via `update_idletasks()`
- **AND** the interface SHALL not appear frozen or unresponsive