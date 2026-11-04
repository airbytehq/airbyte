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

## Local tests

From `unit_tests/`, run `poetry install` and `poetry run pytest -q`. Tests use mocked HTTP requests and do not require a live Calendly token.
