# Google Calendar

Solves https://github.com/airbytehq/airbyte/issues/45995

## Configuration

| Input | Type | Description | Default Value |
| ----- | ---- | ----------- | ------------- |
| `client_id` | `string` | Client ID of the Google Cloud OAuth 2.0 application. | |
| `client_secret` | `string` | Client secret of the OAuth 2.0 application. | |
| `client_refresh_token_2` | `string` | Refresh token for the OAuth application with the Calendar API scope. The `acl` stream also needs the `calendar.acls.readonly` scope. | |
| `calendarid` | `string` | Optional. The ID of a single calendar to sync `events`, `acl` and `freebusy` from; for the primary calendar this is the account's email address, and the alias `primary` also works. Leave empty to sync every calendar in the account's calendar list, hidden calendars included. | |
| `start_date` | `string` | Only sync `events` last modified on or after this date. Applies to every Full Refresh sync, to the first Incremental sync, and to any full re-read; when unset, all events are read. See [Events sync behavior](#events-sync-behavior). | |
| `num_workers` | `integer` | Number of concurrent workers. | 3 |

## Streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
| ----------- | ----------- | ---------- | ------------------- | -------------------- |
| colors | kind | No pagination | ✅ | ❌ |
| settings | id | DefaultPaginator | ✅ | ❌ |
| calendarlist | id | DefaultPaginator | ✅ | ❌ |
| calendars | id | No pagination | ✅ | ❌ |
| events | calendar_id, id | DefaultPaginator | ✅ | ✅ |
| acl | calendar_id, id | DefaultPaginator | ✅ | ❌ |
| freebusy | calendar_id, start, end | No pagination | ✅ | ❌ |

`events`, `acl` and `freebusy` are read per calendar: the configured `calendarid`, or every calendar in the calendar list when it is empty. With it empty, `events` reads only calendars the account can read events from, `acl` only calendars it owns, and `freebusy` every listed calendar. Each record carries the calendar in `calendar_id`.

- **`calendars`** returns the calendar resource (summary, description, location, time zone) of every calendar in the calendar list the account can read; the per-user list fields stay in `calendarlist`.
- **`acl`** lists a calendar's sharing rules. It needs the `calendar.acls.readonly` OAuth scope (or `calendar.acls` / `calendar`); without it the stream fails with a configuration error, so generate a new refresh token for your OAuth client that includes the scope and paste it into **Refresh token**, or deselect the stream. If your connection adds new streams automatically, deselect `acl` until the token has the scope. Google shows sharing rules only to a calendar's owner, so calendars the account does not own are skipped.
- **`freebusy`** lists busy blocks from 30 days ago to 45 days ahead, recomputed on every sync; `start_date` does not apply to it. A calendar Google cannot compute free/busy for is logged and contributes no rows, so it looks the same as a free calendar in the destination.
- **Push notification channels** (`channels`) are intentionally not synced: they are write-only subscriptions the connector would have to create, not data it can read.

## Events sync behavior

The `events` stream is incremental on the event's last modification time (`updated`), using the Google Calendar `updatedMin` filter.

- **Cancelled events** are included (`showDeleted=true`) with `status: cancelled`, so deletions reach the destination. Google returns them as stubs without a modification time, so the connector sets their `updated` itself (the saved cursor, or one hour before the sync, whichever is later) so that the cancelled row replaces the live one under *Append + Deduped*. Filter `status != 'cancelled'` downstream if you only want live events.
- **`calendar_id`** holds the calendar's real ID, so it joins to `calendarlist.id` / `calendars.id`. The alias `primary` is resolved to the account's email address.
- **One cursor for all calendars.** The stream keeps a single `updated` cursor across calendars. A calendar added to the calendar list after the first sync starts from that cursor, so its older events are not synced; clear the `events` stream to backfill it.
- **Recurring series** are returned as a single record (`singleEvents=false`); individual occurrences are not expanded. The record's `updated` is the last time the series was edited.
- **`start_date`** limits every Full Refresh sync, the first Incremental sync, and any full re-read (after a reset, or when the saved cursor is older than 21 days) to events last modified on or after that date. Google applies the filter server-side only within the last 29 days; for an older date the connector downloads the calendar and drops older records itself. Because a recurring series counts as one event, a start date also drops series that have not been edited since that date, even if they still have upcoming occurrences. Leave it unset to read everything.
- **29-day window.** Google rejects `updatedMin` older than 29 days (measured; the limit is undocumented and has been tighter in the past). The connector keeps the newest `updated` it has seen as its cursor; if that cursor is older than 21 days when a sync starts (for example, a calendar with no edits for three weeks, or a connection paused for three weeks) the connector clears the cursor and re-reads the whole calendar (or everything since `start_date`), then continues incrementally. A calendar whose only changes are deletions still advances its cursor (see cancelled events above); one with no changes at all re-reads on every sync until something changes.
- **Recommended sync mode:** *Incremental | Append + Deduped* with `calendar_id` and `id` as the primary key; the same event id appears on every calendar a meeting is on. With plain *Append*, each re-read described above adds another copy of every event.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------- | ---- | ------------ | ------- |
| 1.0.0 | 2026-10-07 | [86470](https://github.com/airbytehq/airbyte/pull/86470) | Add `acl` and `freebusy` streams, read `events`/`acl`/`freebusy` from every calendar when `calendarid` is empty, change the `events` primary key to `[calendar_id, id]`, return calendar resources from `calendars`, change the `colors` primary key to `kind`, and type date and date-time fields (breaking, see the [migration guide](/integrations/sources/google-calendar-migrations)) |
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
