## Why

When the Analyzer GUI processes files, the interface appears frozen with no visual feedback. Users cannot tell if the application is working or has hung. The "Current files" label doesn't update visibly during analysis because the GUI event loop is blocked.

## What Changes

- Add `update_idletasks()` calls to force GUI refresh during the analysis loop
- Show "Analyzing N file(s)..." status immediately when analysis starts
- Update the current files display in real-time as each file is processed

## Impact

- Affected specs: gui (new capability)
- Affected code: `src/ariadne_roots/main.py` (AnalyzerUI.import_file method)