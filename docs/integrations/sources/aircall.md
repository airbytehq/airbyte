# Aircall

This page contains the setup guide and reference information for the [Aircall](https://aircall.io/) source connector. The connector reads calls, contacts, users, numbers, teams, conversations, campaigns and other company data from the [Aircall Public API](https://developers.aircall.io/api-references/).

## Prerequisites

- An Aircall account with the **Admin** role. Only Admins can open the Aircall Dashboard, where API keys are created ([Users](https://developers.aircall.io/api-references/#user-v2-overview)).
- An Aircall API key, made of an **API ID** and an **API token**. The connector signs every request with [Basic authentication](https://developers.aircall.io/api-references/#basic-auth-aircall-customers), using the API ID as the username and the API token as the password.

## Setup guide

### Step 1: Create an Aircall API key

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
6. Optionally, set **Window size (days)** and **Concurrent workers**. See [Configuration options](#configuration-options).
7. Click **Set up source**.

<!-- /env:cloud -->

<!-- env:oss -->

#### For Airbyte Open Source

1. Open your Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**, then click **New source**.
3. Select **Aircall** from the list of sources.
4. Enter a name for the source.
5. Enter your **API ID** and **API Token**.
6. Optionally, set **Window size (days)** and **Concurrent workers**. See [Configuration options](#configuration-options).
7. Click **Set up source**.

<!-- /env:oss -->

### Configuration options

| Field                   | Required | Description                                                                                                                                                                                                                             |
| :---------------------- | :------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **API ID**              | Yes      | The API ID of your Aircall API key.                                                                                                                                                                                                     |
| **API Token**           | Yes      | The API token shown with the API ID when you created the key.                                                                                                                                                                           |
| **Window size (days)**  | No       | Days of records requested at a time for `calls`, `contacts` and `conversations`, from 1 to 365. Leave it empty to use 1 day for `calls` and 30 days for `contacts` and `conversations`. See [10,000-result limit](#10000-result-limit). |
| **Concurrent workers**  | No       | Number of parallel requests, from 1 to 4. The default is 2. All workers share Aircall's [rate limit](#rate-limit).                                                                                                                      |
| **Start date (unused)** | No       | Not used since version 0.5.0. Kept so existing connections keep working. `calls` always starts six months back, and the other streams return every record.                                                                              |

## Supported sync modes

The Aircall source connector supports the following [sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

Two streams support incremental sync:

- `calls` uses `started_at` as its cursor. Each sync re-reads the last three days of calls so that later edits, such as new tags, comments or archiving, reach the destination.
- `conversations` uses `last_engagement_at` as its cursor and also re-reads the last three days.

Every other stream is full refresh only. Aircall filters these lists by creation date, not by update date, so an incremental sync would miss edits to existing records ([List all Contacts](https://developers.aircall.io/api-references/#list-all-contacts), [List all Numbers](https://developers.aircall.io/api-references/#list-all-numbers)).

## Supported streams

| Stream                                                                                                             | Sync modes                | Primary key       | Plan or add-on                  |
| :----------------------------------------------------------------------------------------------------------------- | :------------------------ | :---------------- | :------------------------------ |
| [`calls`](https://developers.aircall.io/api-references/#list-all-calls)                                            | Full refresh, incremental | `id`              | All plans                       |
| [`campaign_outcomes`](https://developers.aircall.io/api-references/#list-all-campaign-outcomes)                    | Full refresh              | `id`              | All plans                       |
| [`campaigns`](https://developers.aircall.io/api-references/#list-all-campaigns)                                    | Full refresh              | `id`              | All plans                       |
| [`company`](https://developers.aircall.io/api-references/#retrieve-company-information)                            | Full refresh              | None              | All plans                       |
| [`contacts`](https://developers.aircall.io/api-references/#list-all-contacts)                                      | Full refresh              | `id`              | All plans                       |
| [`conversation_engagements`](https://developers.aircall.io/api-references/#list-the-engagements-of-a-conversation) | Full refresh              | `id`              | Conversations API               |
| [`conversations`](https://developers.aircall.io/api-references/#list-all-conversations)                            | Full refresh, incremental | `id`              | Conversations API               |
| [`numbers`](https://developers.aircall.io/api-references/#list-all-numbers)                                        | Full refresh              | `id`              | All plans                       |
| [`sms_templates`](https://developers.aircall.io/api-references/#list-sms-templates)                                | Full refresh              | `id`              | All plans                       |
| [`tags`](https://developers.aircall.io/api-references/#list-all-tags)                                              | Full refresh              | `id`              | All plans                       |
| [`teams`](https://developers.aircall.io/api-references/#list-all-teams)                                            | Full refresh              | `id`              | All plans                       |
| [`trackers`](https://developers.aircall.io/api-references/#list-all-trackers)                                      | Full refresh              | `id`              | AI Assist or AI Assist Pro      |
| [`user_availability`](https://developers.aircall.io/api-references/#retrieve-list-of-users-availability)           | Full refresh              | `id`              | All plans                       |
| [`users`](https://developers.aircall.io/api-references/#list-all-users-v2)                                         | Full refresh              | `id`              | All plans                       |
| [`webhooks`](https://developers.aircall.io/api-references/#list-all-webhooks)                                      | Full refresh              | `webhook_id`      | All plans                       |
| [`whatsapp_templates`](https://developers.aircall.io/api-references/#list-whatsapp-templates)                      | Full refresh              | `number_id`, `id` | Numbers registered for WhatsApp |

Notes:

- `company` has no primary key. Aircall returns a single company object with no identifier ([Retrieve Company information](https://developers.aircall.io/api-references/#retrieve-company-information)).
- `contacts` returns shared contacts only ([List all Contacts](https://developers.aircall.io/api-references/#list-all-contacts)).
- `users` reads the [User V2 API](https://developers.aircall.io/api-references/#user-v2-overview). User V2 records don't include a `numbers` object ([Versioning strategy](https://developers.aircall.io/api-references/#versioning-strategy)).
- `webhooks` uses `webhook_id`, the UUID that identifies a webhook. Aircall treats the integer `id` as the old identifier ([List all Webhooks](https://developers.aircall.io/api-references/#list-all-webhooks)).
- `conversation_engagements` returns the calls, messages, assignments, closes and reopens of each conversation.
- `whatsapp_templates` returns the templates of each number, with `number_id` identifying the number.

## Limitations and troubleshooting

### 10,000-result limit

Aircall returns at most 10,000 calls or contacts for a single query, even with pagination ([Pagination](https://developers.aircall.io/api-references/#pagination), [List all Calls](https://developers.aircall.io/api-references/#list-all-calls)). Conversations have the same limit ([List all Conversations](https://developers.aircall.io/api-references/#list-all-conversations)). To stay under it, the connector requests `calls`, `contacts` and `conversations` one date range at a time, sized by **Window size (days)**.

If a sync fails with `Aircall returns at most 10,000 calls or contacts per request window` or `Aircall returns at most 10,000 conversations per request window`, one date range holds more than 10,000 records. Lower **Window size (days)** and run the sync again. `calls` already uses the smallest window, 1 day, by default.

### Six months of call history

Aircall keeps only six months of call history in the API ([List all Calls](https://developers.aircall.io/api-references/#list-all-calls)). The connector starts `calls` 186 days before each sync. Calls older than that aren't returned, and a full refresh or a cleared stream can't bring them back. To get older calls, ask [Aircall Support](https://support.aircall.io/) for a one-time export.

### Rate limit

Aircall allows 120 requests per minute per company, shared by every API key and integration on your Aircall account ([Rate limiting](https://developers.aircall.io/api-references/#rate-limiting)). When Aircall rejects a request for exceeding the limit, the connector waits until Aircall resets the counter, then continues. Raising **Concurrent workers** doesn't raise the limit. If other integrations use the Aircall API heavily, syncs take longer. Aircall Support can raise the limit for your API keys.

### Streams that sync no records

Some streams need an Aircall add-on or a specific number setup. When your company doesn't have it, Aircall refuses the request, and the connector skips the stream and logs a message instead of failing the sync:

| Stream                                      | Requirement                                                                                                                                                                          |
| :------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `conversations`, `conversation_engagements` | The Conversations API must be enabled for your company ([List all Conversations](https://developers.aircall.io/api-references/#list-all-conversations)).                             |
| `trackers`                                  | The AI Assist or AI Assist Pro package ([List all Trackers](https://developers.aircall.io/api-references/#list-all-trackers)).                                                       |
| `whatsapp_templates`                        | Only numbers registered for WhatsApp return templates. Other numbers are skipped ([List WhatsApp Templates](https://developers.aircall.io/api-references/#list-whatsapp-templates)). |

If a sync fails with `Aircall rejected the API ID and API token`, the API key is wrong or was deleted. Create a new API key and update the source.

### Upgrading to 1.0.0

Version 1.0.0 adds primary keys to `calls` and `contacts`, changes the `webhooks` primary key to `webhook_id`, makes `numbers` and `teams` full refresh only, and corrects several column types. Connections that sync `calls`, `contacts`, `webhooks`, `numbers`, `teams` or `users` need a schema refresh and a clear. Clearing `calls` removes calls older than six months for good, so back up the table first. See the [migration guide](aircall-migrations.md#upgrading-to-100).

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 1.0.0 | 2026-11-03 | [90838](https://github.com/airbytehq/airbyte/pull/90838) | Add primary keys to calls, contacts and webhooks, make numbers and teams full refresh only, and correct column types to match the Aircall API |
| 0.6.0 | 2026-11-03 | [90837](https://github.com/airbytehq/airbyte/pull/90837) | Add conversations, conversation engagements, campaigns, campaign outcomes, trackers, SMS templates and WhatsApp templates streams |
| 0.5.0 | 2026-11-03 | [90835](https://github.com/airbytehq/airbyte/pull/90835) | Add incremental sync for calls, rate-limit handling and request windows that avoid Aircall's 10,000-result limit |
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
