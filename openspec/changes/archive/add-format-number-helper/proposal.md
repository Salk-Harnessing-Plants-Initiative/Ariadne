# Add Format Number Helper

## Why

When outputting numeric values to CSV or display, consistent decimal formatting improves readability and data consistency. Matt Platre's branch includes a `format_number()` helper function for this purpose.

However, this feature has **low priority** because:
1. Python's built-in formatting already works well
2. Our CSV output uses Python floats which serialize cleanly
3. The helper is only useful if we need consistent string formatting

## What Changes

### New Function: `format_number()` in `quantify.py`

```python
def format_number(value, decimals=6):
    """Format a number to specified decimal places if it's a float.

    Args:
        value: The value to format
        decimals: Number of decimal places (default: 6)

    Returns:
        Formatted string if float, original value otherwise
    """
    if isinstance(value, float):
        return format(value, f'.{decimals}f')
    return value
```

### Usage

The function can be used when formatting output for display or when specific decimal precision is required in string output.

## Impact

- **CSV Output**: No change (we store floats, not formatted strings)
- **Display**: Optional use for consistent formatting
- **Dependencies**: None (pure Python)

## Recommendation

Consider deferring this feature unless there's a specific need for formatted string output. The current float-based output works well for CSV serialization.
