# Contributing to source-calendly

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Authentication Failures Stop the Sync, but Deleted Parent Events Do Not** -- Invalid tokens or missing permissions require user action. A deleted event is skipped when reading its invitees so other events can still sync.
2. **Rate-Limit Reset Headers Are Durations, Not Epoch Timestamps** -- Free and paid plans have different per-user allowances. The connector adapts to the remaining allowance and waits for rate limits rather than treating the reset delay as a calendar timestamp.
3. **Scheduled Events Use `updated_at`; Invitees Follow Changed Events** -- Each scheduled-events sync scans from the configured start date and uses an `updated_at` cursor, so future start times do not block later bookings or cancellations. Invitees follow only new or changed parent events.
4. **Existing Datetime and Position Fields Carry Documented Types** -- Since 1.0.0, existing datetime and position fields declare their documented formats and types, and `event_types.duration_options` items are integers. Further retypes require a breaking release.
5. **Connection Check Tests Only Current-User Access** -- A successful connection check confirms access to the token owner's profile, not permission to read every selected stream.

## Local tests

From `unit_tests/`, run `poetry install` and `poetry run pytest -q`. Tests use mocked HTTP requests and do not require a live Calendly token.
