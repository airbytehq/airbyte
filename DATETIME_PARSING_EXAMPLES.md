# Datetime Parsing Simplification Examples

This document demonstrates how the enhanced DatetimeBasedCursor with robust datetime parsing fallback eliminates the need for explicit `cursor_datetime_formats` in many cases.

## Changes Made

### source-recurly
**Before:**
```yaml
cursor_datetime_formats:
  - "%Y-%m-%dT%H:%M:%SZ"
datetime_format: "%Y-%m-%dT%H:%M:%SZ"
```

**After:**
```yaml
datetime_format: "%Y-%m-%dT%H:%M:%SZ"
```

**Rationale:** The `cursor_datetime_formats` was identical to `datetime_format`, making it redundant. The robust parsing fallback can handle this standard ISO format automatically.

### source-instagram
**Before:**
```yaml
datetime_format: "%Y-%m-%dT%H:%M:%S+00:00"
cursor_datetime_formats:
  - "%Y-%m-%dT%H:%M:%S+00:00"
```

**After:**
```yaml
datetime_format: "%Y-%m-%dT%H:%M:%S+00:00"
```

**Rationale:** The `cursor_datetime_formats` specified a standard ISO8601/RFC3339 format that the robust parsing fallback can handle automatically.

## Benefits

1. **Simplified Configuration:** Eliminates redundant datetime format specifications
2. **Reduced Errors:** Robust fallback parsing prevents failures on valid datetime formats
3. **Backward Compatibility:** Existing configurations continue to work unchanged
4. **Future-Proof:** New datetime formats are automatically supported without configuration changes

## How It Works

The enhanced DatetimeBasedCursor now:
1. First tries the `datetime_format` (if provided)
2. Falls back to robust parsing using `ab_datetime_try_parse` for any ISO8601/RFC3339 compliant format
3. Only raises an error if the datetime string is truly unparseable

This eliminates the need to specify `cursor_datetime_formats` for standard datetime formats while maintaining full backward compatibility.
