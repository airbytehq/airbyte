# smsmode SMS

<HideInUI>

This page contains the setup guide and reference information for the [smsmode](https://www.smsmode.com/) SMS source connector.

</HideInUI>

A source connector for the smsmode API dedicated to standard SMS services, supporting message logs and general consumption data synchronization.

## Prerequisites

- An smsmode account with at least one SMS channel
- An smsmode API key whose role grants read access to the messages and consumptions of the channels you want to sync

## Setup guide

### Step 1: Create an smsmode API key

smsmode calls API keys *credentials*, and you manage them through the [Credential API](https://dev.smsmode.com/commons/v1/#tag/Credential). Each credential carries one or more roles, and the roles determine how much data the key can read:

- A `USER` key reads the messages and consumptions of its own channel.
- A `MANAGER` key reads them for every channel in its organisation.
- An `ADMIN` key also reads them for channels in sub-organisations.

The connector calls the credential-scoped endpoints, so the key you configure defines the scope of every sync. Use a key with a role broad enough to cover the channels you need. You can revoke a key independently of your other keys, so create a dedicated one for Airbyte.

### Step 2: Configure the connector

Enter the API key. The connector sends it in the `X-Api-Key` header on every request, which is the only authentication method the smsmode API supports.

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your smsmode API key. You can generate and manage API keys in the smsmode dashboard under the &#39;Credentials&#39; section: https://dev.smsmode.com/commons/v1/#tag/Credential. Make sure the key is active and has the required permissions for your use case. |  |

<HideInUI>

## Supported sync modes

Both streams support full refresh only. Neither stream declares a cursor field, so every sync re-reads the current API window described in [Limitations](#limitations).

## Supported streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| messages |  | DefaultPaginator | ✅ |  ❌  |
| consumptions | consumptionId | DefaultPaginator | ✅ |  ❌  |

- **messages** comes from [`GET /sms/v1/messages`](https://dev.smsmode.com/sms/v1/#tag/Message/operation/messages-list). Each record is one message of the channel linked to your API key, with its recipient, encoding, cost, and delivery status. The API defaults to sent messages (`MT`); the connector doesn't request incoming (`MO`) messages.
- **consumptions** comes from [`GET /commons/v1/consumptions`](https://dev.smsmode.com/commons/v1/#tag/Consumption/operation/consumptions-list). Each record aggregates the message quantity and price for one channel over one period. The API defaults to monthly SMS totals (`SMS_MONTH`), so a record covers a calendar month rather than a single day.

The connector requests 100 records per page, the maximum smsmode allows, and walks the `page` parameter until the API stops returning items.

## Limitations

- **Both streams return a fixed, rolling window.** The connector doesn't send `startDate` or `endDate`, so the smsmode defaults apply: `messages` covers the last 10 days up to now, and `consumptions` covers the last 3 months up to today. Older records aren't reachable through this connector, and records that fall out of the window disappear from later syncs. If you need a longer history, sync often enough to capture data before it ages out and use a destination sync mode that appends rather than overwrites.
- **No incremental sync.** Each sync re-reads the whole window.
- **`messages` has no primary key.** Deduplication isn't available for that stream, even though each record carries a `messageId`.
- **Rate limits.** smsmode returns HTTP 429 when you send too many requests in a given period but doesn't publish the numeric limit. If you hit it, sync less often or narrow the connection to one stream.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-08-28 | [79709](https://github.com/airbytehq/airbyte/pull/79709) | Initial release by [@CaladeTechnologies](https://github.com/CaladeTechnologies) via Connector Builder |

</details>

</HideInUI>
