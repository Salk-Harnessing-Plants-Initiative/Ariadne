## Why

When the Analyzer GUI processes files, the interface appears frozen with no visual feedback. Users cannot tell if the application is working or has hung. The "Current files" label doesn't update visibly during analysis because the GUI event loop is blocked.

Additionally, when the label text updates with filenames, the layout shifts causing the "Load file(s)" button to appear duplicated (rendering artifact from the old and new positions overlapping during partial redraws).

The current layout also has visual issues: text is centered in a large empty space instead of being left-aligned at the top, making the interface look unprofessional.

## What Changes

- Add `update_idletasks()` calls to force GUI refresh during the analysis loop
- Show "Analyzing N file(s)..." status immediately when analysis starts
- Update the current files display in real-time as each file is processed
- Disable the Load button during analysis to prevent re-clicks
- **Fix layout stability**: Give left_frame a fixed width to prevent button position shifts when label text changes
- **Polish visual layout**: Left-align text at top, add padding for cleaner appearance

## Impact

- Affected specs: gui (new capability)
- Affected code: `src/ariadne_roots/main.py` (AnalyzerUI.__init__ and import_file methods)