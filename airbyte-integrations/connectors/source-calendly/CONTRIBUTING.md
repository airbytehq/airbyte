# Contributing to source-calendly

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Authentication Failures Stop the Sync, but Deleted Parent Events Do Not** -- Invalid tokens or missing permissions require user action. A deleted event or routing form is skipped when reading its invitees or submissions so other parents can still sync.
2. **Rate-Limit Reset Headers Are Durations, Not Epoch Timestamps** -- Free and paid plans have different per-user allowances. The connector adapts to the remaining allowance and waits for rate limits rather than treating the reset delay as a calendar timestamp. `num_workers` selects 2–10 concurrent workers (default 4), sharing that allowance. Activity logs keep pages of 100: the spec permits 1000, but Calendly checks the Enterprise plan before parameters, so the larger size cannot be verified with the test account; other paginated endpoints document 100.
3. **Scheduled Events Use `updated_at`; Invitees Follow Changed Events** -- Each scheduled-events sync scans from the configured start date and uses an `updated_at` cursor, so future start times do not block later bookings or cancellations. Invitees follow only new or changed parent events.
4. **Existing Datetime and Position Fields Carry Documented Types** -- Since 1.0.0, existing datetime and position fields declare their documented formats and types, and `event_types.duration_options` items are integers. Further retypes require a breaking release. `event_invitees.payment.amount` stays a number: the spec's `InviteePayment.amount` says `type: string, title: float`, but the reference example is `1234.56`, and no credentialed test record carries `payment`.
5. **Connection Check Tests Only Current-User Access** -- A successful connection check confirms access to the token owner's profile, not permission to read every selected stream.
6. **Organization-Member, Event-Type and Group Fan-Out Streams** -- Availability schedules, locations and event type hosts send one request per member or event type, and skip a member or event type that disappears mid-sync; teams are read once for the organization, and locations have no primary key. Group relationships send only `group` (never `organization`) and pagination parameters for each group; no groups means no relationship requests. A deleted group's 404 is skipped with an INFO notice naming the endpoint; all 401s and 403s still fail.
7. **Plan-Gated Streams Skip Only Explicit Upgrade Messages** -- Routing forms require Teams; when unavailable, forms and submissions complete empty without requesting submissions. The handler recognizes `Please upgrade your Calendly account to Teams` with or without a final period. Outgoing communications and activity logs require Enterprise, meeting recaps a paid Notetaker plan, and Calendly documents a paid-plan error for contacts. Only the explicit plan/feature messages are ignored. Missing scopes, owner/admin errors, and unknown 403s still fail.
8. **New Incremental Streams Bound Both Requests and State** -- Communications use `created_at`, activity logs use `occurred_at`, and recaps use meeting `start_time`. All send lower and upper bounds and filter records outside the window. Recaps are re-read for three days because Calendly returns them only after processing.
9. **Outgoing Communications Have No Documented Unique Identifier** -- The API returns email/SMS records without `uri`. Do not invent a key; the stream has no declared primary key and keeps per-partition state, so a sync does not re-read the previous sync's duration.
10. **OAuth Is the Default and Calendly Rotates Refresh Tokens** -- Users sign in with Calendly OAuth (PKCE required); a personal access token remains the fallback, and older configs with a top-level `api_key` are migrated into `credentials`. Every refresh returns a new refresh token, so the connector must persist it and reuse one access token across streams.

## Token scopes per stream

With OAuth, scopes are configured on the Calendly OAuth application, not requested in the authorization URL, so the application must have every scope below. Personal access tokens need the same scopes, selected when the token is created.

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
| `event_type_availability_schedules` | `users:read`, `event_types:read`, `availability:read` |
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

## Full-refresh streams

- `api_user`: one current profile, without an incremental API.
- `groups`: mutable groups without an update filter or ordered update feed.
- `organization_memberships`: partial update scans would omit unchanged members needed by child streams; no update filter is documented.
- `teams`: mutable teams without an update filter or update ordering.
- `event_type_memberships`: host assignments lack an update cursor and filter.
- `event_type_availability_schedules`: availability rules lack an update cursor and filter; separate hosts use the composite key `(event_type, availability_rule_uri)`.
- `group_relationships`: relationship changes lack an update cursor and filter.
- `user_availability_schedules`: schedule changes lack an update cursor and filter.
- `locations`: location snapshots lack an update cursor and filter.
- `organization_invitations`: invitation changes lack an update filter and ordering.
- `webhook_subscriptions`: subscription configuration changes lack an update filter and ordering.
- `routing_forms`: mutable forms lack an update filter and ordering.
- `routing_form_submissions`: only creation-time sorting is available, and submissions change after creation.
- `contacts`: update-time sorting exists, but access is plan-gated and cannot be verified on the test account.

Event-type availability uses the same stale-parent handling as event-type hosts. Live probes returned one item per test event type with no next page; the spec defines no pagination input, so the stream is unpaginated and not suggested by default. Both the API and OAuth authentication hosts must stay allowed for token refresh to work under egress enforcement.

## Local tests

From `unit_tests/`, run `poetry install` and `poetry run pytest -q`. Tests use mocked HTTP requests and do not require live Calendly credentials; `test_authentication.py` covers the OAuth refresh, token reuse and legacy config migration.
