# source-airtable: Unique Behaviors

## 1. Single-Use Rotating Refresh Tokens

Airtable's OAuth implementation issues single-use refresh tokens. Every time an access token is refreshed, the old refresh token is invalidated and a new one is returned. The connector uses `refresh_token_updater` to persist the new refresh token back to the connection configuration after each token exchange.

**Why this matters:** If a token refresh succeeds but the new refresh token fails to persist (e.g., due to a crash or network issue between the exchange and the config update), the connection becomes permanently broken and requires re-authentication. Standard OAuth connectors can retry with the same refresh token, but Airtable cannot.

## Incremental Stream Considerations

This connector generates streams at runtime via the `dynamic_streams` / `DynamicDeclarativeStream` mechanism in `manifest.yaml`. An `HttpComponentsResolver` iterates over all user-accessible Airtable bases and tables (via `meta/bases/{base_id}/tables`) and stamps each table as a separate stream. User inputs that drive generation are: the authenticated user's base/table permissions and the optional `add_base_id_to_stream_name` config flag. Currently, **none** of the dynamically generated streams support incremental sync. The Airtable [List Records API](https://airtable.com/developers/web/api/list-records) does not expose a reliable server-side `modified_since` filter parameter. While `filterByFormula` with `LAST_MODIFIED_TIME()` exists, community reports indicate it is unreliable for incremental use cases (returns all records regardless of the filter in many scenarios).

| Stream Type / Pattern | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| `airtable_table` (any user-selected table) | medium–large (varies by user) | top-level dynamic | `none` (records have `createdTime` but no per-record `modifiedTime`) | `none` — `filterByFormula` with `LAST_MODIFIED_TIME()` is unreliable; no dedicated `modified_since` query param | `full_refresh` | Each record exposes `createdTime` (mapped to `_airtable_created_time`) and `id` (mapped to `_airtable_id`). A `lastModifiedTime` field type exists in field metadata but is per-field, user-configured, and not present on the record envelope. The API returns records in an unspecified order with no server-side cursor-based filtering. See design note for proposed strategies. |

### Deferred & framework-level work

1. **No reliable server-side modified-since filter.** The Airtable List Records API does not support `modified_since`, `updated_after`, or equivalent query parameters. The `filterByFormula` approach with `LAST_MODIFIED_TIME()` has been reported as unreliable. Without server-side filtering, every sync must fetch all records from every table.
2. **Client-side cursor tracking (potential future approach).** A `DatetimeBasedCursor` could be added to the dynamic stream template to track the latest `_airtable_created_time` seen, enabling the platform to detect "no new data" between syncs. However, this would only track *created* records (not updated ones) and would not reduce API calls since all records must still be fetched. This is a low-value optimization.
3. **Airtable Webhooks / Sync API (potential future approach).** Airtable offers a [Webhooks API](https://airtable.com/developers/web/api/webhooks-overview) that can notify on record changes. A future redesign could use webhooks or the experimental sync endpoints to achieve true incremental behavior, but this requires significant framework changes beyond the current dynamic-stream model.

See [`INCREMENTALITY_DESIGN.md`](./INCREMENTALITY_DESIGN.md) for the full design note with proposed strategies and next steps.
