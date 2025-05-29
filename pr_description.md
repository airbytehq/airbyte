## What
Modified the timestamp validation regex in CustomFormatChecker to make timezone component optional.

## Why  
Timestamp without timezone fields were incorrectly triggering RFC 3339 validation warnings despite data being written correctly.

## How
Changed timestamp_regex pattern from `.*$` to `.*?$` to make timezone matching optional while maintaining backward compatibility.

Fixes validation errors like: "does not match the date-time pattern must be a valid RFC 3339 date-time" for timestamp_without_timezone fields.

Link to Devin run: https://app.devin.ai/sessions/5e7c54d3c0624097a762caf133c8f3b8

Requested by: Matt Bayley (matt.bayley@airbyte.io)
