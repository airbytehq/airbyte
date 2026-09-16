# smsmode RCS

The smsmode RCS source connector syncs RCS (Rich Communication Services) message logs and monthly RCS consumption data from your [smsmode](https://www.smsmode.com/) account. It reads from the [smsmode RCS API](https://dev.smsmode.com/rcs/v1/) and the [smsmode Commons API](https://dev.smsmode.com/commons/v1/).

This connector reads RCS data only. To sync SMS data, use the [smsmode SMS](smsmode-sms) connector.

## Prerequisites

- A smsmode account with RCS enabled.
- A smsmode API key. See [Get your API key](#get-your-api-key).

## Setup guide

### Get your API key

The connector authenticates every request with an API key sent in the `X-Api-Key` header.

You create and manage API keys with the smsmode [Credential API](https://dev.smsmode.com/commons/v1/#tag/Credential). Each key is attached to a role, and the role determines which messages the connector can read:

- **User**: messages sent or received through the user's own channels.
- **Manager**: messages for the whole organization.
- **Administrator**: messages for the organization and its sub-organizations.

Create a key with a role that covers all the RCS channels you want to sync. You can revoke a key at any time without affecting other keys on the account.

### Set up the connector in Airbyte

1. In the Airbyte UI, create a new source and select **smsmode RCS**.
2. Enter a name for the source.
3. In **API Key**, paste your smsmode API key.
4. Click **Set up source**.

## Supported sync modes

Both streams support **Full Refresh** only. Incremental syncs aren't supported.

Because each sync returns a fixed lookback window (30 days of messages and 12 months of consumption), a **Full Refresh | Overwrite** sync replaces older data in your destination with only the most recent window. To keep a history that extends past the lookback window, use **Full Refresh | Append** and deduplicate records in your destination.

## Supported streams

| Stream | Source endpoint | What it returns |
|---|---|---|
| `rcs_messages` | [`GET /rcs/v1/messages`](https://dev.smsmode.com/rcs/v1/#tag/Message) | RCS message logs from the last 30 days, including both directions. |
| `consumptions_rcs` | [`GET /commons/v1/consumptions`](https://dev.smsmode.com/commons/v1/#tag/Consumption) | Monthly RCS consumption records for the last 12 months. |

### rcs_messages

This stream returns message logs for a rolling 30-day window that ends at sync time (in UTC). You can't configure the window.

The connector requests each direction separately and merges the results into a single stream:

- **MT** (Mobile Terminated): messages your account sent to recipients.
- **MO** (Mobile Originated): messages recipients sent to your RCS agent.

Each record includes a `direction` field (`MT` or `MO`) so you can tell the two apart downstream.

The connector retries failed requests to this endpoint up to 5 times with exponential backoff.

### consumptions_rcs

This stream returns one record per month of RCS consumption, starting 365 days before the sync date. The connector filters the Commons consumption endpoint to `periodType=MONTH` and `channel.type=RCS`, so it doesn't include daily breakdowns or SMS consumption.

## Limitations

- The 30-day message window and the 12-month consumption window are fixed in the connector. To backfill older data, export it from smsmode directly.
- Neither stream defines a primary key, so Airbyte can't deduplicate records for you.
- The connector pages through results 100 records at a time, which is the maximum page size the smsmode API allows.
- smsmode doesn't publish rate limits for these endpoints.

## Reference

### Configuration

| Input | Type | Description | Default Value |
|---|---|---|---|
| `api_key` | `string` | API Key. Your smsmode API key, created with the [Credential API](https://dev.smsmode.com/commons/v1/#tag/Credential). |  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-09-16 | [79710](https://github.com/airbytehq/airbyte/pull/79710) | Initial release by [@CaladeTechnologies](https://github.com/CaladeTechnologies) via Connector Builder. Syncs a rolling 30-day window of `rcs_messages` across MT and MO directions, and monthly `consumptions_rcs`. |

</details>
