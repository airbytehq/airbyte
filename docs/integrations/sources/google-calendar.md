# Google Calendar

The Google Calendar source connector syncs calendar metadata, Calendar settings, and the events of one calendar from the [Google Calendar API v3](https://developers.google.com/workspace/calendar/api/v3/reference).

## Prerequisites

- A Google account that can read the calendar you want to sync.
- A Google Cloud project with the Google Calendar API enabled.
- An OAuth 2.0 client ID and client secret from that project.
- A refresh token issued to that OAuth client for a scope that grants read access to calendars, such as `https://www.googleapis.com/auth/calendar.readonly`.

This connector doesn't offer a built-in **Sign in with Google** flow. You create your own OAuth client in Google Cloud and enter its credentials and a refresh token.

## Setup guide

### Step 1: Enable the Google Calendar API

1. In the [Google Cloud console](https://console.cloud.google.com/), select or create a project.
2. Go to **APIs & Services** > **Library**, search for **Google Calendar API**, and click **Enable**.

### Step 2: Create an OAuth client

1. [Configure the OAuth consent screen](https://developers.google.com/workspace/guides/configure-oauth-consent) for the project.
2. [Create an OAuth client ID](https://developers.google.com/workspace/guides/create-credentials#oauth-client-id) with the **Web application** application type.
3. Under **Authorized redirect URIs**, add `https://developers.google.com/oauthplayground` so you can use the OAuth 2.0 Playground in the next step.
4. Copy the client ID and client secret.

:::note
If the consent screen uses the **External** user type and its publishing status is **Testing**, Google issues refresh tokens that [expire after 7 days](https://developers.google.com/identity/protocols/oauth2#expiration), and syncs then fail with an authentication error. To get a long-lived refresh token, use the **Internal** user type (Google Workspace organizations only) or move the app to production.
:::

### Step 3: Get a refresh token

You can use any OAuth 2.0 tool that requests offline access. To use the [OAuth 2.0 Playground](https://developers.google.com/oauthplayground):

1. Click the settings icon, select **Use your own OAuth credentials**, and enter your client ID and client secret.
2. Enter `https://www.googleapis.com/auth/calendar.readonly` as the scope and click **Authorize APIs**.
3. Sign in with the Google account whose calendars you want to sync and grant access.
4. Click **Exchange authorization code for tokens** and copy the refresh token.

The connector reads data as the Google account that authorized the refresh token. The `settings`, `calendarlist`, and `calendars` streams return that account's data, and that account must be able to read the calendar you enter in **Calendar Id**.

### Step 4: Find the calendar ID

In Google Calendar, open **Settings**, select the calendar under **Settings for my calendars**, and copy the **Calendar ID** from the **Integrate calendar** section. For an account's primary calendar, the ID is the account's email address. After a first sync, you can also find calendar IDs in the `id` column of the `calendarlist` stream.

### Step 5: Set up the connector in Airbyte

1. Create a new Google Calendar source.
2. Enter the **Client ID**, **Client secret**, and **Refresh token** from the previous steps.
3. For **Calendar Id**, enter the calendar ID from step 4. The alias `primary` also works, but the connector writes the value you enter to the `calendar_id` column of the `events` stream, so `primary` won't join to `calendarlist.id`.
4. (Optional) For **Start date**, enter a UTC date-time such as `2026-01-01T00:00:00Z` to sync only events last modified on or after that date. See [Events sync behavior](#events-sync-behavior) before you set it.
5. (Optional) For **Number of concurrent workers**, enter a value from 1 to 10. The default is 3.
6. Click **Set up source**.

## Supported sync modes

All streams support Full Refresh. The `events` stream also supports Incremental.

## Supported streams

| Stream | API endpoint | Primary key | Incremental | Description |
| ------ | ------------ | ----------- | ----------- | ----------- |
| `colors` | [Colors: get](https://developers.google.com/workspace/calendar/api/v3/reference/colors/get) | `calendar`, `event` | No | Color definitions for calendars and events, returned as a single record. |
| `settings` | [Settings: list](https://developers.google.com/workspace/calendar/api/v3/reference/settings/list) | `id` | No | The authorizing account's Calendar settings, such as time zone and date format. |
| `calendarlist` | [CalendarList: list](https://developers.google.com/workspace/calendar/api/v3/reference/calendarList/list) | `id` | No | Calendars in the authorizing account's calendar list. |
| `calendars` | [CalendarList: list](https://developers.google.com/workspace/calendar/api/v3/reference/calendarList/list) | `id` | No | Same endpoint and schema as `calendarlist`, so it returns the same records. Sync only one of the two. |
| `events` | [Events: list](https://developers.google.com/workspace/calendar/api/v3/reference/events/list) | `id` | Yes | Events from the calendar in **Calendar Id**, including cancelled events. |

## Events sync behavior

The `events` stream is incremental on the event's last modification time (`updated`), using the Google Calendar `updatedMin` filter.

- **Cancelled events** are included (`showDeleted=true`) with `status: cancelled`, so deletions reach the destination. Google returns them as stubs without a modification time, so the connector sets their `updated` itself (the saved cursor, or one hour before the sync, whichever is later) so that the cancelled row replaces the live one under *Append + Deduped*. Filter `status != 'cancelled'` downstream if you only want live events.
- **`calendar_id`** holds the configured Calendar Id exactly as entered. With the alias `primary` it is a label, not the calendar's ID, and will not join to `calendarlist.id` / `calendars.id`; enter the real ID (the account's email address for the primary calendar) if you need that join.
- **Recurring series** are returned as a single record (`singleEvents=false`); individual occurrences are not expanded. The record's `updated` is the last time the series was edited.
- **`start_date`** limits every Full Refresh sync, the first Incremental sync, and any full re-read (after a reset, or when the saved cursor is older than 21 days) to events last modified on or after that date. Google applies the filter server-side only within the last 29 days; for an older date the connector downloads the calendar and drops older records itself. Because a recurring series counts as one event, a start date also drops series that have not been edited since that date, even if they still have upcoming occurrences. Leave it unset to read everything.
- **29-day window.** Google rejects `updatedMin` older than 29 days (measured; the limit is undocumented and has been tighter in the past). The connector keeps the newest `updated` it has seen as its cursor; if that cursor is older than 21 days when a sync starts (for example, a calendar with no edits for three weeks, or a connection paused for three weeks) the connector clears the cursor and re-reads the whole calendar (or everything since `start_date`), then continues incrementally. A calendar whose only changes are deletions still advances its cursor (see cancelled events above); one with no changes at all re-reads on every sync until something changes.
- **Recommended sync mode:** *Incremental | Append + Deduped* with `id` as the primary key. With plain *Append*, each re-read described above adds another copy of every event.

## Rate limits

Google enforces [Calendar API quotas](https://developers.google.com/workspace/calendar/api/guides/quota) per minute per project and per minute per user per project. The connector sends at most 500 requests per minute, regardless of the number of concurrent workers.

When Google returns HTTP 429 or a `rateLimitExceeded` or `userRateLimitExceeded` error, the connector waits and retries the request with exponential backoff. When the project or user quota is exhausted (`quotaExceeded` or `dailyLimitExceeded`), the sync fails with a transient error and succeeds once the quota resets. The connector also retries HTTP 500, 502, 503, and 504 responses.

## Troubleshooting

| HTTP status | Cause | Resolution |
| ----------- | ----- | ---------- |
| 401 | Google rejected the OAuth credentials. The refresh token expired or was revoked, or it was issued to a different OAuth client. | Generate a new refresh token for the configured client ID. If tokens expire after 7 days, see the note in [Step 2](#step-2-create-an-oauth-client). |
| 403 | The Google Calendar API isn't enabled in the Google Cloud project, or the authorizing account can't read the configured calendar. | Enable the API in the project that owns the OAuth client, and confirm the account can open the calendar in Google Calendar. |
| 404 | Google can't find the calendar in **Calendar Id**. | Copy the ID again from the calendar's settings, or use `primary`. |
| 410 | The calendar was deleted, or the saved `events` cursor is older than Google accepts. | For a deleted calendar, update **Calendar Id** and reset the `events` stream. For an old cursor, the next sync re-reads the calendar automatically. |

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------- | ---- | ------------ | ------- |
| 0.1.0 | 2026-10-07 | [86468](https://github.com/airbytehq/airbyte/pull/86468) | Add error handling, API budget, concurrency, incremental `events` (now includes cancelled events via `showDeleted=true`) with a `calendar_id` column and an optional `start_date`, and enable acceptance tests |
| 0.0.55 | 2026-10-06 | [87901](https://github.com/airbytehq/airbyte/pull/87901) | Update dependencies |
| 0.0.54 | 2026-09-29 | [87194](https://github.com/airbytehq/airbyte/pull/87194) | Update dependencies |
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
