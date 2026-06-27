# source-google-sheets: Unique Behaviors

## 1. Schema Derived from Row 1 with Positional Value Matching

Google Sheets has no formal schema. The connector derives each stream's schema by reading row 1 of each sheet as column headers. All subsequent rows are matched to these headers by cell position, not by any key in the data. If row 1 has headers `["Name", "Age", "City"]`, then the third cell in every data row is assumed to be "City" regardless of its actual content.

Duplicate headers are automatically deduplicated by appending the column letter (e.g., two columns named "Name" become "Name_A1" and "Name_C1"). Empty header cells terminate header parsing by default, but when `read_empty_header_columns` is enabled, empty headers get generated names like "column_C".

**Why this matters:** The schema is entirely user-controlled via spreadsheet headers and can change between syncs if someone edits row 1. A renamed or reordered column silently shifts which data maps to which field, potentially corrupting downstream data without any error being raised. The positional matching also means that a row with fewer cells than headers will simply have missing fields rather than misaligned data.

## 2. Batch Row Fetching with Per-Request Timeout Constraint

Large sheets are fetched in configurable row batches (default 1,000,000 rows per batch) via `RangePartitionRouter`. Each batch is a separate Google Sheets API request. Google enforces a 180-second per-request timeout, so wide sheets (many columns) with large batch sizes may hit this limit before all rows in the batch are returned.

**Why this matters:** A sheet with many columns may need a smaller `batch_size` to avoid 180-second timeouts, even if the total row count is modest. The default of 1M rows assumes relatively narrow sheets, and there is no automatic fallback if a batch times out.
