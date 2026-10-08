# Ramp

The Ramp source syncs data from the [Ramp Developer API](https://docs.ramp.com/developer-api) for a single Ramp business. It covers card spend (cards, transactions, and reimbursements), your organization and spend controls (users, departments, locations, entities, business details, funds, and spend programs), and accounts payable and procurement (bills, vendors, receipts, merchants, and purchase orders).

## Prerequisites

- A Ramp account with administrator access, so you can create a developer app.
- A Ramp developer app that uses the **Client Credentials** grant type, with the `transactions:read`, `cards:read`, and `reimbursements:read` scopes enabled, plus the read scope for each other stream you want to sync. See [Supported streams](#supported-streams) for the scope each stream needs.
- The client ID and client secret for that app.

## Set up the Ramp source

### Step 1: Create a Ramp developer app

1. In your Ramp account, go to **Company** > **Developer**.
2. Select **Create New App**, name the app, and accept the terms.
3. Under **Grant types**, select **Add new grant type** > **Client Credentials**. The connector authenticates server-to-server, so it doesn't use the authorization code flow and doesn't need a redirect URI.
4. Under **Scopes**, select **Configure allowed scopes**. Enable `transactions:read`, `cards:read`, and `reimbursements:read`, and the read scope for every other stream you plan to sync.
5. Copy the client ID and client secret.

For more detail, see Ramp's [quickstart](https://docs.ramp.com/developer-api/v1/getting-started) and [authorization guide](https://docs.ramp.com/developer-api/v1/authorization).

### Step 2: Configure the source in Airbyte

1. Enter the **Ramp Client ID** and **Ramp Client Secret** from your developer app.
2. Optionally, set **Start Date**. On the first sync, the `transactions` and `reimbursements` streams only read records with an `updated_at` on or after this date, and the `receipts` stream only reads receipts with a `created_at` after this date. Later syncs use the saved cursor instead. Other streams ignore Start Date. If you leave it empty, the connector uses `2019-01-01T00:00:00Z`.

   Enter Start Date as a UTC timestamp with a `Z` suffix, such as `2024-01-01T00:00:00Z`. Fractional seconds, such as `2024-01-01T00:00:00.000Z`, are accepted. Values with a numeric offset, such as `2024-01-01T00:00:00+00:00`, are rejected.

The connection test only reads the `transactions` stream. If your app is missing the scope for another stream, the test still passes, and that stream fails during the sync.

## Supported streams

All endpoints are under `/developer/v1`.

| Stream | API endpoint | Required scope | Primary key | Sync modes | Incremental cursor |
| --- | --- | --- | --- | --- | --- |
| `cards` | `GET /cards` | `cards:read` | `id` | Full refresh | None |
| `transactions` | `GET /transactions` | `transactions:read` | `id` | Full refresh, incremental | `updated_at` |
| `reimbursements` | `GET /reimbursements` | `reimbursements:read` | `id` | Full refresh, incremental | `updated_at` |
| `users` | `GET /users` | `users:read` | `id` | Full refresh | None |
| `departments` | `GET /departments` | `departments:read` | `id` | Full refresh | None |
| `locations` | `GET /locations` | `locations:read` | `id` | Full refresh | None |
| `entities` | `GET /entities` | `entities:read` | `id` | Full refresh | None |
| `business` | `GET /business` | `business:read` | `id` | Full refresh | None |
| `business_balance` | `GET /business/balance` | `business:read` | None | Full refresh | None |
| `funds` | `GET /funds` | `funds:read` | `id` | Full refresh | None |
| `spend_programs` | `GET /spend-programs` | `spend_programs:read` | `id` | Full refresh | None |
| `bills` | `GET /bills` | `bills:read` | `id` | Full refresh | None |
| `vendors` | `GET /vendors` | `vendors:read` | `id` | Full refresh | None |
| `vendor_contacts` | `GET /vendors/{vendor_id}/contacts` | `vendors:read` | `vendor_id`, `id` | Full refresh | None |
| `vendor_agreements` | `POST /vendors/agreements` | `vendors:read` | `id` | Full refresh | None |
| `receipts` | `GET /receipts` | `receipts:read` | `id` | Full refresh, incremental | `created_at` |
| `merchants` | `GET /merchants` | `merchants:read` | `id` | Full refresh | None |
| `purchase_orders` | `GET /purchase-orders` | `purchase_orders:read` | `id` | Full refresh | None |

### Card spend

`cards` returns physical and virtual cards, including their state, cardholder, card program, and spending restrictions. It doesn't return terminated cards, because Ramp's cards list leaves them out. With the **Overwrite** or **Overwrite + Deduped** sync mode, a card disappears from the destination on the first sync after it's terminated. Its transactions stay in the `transactions` stream, so use a left join from `transactions.card_id` to `cards`, or read the cardholder from `transactions.card_holder`. With **Append**, the destination keeps every earlier copy of the card, and the newest copy still shows the `state` it had before termination, such as `ACTIVE`.

`transactions` returns card transactions in every state, including `DECLINED`. Declined transactions have `state: DECLINED` and a populated `decline_details` object, so filter them out if you calculate spend totals.

The connector also requests the purchase data merchants send to Ramp, and stores it in the `merchant_data` field. It can include itemized receipt lines, a merchant reference, and flight, lodging, or car rental details. `merchant_data` is null for transactions whose merchant sent no purchase data. Versions before 0.3.0 didn't request this data, so to fill in `merchant_data` for transactions you've already synced, refresh the `transactions` stream.

`reimbursements` returns out-of-pocket reimbursements and repayments. Ramp's endpoint returns one direction at a time, so the connector requests both `BUSINESS_TO_USER` (out-of-pocket reimbursements) and `USER_TO_BUSINESS` (repayments) and emits them into one stream. Use the `direction` field to tell them apart.

### Organization and spend controls

`users` returns users in every status. Ramp's users list leaves out suspended users by default, so the connector reads suspended users in a second request.

`business` returns one record with your business's details. `business_balance` returns one snapshot of your current balances on each sync. It has no primary key, so with **Append** each sync adds a new row.

`funds` includes terminated funds. The connector reads active and terminated funds in separate requests.

### Accounts payable and procurement

`bills` includes archived (deleted) bills. The connector reads active and archived bills in separate requests.

`vendors` doesn't include draft vendors or vendors still waiting for approval, because Ramp's vendors list leaves them out by default. The connector requests each vendor's ERP subsidiary identifiers.

`vendor_contacts` reads the contacts of each vendor in the `vendors` stream and adds the `vendor_id` to every record. If Ramp returns `404 Not Found` for a vendor, the connector skips that vendor.

`vendor_agreements` and `purchase_orders` include archived records.

`receipts` includes Ramp's OCR data for each receipt. Ramp's receipts have no `updated_at` field, so incremental syncs use `created_at` and only pick up new receipts. Changes to a receipt after the sync that first read it aren't synced until you refresh the stream.

`purchase_orders` requires Ramp Plus. If your Ramp plan doesn't include purchase orders, deselect this stream.

## Sync behavior and limitations

- **Incremental syncs filter on the server.** For `transactions` and `reimbursements`, the connector sends the cursor as the `updated_after` query parameter. For `receipts`, it sends the cursor as `created_after`. Ramp doesn't list `updated_after` in its published parameters for the transactions endpoint, but the API honors it.
- **Records at the cursor boundary are read again.** `updated_after` is inclusive, so the next sync re-emits records whose `updated_at` equals the saved cursor. Use the **Incremental | Append + Deduped** sync mode to keep one row per `id`.
- **Declined transactions from before version 0.1.0 aren't backfilled automatically.** Versions before 0.1.0 didn't sync declined transactions. To pull in declined transactions older than your current cursor, refresh the `transactions` stream.
- **Most streams are full refresh only.** Every stream except `transactions`, `reimbursements`, and `receipts` re-reads all records on every sync.
- **One business per source.** Client credentials are issued to a single Ramp business. To sync several businesses, create one Airbyte source per business.

## Troubleshooting

The connector reports these Ramp errors as configuration errors, so Airbyte doesn't retry them:

| Error | Cause | Fix |
| --- | --- | --- |
| `Ramp rejected the client ID or client secret` | The token request returned `400` or `401`. | Copy the client ID and client secret again from **Company** > **Developer** > your app, and confirm the app has the **Client Credentials** grant type. |
| `Your Ramp app is not allowed to read this data` | Ramp returned error code `DEVELOPER_7100`. The connector requests every stream's scope when it gets a token. Ramp doesn't fail the token request when the app lacks one of those scopes. It issues a token without that scope, and only the streams that need it fail. | Enable the scope named in the error on your app, then test the source again. Or deselect the streams that need it. |
| `Ramp no longer accepts this connector's access token` | Ramp returned error code `DEVELOPER_7002`. | Check that the Ramp app still exists and that its client secret hasn't been rotated, then test the source again. |
| `Ramp rejected the connector's credentials` | Any other `401` response. | Re-enter the client ID and client secret. |
| `Ramp denied access to this data` | Any other `403` response. | Confirm the app has the scope named in the error. For `purchase_orders`, confirm your plan includes Ramp Plus. |

## Test against the Ramp sandbox

The connector calls `https://api.ramp.com` by default. Since version 0.0.4, an **API Base URL** (`api_url`) field can point it at Ramp's [sandbox](https://docs.ramp.com/developer-api/v1/sandbox) at `https://demo-api.ramp.com` instead. The value must start with `https://`. Leave the default for production accounts.

The field is hidden in the Airbyte UI, so set it programmatically. For example, include it in the source configuration you send through the Airbyte API, Terraform provider, or PyAirbyte. Sandbox and production credentials aren't interchangeable: create a developer app in the sandbox (`https://demo.ramp.com`) with the same grant type and scopes, and use that app's client ID and secret with the sandbox base URL.

## Performance considerations

Ramp allows 200 requests per rolling 10-second window per source IP address, and returns `429 Too Many Requests` when you exceed it. The connector limits itself to 180 requests per 10 seconds and retries failed requests up to 5 times with exponential backoff. Other Ramp sources or integrations that run from the same IP address share Ramp's limit, so they can still trigger `429` responses.

The connector reads 50 records per page. `vendor_contacts` makes at least one request per vendor, so its request count grows with the number of vendors. Ramp terminates requests that take longer than 60 seconds with a `504 Gateway Timeout`. See Ramp's [rate limits and timeouts](https://docs.ramp.com/developer-api/v1/rate-limiting) guide.

Ramp's client credentials access tokens last 10 days. The connector requests a token for each stream it reads and reuses that token for the stream's requests.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.3.0 | 2026-10-08 | [88365](https://github.com/airbytehq/airbyte/pull/88365) | Request merchant purchase data on `transactions` and declare 10 more fields Ramp already returns |
| 0.2.1 | 2026-10-06 | [87999](https://github.com/airbytehq/airbyte/pull/87999) | Update dependencies |
| 0.2.0 | 2026-10-02 | [87610](https://github.com/airbytehq/airbyte/pull/87610) | Add 15 streams for Ramp's organisation, spend-control, accounts-payable and procurement resources |
| 0.1.0 | 2026-10-01 | [86957](https://github.com/airbytehq/airbyte/pull/86957) | Map Ramp auth and scope errors to config errors, add a rate-limit budget, filter `transactions` server-side, sync declined transactions, declare missing fields, and make `start_date` optional |
| 0.0.8 | 2026-09-29 | [87331](https://github.com/airbytehq/airbyte/pull/87331) | Update dependencies |
| 0.0.7 | 2026-09-22 | [86778](https://github.com/airbytehq/airbyte/pull/86778) | Update dependencies |
| 0.0.6 | 2026-09-15 | [86193](https://github.com/airbytehq/airbyte/pull/86193) | Update dependencies |
| 0.0.5 | 2026-09-08 | [85624](https://github.com/airbytehq/airbyte/pull/85624) | Update dependencies |
| 0.0.4 | 2026-08-20 | [84843](https://github.com/airbytehq/airbyte/pull/84843) | Add hidden configurable API base URL for sandbox testing |
| 0.0.3 | 2026-08-18 | [84721](https://github.com/airbytehq/airbyte/pull/84721) | Update dependencies |
| 0.0.2 | 2026-08-11 | [84077](https://github.com/airbytehq/airbyte/pull/84077) | Update dependencies |
| 0.0.1 | 2026-08-06 | [83706](https://github.com/airbytehq/airbyte/pull/83706) | Initial release by [@MercureTony](https://github.com/MercureTony) via Connector Builder |

</details>
