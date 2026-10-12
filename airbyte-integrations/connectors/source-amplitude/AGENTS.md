> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-amplitude: Unique Behaviors

## 1. Matrix-Style API Response Extraction

Amplitude's Dashboard REST API (Average Session Length, Active Users) does not return records as individual objects. Instead, it returns parallel arrays: `xValues` contains dates and `series` contains nested value arrays. The connector uses custom extractors (`AverageSessionLengthRecordExtractor`, `ActiveUsersRecordExtractor`) to zip these arrays together and construct individual records.

For Active Users specifically, the `series` field is a 2D matrix (one row per metric label like "1 Day Active", "7 Day Active"), and the extractor transposes this matrix with `zip(*series)` before pairing with dates.

**Why this matters:** What looks like a single API response actually requires matrix transposition and array zipping to produce usable records. Adding a new analytics stream that uses this response format requires a custom extractor rather than a standard DpathExtractor.

## 2. Oversized Events Exports Are Split Automatically

The Export API (`/2/export`, used only by the `events` stream) returns HTTP 400 when an export exceeds 4GB and HTTP 504 when too much data makes it time out. Both response filters on the `events` stream use `action: SPLIT_REQUEST_WINDOW`, and its retriever declares `request_window_splitting`, so the CDK splits the rejected window in half and reads each half, recursively.

- The filters match on status code alone. Amplitude documents 400 and 504 on this endpoint only as data-volume errors and does not document an error body to match on. Do not add a `predicate` or `error_message_contains` next to `http_codes`: `HttpResponseFilter` ORs its conditions, so the status code would still match every 400/504.
- The window floor is the cursor's `PT1H` granularity. The CDK also stops after 10 splits. With the default 24-hour `request_time_range`, the 1-hour floor is reached within 5 splits; a `request_time_range` above 1024 hours hits the 10-split cap first (the 8760-hour maximum stops at windows of 8-9 hours). Only a `request_time_range` of 1024 hours or less lets the split reach the 1-hour floor.
- If a window is still rejected at that point, the stream fails with a `transient_error` carrying the `failure_message` from `request_window_splitting`. The platform retries `transient_error` attempts, and each retry repeats the splits and re-reads the halves that already succeeded, because the failed partition is never checkpointed (Append + Deduped removes them by the `uuid` primary key). An hour over 4GB can only be exported with Amplitude's Amazon S3 export.
- The export is a single zip file per window with no pagination, so the error always arrives before any record of that window is emitted. A split that succeeds never re-emits records.
- Splitting is not remembered: it restarts for every window, attempt and sync. A 24-hour window that only 1-hour windows fit costs 47 requests instead of 24, so projects whose windows split on most syncs should lower `request_time_range`.
- The Dashboard REST API streams (`active_users`, `average_session_length`, `annotations`, `cohorts`, `events_list`) must not split: a 400 there means something else (for example "Invalid chart definition" for `active_users`), so they fail with a `config_error` that shows Amplitude's own `error.message` and `error.metadata.details`. Their 504s use the CDK default (retry with backoff, then `transient_error`).

The mechanism comes from airbytehq/airbyte-python-cdk#1171.

**Why this matters:** Oversized windows now recover without a config change, within two hard limits: an hour of data over 4GB fails on every retry (only Amplitude's Amazon S3 export can move it), and above 1024 hours the 10-split cap can stop at windows that are still too large until `request_time_range` is lowered.

## Incremental Stream Considerations

The connector is manifest-only: every stream is declared in `manifest.yaml`. `components.py` holds only custom record extractors (`AverageSessionLengthRecordExtractor`, `ActiveUsersRecordExtractor`) and the `TransformDatetimesToRFC3339` transformation, referenced by `class_name`. Incremental streams (`events`, `average_session_length`, `active_users`) use `DatetimeBasedCursor`.
