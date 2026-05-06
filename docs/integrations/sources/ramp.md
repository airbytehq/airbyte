# Ramp

The Airbyte connector for [Ramp](https://ramp.com) replicates corporate-card spend, reimbursements, bills, and related finance data into your warehouse for FP&A analytics. The connector authenticates with Ramp's Developer API using OAuth 2.0 client credentials and supports both production (`api.ramp.com`) and sandbox (`demo-api.ramp.com`) environments.

## Prerequisites

You need a Ramp Developer App with a `client_id` and `client_secret`. Create one in your Ramp workspace under **Settings → Developer API → Create app**. The app must be granted the OAuth scopes for the streams you intend to sync (see the table below).

If you are validating a configuration before connecting it to your production data, request a sandbox app and toggle **Use sandbox** in the connection settings. Sandbox apps point to `https://demo-api.ramp.com`.

## Setup guide

1. In Ramp, go to **Settings → Developer API** and create a new app.
2. Choose **Server-to-server** and grant the scopes you need.
3. Copy the generated `client_id` and `client_secret`.
4. In Airbyte, create a new **Ramp** source.
5. Provide:
   - **Start date** — the earliest UTC datetime to fetch records from on the first sync (`YYYY-MM-DDTHH:MM:SSZ`).
   - **Use sandbox** — leave unchecked for production, check to point at `demo-api.ramp.com`.
   - **Lookback window (days)** — number of days to re-fetch on every incremental sync to pick up late edits. Defaults to 30.
   - **Client ID** and **Client secret** from your Ramp Developer App.
6. Click **Set up source** to validate the connection.

## Configuration

| Input | Type | Description | Default |
|---|---|---|---|
| `start_date` | string (date-time) | Earliest UTC datetime to fetch records from on the first sync. | — |
| `use_sandbox` | boolean | When true, the connector targets `https://demo-api.ramp.com` instead of `https://api.ramp.com`. | `false` |
| `lookback_window_days` | integer | Number of days to re-fetch on every incremental sync. | `30` |
| `credentials.client_id` | string (secret) | Client ID from your Ramp Developer App. | — |
| `credentials.client_secret` | string (secret) | Client secret from your Ramp Developer App. | — |

## OAuth scopes

Each stream below requires the corresponding read scope on your Ramp Developer App. Because the connector requests every read scope listed below on each token call, the Ramp app must be configured with **all of them** — granting only a subset will cause `invalid_scope` errors at token exchange. To sync only some streams, deselect the others in the Airbyte connection's stream catalog rather than narrowing the app's scopes.

| Stream | Required scope |
|---|---|
| `transactions` | `transactions:read` |
| `reimbursements` | `reimbursements:read` |
| `bills` | `bills:read` |
| `transfers` | `transfers:read` |
| `cashbacks` | `cashbacks:read` |
| `statements` | `statements:read` |
| `audit_log_events` | `audit_logs:read` |
| `vendors`, `vendor_credits` | `vendors:read` |
| `purchase_orders` | `purchase_orders:read` |
| `unified_requests` | `unified_requests:read` |
| `trips` | `trips:read` |
| `repayments` | `repayments:read` |
| `memos` | `memos:read` |
| `receipts` | `receipts:read` |
| `limits` | `limits:read` |
| `users` | `users:read` |
| `departments` | `departments:read` |
| `locations` | `locations:read` |
| `entities` | `entities:read` |
| `cards` | `cards:read` |
| `merchants` | `merchants:read` |
| `spend_programs` | `spend_programs:read` |
| `bank_accounts` | `bank_accounts:read` |
| `item_receipts` | `item_receipts:read` |

## Lookback window

Most Ramp list endpoints filter records by event date (for example `from_date` filters `transactions` by `user_transaction_time`), not by `updated_at`. As a result, edits to records that occurred before the last sync window will not be picked up by a strict incremental cursor.

The `lookback_window_days` setting (default 30 days) compensates by re-fetching the most recent N days on every sync. Tune it to balance API call volume against how long after creation a record's status can change in your workflow. Setting it to `0` disables the lookback.

For the `bills`, `vendors`, `purchase_orders`, and `memos` streams, no incremental cursor is available in the response that reliably reflects late edits. These streams use full refresh in v1; expect them to re-fetch every record on every sync.

### Per-stream cursor caveats

- **`transactions`** uses `user_transaction_time` (transaction time, not sync time). Status changes (approval, sync to ERP, late settlement) on transactions older than `lookback_window_days` will not be re-emitted. If you rely on status freshness for older transactions, increase the lookback window or use full refresh.
- **`trips`** uses `start_date` to match Ramp's `from_date` / `to_date` filter, which filters trips by start date with overlap. Trips edited after the lookback window has passed their start date will not be re-emitted. There is no `updated_at` filter exposed by Ramp for this resource.
- **`reimbursements`** uses `updated_at` with Ramp's `updated_after` filter (a true updated-at filter). The lookback window is applied for safety but is not strictly necessary for completeness.

## Streams

| Stream | Primary key | Sync mode | Cursor field |
|---|---|---|---|
| `transactions` | `id` | Incremental | `user_transaction_time` |
| `reimbursements` | `id` | Incremental | `updated_at` |
| `bills` | `id` | Full refresh | — |
| `transfers` | `id` | Incremental | `created_at` |
| `cashbacks` | `id` | Incremental | `created_at` |
| `statements` | `id` | Incremental | `end_date` |
| `audit_log_events` | `id` | Incremental | `event_time` |
| `vendors` | `id` | Full refresh | — |
| `vendor_credits` | `id` | Incremental | `created_at` |
| `purchase_orders` | `id` | Full refresh | — |
| `unified_requests` | `id` | Full refresh | — |
| `trips` | `id` | Incremental | `start_date` |
| `repayments` | `id` | Incremental | `repaid_at` |
| `memos` | `id` | Full refresh | — |
| `receipts` | `id` | Incremental | `created_at` |
| `limits` | `id` | Incremental | `created_at` |
| `users` | `id` | Full refresh | — |
| `departments` | `id` | Full refresh | — |
| `locations` | `id` | Full refresh | — |
| `entities` | `id` | Full refresh | — |
| `cards` | `id` | Full refresh | — |
| `merchants` | `id` | Full refresh | — |
| `spend_programs` | `id` | Full refresh | — |
| `bank_accounts` | `id` | Full refresh | — |
| `item_receipts` | `id` | Full refresh | — |

## Troubleshooting

### `403 Forbidden` or `403 missing_scope` on a specific stream

The OAuth scope for that stream is not granted to your Developer App. Update the app in Ramp to include the required scope (see [OAuth scopes](#oauth-scopes)) and reconnect.

### Long-running queries return `504 Gateway Timeout`

Ramp's API enforces a 60-second per-request timeout on certain queries. The connector retries on 5xx errors automatically. If timeouts persist for a single stream, narrow the sync window by increasing `start_date` or reducing `lookback_window_days`.

### `unified_requests` notes

The `unified_requests` stream is marked unstable by Ramp and returns a raw array (not the standard `{ data, page }` envelope). The connector paginates by injecting `start=<last record id>` and `page_size=100`, stopping when fewer than `page_size` records are returned. The response schema is a discriminator union and may change without notice.

### Sandbox vs. production

Toggling **Use sandbox** changes both the API host and the OAuth token endpoint to `https://demo-api.ramp.com`. Production credentials will not authenticate against the sandbox host and vice versa.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---|---|---|---|
| 0.1.0 | 2026-05-06 | [77803](https://github.com/airbytehq/airbyte/pull/77803) | Initial release |

</details>
