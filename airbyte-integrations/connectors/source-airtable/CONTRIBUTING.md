# source-airtable: Unique Behaviors

## 1. Single-Use Rotating Refresh Tokens

Airtable's OAuth implementation issues single-use refresh tokens. Every time an access token is refreshed, the old refresh token is invalidated and a new one is returned. The connector uses `refresh_token_updater` to persist the new refresh token back to the connection configuration after each token exchange.

**Why this matters:** If a token refresh succeeds but the new refresh token fails to persist (e.g., due to a crash or network issue between the exchange and the config update), the connection becomes permanently broken and requires re-authentication. Standard OAuth connectors can retry with the same refresh token, but Airtable cannot.

## Incremental Stream Considerations

This connector generates streams at runtime via the `dynamic_streams` / `DynamicDeclarativeStream` mechanism in `manifest.yaml`. An `HttpComponentsResolver` iterates over all user-accessible Airtable bases and tables (via `meta/bases/{base_id}/tables`) and stamps each table as a separate stream. User inputs that drive generation are: the authenticated user's base/table permissions and the optional `add_base_id_to_stream_name` config flag. Currently, **none** of the dynamically generated streams support incremental sync. The Airtable [List Records API](https://airtable.com/developers/web/api/list-records) does not expose a reliable server-side `modified_since` filter parameter. While `filterByFormula` with `LAST_MODIFIED_TIME()` exists, community reports indicate it is unreliable for incremental use cases (returns all records regardless of the filter in many scenarios).

| Stream Type / Pattern | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| `airtable_table` (any user-selected table) | medium–large (varies by user) | top-level dynamic | `none` (records have `createdTime` but no per-record `modifiedTime`) | `none` — `filterByFormula` with `LAST_MODIFIED_TIME()` is unreliable; no dedicated `modified_since` query param | `full_refresh` | Each record exposes `createdTime` (mapped to `_airtable_created_time`) and `id` (mapped to `_airtable_id`). A `lastModifiedTime` field type exists in field metadata but is per-field, user-configured, and not present on the record envelope. The API returns records in an unspecified order with no server-side cursor-based filtering. |

### Why incremental sync is not feasible

**Record level:** The Airtable List Records API does not provide a system-maintained `modifiedTime` or `updatedAt` field on records. Records expose only `createdTime` (creation timestamp) and `id`. The `lastModifiedTime` field type that exists in Airtable is user-defined — users must manually add it to their table schema and configure which fields it tracks. It is not automatically present on all tables, field names vary per user, and it cannot be relied on as a universal cursor.

**Table level:** The table metadata endpoint (`meta/bases/{base_id}/tables`) does not include a table-level modification timestamp. There is no way to detect whether a table's records have changed since the last sync without reading the records themselves.

**Server-side filtering:** The `filterByFormula` mechanism with `LAST_MODIFIED_TIME()` is unreliable — community reports confirm it returns all records regardless of the filter condition. There is no dedicated `modified_since` query parameter like Salesforce (`SystemModstamp`), Zoho CRM (`If-Modified-Since`), or Google Drive (`modifiedTime`). See: [Airtable Community thread](https://community.airtable.com/development-apis-11/api-doesn-t-respect-is-after-filter-issue-also-reported-3-years-ago-47358).

**Webhooks:** The [Webhooks API](https://airtable.com/developers/web/api/webhooks-overview) can push change notifications, but this is a fundamentally different integration pattern (push vs. pull) that is incompatible with the Airbyte connector framework. Webhooks require a receiver endpoint, expire after 7 days, and would need CDK-level support for push-based sources that does not exist. This is not a viable path.

### Deferred & framework-level work

1. **Hard blocker: no system-maintained modification timestamps.** Airtable's API does not provide system-maintained modification timestamps at either the record or table level. Until Airtable adds a `modified_since` query parameter or a system-maintained `modifiedTime` field on records, incremental sync is not possible for this connector.
2. **Monitor Airtable API updates.** If Airtable adds a dedicated `modified_since` query parameter or a system-maintained record modification timestamp, incremental support could be added with minimal manifest changes to the `DynamicDeclarativeStream` template.

### References

- [Airtable List Records API](https://airtable.com/developers/web/api/list-records)
- [Airtable Field Model](https://airtable.com/developers/web/api/field-model)
- [Airtable Community — IS_AFTER filter issue](https://community.airtable.com/development-apis-11/api-doesn-t-respect-is-after-filter-issue-also-reported-3-years-ago-47358)
- [Airbyte incremental sync docs](https://docs.airbyte.com/platform/connector-development/config-based/understanding-the-yaml-file/incremental-syncs)
- Dynamic stream manifest: `manifest.yaml:508` (`dynamic_streams` block)
- Stream template: `manifest.yaml:84` (`airtable_stream` definition)
