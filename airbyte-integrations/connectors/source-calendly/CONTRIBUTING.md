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
6. **Plan-Gated Streams Skip Only Explicit Upgrade Messages** -- Outgoing communications and activity logs require Enterprise; meeting recaps need a paid Notetaker plan. Only the documented plan/feature messages are ignored. Missing scopes, owner/admin errors, and unknown 403s still fail.
7. **New Incremental Streams Bound Both Requests and State** -- Communications use `created_at`, activity logs use `occurred_at`, and recaps use meeting `start_time`. All send lower and upper bounds and filter records outside the window. Recaps that become available later for an older meeting need Full refresh.
8. **Outgoing Communications Have No Documented Unique Identifier** -- The API returns email/SMS records without `uri`. Do not invent a key or deduplicate unrelated messages; the stream has no declared primary key.

## Token scopes

Select the read scope for every selected stream. Organization-scoped streams and the connection check also require `users:read`. A successful check does not validate all stream scopes; missing scope names appear in the appended `required_scopes` error detail.

| Stream | Required read scope |
| --- | --- |
| `api_user` | `users:read` |
| `event_types` | `event_types:read` |
| `groups` | `groups:read` |
| `organization_memberships` | `organizations:read` |
| `scheduled_events` | `scheduled_events:read` |
| `event_invitees` | `scheduled_events:read` |
| `routing_forms` | `routing_forms:read` |
| `routing_form_submissions` | `routing_forms:read` |
| `contacts` | `contacts:read` |
| `outgoing_communications` | `outgoing_communications:read` |
| `activity_log_entries` | `activity_log:read` |
| `meeting_recaps` | `meeting_recaps:read` |

## Local tests

From `unit_tests/`, run `poetry install` and `poetry run pytest -q`. Tests use mocked HTTP requests and do not require a live Calendly token.
