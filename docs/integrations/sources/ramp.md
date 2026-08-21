# Ramp

The Ramp source syncs cards, transactions, and reimbursements from the [Ramp Developer API](https://docs.ramp.com/developer-api) for a single Ramp business.

## Prerequisites

- A Ramp account with administrator access, so you can create a developer app.
- A Ramp developer app that uses the **Client Credentials** grant type, with the `cards:read`, `transactions:read`, and `reimbursements:read` scopes enabled.
- The client ID and client secret for that app.

## Set up the Ramp source

### Step 1: Create a Ramp developer app

1. In your Ramp account, go to **Company** > **Developer**.
2. Select **Create New App**, name the app, and accept the terms.
3. Under **Grant types**, select **Add new grant type** > **Client Credentials**. The connector authenticates server-to-server, so the authorization code flow isn't used and no redirect URI is needed.
4. Under **Scopes**, select **Configure allowed scopes** and enable `cards:read`, `transactions:read`, and `reimbursements:read`. The connector requests all three scopes on every token request, so a missing scope fails the connection check.
5. Copy the client ID and client secret.

For more detail, see Ramp's [quickstart](https://docs.ramp.com/developer-api/v1/getting-started) and [authorization guide](https://docs.ramp.com/developer-api/v1/authorization).

### Step 2: Configure the source in Airbyte

Enter the client ID and client secret, then set **Start Date**. Start Date is required and must be an ISO 8601 timestamp with a `Z` suffix, such as `2024-01-01T00:00:00Z`. Values with a numeric UTC offset, such as `2024-01-01T00:00:00+00:00`, are rejected.

Start Date is the earliest `updated_at` the `transactions` and `reimbursements` streams read on their first sync. Later incremental syncs use the saved cursor instead. The `cards` stream ignores Start Date.

## Supported streams

| Stream | API endpoint | Primary key | Sync modes | Incremental cursor |
| --- | --- | --- | --- | --- |
| `cards` | `GET /developer/v1/cards` | `id` | Full refresh | — |
| `transactions` | `GET /developer/v1/transactions` | `id` | Full refresh, incremental | `updated_at` |
| `reimbursements` | `GET /developer/v1/reimbursements` | `id` | Full refresh, incremental | `updated_at` |

`cards` returns both physical and virtual cards, including their state, cardholder, card program, and spending restrictions.

`transactions` returns card transactions with merchant, cardholder, accounting, and receipt details.

`reimbursements` returns out-of-pocket reimbursements and repayments. Ramp's endpoint returns one direction at a time and defaults to `BUSINESS_TO_USER`, so the connector requests both `BUSINESS_TO_USER` (out-of-pocket reimbursements) and `USER_TO_BUSINESS` (repayments) and emits them into one stream. Use the `direction` field to tell them apart.

## Sync behavior and limitations

- **Declined transactions aren't synced.** Ramp's transactions endpoint omits `DECLINED` transactions unless the request sets `state=ALL`, and the connector doesn't set that parameter. Only transactions in other states, such as `PENDING`, `CLEARED`, and `ERROR`, reach your destination.
- **`transactions` filters incrementally after the fetch.** The connector doesn't send a date filter to the transactions endpoint. Every sync pages through the account's full transaction list and emits only the records whose `updated_at` is newer than the cursor. Sync duration scales with the size of your transaction history, not with how much changed, so syncs get slower as history grows. `reimbursements` doesn't have this problem: the connector sends the cursor as the API's `updated_after` filter.
- **`cards` is full refresh only.** The cards endpoint has no updated-at filter, so every sync re-reads all cards.
- **One business per source.** Client credentials are issued to a single Ramp business. To sync several businesses, create one Airbyte source per business.

## Test against the Ramp sandbox

The connector calls `https://api.ramp.com` by default. As of version 0.0.4, an **API Base URL** (`api_url`) field can point it at Ramp's [sandbox](https://docs.ramp.com/developer-api/v1/sandbox) at `https://demo-api.ramp.com` instead. Production accounts should leave the default.

The field is hidden in the Airbyte UI, so set it programmatically. For example, include it in the source configuration you send through the Airbyte API, Terraform provider, or PyAirbyte. Sandbox and production credentials aren't interchangeable: create a developer app in the sandbox (`https://demo.ramp.com`) with the same grant type and scopes, and use that app's client ID and secret with the sandbox base URL.

## Performance considerations

Ramp allows 200 requests per rolling 10-second window per source IP address, and returns `429 Too Many Requests` when you exceed it. The connector retries failed requests up to 5 times with exponential backoff. If you run several Ramp sources or other Ramp integrations from the same IP, they share this budget.

The connector reads 50 records per page. Requests that take longer than 60 seconds are terminated by Ramp with a `504 Gateway Timeout`.

Ramp's client credentials access tokens last 10 days. The connector fetches a token at the start of a sync and reuses it for that long, so it doesn't spend requests re-authenticating.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Ramp Client ID. Your Ramp API client ID, created in Ramp&#39;s developer settings. |  |
| `client_secret` | `string` | Ramp Client Secret. Your Ramp API client secret. |  |
| `start_date` | `string` | Start Date. Earliest updated_at to pull on the initial sync of the transactions and reimbursements streams. Format ISO 8601 with Z suffix (e.g. 2024-01-01T00:00:00Z). Ignored on subsequent incremental syncs. |  |

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.4 | 2026-08-20 | [84843](https://github.com/airbytehq/airbyte/pull/84843) | Add hidden configurable API base URL for sandbox testing |
| 0.0.3 | 2026-08-18 | [84721](https://github.com/airbytehq/airbyte/pull/84721) | Update dependencies |
| 0.0.2 | 2026-08-11 | [84077](https://github.com/airbytehq/airbyte/pull/84077) | Update dependencies |
| 0.0.1 | 2026-08-06 | [83706](https://github.com/airbytehq/airbyte/pull/83706) | Initial release by [@MercureTony](https://github.com/MercureTony) via Connector Builder |

</details>
