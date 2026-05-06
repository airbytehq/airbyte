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

Each stream requires the corresponding read scope on your Ramp Developer App. Grant only the scopes for streams you intend to sync.

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

For the `bills`, `vendors`, `purchase_orders`, `unified_requests`, and `memos` streams, no incremental cursor is available in the response that reliably reflects late edits. These streams use full refresh in v1; expect them to re-fetch every record on every sync.

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
| `trips` | `id` | Incremental | `updated_at` |
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

### `unified_requests` returns no records

The `unified_requests` stream is marked unstable by Ramp and returns a raw array (not an envelope) without a stable cursor. Only the first page is returned in v1. File a connector issue if you need full pagination of this stream.

### Sandbox vs. production

Toggling **Use sandbox** changes both the API host and the OAuth token endpoint to `https://demo-api.ramp.com`. Production credentials will not authenticate against the sandbox host and vice versa.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---|---|---|---|
| 0.1.0 | 2026-05-05 | [TBD](https://github.com/airbytehq/airbyte/pull/0) | Initial release |

</details>
