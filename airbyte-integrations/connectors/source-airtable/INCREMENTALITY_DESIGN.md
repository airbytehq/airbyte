# source-airtable: Incrementality Design Note

## Status

**Deferred — no reliable server-side incremental filter available.**

This document captures the investigation results and proposes strategies for future work.

## Current Architecture

source-airtable is a **manifest-only declarative connector** that generates streams at runtime using the `dynamic_streams` / `DynamicDeclarativeStream` mechanism (`manifest.yaml:508`).

### Stream generation flow

1. `HttpComponentsResolver` fetches all bases via `meta/bases` (paginated).
2. For each base, it fetches all tables via `meta/bases/{base_id}/tables`.
3. Each table becomes a separate stream via `components_mapping`, with the stream name derived from `{base_name}/{table_name}/{table_id}`.
4. The stream template (`airtable_stream`) fetches records via `GET /{base_id}/{table_id}` with offset-based pagination.
5. Records are transformed: `fields` is flattened, keys lowercased/space-replaced, and metadata fields (`_airtable_id`, `_airtable_created_time`, `_airtable_table_name`) are added.

### Schema generation

Uses `DynamicSchemaLoader` with `SchemaTypeIdentifier` to map Airtable field types to JSON Schema types at runtime. Each table has a unique schema derived from its field metadata.

## API Incremental Support Analysis

### What the API exposes per record

- `id` — unique record ID (mapped to `_airtable_id`)
- `createdTime` — record creation timestamp (mapped to `_airtable_created_time`)
- No `modifiedTime` or `updatedAt` field on the record envelope

### Server-side filtering options

1. **`filterByFormula` with `LAST_MODIFIED_TIME()`**: The Airtable formula language includes `LAST_MODIFIED_TIME()` which returns the last modification timestamp. However, community reports (as of 2026-01) indicate this filter is unreliable when used with the List Records API — it often returns all records regardless of the filter condition. See: [Airtable Community thread](https://community.airtable.com/development-apis-11/api-doesn-t-respect-is-after-filter-issue-also-reported-3-years-ago-47358).

2. **`filterByFormula` with user-configured `Last Modified` field**: Users can create a `lastModifiedTime` field in their table schema. If present, it could theoretically be used as a filter. However: (a) it's user-configured and not guaranteed to exist, (b) the field name varies by user, (c) it still goes through `filterByFormula` which has the same reliability concerns.

3. **No `modified_since` query parameter**: Unlike APIs such as Salesforce (`SystemModstamp`), Zoho CRM (`If-Modified-Since` header), or Google Drive (`modifiedTime`), Airtable does not offer a dedicated incremental query parameter.

4. **Airtable Webhooks API**: Airtable offers a [Webhooks API](https://airtable.com/developers/web/api/webhooks-overview) that can push change notifications. This is a fundamentally different integration pattern (push vs. pull) and would require significant framework changes.

### Conclusion

There is **no reliable mechanism** to perform server-side incremental filtering on the Airtable List Records API today. Any incremental implementation would be client-side only.

## Proposed Strategies (ranked by feasibility)

### Strategy 1: Client-side cursor tracking on `_airtable_created_time` (low value)

Add a `DatetimeBasedCursor` to the `airtable_stream` template with `cursor_field: _airtable_created_time` and no `start_time_option` (no server-side injection). This would:

- Track the latest `createdTime` seen per stream
- Enable the platform to detect "no new records created since last sync"
- Still fetch all records every sync (no API call reduction)
- Only track *new* records, not *updated* records

**Verdict**: Low value. The cursor would track creation time only, not modifications. Every sync still reads all records. The only benefit is platform-level "no new data" detection.

### Strategy 2: Conditional `filterByFormula` with user-configured cursor field (medium complexity)

Add an optional config field (e.g., `cursor_field_name`) that users can set to the name of a `lastModifiedTime`-type field in their tables. When set:

- Inject `filterByFormula=IS_AFTER({cursor_field_name}, '{last_cursor_value}')` into requests
- Track the cursor value in state

**Challenges**:
- Requires user configuration (not automatic)
- `filterByFormula` with time-based functions is unreliable (see analysis above)
- Different tables may have different cursor field names
- Would need the `DynamicDeclarativeStream` template to support per-stream cursor field configuration, which the current framework does not support

**Verdict**: Medium complexity, but blocked by API reliability issues. Not recommended until Airtable fixes `filterByFormula` behavior with time functions.

### Strategy 3: Webhooks-based change detection (high complexity, highest value)

Use the Airtable Webhooks API to receive change notifications:

1. Register a webhook per base/table during connection setup
2. On each sync, fetch only records that changed since the last webhook cursor
3. Use the webhook `cursor` field to track sync position

**Challenges**:
- Requires a webhook receiver endpoint (the connector framework doesn't support this)
- Webhooks have a 7-day expiry and must be refreshed
- Significant departure from the pull-based connector model
- Would require CDK-level support for webhook-based sources

**Verdict**: Highest value but requires framework-level changes beyond the current CDK capabilities.

## Recommended Next Steps

1. **Monitor Airtable API updates.** If Airtable adds a `modified_since` query parameter or fixes `filterByFormula` reliability with time functions, Strategy 2 becomes viable with minimal changes.
2. **Consider client-side `is_client_side_incremental` cursor.** If the CDK's `DynamicDeclarativeStream` adds support for `is_client_side_incremental: true` on `DatetimeBasedCursor`, a client-side cursor on `_airtable_created_time` could be added with minimal risk. This would not reduce API calls but would provide platform-level state tracking.
3. **Evaluate Webhooks API for a future connector redesign.** This is the only path to true incremental behavior but requires CDK framework support for push-based sources.

## References

- Airtable List Records API: https://airtable.com/developers/web/api/list-records
- Airtable Field Model: https://airtable.com/developers/web/api/field-model
- Airtable Webhooks API: https://airtable.com/developers/web/api/webhooks-overview
- Airtable Community — IS_AFTER filter issue: https://community.airtable.com/development-apis-11/api-doesn-t-respect-is-after-filter-issue-also-reported-3-years-ago-47358
- Airbyte incremental sync docs: https://docs.airbyte.com/platform/connector-development/config-based/understanding-the-yaml-file/incremental-syncs
- Dynamic stream manifest: `manifest.yaml:508` (`dynamic_streams` block)
- Stream template: `manifest.yaml:84` (`airtable_stream` definition)
