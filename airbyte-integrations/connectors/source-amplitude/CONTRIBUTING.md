# source-amplitude: Unique Behaviors

## 1. Matrix-Style API Response Extraction

Amplitude's Dashboard REST API (Average Session Length, Active Users) does not return records as individual objects. Instead, it returns parallel arrays: `xValues` contains dates and `series` contains nested value arrays. The connector uses custom extractors (`AverageSessionLengthRecordExtractor`, `ActiveUsersRecordExtractor`) to zip these arrays together and construct individual records.

For Active Users specifically, the `series` field is a 2D matrix (one row per metric label like "1 Day Active", "7 Day Active"), and the extractor transposes this matrix with `zip(*series)` before pairing with dates.

**Why this matters:** What looks like a single API response actually requires matrix transposition and array zipping to produce usable records. Adding a new analytics stream that uses this response format requires a custom extractor rather than a standard DpathExtractor.

## 2. Oversized Events Exports Are Split Automatically

Amplitude's Export API rejects an Events export with HTTP 400 when it exceeds 4GB and with HTTP 504 when too much data makes it time out. The `events` stream splits the rejected time window in half and retries each half using the CDK's `SPLIT_REQUEST_WINDOW` action, down to a one-hour window when `request_time_range` is 1024 hours or less. A split that succeeds never duplicates records; if a window is still rejected, the sync fails with a transient error and each retry re-reads the parts already read. Only the `events` stream does this; a 400 from the Dashboard REST API streams means something else.

**Why this matters:** Syncs whose time range grows past the export limit now recover on their own instead of failing until a user shortens `request_time_range`. See `AGENTS.md` for the exact limits and failure behavior.

## Incremental Stream Considerations

The connector is manifest-only: every stream is declared in `manifest.yaml`, and `components.py` holds only custom extractors and a datetime transformation. Incremental streams (`events`, `average_session_length`, `active_users`) use `DatetimeBasedCursor`.
