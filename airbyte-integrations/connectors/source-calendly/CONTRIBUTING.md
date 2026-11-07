# Contributing to source-calendly

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Authentication Failures Stop the Sync, but Deleted Parent Events Do Not** -- Invalid tokens or missing permissions require user action. A deleted event or routing form is skipped when reading its invitees or submissions so other parents can still sync.
2. **Rate-Limit Reset Headers Are Durations, Not Epoch Timestamps** -- Free and paid plans have different per-user allowances. The connector adapts to the remaining allowance and waits for rate limits rather than treating the reset delay as a calendar timestamp.
3. **Scheduled Events Use `updated_at`; Invitees Follow Changed Events** -- Each scheduled-events sync scans from the configured start date and uses an `updated_at` cursor, so future start times do not block later bookings or cancellations. Invitees follow only new or changed parent events.
4. **Existing Datetime and Position Fields Carry Documented Types** -- Since 1.0.0, existing datetime and position fields declare their documented formats and types, and `event_types.duration_options` items are integers. Further retypes require a breaking release.
5. **Connection Check Tests Only Current-User Access** -- A successful connection check confirms access to the token owner's profile, not permission to read every selected stream.
6. **Organization-Member and Event-Type Fan-Out Streams** -- Availability schedules, locations and event type hosts send one request per member or event type, and skip a member or event type that disappears mid-sync; teams are read once for the organization, and locations have no primary key.
7. **Plan-Gated Streams Skip Only Explicit Upgrade Messages** -- Outgoing communications and activity logs require Enterprise, meeting recaps a paid Notetaker plan, and Calendly documents a paid-plan error for contacts. Only the documented plan/feature messages are ignored. Missing scopes, owner/admin errors, and unknown 403s still fail.
8. **New Incremental Streams Bound Both Requests and State** -- Communications use `created_at`, activity logs use `occurred_at`, and recaps use meeting `start_time`. All send lower and upper bounds and filter records outside the window. Recaps are re-read for three days because Calendly returns them only after processing.
9. **Outgoing Communications Have No Documented Unique Identifier** -- The API returns email/SMS records without `uri`. Do not invent a key; the stream has no declared primary key and keeps per-partition state, so a sync does not re-read the previous sync's duration.

## Token scopes per stream

The connection check and most streams read the current user (`users:read`) to find the organization; member-based streams also read `organization_memberships` (`organizations:read`). A successful check does not validate all stream scopes; missing scope names appear in the appended `required_scopes` error detail.

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
| `routing_forms` | `users:read`, `routing_forms:read` |
| `routing_form_submissions` | `users:read`, `routing_forms:read` |
| `contacts` | `contacts:read` |
| `outgoing_communications` | `users:read`, `outgoing_communications:read` |
| `activity_log_entries` | `users:read`, `activity_log:read` |
| `meeting_recaps` | `meeting_recaps:read` |

## Local tests

From `unit_tests/`, run `poetry install` and `poetry run pytest -q`. Tests use mocked HTTP requests and do not require a live Calendly token.
