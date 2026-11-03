# Calendly

The Calendly source syncs your organization members, groups, teams, invitations, event types and their hosts, availability schedules, meeting locations, webhook subscriptions, scheduled events, and event invitees from the Calendly API v2.

## Prerequisites

- A Calendly account. The connector's read endpoints are available on [all Calendly plans, including Free](https://developer.calendly.com/docs/getting-started/frequently-asked-questions).
- An organization owner or administrator account to read organization-wide data such as scheduled events and webhook subscriptions. The connector reads the current organization associated with the token owner's profile; you don't need to enter an organization ID.
- A [personal access token](https://developer.calendly.com/docs/authentication/how-to-authenticate-with-personal-access-tokens) with the [read scopes](https://developer.calendly.com/docs/authentication/scopes) of every stream you sync, listed in [Token scopes](#token-scopes).

## Setup

1. In Calendly, open the **Profile** menu, select **Developer**, then **Personal access tokens**. If **Developer** isn't available, use the **Integrations** page instead.
2. Select **Create personal access token**, name the token, and select the read scopes listed in [Token scopes](#token-scopes).
3. Create the token, complete the email verification, and copy it. Calendly shows the token only once.
4. In Airbyte, create a Calendly source and enter the token in **Calendly personal access token**. Enter a **Start date (UTC)** and, optionally, a **Lookback window (days)** as described below.

The connection check reads only the token owner's profile (`api_user`). A successful check confirms `users:read` access, not the permissions needed for every stream. Missing stream-specific scopes or organization permissions can still cause a sync to fail.

## Configuration

| Input | Type | Description | Default Value |
| --- | --- | --- | --- |
| `api_key` | `string` | Required. The personal access token created during setup. | |
| `start_date` | `string` | Required. Read scheduled events starting on or after this time. Use UTC in the format `YYYY-MM-DDTHH:mm:ssZ`, for example `2024-01-01T00:00:00Z`. This filters event start times, not when invitees booked. | |
| `lookback_days` | `number` | Optional. Days to subtract from the latest synced event's start time for incremental `scheduled_events` reads. The connector rereads events in that window, including their invitees. Use a non-negative value and see the incremental sync limitation below. | 0 |

## Token scopes

Since March 2026, Calendly grants newly created tokens no API access until you select scopes for them; tokens created earlier keep their access. Select the scopes of every stream you sync. When a scope is missing, the sync error lists it. Version 0.3.0 added streams that need `availability:read`, `locations:read` and `webhooks:read`: add these scopes to your token before you enable those streams.

| Stream | Required scopes |
| --- | --- |
| `api_user` | `users:read` |
| `event_types` | `users:read`, `event_types:read` |
| `groups` | `users:read`, `groups:read` |
| `organization_memberships` | `users:read`, `organizations:read` |
| `scheduled_events` | `users:read`, `scheduled_events:read` |
| `event_invitees` | `users:read`, `scheduled_events:read` |
| `teams` | `organizations:read` |
| `event_type_memberships` | `users:read`, `event_types:read` |
| `group_relationships` | `users:read`, `groups:read` |
| `user_availability_schedules` | `users:read`, `organizations:read`, `availability:read` |
| `locations` | `users:read`, `organizations:read`, `locations:read` |
| `organization_invitations` | `users:read`, `organizations:read` |
| `webhook_subscriptions` | `users:read`, `webhooks:read` |

## Streams

| Stream | Data | Primary key | Full refresh | Incremental |
| --- | --- | --- | --- | --- |
| `event_types` | Event types in the organization, such as meeting names, durations, and scheduling URLs | `uri` | Yes | Yes, using `updated_at` |
| `api_user` | The token owner's profile and current organization | `uri` | Yes | No |
| `groups` | Groups in the organization | `uri` | Yes | No |
| `organization_memberships` | Organization members, their roles, and user profiles | `uri` | Yes | No |
| `scheduled_events` | Scheduled meetings, including their times, status, and location | `uri` | Yes | Yes, using `start_time` |
| `event_invitees` | Invitees for each scheduled event, including answers, tracking data, and cancellation information | `uri` | Yes | Yes, dependent on `scheduled_events` |
| `teams` | Teams in the organization | `uri` | Yes | No |
| `event_type_memberships` | Hosts assigned to each event type | `uri` | Yes | No |
| `group_relationships` | Owner and admin relationships between users and groups | `uri` | Yes | No |
| `user_availability_schedules` | Availability schedules of each organization member | `uri` | Yes | No |
| `locations` | Meeting location types available to each organization member | None | Yes | No |
| `organization_invitations` | Invitations sent to join the organization | `uri` | Yes | No |
| `webhook_subscriptions` | Organization-scoped webhook subscriptions | `uri` | Yes | No |

The connector reads `event_invitees` for the scheduled events returned by the parent stream. It adds `scheduled_event_id` to each invitee record so you can join it to the `id` in `scheduled_events`.

`user_availability_schedules` and `locations` send one request per organization member, and `event_type_memberships` sends one per event type, so they are not suggested by default. `locations` has no primary key because Calendly returns no identifier for a location and can list a location kind more than once. `webhook_subscriptions` lists organization-scoped subscriptions only; user- and group-scoped subscriptions are not synced.

### Incremental sync limitation

:::caution

`scheduled_events` uses the event's `start_time`, not its creation or modification time, as its incremental cursor. Calendly also returns upcoming events, so the saved cursor can move into the future. Later syncs can miss new bookings for earlier times and updates, such as cancellations, to events outside the lookback window. `event_invitees` depends on these parent events and has the same limitation.

Use Full refresh for both `scheduled_events` and `event_invitees` to reread the events covered by your start date. If you use incremental syncs, set `lookback_days` to at least how far in advance invitees can book. This rereads events in that window, but doesn't capture later changes to older events outside it.

:::

## Rate limits

[Calendly limits API requests](https://developer.calendly.com/api-docs/overview/rate-limits) to 500 requests per user per minute on paid plans and 50 on the Free plan. Other applications using the same Calendly user share this allowance.

The connector monitors `X-RateLimit-Remaining` and waits when the allowance is exhausted. If Calendly returns HTTP 429, the connector retries after the delay in `X-RateLimit-Reset`. Syncing invitees requires requests for each scheduled event, so large event histories can take longer to sync.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| HTTP 401: invalid or revoked token | Create a new personal access token and update the Airbyte source settings. |
| HTTP 403: insufficient scope or permission denied | Check the error for missing scopes. Create a token with the required read scopes, and use an organization owner or administrator account for organization-wide data such as scheduled events and webhook subscriptions. Update the token in Airbyte. |
| A scheduled event, event type or member disappears during a sync | The connector logs and skips that event's invitees, that event type's hosts, or that member's availability schedules and locations, then continues. A 404 on other endpoints fails the sync. |
| New bookings or cancellations are missing | Review the [incremental sync limitation](#incremental-sync-limitation). Use Full refresh for `scheduled_events` and `event_invitees` to reread events covered by your start date. |

## Upgrading to 0.2.0

Version 0.2.0 includes event types last updated before 2021 and invitees booked before the configured start date, which earlier versions could omit. Refresh the `event_types` and `event_invitees` streams to backfill these records. Invitees are still limited to the scheduled events selected by the parent stream. Refresh the connection schema to make the newly declared fields available.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| --- | --- | --- | --- |
| 0.3.0 | 2026-11-03 | [90847](https://github.com/airbytehq/airbyte/pull/90847) | Add teams, event type memberships, group relationships, user availability schedules, locations, organization invitations and webhook subscriptions streams; the last three need the `availability:read`, `locations:read` and `webhooks:read` scopes |
| 0.2.0 | 2026-11-03 | [90829](https://github.com/airbytehq/airbyte/pull/90829) | Handle rate limits and token errors, declare missing fields, fix the crash when `lookback_days` is unset, stop dropping event types updated before 2021 and invitees booked before the start date (refresh these streams to backfill) |
| 0.1.58 | 2026-11-03 | [90473](https://github.com/airbytehq/airbyte/pull/90473) | Update dependencies |
| 0.1.57 | 2026-10-27 | [89813](https://github.com/airbytehq/airbyte/pull/89813) | Update dependencies |
| 0.1.56 | 2026-10-20 | [89122](https://github.com/airbytehq/airbyte/pull/89122) | Update dependencies |
| 0.1.55 | 2026-10-13 | [88545](https://github.com/airbytehq/airbyte/pull/88545) | Update dependencies |
| 0.1.54 | 2026-10-06 | [87778](https://github.com/airbytehq/airbyte/pull/87778) | Update dependencies |
| 0.1.53 | 2026-09-29 | [87092](https://github.com/airbytehq/airbyte/pull/87092) | Update dependencies |
| 0.1.52 | 2026-09-22 | [86548](https://github.com/airbytehq/airbyte/pull/86548) | Update dependencies |
| 0.1.51 | 2026-09-15 | [85958](https://github.com/airbytehq/airbyte/pull/85958) | Update dependencies |
| 0.1.50 | 2026-09-08 | [85409](https://github.com/airbytehq/airbyte/pull/85409) | Update dependencies |
| 0.1.49 | 2026-08-18 | [84504](https://github.com/airbytehq/airbyte/pull/84504) | Update dependencies |
| 0.1.48 | 2026-08-11 | [83834](https://github.com/airbytehq/airbyte/pull/83834) | Update dependencies |
| 0.1.47 | 2026-08-04 | [83371](https://github.com/airbytehq/airbyte/pull/83371) | Update dependencies |
| 0.1.46 | 2026-07-28 | [82826](https://github.com/airbytehq/airbyte/pull/82826) | Update dependencies |
| 0.1.45 | 2026-07-21 | [82322](https://github.com/airbytehq/airbyte/pull/82322) | Update dependencies |
| 0.1.44 | 2026-07-14 | [81752](https://github.com/airbytehq/airbyte/pull/81752) | Update dependencies |
| 0.1.43 | 2026-06-30 | [80989](https://github.com/airbytehq/airbyte/pull/80989) | Update dependencies |
| 0.1.42 | 2026-06-23 | [80355](https://github.com/airbytehq/airbyte/pull/80355) | Update dependencies |
| 0.1.41 | 2026-06-16 | [79778](https://github.com/airbytehq/airbyte/pull/79778) | Update dependencies |
| 0.1.40 | 2026-06-09 | [79236](https://github.com/airbytehq/airbyte/pull/79236) | Update dependencies |
| 0.1.39 | 2026-06-02 | [78555](https://github.com/airbytehq/airbyte/pull/78555) | Update dependencies |
| 0.1.38 | 2026-04-28 | [77167](https://github.com/airbytehq/airbyte/pull/77167) | Update dependencies |
| 0.1.37 | 2026-04-21 | [76522](https://github.com/airbytehq/airbyte/pull/76522) | Update dependencies |
| 0.1.36 | 2026-03-31 | [75659](https://github.com/airbytehq/airbyte/pull/75659) | Update dependencies |
| 0.1.35 | 2026-03-17 | [74912](https://github.com/airbytehq/airbyte/pull/74912) | Update dependencies |
| 0.1.34 | 2026-03-10 | [74632](https://github.com/airbytehq/airbyte/pull/74632) | Update dependencies |
| 0.1.33 | 2026-03-03 | [73791](https://github.com/airbytehq/airbyte/pull/73791) | Update dependencies |
| 0.1.32 | 2026-02-03 | [72615](https://github.com/airbytehq/airbyte/pull/72615) | Update dependencies |
| 0.1.31 | 2026-01-20 | [72052](https://github.com/airbytehq/airbyte/pull/72052) | Update dependencies |
| 0.1.30 | 2026-01-14 | [71456](https://github.com/airbytehq/airbyte/pull/71456) | Update dependencies |
| 0.1.29 | 2025-12-18 | [70622](https://github.com/airbytehq/airbyte/pull/70622) | Update dependencies |
| 0.1.28 | 2025-11-25 | [69971](https://github.com/airbytehq/airbyte/pull/69971) | Update dependencies |
| 0.1.27 | 2025-11-18 | [69431](https://github.com/airbytehq/airbyte/pull/69431) | Update dependencies |
| 0.1.26 | 2025-10-29 | [68715](https://github.com/airbytehq/airbyte/pull/68715) | Update dependencies |
| 0.1.25 | 2025-10-21 | [68240](https://github.com/airbytehq/airbyte/pull/68240) | Update dependencies |
| 0.1.24 | 2025-10-14 | [67837](https://github.com/airbytehq/airbyte/pull/67837) | Update dependencies |
| 0.1.23 | 2025-10-07 | [67205](https://github.com/airbytehq/airbyte/pull/67205) | Update dependencies |
| 0.1.22 | 2025-09-30 | [66320](https://github.com/airbytehq/airbyte/pull/66320) | Update dependencies |
| 0.1.21 | 2025-08-09 | [64664](https://github.com/airbytehq/airbyte/pull/64664) | Update dependencies |
| 0.1.20 | 2025-08-02 | [64409](https://github.com/airbytehq/airbyte/pull/64409) | Update dependencies |
| 0.1.19 | 2025-07-26 | [63801](https://github.com/airbytehq/airbyte/pull/63801) | Update dependencies |
| 0.1.18 | 2025-07-19 | [63484](https://github.com/airbytehq/airbyte/pull/63484) | Update dependencies |
| 0.1.17 | 2025-07-12 | [63040](https://github.com/airbytehq/airbyte/pull/63040) | Update dependencies |
| 0.1.16 | 2025-06-28 | [62148](https://github.com/airbytehq/airbyte/pull/62148) | Update dependencies |
| 0.1.15 | 2025-06-21 | [61888](https://github.com/airbytehq/airbyte/pull/61888) | Update dependencies |
| 0.1.14 | 2025-05-28 | [60946](https://github.com/airbytehq/airbyte/pull/60946) | update scheduled events to ingest future events |
| 0.1.13 | 2025-05-24 | [60689](https://github.com/airbytehq/airbyte/pull/60689) | Update dependencies |
| 0.1.12 | 2025-05-10 | [59878](https://github.com/airbytehq/airbyte/pull/59878) | Update dependencies |
| 0.1.11 | 2025-05-03 | [59314](https://github.com/airbytehq/airbyte/pull/59314) | Update dependencies |
| 0.1.10 | 2025-04-26 | [58702](https://github.com/airbytehq/airbyte/pull/58702) | Update dependencies |
| 0.1.9 | 2025-04-19 | [58247](https://github.com/airbytehq/airbyte/pull/58247) | Update dependencies |
| 0.1.8 | 2025-04-12 | [57661](https://github.com/airbytehq/airbyte/pull/57661) | Update dependencies |
| 0.1.7 | 2025-04-05 | [57123](https://github.com/airbytehq/airbyte/pull/57123) | Update dependencies |
| 0.1.6 | 2025-03-29 | [56618](https://github.com/airbytehq/airbyte/pull/56618) | Update dependencies |
| 0.1.5 | 2025-03-22 | [56087](https://github.com/airbytehq/airbyte/pull/56087) | Update dependencies |
| 0.1.4 | 2025-03-08 | [55375](https://github.com/airbytehq/airbyte/pull/55375) | Update dependencies |
| 0.1.3 | 2025-03-01 | [54839](https://github.com/airbytehq/airbyte/pull/54839) | Update dependencies |
| 0.1.2 | 2025-02-22 | [54274](https://github.com/airbytehq/airbyte/pull/54274) | Update dependencies |
| 0.1.1 | 2025-02-15 | [51240](https://github.com/airbytehq/airbyte/pull/51240) | Update dependencies |
| 0.1.0 | 2025-02-12 | [52566](https://github.com/airbytehq/airbyte/pull/52566) | Add stream organization members, groups, available event types, and scheduled events. |
| 0.0.8 | 2024-12-28 | [50462](https://github.com/airbytehq/airbyte/pull/50462) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50152](https://github.com/airbytehq/airbyte/pull/50152) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49551](https://github.com/airbytehq/airbyte/pull/49551) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49275](https://github.com/airbytehq/airbyte/pull/49275) | Update dependencies |
| 0.0.4 | 2024-12-11 | [49022](https://github.com/airbytehq/airbyte/pull/49022) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-11-04 | [48279](https://github.com/airbytehq/airbyte/pull/48279) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47568](https://github.com/airbytehq/airbyte/pull/47568) | Update dependencies |
| 0.0.1 | 2024-09-01 | | Initial release by [@natikgadzhi](https://github.com/natikgadzhi) via Connector Builder |

</details>
