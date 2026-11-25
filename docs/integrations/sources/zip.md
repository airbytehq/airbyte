# Zip

The Zip source syncs purchase requests, purchase orders and invoices from [Zip](https://ziphq.com), the procurement and spend approval platform, through Zip's public API. Each stream syncs incrementally on the record's last update time.

## Prerequisites

- A Zip account with an administrator who can create API keys.
- A Zip API key with read access to requests, purchase orders and invoices.

## Setup guide

### Set up Zip

1. In Zip, go to **Settings** > **API Keys**.
2. Create a key with read access to requests, purchase orders and invoices. A restricted, read-only key is enough.
3. Copy the key. Zip shows it once.

Zip's API reference at [developer.zip.com](https://developer.zip.com) is only readable with a Zip login.

<HideInUI>

### Set up the Zip connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or open your self-managed Airbyte instance.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Zip** from the Source type dropdown.
4. Enter a name for the Zip connector.
5. Enter the **API Key**.
6. Leave **API Version** at its default unless Zip has asked you to use another version.
7. Optionally, set **Start Date**. See [Start Date](#start-date).
8. Click **Set up source**.

</HideInUI>

## Connector settings

| Input | Type | Description | Default |
| --- | --- | --- | --- |
| `api_key` | `string` | API key created in Zip under Settings > API Keys. Sent in the `Zip-Api-Key` header. | |
| `api_version` | `string` | Value sent in the `Zip-Api-Version` header. | `2024-06-06` |
| `start_date` | `string` | Only records updated on or after this date are synced on the first sync. UTC, with a `Z` suffix. | `2020-01-01T00:00:00Z` |

### Start Date

On the first sync, every stream reads only records whose `updated_at` is on or after this date. Later syncs use the saved cursor instead. Enter the date as a UTC timestamp with a `Z` suffix, such as `2024-01-01T00:00:00Z`. Fractional seconds are accepted. Values with a numeric offset are rejected.

### Connection test

The connection test reads the first page of the `requests` stream.

## Supported sync modes

The Zip source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

All three streams support incremental syncs on `updated_at`.

- **Incremental syncs filter on the server.** The connector sends the saved cursor as a query parameter. Zip names that parameter differently per endpoint: `updated_after` on `/invoices`, and `last_updated_after` on `/requests` and `/purchase_orders`. The connector handles this for you.
- **Records at the cursor boundary are read again.** Zip's filter includes records whose `updated_at` equals the given value, so the next sync re-emits the records at the saved cursor. Use **Incremental - Append + Deduped** to keep one row per `id`.
- **`purchase_orders` also returns records with an older `updated_at`.** On `/purchase_orders`, Zip's `last_updated_after` filter matches on the purchase order's `last_activity_at`, not on `updated_at`. A purchase order with recent activity (for example a new invoice matched to it) is returned even when its `updated_at` is older than the cursor. The connector emits these records as Zip returns them and the cursor still advances on `updated_at`. With **Append + Deduped**, the destination keeps one row per `id`. On `/requests` and `/invoices`, every returned record had an `updated_at` inside the window.
- **Timestamps are Unix epoch seconds.** `updated_at`, `created_at` and the other `*_at` fields hold integers such as `1718000500`, not ISO 8601 strings. The connector declares `updated_at` as an integer and leaves the others as strings.

## Supported streams

| Stream | API endpoint | Primary key | Sync modes | Incremental cursor | Page size |
| --- | --- | --- | --- | --- | --- |
| `requests` | `GET /requests` | `id` | Full refresh, incremental | `updated_at` | 30 |
| `purchase_orders` | `GET /purchase_orders` | `id` | Full refresh, incremental | `updated_at` | 50 |
| `invoices` | `GET /invoices` | `id` | Full refresh, incremental | `updated_at` | 50 |

Every request asks Zip to include the account's custom fields (`include_attributes=true`). They arrive in the `attributes` array of each record.

## How the schema is built

The connector does not ship a fixed list of columns. Each stream declares two fields itself, `id` (string) and `updated_at` (integer), and discovers the rest at runtime:

- When Airbyte discovers the schema, and once more at the start of each sync, the connector reads the first page of the endpoint, sorted newest first, and declares every top-level key of the **first record** as a nullable string. Zip returns every key on every record (null when unset), so the first record carries the full field set.
- Nested objects and arrays, such as `vendor`, `line_items`, `approvals` and `attributes`, are declared as strings and land as JSON text. Parse them in your destination, for example with your warehouse's JSON functions.
- Numbers, booleans and epoch timestamps other than `updated_at` also land as strings. Cast them downstream.
- When Zip adds a field, it appears on the next schema refresh in Airbyte. No connector update is needed.
- If an endpoint returns no records when the schema is read, the stream declares only `id` and `updated_at`. The schema does not forbid other fields, so the records themselves are still complete, but typed destinations may not create columns for the undeclared fields until you refresh the schema after data exists.

This uses the Airbyte CDK's `DynamicSchemaLoader`, which the CDK marks as experimental.

## Limitations & Troubleshooting

### Limitations

- **Three streams.** Zip's API exposes more objects (vendors, users, accounting codes and others). They are not included yet.
- **One schema read per stream per sync.** The runtime schema read above costs one extra request per stream on each sync.
- **Incremental syncs rely on a Zip fix from August 2026.** Before it, Zip's pagination cursor did not tie-break on `updated_at`, so records sharing one timestamp could be skipped under the date filters (Zip support ticket 110091). Zip deployed the fix for `/invoices` and `/purchase_orders` on 2026-08-07 and for `/requests` on 2026-08-25. If you suspect skipped records from before those dates, run a full refresh.
- **Private API documentation.** Zip's developer portal requires a Zip login, so this page cannot link to the reference for each endpoint.

### Errors

| Error | Cause | Fix |
| --- | --- | --- |
| `Zip rejected the API key` | Zip returned `401` or `403`. | Check the key under **Settings** > **API Keys** in Zip, that it has read access to the three objects, and that **API Version** is one Zip still supports. |
| `400` with `INVALID_PARAM` | Zip rejected a query parameter. The connector sends each endpoint's own filter name, so this usually means the API version changed what the endpoint accepts. | Check the **API Version** setting. |

The connector retries `429` and `5xx` responses with exponential backoff, up to five times.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                       |
| ------- | ---------- | --------------------------------------------------------- | --------------------------------------------- |
| 0.0.1   | 2026-11-25 | [XXXXX](https://github.com/airbytehq/airbyte/pull/XXXXX)  | Initial release by [@MercureTony](https://github.com/MercureTony) |

</details>
