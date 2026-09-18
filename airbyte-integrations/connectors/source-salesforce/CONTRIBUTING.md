# source-salesforce: Unique Behaviors

## 1. Dynamic sObject-Based Stream Generation

This connector generates streams entirely at runtime from the Salesforce sObject metadata API. The `Salesforce.get_validated_streams()` method queries the org's available sObjects, filters by user configuration (selected streams, exclusion lists), and generates one stream per sObject. Each stream's schema is built dynamically by calling the Describe API for each sObject and mapping Salesforce field types to JSON Schema types via `field_to_property_schema()` in `api.py`.

## 2. Automatic Cursor Detection

The connector automatically detects the best cursor field for each sObject using a priority hierarchy in `api.py:get_pk_and_replication_key()`:

1. `SystemModstamp` (preferred — most reliable system-maintained timestamp)
2. `LastModifiedDate` (fallback for sObjects without SystemModstamp)
3. `CreatedDate` (fallback — only tracks new records, not updates)
4. `LoginTime` (special case for login-related sObjects)

If none of these fields exist in the sObject's schema, the stream is created as full-refresh.

## 3. Dual API Strategy (Bulk vs REST)

The connector dynamically chooses between the Salesforce Bulk API and REST API per stream based on schema analysis (`_get_api_type()` in `source.py`):

- **Bulk API** (default): Used for most sObjects. Supports large data volumes via async job-based queries.
- **REST API**: Used when the sObject has `base64` or `object`-typed fields (unsupported by Bulk API), or when the sObject is in the `UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS` list.

Both API types support incremental queries via SOQL `WHERE` clauses on the cursor field.

## 4. Concurrent Stream Processing

The connector uses `ConcurrentSourceAdapter` with `ConcurrentCursor` for parallel stream processing. The concurrency level is configurable via the `num_workers` config parameter (default: 20, max: 50).

## 5. Token Refresh for Long-Running Syncs

The `SalesforceTokenProvider` in `api.py` proactively refreshes the access token every 30 minutes during long-running Bulk API syncs to prevent `INVALID_SESSION_ID` errors that would otherwise occur when sessions exceed the default 2-hour timeout.

## Incremental Stream Considerations

This connector generates streams at runtime from Salesforce sObject metadata. User inputs that drive stream generation are: the org's available sObjects, user-selected streams in the connection catalog, and optional config filters. The connector's incremental story is **mature and mostly automatic**: the `get_pk_and_replication_key()` method in `api.py` detects cursor fields per sObject, and `prepare_stream()` in `source.py` automatically selects the incremental stream class when a cursor is available and the sObject supports filtering. Incremental queries use SOQL `WHERE` clauses with the cursor field and time-slice boundaries.

| Stream Type / Pattern | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| `salesforce_sobject_standard` (sObjects with `SystemModstamp`) | large–xlarge | top-level dynamic | `SystemModstamp` | `updated_at` — SOQL `WHERE SystemModstamp >= X AND SystemModstamp < Y` | `incremental` | Most standard sObjects (Account, Contact, Opportunity, Case, etc.) have `SystemModstamp`. Both Bulk and REST API paths support the filter. `ConcurrentCursor` manages time-sliced partitioning with configurable `stream_slice_step` (default P30D) and `lookback_window`. |
| `salesforce_sobject_lastmodified` (sObjects with `LastModifiedDate` but no `SystemModstamp`) | medium–large | top-level dynamic | `LastModifiedDate` | `updated_at` — SOQL `WHERE LastModifiedDate >= X AND LastModifiedDate < Y` | `incremental` | Fallback cursor. Same incremental mechanism as `SystemModstamp`. |
| `salesforce_sobject_createddate` (sObjects with only `CreatedDate`) | small–medium | top-level dynamic | `CreatedDate` | `created_at_only` — SOQL `WHERE CreatedDate >= X AND CreatedDate < Y` | `incremental` | Only detects new records, not updates. Acceptable for append-only sObjects. |
| `salesforce_sobject_logintime` (login sObjects) | small | top-level dynamic | `LoginTime` | `updated_at` — SOQL `WHERE LoginTime >= X AND LoginTime < Y` | `incremental` | Special case for `LoginHistory` and similar sObjects. |
| `salesforce_sobject_no_cursor` (sObjects without any of the above fields) | small | top-level dynamic | `none` | `none` | `full_refresh` | Rare. These sObjects have no system timestamp fields. `get_pk_and_replication_key()` returns `replication_key=None`, forcing full-refresh class selection. Examples include certain metadata-only sObjects. |
| `salesforce_sobject_unsupported_filtering` (sObjects in `UNSUPPORTED_FILTERING_STREAMS`) | small–medium | top-level dynamic | `SystemModstamp` (exists but unusable) | `none` — SOQL WHERE clause restrictions | `full_refresh` | 21 sObjects (`api.py:200-222`) like `ContentDocumentLink`, `ApiEvent`, `LoginEvent`, etc. have Salesforce-imposed restrictions on WHERE clauses that prevent cursor-based filtering. The cursor field exists in the schema but cannot be used in queries. |
| `ContentDocumentLink` (substream of `ContentDocument`) | medium | child of `ContentDocument` | `none` (inherits parent iteration) | `none` — Salesforce query restrictions | `full_refresh` | The only configured substream (`PARENT_SALESFORCE_OBJECTS` in `api.py:135`). Uses `BulkSalesforceSubStream` with batched parent ID slicing (`WHERE ContentDocumentId IN (...)`). Cannot use cursor-based filtering due to Salesforce API restrictions on this sObject. |
| `Describe` (sObject metadata stream) | small | top-level static | `none` | `none` | `full_refresh` | Not a dynamic sObject stream. Returns Describe metadata for all sObjects in the catalog. Always full-refresh by design. |

### Deferred & framework-level work

1. **UNSUPPORTED_FILTERING_STREAMS cannot be made incremental without Salesforce API changes.** The 21 sObjects listed in `api.py:200-222` have Salesforce-imposed WHERE clause restrictions. These cannot be resolved by connector changes alone. Monitor Salesforce API release notes for relaxed restrictions on specific sObjects.
2. **sObjects without cursor fields.** A small number of sObjects lack `SystemModstamp`, `LastModifiedDate`, `CreatedDate`, and `LoginTime`. These are typically metadata-only or system sObjects with low volume. No action needed unless specific high-volume sObjects are identified as lacking cursors.
3. **ContentDocumentLink substream optimization.** Currently iterates all parent `ContentDocument` records regardless of modification time. If `ContentDocument` becomes incremental (it already is via `SystemModstamp`), the substream benefits from reduced parent iteration. However, the `incremental_dependency` pattern from the declarative CDK does not apply here since this is a Python CDK connector with custom substream logic.
4. **`CreatedDate`-only sObjects miss updates.** sObjects using `CreatedDate` as cursor only detect new records. Updated records are missed until the next full refresh. This is an inherent API limitation — these sObjects do not expose a modification timestamp.
