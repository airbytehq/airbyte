# source-airtable: Unique Behaviors

## 1. Single-Use Rotating Refresh Tokens

Airtable's OAuth implementation issues single-use refresh tokens. Every time an access token is refreshed, the old refresh token is invalidated and a new one is returned. The connector uses `refresh_token_updater` to persist the new refresh token back to the connection configuration after each token exchange.

**Why this matters:** If a token refresh succeeds but the new refresh token fails to persist (e.g., due to a crash or network issue between the exchange and the config update), the connection becomes permanently broken and requires re-authentication. Standard OAuth connectors can retry with the same refresh token, but Airtable cannot.

## Incremental Stream Considerations

This connector generates streams at runtime via the `dynamic_streams` / `DynamicDeclarativeStream` mechanism in `manifest.yaml`. An `HttpComponentsResolver` iterates over all user-accessible Airtable bases and tables (via `meta/bases/{base_id}/tables`) and stamps each table as a separate stream. User inputs that drive generation are: the authenticated user's base/table permissions and the optional `add_base_id_to_stream_name` config flag. Currently, **none** of the dynamically generated streams support incremental sync. The Airtable [List Records API](https://airtable.com/developers/web/api/list-records) does not expose a reliable server-side `modified_since` filter parameter. While `filterByFormula` with `LAST_MODIFIED_TIME()` exists, community reports indicate it is unreliable for incremental use cases (returns all records regardless of the filter in many scenarios).

| Stream Type / Pattern | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| `airtable_table` (any user-selected table) | medium–large (varies by user) | top-level dynamic | `none` (records have `createdTime` but no per-record `modifiedTime`) | `none` — `filterByFormula` with `LAST_MODIFIED_TIME()` is unreliable; no dedicated `modified_since` query param | `full_refresh` | Each record exposes `createdTime` (mapped to `_airtable_created_time`) and `id` (mapped to `_airtable_id`). A `lastModifiedTime` field type exists in field metadata but is per-field, user-configured, and not present on the record envelope. The API returns records in an unspecified order with no server-side cursor-based filtering. |

### API incremental support analysis

Per-record fields: `id` (unique record ID, mapped to `_airtable_id`) and `createdTime` (creation timestamp, mapped to `_airtable_created_time`). There is no `modifiedTime` or `updatedAt` on the record envelope.

Server-side filtering options:
1. **`filterByFormula` with `LAST_MODIFIED_TIME()`**: Airtable's formula language includes `LAST_MODIFIED_TIME()`, but community reports indicate this filter is unreliable with the List Records API — it often returns all records regardless of the filter. See: [Airtable Community thread](https://community.airtable.com/development-apis-11/api-doesn-t-respect-is-after-filter-issue-also-reported-3-years-ago-47358).
2. **User-configured `Last Modified` field**: Users can add a `lastModifiedTime` field to their table schema. If present, it could theoretically be used as a filter, but: it's user-configured and not guaranteed to exist, the field name varies, and it still goes through `filterByFormula` which has reliability concerns.
3. **No `modified_since` query parameter**: Unlike Salesforce (`SystemModstamp`), Zoho CRM (`If-Modified-Since`), or Google Drive (`modifiedTime`), Airtable has no dedicated incremental query parameter.
4. **Airtable Webhooks API**: The [Webhooks API](https://airtable.com/developers/web/api/webhooks-overview) can push change notifications but requires a fundamentally different integration pattern (push vs. pull) and CDK-level support that does not exist today.

### Proposed strategies (ranked by feasibility)

**Strategy 1: Client-side cursor tracking on `_airtable_created_time` (low value)**. Add a `DatetimeBasedCursor` with `cursor_field: _airtable_created_time` and no `start_time_option`. This would track the latest `createdTime` seen and enable platform-level "no new records created since last sync" detection. However, every sync still reads all records and only new records (not updates) are tracked. Low value.

**Strategy 2: Conditional `filterByFormula` with user-configured cursor field (medium complexity)**. Add an optional config field (e.g., `cursor_field_name`) that users set to a `lastModifiedTime`-type field name. When set, inject `filterByFormula=IS_AFTER({cursor_field_name}, '{last_cursor_value}')` into requests. Blocked by: `filterByFormula` reliability issues, per-table field name variation, and lack of per-stream cursor field support in `DynamicDeclarativeStream`.

**Strategy 3: Webhooks-based change detection (high complexity, highest value)**. Register a webhook per base/table during connection setup, then fetch only changed records using the webhook cursor. Blocked by: requires a webhook receiver endpoint (connector framework doesn't support this), webhooks expire after 7 days, and this requires CDK-level support for push-based sources.

### Deferred & framework-level work

1. **No reliable server-side modified-since filter.** The Airtable List Records API does not support `modified_since`, `updated_after`, or equivalent query parameters. The `filterByFormula` approach with `LAST_MODIFIED_TIME()` has been reported as unreliable. Without server-side filtering, every sync must fetch all records from every table.
2. **Client-side cursor tracking (potential future approach).** If the CDK's `DynamicDeclarativeStream` adds support for `is_client_side_incremental: true` on `DatetimeBasedCursor`, a client-side cursor on `_airtable_created_time` could be added with minimal risk. This would not reduce API calls but would provide platform-level state tracking.
3. **Airtable Webhooks / Sync API (potential future approach).** Airtable offers a [Webhooks API](https://airtable.com/developers/web/api/webhooks-overview) that can notify on record changes. A future redesign could use webhooks or the experimental sync endpoints to achieve true incremental behavior, but this requires significant framework changes beyond the current dynamic-stream model.
4. **Monitor Airtable API updates.** If Airtable adds a `modified_since` query parameter or fixes `filterByFormula` reliability with time functions, Strategy 2 becomes viable with minimal manifest changes.

### References

- [Airtable List Records API](https://airtable.com/developers/web/api/list-records)
- [Airtable Field Model](https://airtable.com/developers/web/api/field-model)
- [Airtable Webhooks API](https://airtable.com/developers/web/api/webhooks-overview)
- [Airtable Community — IS_AFTER filter issue](https://community.airtable.com/development-apis-11/api-doesn-t-respect-is-after-filter-issue-also-reported-3-years-ago-47358)
- [Airbyte incremental sync docs](https://docs.airbyte.com/platform/connector-development/config-based/understanding-the-yaml-file/incremental-syncs)
- Dynamic stream manifest: `manifest.yaml:508` (`dynamic_streams` block)
- Stream template: `manifest.yaml:84` (`airtable_stream` definition)
