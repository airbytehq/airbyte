# Aircall

The Aircall source syncs call, contact, user, and messaging data from the [Aircall API](https://developers.aircall.io/api-references/).

## Prerequisites

- An Aircall user with permission to create API keys. If you lack this permission, ask an Aircall admin to grant it.
- An Aircall API key, consisting of an API ID and API token. The connector uses [HTTP Basic authentication](https://developers.aircall.io/api-references/#basic-auth-aircall-customers).
- For `conversations` and `conversation_engagements`, the [Conversations API](https://developers.aircall.io/api-references/#list-all-conversations) must be enabled for your company.
- For `trackers`, your company must have [AI Assist or AI Assist Pro](https://developers.aircall.io/api-references/#list-all-trackers).
- For `whatsapp_templates`, you need a number [registered for WhatsApp](https://developers.aircall.io/api-references/#list-whatsapp-templates).

## Setup guide

### Step 1: Create an Aircall API key

1. Open the [Aircall Dashboard API keys page](https://dashboard.aircall.io/integrations/api-keys) under **Integrations > API Keys**.
2. Click **Generate an API key** and enter a name for the key.
3. Copy the API ID and API token to a secure location before you close the window. Aircall cannot retrieve the token for you later.
4. Click **Confirm** to finish creating the key. See [Aircall's API key guide](https://support.aircall.io/en-gb/articles/10375395181853) for details.

### Step 2: Set up the source in Airbyte

1. Open your [Airbyte Cloud workspace](https://cloud.airbyte.com/workspaces) or your Airbyte Open Source dashboard.
2. Go to **Sources**, create a new source, and select **Aircall**.
3. Enter a name for the source, your **API ID**, and your **API Token**.
4. Optionally, adjust the settings in the configuration table.
5. Click **Set up source**. Airbyte checks the connection using the `company` stream.
6. When you create a connection, select the streams to sync. Deselect streams for features your Aircall company does not have.

### Configuration

| Setting | Required? | Default | Description |
| :--- | :--- | :--- | :--- |
| **API ID** (`api_id`) | Yes | None | API ID from your Aircall API key. |
| **API Token** (`api_token`) | Yes | None | API token associated with the API ID. |
| **Window size (days)** (`window_in_days`) | No | 1 day when omitted | Integer from 1 to 365. Days of calls requested per window. Larger windows can cause more retries at the 10,000-result limit. |
| **Contacts window size (days)** (`contacts_window_in_days`) | No | 30 days when omitted | Integer from 1 to 365. Days of new contacts requested per window. Reduce this value if a contacts sync reaches the 10,000-result limit. |
| **Concurrent workers** (`num_workers`) | No | 2 | Integer from 1 to 4. All workers share the same request budget. |

The legacy `start_date` setting is hidden and no longer used. Configurations saved before version 0.5.0 can retain it.

## Supported sync modes

The Aircall source supports full refresh and incremental syncs. It does not replicate deletes or support namespaces.

## Supported streams

| Stream | Sync modes | Primary key | Notes |
| :--- | :--- | :--- | :--- |
| `calls` | Full refresh, incremental | `id` | Cursor: `started_at`. |
| `company` | Full refresh | None | Aircall returns one company object without an identifier. Also used for connection checks. |
| `contacts` | Full refresh | `id` | Read in date windows. |
| `numbers` | Full refresh | `id` | Full refresh only since 1.0.0. |
| `tags` | Full refresh | `id` | Call tags. |
| `user_availability` | Full refresh | `id` | User availability. |
| `users` | Full refresh | `id` | Uses the User V2 API. |
| `teams` | Full refresh | `id` | Full refresh only since 1.0.0. |
| `webhooks` | Full refresh | `webhook_id` | Webhook configuration. |
| `conversations` | Full refresh, incremental | `id` | Cursor: `last_engagement_at`. |
| `conversation_engagements` | Full refresh, incremental | `id` | Reads engagements per conversation. |
| `campaigns` | Full refresh | `id` | Outbound campaigns. |
| `campaign_outcomes` | Full refresh | `id` | Custom outcome catalog, not per-call results. |
| `trackers` | Full refresh | `id` | Requires AI Assist or AI Assist Pro. |
| `sms_templates` | Full refresh | `id` | Company SMS templates. |
| `whatsapp_templates` | Full refresh | `number_id`, `id` | Reads templates per number. |

Version 1.0.0 is a breaking change that adds primary keys, makes `numbers` and `teams` full refresh only, and changes several column types. Clearing `calls` permanently deletes calls older than six months, because Aircall no longer returns them. Read the [migration guide](/integrations/sources/aircall-migrations#upgrading-to-100) before you upgrade.

## Sync behavior and limitations

### Incremental syncs and duplicates

- **Calls:** The first sync and full refreshes start 365 days before the sync. Aircall exposes only [six months of call history](https://developers.aircall.io/api-references/#list-all-calls). Incremental syncs reread the three days before the saved `started_at` cursor to capture recent changes. To capture edits to older calls, run a full refresh.
- **Conversations:** The first sync and full refreshes start at January 1, 2014, in fixed 30-day windows. Incremental syncs reread the three days before the saved `last_engagement_at` cursor. A new call or message updates this field; closing, reopening, or assigning a conversation does not. These status or assignment changes appear with the next activity or a full refresh.
- **Conversation engagements:** Incremental syncs read all engagements of each conversation returned by the parent conversation's incremental read, including its three-day lookback. The stream tracks `created_at`, but does not filter engagement requests by that field. The first sync makes at least one engagement request per conversation, plus requests to list conversations; pagination adds more requests. Subsequent syncs reread all engagements of the conversations in scope.

Lookback windows and retries can emit duplicate records for `calls`, `conversations`, and `conversation_engagements`. Use `Incremental | Append + Deduped` to keep one row per primary key. An Overwrite mode for `calls` keeps only the six months of history Aircall returns.

### Result limits

Aircall limits [calls and contacts](https://developers.aircall.io/api-references/#pagination) and [conversations](https://developers.aircall.io/api-references/#list-all-conversations) to 10,000 results per query.

- Calls split an oversized date window and read it again. If splitting still cannot reduce the results below the limit, the sync fails.
- Contacts fail with a configuration error when a window exceeds the limit. Lower **Contacts window size (days)** and retry. A single day with more than 10,000 new contacts cannot be read with this setting.
- Conversations continue from the last record's timestamp after 10,000 results. If 10,000 or more conversations share the same `last_engagement_at` second, the sync cannot advance.
- Aircall returns only the newest 10,000 engagements per conversation. The connector skips the result-limit error and keeps the engagements already read. It also skips a conversation that Aircall reports no longer exists.

### Feature access and authentication errors

The connector skips requests only when Aircall's HTTP 403 response identifies a feature restriction: the Conversations API is not enabled, AI Assist is unavailable, or a number cannot provide WhatsApp templates. Other streams can continue. A plain gateway `403 Forbidden` or a 401 response fails the sync as a configuration error. Check your API ID, API token, and access to the URL shown in the error.

If the Conversations API is not enabled, deselect both `conversations` and `conversation_engagements`. Otherwise, every sync still makes a rejected request for each 30-day history window.

### Rate limits

Aircall allows [120 requests per minute per company](https://developers.aircall.io/api-references/#rate-limiting), shared with other integrations. The connector limits its own requests to 100 per minute across all workers. Increasing **Concurrent workers** does not increase this budget. The connector retries rate-limit responses using the `X-AircallApi-Reset` header and retries server errors.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 1.0.0 | 2026-11-11 | [90838](https://github.com/airbytehq/airbyte/pull/90838) | Add primary keys to `calls` and `contacts`, key `webhooks` on `webhook_id`, make `numbers` and `teams` full refresh only, and declare the column types the Aircall API documents |
| 0.6.1 | 2026-11-10 | [91341](https://github.com/airbytehq/airbyte/pull/91341) | Update dependencies |
| 0.6.0 | 2026-11-09 | [90837](https://github.com/airbytehq/airbyte/pull/90837) | Add `conversations`, `conversation_engagements`, `campaigns`, `campaign_outcomes`, `trackers`, `sms_templates` and `whatsapp_templates` streams |
| 0.5.0 | 2026-11-09 | [90835](https://github.com/airbytehq/airbyte/pull/90835) | Read calls incrementally in daily windows that split at Aircall's 10,000-result limit, read contacts in date windows, honour Aircall's rate limit, declare `user_availability` `id` and `availability`, and read numbers and teams once per sync |
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
