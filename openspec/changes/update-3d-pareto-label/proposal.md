## Why

The current 3D Pareto checkbox label ("Include 3D Pareto analysis (slower)") does not communicate what additional metric is being evaluated. Users cannot make an informed decision without understanding that 3D adds path tortuosity analysis.

## What Changes

- Update checkbox label from "Include 3D Pareto analysis (slower)" to "Add path tortuosity to Pareto (3D, slower)"
- This makes the key addition (path tortuosity) immediately visible while keeping the performance warning

## Impact

- Affected specs: gui (new capability)
- Affected code: [main.py:1087](src/ariadne_roots/main.py#L1087)