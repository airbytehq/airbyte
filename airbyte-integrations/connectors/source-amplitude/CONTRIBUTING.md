# source-amplitude: Unique Behaviors

## 1. Matrix-Style API Response Extraction

Amplitude's Dashboard REST API (Average Session Length, Active Users) does not return records as individual objects. Instead, it returns parallel arrays: `xValues` contains dates and `series` contains nested value arrays. The connector uses custom extractors (`AverageSessionLengthRecordExtractor`, `ActiveUsersRecordExtractor`) to zip these arrays together and construct individual records.

For Active Users specifically, the `series` field is a 2D matrix (one row per metric label like "1 Day Active", "7 Day Active"), and the extractor transposes this matrix with `zip(*series)` before pairing with dates.

**Why this matters:** What looks like a single API response actually requires matrix transposition and array zipping to produce usable records. Adding a new analytics stream that uses this response format requires a custom extractor rather than a standard DpathExtractor.

## 2. Hard Export Size Limit with Timeout Fallback

Amplitude's API enforces a 4GB export size limit, returning HTTP 400 when exceeded. Additionally, large data volumes can trigger HTTP 504 timeouts. Amplitude's own documentation recommends using their Amazon S3 destination for large exports instead of the REST API. The connector surfaces these as config errors with guidance to shorten the `request_time_range` interval.

**Why this matters:** Syncs that work fine for small date ranges can suddenly fail when the date range grows large enough to exceed 4GB or trigger a timeout, with no way to resume from where it left off within that range.
