# Aircall

This page contains the setup guide and reference information for the [Aircall](https://aircall.io/) source connector. The connector reads calls, contacts, users, numbers, teams, conversations, campaigns and other company data from the [Aircall Public API](https://developers.aircall.io/api-references/).

## Prerequisites

- An Aircall account with the **Admin** role. Only Admins can open the Aircall Dashboard, where API keys are created ([Users](https://developers.aircall.io/api-references/#user-v2-overview)).
- An Aircall API key, made of an **API ID** and an **API token**. The connector authenticates every request with [Basic authentication](https://developers.aircall.io/api-references/#basic-auth-aircall-customers), using the API ID as the username and the API token as the password.

## Setup guide

### Step 1: Set up Aircall

Create an Aircall API key:

1. Log in to the [Aircall Dashboard](https://dashboard.aircall.io/) as an Admin.
2. Go to **Integrations & API** > [**API Keys**](https://dashboard.aircall.io/integrations/api-keys). Aircall's reference calls this the **API Keys** section of your company's settings.
3. Click **Add a new API key**.
4. Copy the **API ID** and the **API token**. Aircall doesn't store the token in plain text and can't show it again, so keep it somewhere safe. If you lose it, create a new key ([Basic authentication](https://developers.aircall.io/api-references/#basic-auth-aircall-customers)).

### Step 2: Set up the Aircall connector in Airbyte

<!-- env:cloud -->

#### For Airbyte Cloud

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**, then click **New source**.
3. Select **Aircall** from the list of sources.
4. Enter a name for the source.
5. Enter your **API ID** and **API Token**.
6. Optionally, set **Window size (days)**, **Contacts window size (days)** and **Concurrent workers**. See [Configuration options](#configuration-options).
7. Click **Set up source**.

<!-- /env:cloud -->

<!-- env:oss -->

#### For Airbyte Open Source

1. Open your Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**, then click **New source**.
3. Select **Aircall** from the list of sources.
4. Enter a name for the source.
5. Enter your **API ID** and **API Token**.
6. Optionally, set **Window size (days)**, **Contacts window size (days)** and **Concurrent workers**. See [Configuration options](#configuration-options).
7. Click **Set up source**.

<!-- /env:oss -->

### Configuration options

| Field | Required | Description |
| :--- | :--- | :--- |
| **API ID** | Yes | The API ID of your Aircall API key. |
| **API Token** | Yes | The API token shown with the API ID when you created the key. |
| **Window size (days)** | No | Days of calls requested at a time, from 1 to 365. Leave it empty for 1 day. A window that holds more than 10,000 calls is split and partly read again, so a larger window only saves requests for companies with few calls. If a sync fails with `could not split its request window`, lower this setting. See [10,000-result limit](#10000-result-limit). |
| **Contacts window size (days)** | No | Days of newly created contacts requested at a time, from 1 to 365. Leave it empty for 30 days. Lower it if a sync fails with the 10,000-results error for contacts. |
| **Concurrent workers** | No | Number of parallel requests, from 1 to 4. The default is 2. All workers share one [rate limit](#rate-limit). |

Connections created before version 0.5.0 also have a Start date. The connector no longer uses it, and the form hides it.

## Supported sync modes

The Aircall source connector supports the following [sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/):

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |
| Namespaces | No |

Three streams support incremental sync. Each incremental sync reads the last three days again, so use `Incremental | Append + Deduped` to keep one row per record.

- `calls` uses `started_at`. Calls still in progress and edits made soon after a call reach the destination. Later edits to older calls, such as a tag added weeks later, arrive only with a [Refresh and Retain Records](https://docs.airbyte.com/platform/operator-guides/refreshes#refresh-and-retain-records) sync. Clearing `calls`, a Refresh and Remove Records sync or an Overwrite mode deletes calls older than six months for good (see [Six months of call history](#six-months-of-call-history)).
- `conversations` uses the time of the last call or message. Closing, reopening or assigning a conversation without a new call or message doesn't change that time, so those changes arrive with the next activity or a full refresh.
- `conversation_engagements` reads the engagements of the conversations that `conversations` returns, so incremental syncs read only conversations active since three days before the previous sync.

Every other stream is full refresh only. Aircall filters some of these lists, such as contacts, numbers and users, by creation date and none of them by update date, so an incremental sync would miss edits to existing records ([List all Contacts](https://developers.aircall.io/api-references/#list-all-contacts), [List all Numbers](https://developers.aircall.io/api-references/#list-all-numbers)).

## Supported Streams

| Stream | Sync modes | Primary key | Plan or add-on |
| :--- | :--- | :--- | :--- |
| [`calls`](https://developers.aircall.io/api-references/#list-all-calls) | Full refresh, incremental | `id` | All plans |
| [`campaign_outcomes`](https://developers.aircall.io/api-references/#list-all-campaign-outcomes) | Full refresh | `id` | Outbound Campaigns |
| [`campaigns`](https://developers.aircall.io/api-references/#list-all-campaigns) | Full refresh | `id` | Outbound Campaigns |
| [`company`](https://developers.aircall.io/api-references/#retrieve-company-information) | Full refresh | None | All plans |
| [`contacts`](https://developers.aircall.io/api-references/#list-all-contacts) | Full refresh | `id` | All plans |
| [`conversation_engagements`](https://developers.aircall.io/api-references/#list-the-engagements-of-a-conversation) | Full refresh, incremental | `id` | Conversations API |
| [`conversations`](https://developers.aircall.io/api-references/#list-all-conversations) | Full refresh, incremental | `id` | Conversations API |
| [`numbers`](https://developers.aircall.io/api-references/#list-all-numbers) | Full refresh | `id` | All plans |
| [`sms_templates`](https://developers.aircall.io/api-references/#list-sms-templates) | Full refresh | `id` | All plans |
| [`tags`](https://developers.aircall.io/api-references/#list-all-tags) | Full refresh | `id` | All plans |
| [`teams`](https://developers.aircall.io/api-references/#list-all-teams) | Full refresh | `id` | All plans |
| [`trackers`](https://developers.aircall.io/api-references/#list-all-trackers) | Full refresh | `id` | AI Assist or AI Assist Pro |
| [`user_availability`](https://developers.aircall.io/api-references/#retrieve-list-of-users-availability) | Full refresh | `id` | All plans |
| [`users`](https://developers.aircall.io/api-references/#list-all-users-v2) | Full refresh | `id` | All plans |
| [`webhooks`](https://developers.aircall.io/api-references/#list-all-webhooks) | Full refresh | `webhook_id` | All plans |
| [`whatsapp_templates`](https://developers.aircall.io/api-references/#list-whatsapp-templates) | Full refresh | `number_id`, `id` | Numbers registered for WhatsApp |

Notes:

- `company` has no primary key. Aircall returns a single company object with no identifier ([Retrieve Company information](https://developers.aircall.io/api-references/#retrieve-company-information)).
- `contacts` returns shared contacts only ([List all Contacts](https://developers.aircall.io/api-references/#list-all-contacts)).
- `users` reads the [User V2 API](https://developers.aircall.io/api-references/#user-v2-overview).
- `webhooks` uses `webhook_id`, the UUID that identifies a webhook. Aircall treats the integer `id` as the old identifier ([List all Webhooks](https://developers.aircall.io/api-references/#list-all-webhooks)).
- `conversation_engagements` returns the calls, messages, WhatsApp messages, assignments, unassignments, closes and reopens of each conversation. The first sync and every full refresh make at least one request per conversation. Each incremental sync re-reads the engagements of every conversation active since three days before the previous sync, so syncing more often than daily repeats most of that work.
- `whatsapp_templates` returns the templates of each number, with `number_id` identifying the number.

## Limitations and troubleshooting

### 10,000-result limit

Aircall returns at most 10,000 calls, contacts, conversations or engagements for a single query, even with pagination ([Pagination](https://developers.aircall.io/api-references/#pagination), [List all Conversations](https://developers.aircall.io/api-references/#list-all-conversations)). The connector works around it per stream:

- `calls` are requested one day at a time by default (**Window size (days)**). A window with more than 10,000 calls is split into smaller time ranges and read again, so some of its calls are sent more than once; `Incremental | Append + Deduped` keeps one row per call.
- `contacts` are requested 30 days of creation date at a time (**Contacts window size (days)**). If a sync fails with `Aircall returns at most 10,000 contacts per request window`, lower that setting. A single day with more than 10,000 new contacts can't be read.
- `conversations` continue from the time of the last record after every 10,000 records.
- `conversation_engagements` returns at most the newest 10,000 engagements of a conversation; older ones aren't synced.

### Six months of call history

Aircall keeps only six months of call history in the API ([List all Calls](https://developers.aircall.io/api-references/#list-all-calls)). The connector reads `calls` from 365 days back on every full refresh and on the first incremental sync, which covers all the history Aircall keeps. Older calls aren't returned, so syncing `calls` in an Overwrite mode, clearing it, or running a Refresh and Remove Records sync deletes calls older than six months from the destination for good. Keep `calls` in `Incremental | Append + Deduped`, and use [Refresh and Retain Records](https://docs.airbyte.com/platform/operator-guides/refreshes#refresh-and-retain-records) to re-read the last six months. To get older calls, ask [Aircall Support](https://support.aircall.io/) for a one-time export.

### Rate limit

Aircall allows 120 requests per minute per company, shared by every API key and integration on your Aircall account ([Rate limiting](https://developers.aircall.io/api-references/#rate-limiting)). The connector uses at most 100 of them and, when Aircall rejects a request for exceeding the limit, waits until Aircall resets the counter. Raising **Concurrent workers** doesn't raise the limit. Aircall Support can raise the limit for your API keys.

### Streams that sync no records

Some streams need an Aircall add-on or a specific number setup. When your company doesn't have it, Aircall refuses the requests, and the connector logs a message for each refused request instead of failing the sync:

| Stream | Requirement |
| :--- | :--- |
| `conversations`, `conversation_engagements` | The Conversations API must be enabled for your company ([List all Conversations](https://developers.aircall.io/api-references/#list-all-conversations)). Without it, each sync still spends one request per 30 days since January 2014 on each of the two streams, about 157 each, so deselect both streams. |
| `trackers` | The AI Assist or AI Assist Pro package ([List all Trackers](https://developers.aircall.io/api-references/#list-all-trackers)). |
| `whatsapp_templates` | Only numbers registered for WhatsApp return templates ([List WhatsApp Templates](https://developers.aircall.io/api-references/#list-whatsapp-templates)). |

If a sync fails with `Aircall rejected the API ID and API token` or `Aircall returned HTTP 403`, the API key is wrong or was deleted, or your Aircall plan doesn't include that data. Create a new API key and update the source, or check your plan.

### Upgrading to 1.0.0

Version 1.0.0 adds primary keys to `calls` and `contacts`, changes the `webhooks` primary key to `webhook_id`, makes `numbers` and `teams` full refresh only, and changes several column types. Some destinations need a step before you upgrade or before the first 1.0.0 sync: ClickHouse for `Full Refresh | Append` `users` ([Before you upgrade](aircall-migrations.md#before-you-upgrade)) and Snowflake for append-mode `calls` ([If you keep an append-mode calls table](aircall-migrations.md#if-you-keep-an-append-mode-calls-table)). After upgrading, refresh the source schema and switch `numbers` and `teams` from an Incremental mode to `Full Refresh | Overwrite`. Clearing `calls` or switching it to an Overwrite mode deletes calls older than six months for good. Follow the [migration guide](aircall-migrations.md#upgrading-to-100).

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 1.0.0 | 2026-11-03 | [90838](https://github.com/airbytehq/airbyte/pull/90838) | Add primary keys to `calls` and `contacts`, key `webhooks` on `webhook_id`, make `numbers` and `teams` full refresh only, and declare the column types the Aircall API documents |
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
