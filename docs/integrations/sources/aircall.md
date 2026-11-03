# Aircall

This page contains the setup guide and reference information for the [Aircall](https://developers.aircall.io/api-references/#rest-api) source

## Prerequisites

Create an API key in the Aircall Dashboard under **Integrations & API > API Keys**. The API ID and API token are both required.

## Setup guide

### Step 1: Set up Aircall connection

- Create an API key in **Integrations & API > API Keys** in the Aircall Dashboard.
- Enter the required API ID and API token.
- Available params
  - `api_id`: Your Aircall API ID.
  - `api_token`: The API token shown with the API ID.
  - `window_in_days` (Window size): optional days of calls per request window, default 1. Calls split a window that hits Aircall's 10,000-result limit on their own; larger windows save requests only for companies with few calls.
  - `contacts_window_in_days` (Contacts window size): optional days of new contacts per request window, default 30. Lower it if a contacts sync fails with the 10,000-results error.
  - `num_workers`: optional concurrent workers, from 1 to 4 (default 2). All workers share one budget of 100 requests per minute, below Aircall's company-wide limit of 120.

### Step 2: Set up the Aircall connector in Airbyte

#### For Airbyte Cloud

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Aircall connector and select **Aircall** from the Source type dropdown.
4. Enter your API ID and API token.
5. Click **Set up source**.

#### For Airbyte OSS

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your API ID and API token.
4. Click **Set up source**.

## Supported sync modes

The Aircall source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

| Stream                   | Sync mode                 | Notes                                                                                                                                                                                                                                                                                                                                                                                                           |
| :----------------------- | :------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| calls                    | Full refresh, incremental | Incremental syncs read the last three days again. See below.                                                                                                                                                                                                                                                                                                                                                    |
| company                  | Full refresh              | Used for connection checks.                                                                                                                                                                                                                                                                                                                                                                                     |
| contacts                 | Full refresh              |                                                                                                                                                                                                                                                                                                                                                                                                                 |
| numbers                  | Full refresh, incremental | Incremental sync rereads all records to capture edits.                                                                                                                                                                                                                                                                                                                                                          |
| tags                     | Full refresh              |                                                                                                                                                                                                                                                                                                                                                                                                                 |
| user_availability        | Full refresh              |                                                                                                                                                                                                                                                                                                                                                                                                                 |
| users                    | Full refresh              | Uses the Aircall User V2 API.                                                                                                                                                                                                                                                                                                                                                                                   |
| teams                    | Full refresh, incremental | Incremental sync rereads all records to capture edits.                                                                                                                                                                                                                                                                                                                                                          |
| webhooks                 | Full refresh              |                                                                                                                                                                                                                                                                                                                                                                                                                 |
| conversations            | Full refresh, incremental | Needs the Conversations API. Incremental syncs pick up conversations with a new call or message; a close, reopen or assignment without new activity arrives with the next activity or a full refresh.                                                                                                                                                                                                           |
| conversation_engagements | Full refresh, incremental | Needs the Conversations API. The first sync makes one request per conversation. Incremental syncs read the engagements of every conversation with activity since three days before the last sync, so a daily schedule keeps them small; closes, reopens and assignments without a new call or message arrive only with a full refresh. Aircall returns at most the newest 10,000 engagements of a conversation. |
| campaigns                | Full refresh              | Outbound campaigns.                                                                                                                                                                                                                                                                                                                                                                                             |
| campaign_outcomes        | Full refresh              | Outcomes agents can set on campaign calls.                                                                                                                                                                                                                                                                                                                                                                      |
| trackers                 | Full refresh              | Needs AI Assist or AI Assist Pro; returns no records without it.                                                                                                                                                                                                                                                                                                                                                |
| sms_templates            | Full refresh              |                                                                                                                                                                                                                                                                                                                                                                                                                 |
| whatsapp_templates       | Full refresh              | Read per number; numbers not registered for WhatsApp return no templates.                                                                                                                                                                                                                                                                                                                                       |

## API method example

GET https://api.aircall.io/v1/numbers

## Performance considerations

The connector uses Aircall's [v1 API](https://developers.aircall.io/api-references/), and the [User V2 API](https://developers.aircall.io/api-references/#list-all-users-v2) for users. Calls, contacts and conversations are read in date windows because Aircall returns at most [10,000 records per query](https://developers.aircall.io/api-references/#pagination); a calls window that hits the limit is split and read again, and conversations continue from the last record's time. Without the Conversations API, every sync that selects `conversations` or `conversation_engagements` still spends one request per 30 days of history on the refused windows, so deselect both streams when the API is not enabled. The connector uses 100 of the [120 requests per minute](https://developers.aircall.io/api-references/#rate-limiting) Aircall allows each company, leaving room for the company's other integrations. Calls cover the six months of history Aircall keeps; the Start date saved by versions before 0.5.0 is no longer used.

The `calls` stream has no primary key before version 1.0.0. Incremental syncs read the last three days of calls again, and a day with more than 10,000 calls is read more than once, so Append mode stores those calls again. Use Append + Deduped with `id` as the primary key to keep one row per call. The same applies to `conversations` and `conversation_engagements`, whose incremental syncs also read the last three days again.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.6.0 | 2026-11-03 | [90837](https://github.com/airbytehq/airbyte/pull/90837) | Add `conversations`, `conversation_engagements`, `campaigns`, `campaign_outcomes`, `trackers`, `sms_templates` and `whatsapp_templates` streams |
| 0.5.0 | 2026-11-03 | [90835](https://github.com/airbytehq/airbyte/pull/90835) | Read calls incrementally in daily windows that split at Aircall's 10,000-result limit, read contacts in date windows, honour Aircall's rate limit, declare `user_availability` `id` and `availability`, and read numbers and teams once per sync |
| 0.4.27 | 2026-10-13 | [88524](https://github.com/airbytehq/airbyte/pull/88524) | Update dependencies |
| 0.4.26 | 2026-10-06 | [87742](https://github.com/airbytehq/airbyte/pull/87742) | Update dependencies |
| 0.4.25 | 2026-09-29 | [87057](https://github.com/airbytehq/airbyte/pull/87057) | Update dependencies |
| 0.4.24 | 2026-09-23 | [85909](https://github.com/airbytehq/airbyte/pull/85909) | Migrate the `users` stream to the Aircall User V2 API ahead of the V1 sunset and add pagination |
| 0.4.23 | 2026-09-22 | [86517](https://github.com/airbytehq/airbyte/pull/86517) | Update dependencies |
| 0.4.22 | 2026-09-15 | [85956](https://github.com/airbytehq/airbyte/pull/85956) | Update dependencies |
| 0.4.21 | 2026-09-08 | [85381](https://github.com/airbytehq/airbyte/pull/85381) | Update dependencies |
| 0.4.20 | 2026-08-18 | [84505](https://github.com/airbytehq/airbyte/pull/84505) | Update dependencies |
| 0.4.19 | 2026-08-11 | [83832](https://github.com/airbytehq/airbyte/pull/83832) | Update dependencies |
| 0.4.18 | 2026-08-04 | [83374](https://github.com/airbytehq/airbyte/pull/83374) | Update dependencies |
| 0.4.17 | 2026-07-28 | [82810](https://github.com/airbytehq/airbyte/pull/82810) | Update dependencies |
| 0.4.16 | 2026-07-21 | [82307](https://github.com/airbytehq/airbyte/pull/82307) | Update dependencies |
| 0.4.15 | 2026-07-14 | [81718](https://github.com/airbytehq/airbyte/pull/81718) | Update dependencies |
| 0.4.14 | 2026-06-30 | [80992](https://github.com/airbytehq/airbyte/pull/80992) | Update dependencies |
| 0.4.13 | 2026-06-23 | [80364](https://github.com/airbytehq/airbyte/pull/80364) | Update dependencies |
| 0.4.12 | 2026-06-16 | [79750](https://github.com/airbytehq/airbyte/pull/79750) | Update dependencies |
| 0.4.11 | 2026-06-09 | [79207](https://github.com/airbytehq/airbyte/pull/79207) | Update dependencies |
| 0.4.10 | 2026-06-02 | [78574](https://github.com/airbytehq/airbyte/pull/78574) | Update dependencies |
| 0.4.9 | 2026-04-28 | [77183](https://github.com/airbytehq/airbyte/pull/77183) | Update dependencies |
| 0.4.8 | 2026-04-21 | [76490](https://github.com/airbytehq/airbyte/pull/76490) | Update dependencies |
| 0.4.7 | 2026-03-17 | [74979](https://github.com/airbytehq/airbyte/pull/74979) | Update dependencies |
| 0.4.6 | 2026-02-10 | [73001](https://github.com/airbytehq/airbyte/pull/73001) | Update dependencies |
| 0.4.5 | 2026-01-27 | [72373](https://github.com/airbytehq/airbyte/pull/72373) | Update dependencies |
| 0.4.4 | 2026-01-14 | [71503](https://github.com/airbytehq/airbyte/pull/71503) | Update dependencies |
| 0.4.3 | 2025-12-02 | [70282](https://github.com/airbytehq/airbyte/pull/70282) | Update dependencies |
| 0.4.2 | 2025-10-29 | [65055](https://github.com/airbytehq/airbyte/pull/65055) | Update dependencies |
| 0.4.1 | 2025-09-12 | [66197](https://github.com/airbytehq/airbyte/pull/66197) | Update to CDK v7 |
| 0.4.0 | 2024-08-23 | [44597](https://github.com/airbytehq/airbyte/pull/44597) | Refactor connector to manifest-only format |
| 0.3.0 | 2024-08-19 | [44437](https://github.com/airbytehq/airbyte/pull/44437) | Fix pagination |
| 0.2.12 | 2024-08-17 | [43879](https://github.com/airbytehq/airbyte/pull/43879) | Update dependencies |
| 0.2.11 | 2024-08-10 | [43482](https://github.com/airbytehq/airbyte/pull/43482) | Update dependencies |
| 0.2.10 | 2024-08-03 | [43101](https://github.com/airbytehq/airbyte/pull/43101) | Update dependencies |
| 0.2.9 | 2024-07-27 | [42743](https://github.com/airbytehq/airbyte/pull/42743) | Update dependencies |
| 0.2.8 | 2024-07-20 | [42357](https://github.com/airbytehq/airbyte/pull/42357) | Update dependencies |
| 0.2.7 | 2024-07-13 | [41708](https://github.com/airbytehq/airbyte/pull/41708) | Update dependencies |
| 0.2.6 | 2024-07-10 | [41448](https://github.com/airbytehq/airbyte/pull/41448) | Update dependencies |
| 0.2.5 | 2024-07-09 | [41156](https://github.com/airbytehq/airbyte/pull/41156) | Update dependencies |
| 0.2.4 | 2024-07-06 | [40801](https://github.com/airbytehq/airbyte/pull/40801) | Update dependencies |
| 0.2.3 | 2024-06-25 | [40503](https://github.com/airbytehq/airbyte/pull/40503) | Update dependencies |
| 0.2.2 | 2024-06-21 | [39920](https://github.com/airbytehq/airbyte/pull/39920) | Update dependencies |
| 0.2.2 | 2024-06-20 | [39681](https://github.com/airbytehq/airbyte/pull/39681) | Update dependencies |
| 0.2.1 | 2024-06-06 | [38454](https://github.com/airbytehq/airbyte/pull/38454) | [autopull] base image + poetry + up_to_date |
| 0.2.0 | 2023-06-20 | [Correcting availablity typo](https://github.com/airbytehq/airbyte/pull/27433) | Correcting availablity typo |
| 0.1.0 | 2023-04-19 | [Init](https://github.com/airbytehq/airbyte/pull/) | Initial commit |

</details>
