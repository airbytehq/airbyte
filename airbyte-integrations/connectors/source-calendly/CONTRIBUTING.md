# Contributing to source-calendly

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Authentication Failures Stop the Sync, but Deleted Parent Events Do Not** -- Invalid tokens or missing permissions require user action. A deleted event is skipped when reading its invitees so other events can still sync.
2. **Rate-Limit Reset Headers Are Durations, Not Epoch Timestamps** -- Free and paid plans have different per-user allowances. The connector adapts to the remaining allowance and waits for rate limits rather than treating the reset delay as a calendar timestamp.
3. **The Scheduled-Events Cursor Can Move Into the Future** -- Calendly returns upcoming events, so incremental state can jump ahead and later syncs miss new bookings for earlier times; event invitees follow the same cursor. Users should sync both streams in Full refresh, or set the lookback to their booking horizon, until a breaking release fixes it.
4. **Existing Datetime Fields Intentionally Remain Strings Without Formats** -- Retyping existing fields can break destination schemas. Keep additions separate from changes to existing datetime column types.
5. **Connection Check Tests Only Current-User Access** -- A successful connection check confirms access to the token owner's profile, not permission to read every selected stream.
6. **Organization-Member and Event-Type Fan-Out Streams** -- Member- and event-type-based streams fan out into multiple requests; teams can be repeated for each member, and availability schedules and locations are not paginated.

## Token scopes per stream

Every stream reads the current user (`users:read`) to find the organization, and member-based streams read `organization_memberships` (`organizations:read`).

| Stream | Required scopes |
|---|---|
| api_user | `users:read` |
| event_types | `users:read`, `event_types:read` |
| groups | `users:read`, `groups:read` |
| organization_memberships | `users:read`, `organizations:read` |
| scheduled_events | `users:read`, `scheduled_events:read` |
| event_invitees | `users:read`, `scheduled_events:read` |
| teams | `users:read`, `organizations:read` |
| event_type_memberships | `users:read`, `event_types:read` |
| group_relationships | `users:read`, `groups:read` |
| user_availability_schedules | `users:read`, `organizations:read`, `availability:read` |
| locations | `users:read`, `organizations:read`, `locations:read` |
| organization_invitations | `users:read`, `organizations:read` |
| webhook_subscriptions | `users:read`, `webhooks:read` |

## Local tests

From `unit_tests/`, run `poetry install` and `poetry run pytest -q`. Tests use mocked HTTP requests and do not require a live Calendly token.
