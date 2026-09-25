# Google Calendar

<HideInUI>

This page contains the setup guide and reference information for the [Google Calendar](https://calendar.google.com) source connector.

</HideInUI>

## Prerequisites

- A Google account with access to the calendars you want to sync.
- **Airbyte Cloud:** nothing else — you authenticate with your Google account during setup.
- **Airbyte Open Source:** a Google Cloud project with the Google Calendar API enabled and OAuth credentials (Client ID, Client Secret, and a Refresh Token). See the setup steps below.
- (Optional) A specific Calendar ID if you only want to sync one calendar.
- (Optional) A Start Date to limit how far back incremental `events` syncs look.

## Setup guide

### Step 1: Obtain Google credentials

<!-- env:cloud -->

#### For Airbyte Cloud

No prerequisite work is needed. In Step 2 you click **Authenticate your Google account** and sign in with the Google account whose calendars you want to sync.

<!-- /env:cloud -->

<!-- env:oss -->

#### For Airbyte Open Source

To authenticate with OAuth you need a **Client ID**, **Client Secret**, and **Refresh Token** from your own Google Cloud project:

1. Enable the Google Calendar API for your project in the [API Library](https://console.cloud.google.com/apis/library/calendar-json.googleapis.com).
2. Create an OAuth client (type **Web application**) on the [Credentials page](https://console.cloud.google.com/apis/credentials). Add `https://developers.google.com/oauthplayground` as an authorized redirect URI.
3. Obtain a refresh token with the [OAuth 2.0 Playground](https://developers.google.com/oauthplayground):
   - Click the gear icon, check **Use your own OAuth credentials**, and enter your Client ID and Client Secret.
   - Authorize the scopes `https://www.googleapis.com/auth/calendar.readonly` and `https://www.googleapis.com/auth/calendar.acls.readonly`, then exchange the authorization code for tokens. The `calendar.acls.readonly` scope is required for the `acl` stream; `calendar.readonly` alone is sufficient for all other streams.

<!-- /env:oss -->

### Step 2: Set up the Google Calendar connector in Airbyte

<!-- env:cloud -->

#### For Airbyte Cloud

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Google Calendar** from the Source type dropdown.
4. Enter a name for the connector.
5. Under **Authentication**, choose **Authenticate via Google (OAuth)** and click **Authenticate your Google account** to authorize.
6. (Optional) For **Calendar Id**, enter a specific calendar ID to sync only that calendar. The calendar does not need to appear in the account's calendar list; it is read directly. The value `primary` is accepted for the account's primary calendar. Leave empty to sync every calendar in the account's calendar list.
7. (Optional) For **Start Date**, enter the earliest `updated` timestamp for incremental `events` syncs in the format `YYYY-MM-DDTHH:mm:ssZ` or `YYYY-MM-DDTHH:mm:ss.SSSZ`. When unset, the first sync fetches all events; Google rejects values older than roughly 30 days.
8. (Optional) For **Number of concurrent workers**, set the number of concurrent request workers (1–10, default 3).
9. Click **Set up source** and wait for the tests to complete.

<!-- /env:cloud -->

<!-- env:oss -->

#### For Airbyte Open Source

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Google Calendar** from the Source type dropdown.
4. Enter a name for the connector.
5. Under **Authentication**, choose one of:
   - **Authenticate via Google (OAuth):** sign in with Google using Airbyte's OAuth app (Cloud); enter the **Client ID**, **Client Secret**, and **Refresh Token** you obtained in Step 1.
   - **Authenticate with custom app (client ID / secret):** enter a refresh token issued by *your own* Google Cloud OAuth app with the `calendar.readonly` and `calendar.acls.readonly` scopes, plus that app's **Client ID** and **Client Secret**. Without `calendar.acls.readonly`, the `acl` stream is skipped (its 403 responses are ignored). Existing configurations with flat `client_id`/`client_secret`/`client_refresh_token_2` fields are migrated automatically to this option.
6. (Optional) For **Calendar Id**, enter a specific calendar ID to sync only that calendar, or `primary` for the account's primary calendar. The calendar does not need to appear in the account's calendar list; it is read directly. Leave empty to sync all calendars.
7. (Optional) For **Start Date**, enter the earliest `updated` timestamp for incremental `events` syncs (`YYYY-MM-DDTHH:mm:ssZ` or `YYYY-MM-DDTHH:mm:ss.SSSZ`). When unset, the first sync fetches all events; Google rejects values older than roughly 30 days.
8. (Optional) For **Number of concurrent workers**, set the number of concurrent request workers (1–10, default 3).
9. Click **Set up source** and wait for the tests to complete.

<!-- /env:oss -->

<HideInUI>

## Supported sync modes

The Google Calendar source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append) (`events` only)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped) (`events` only)

## Supported streams

The `events`, `acl`, and `freebusy` streams sync once per calendar. When **Calendar Id** is configured, only that calendar is synced — it is read directly, so it does not need to appear in the account's calendar list; otherwise every calendar in the account's calendar list is synced.

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|--------------------|-----------------------|
| colors | calendar.event | No pagination | ✅ | ❌ |
| settings | id | DefaultPaginator | ✅ | ❌ |
| calendarlist | id | DefaultPaginator | ✅ | ❌ |
| calendars | id | DefaultPaginator | ✅ | ❌ |
| events | id | DefaultPaginator | ✅ | ✅ |
| acl | calendar_id, id | DefaultPaginator | ✅ | ❌ |
| freebusy | calendar_id, start, end | No pagination | ✅ | ❌ |

Deleted events are replicated: cancelled events arrive with `status: "cancelled"` (`showDeleted=true`).

## Limitations & troubleshooting

<details>
<summary>
Expand to see details about Google Calendar connector limitations and troubleshooting.
</summary>

### Connector limitations

- **API quota:** the Google Calendar API enforces per-user quotas (600 requests per minute per user per project; 10,000 per minute per project). The connector rate-limits itself to 500 requests/minute and retries rate-limit responses (403/429) automatically. See [Google's quota documentation](https://developers.google.com/calendar/api/guides/quota).
- **Stale cursor (410):** if the saved incremental position for `events` is older than ~30 days, Google rejects the `updatedMin` bound with a `410` error. Syncs older than that window fail until the `events` stream is reset.
- **`acl` scope and ownership:** the `acl` stream requires the `calendar.acls.readonly` scope and can only read ACLs for calendars the authenticated account owns; ACLs of other calendars are skipped.
- **`freebusy` is a point-in-time window:** each sync queries busy blocks from `Start Date` (or 30 days ago) through 45 days in the future. It is a snapshot, not a historical record.
- **`settings.value` is always a string**, including for numeric-looking settings.
- **`colors` is a singleton:** it returns a single record containing `calendar` and `event` color-palette objects.
- The `calendars` stream currently returns calendar-list entries; a fix is planned in a future major release.

### Troubleshooting

- Check out common troubleshooting issues for the Google Calendar source connector on our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions).

</details>

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog


<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.3.0 | 2026-09-21 | [86470](https://github.com/airbytehq/airbyte/pull/86470) | Add `acl` and `freebusy` streams, partition `events`/`acl`/`freebusy` over all calendars, make `calendarid` optional |
| 0.2.0 | 2026-09-21 | [86468](https://github.com/airbytehq/airbyte/pull/86468) | Add error handling, API budget, concurrency, incremental `events`, and enable acceptance tests |
| 0.1.0 | 2026-09-21 | [86469](https://github.com/airbytehq/airbyte/pull/86469) | Add declarative OAuth (`advanced_auth`); legacy flat credentials migrate to the custom-app `credentials` option |
| 0.0.53 | 2026-09-22 | [86679](https://github.com/airbytehq/airbyte/pull/86679) | Update dependencies |
| 0.0.52 | 2026-09-15 | [86070](https://github.com/airbytehq/airbyte/pull/86070) | Update dependencies |
| 0.0.51 | 2026-09-08 | [85541](https://github.com/airbytehq/airbyte/pull/85541) | Update dependencies |
| 0.0.50 | 2026-08-18 | [84636](https://github.com/airbytehq/airbyte/pull/84636) | Update dependencies |
| 0.0.49 | 2026-08-11 | [83962](https://github.com/airbytehq/airbyte/pull/83962) | Update dependencies |
| 0.0.48 | 2026-08-04 | [83499](https://github.com/airbytehq/airbyte/pull/83499) | Update dependencies |
| 0.0.47 | 2026-07-28 | [82972](https://github.com/airbytehq/airbyte/pull/82972) | Update dependencies |
| 0.0.46 | 2026-07-21 | [82435](https://github.com/airbytehq/airbyte/pull/82435) | Update dependencies |
| 0.0.45 | 2026-07-14 | [81849](https://github.com/airbytehq/airbyte/pull/81849) | Update dependencies |
| 0.0.44 | 2026-06-30 | [81038](https://github.com/airbytehq/airbyte/pull/81038) | Update dependencies |
| 0.0.43 | 2026-06-23 | [80483](https://github.com/airbytehq/airbyte/pull/80483) | Update dependencies |
| 0.0.42 | 2026-06-16 | [79880](https://github.com/airbytehq/airbyte/pull/79880) | Update dependencies |
| 0.0.41 | 2026-06-09 | [79339](https://github.com/airbytehq/airbyte/pull/79339) | Update dependencies |
| 0.0.40 | 2026-06-02 | [78738](https://github.com/airbytehq/airbyte/pull/78738) | Update dependencies |
| 0.0.39 | 2026-04-28 | [77268](https://github.com/airbytehq/airbyte/pull/77268) | Update dependencies |
| 0.0.38 | 2026-04-21 | [76584](https://github.com/airbytehq/airbyte/pull/76584) | Update dependencies |
| 0.0.37 | 2026-03-31 | [75671](https://github.com/airbytehq/airbyte/pull/75671) | Update dependencies |
| 0.0.36 | 2026-03-17 | [74985](https://github.com/airbytehq/airbyte/pull/74985) | Update dependencies |
| 0.0.35 | 2026-02-24 | [73746](https://github.com/airbytehq/airbyte/pull/73746) | Update dependencies |
| 0.0.34 | 2026-02-17 | [73085](https://github.com/airbytehq/airbyte/pull/73085) | Update dependencies |
| 0.0.33 | 2026-01-20 | [71931](https://github.com/airbytehq/airbyte/pull/71931) | Update dependencies |
| 0.0.32 | 2026-01-14 | [71428](https://github.com/airbytehq/airbyte/pull/71428) | Update dependencies |
| 0.0.31 | 2025-12-18 | [70696](https://github.com/airbytehq/airbyte/pull/70696) | Update dependencies |
| 0.0.30 | 2025-11-25 | [69889](https://github.com/airbytehq/airbyte/pull/69889) | Update dependencies |
| 0.0.29 | 2025-11-18 | [69373](https://github.com/airbytehq/airbyte/pull/69373) | Update dependencies |
| 0.0.28 | 2025-10-29 | [69049](https://github.com/airbytehq/airbyte/pull/69049) | Update dependencies |
| 0.0.27 | 2025-10-21 | [68310](https://github.com/airbytehq/airbyte/pull/68310) | Update dependencies |
| 0.0.26 | 2025-10-14 | [68007](https://github.com/airbytehq/airbyte/pull/68007) | Update dependencies |
| 0.0.25 | 2025-10-07 | [67257](https://github.com/airbytehq/airbyte/pull/67257) | Update dependencies |
| 0.0.24 | 2025-09-30 | [66309](https://github.com/airbytehq/airbyte/pull/66309) | Update dependencies |
| 0.0.23 | 2025-09-09 | [66046](https://github.com/airbytehq/airbyte/pull/66046) | Update dependencies |
| 0.0.22 | 2025-08-23 | [65366](https://github.com/airbytehq/airbyte/pull/65366) | Update dependencies |
| 0.0.21 | 2025-08-09 | [64614](https://github.com/airbytehq/airbyte/pull/64614) | Update dependencies |
| 0.0.20 | 2025-08-02 | [64218](https://github.com/airbytehq/airbyte/pull/64218) | Update dependencies |
| 0.0.19 | 2025-07-26 | [63813](https://github.com/airbytehq/airbyte/pull/63813) | Update dependencies |
| 0.0.18 | 2025-07-19 | [63491](https://github.com/airbytehq/airbyte/pull/63491) | Update dependencies |
| 0.0.17 | 2025-07-12 | [63149](https://github.com/airbytehq/airbyte/pull/63149) | Update dependencies |
| 0.0.16 | 2025-07-05 | [62653](https://github.com/airbytehq/airbyte/pull/62653) | Update dependencies |
| 0.0.15 | 2025-06-28 | [62156](https://github.com/airbytehq/airbyte/pull/62156) | Update dependencies |
| 0.0.14 | 2025-06-21 | [61833](https://github.com/airbytehq/airbyte/pull/61833) | Update dependencies |
| 0.0.13 | 2025-06-14 | [61121](https://github.com/airbytehq/airbyte/pull/61121) | Update dependencies |
| 0.0.12 | 2025-05-24 | [60587](https://github.com/airbytehq/airbyte/pull/60587) | Update dependencies |
| 0.0.11 | 2025-05-10 | [59250](https://github.com/airbytehq/airbyte/pull/59250) | Update dependencies |
| 0.0.10 | 2025-04-26 | [58812](https://github.com/airbytehq/airbyte/pull/58812) | Update dependencies |
| 0.0.9 | 2025-04-19 | [58175](https://github.com/airbytehq/airbyte/pull/58175) | Update dependencies |
| 0.0.8 | 2025-04-12 | [57066](https://github.com/airbytehq/airbyte/pull/57066) | Update dependencies |
| 0.0.7 | 2025-03-29 | [56487](https://github.com/airbytehq/airbyte/pull/56487) | Update dependencies |
| 0.0.6 | 2025-03-22 | [55939](https://github.com/airbytehq/airbyte/pull/55939) | Update dependencies |
| 0.0.5 | 2025-03-08 | [55325](https://github.com/airbytehq/airbyte/pull/55325) | Update dependencies |
| 0.0.4 | 2025-03-01 | [54992](https://github.com/airbytehq/airbyte/pull/54992) | Update dependencies |
| 0.0.3 | 2025-02-22 | [54395](https://github.com/airbytehq/airbyte/pull/54395) | Update dependencies |
| 0.0.2 | 2025-02-15 | [47915](https://github.com/airbytehq/airbyte/pull/47915) | Update dependencies |
| 0.0.1 | 2024-10-06 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>

</HideInUI>
