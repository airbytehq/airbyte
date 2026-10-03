> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-amplitude: Unique Behaviors

## 1. Matrix-Style API Response Extraction

Amplitude's Dashboard REST API (Average Session Length, Active Users) does not return records as individual objects. Instead, it returns parallel arrays: `xValues` contains dates and `series` contains nested value arrays. The connector uses custom extractors (`AverageSessionLengthRecordExtractor`, `ActiveUsersRecordExtractor`) to zip these arrays together and construct individual records.

For Active Users specifically, the `series` field is a 2D matrix (one row per metric label like "1 Day Active", "7 Day Active"), and the extractor transposes this matrix with `zip(*series)` before pairing with dates.

**Why this matters:** What looks like a single API response actually requires matrix transposition and array zipping to produce usable records. Adding a new analytics stream that uses this response format requires a custom extractor rather than a standard DpathExtractor.

## 2. Oversized Events Exports Are Split Automatically

The Export API (`/2/export`, used only by the `events` stream) returns HTTP 400 when an export exceeds 4GB and HTTP 504 when too much data makes it time out. Both response filters on the `events` stream use `action: SPLIT_REQUEST_WINDOW`, and its retriever declares `request_window_splitting`, so the CDK splits the rejected window in half and reads each half, recursively.

- The filters match on status code alone. Amplitude documents 400 and 504 on this endpoint only as data-volume errors and does not document an error body to match on. Do not add a `predicate` or `error_message_contains` next to `http_codes`: `HttpResponseFilter` ORs its conditions, so the status code would still match every 400/504.
- The window floor is the cursor's `PT1H` granularity. The CDK also stops after 10 splits. With the default 24-hour `request_time_range`, the 1-hour floor is reached within 5 splits; a `request_time_range` above 1024 hours hits the 10-split cap first (the 8760-hour maximum stops at windows of about 9 hours). Lowering `request_time_range` lets the split reach smaller windows.
- If a window is still rejected at that point, the stream fails with a `transient_error` carrying the `failure_message` from `request_window_splitting`. The platform retries `transient_error` attempts, and each retry repeats the splits.
- The export is a single zip file per window with no pagination, so the error always arrives before any record is emitted. Splitting never re-emits records.
- The Dashboard REST API streams (`active_users`, `average_session_length`, `annotations`, `cohorts`, `events_list`) carry similar 400/504 filters, but a 400 there means something else (for example "Invalid chart definition" for `active_users`), so those streams must not split on it.

The mechanism comes from airbytehq/airbyte-python-cdk#1171.

## Incremental Stream Considerations

The connector is manifest-only: every stream is declared in `manifest.yaml`. `components.py` holds only custom record extractors (`AverageSessionLengthRecordExtractor`, `ActiveUsersRecordExtractor`) and the `TransformDatetimesToRFC3339` transformation, referenced by `class_name`. Incremental streams (`events`, `average_session_length`, `active_users`) use `DatetimeBasedCursor`.
