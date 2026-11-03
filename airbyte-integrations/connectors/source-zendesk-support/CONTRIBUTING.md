# Contributing to source-zendesk-support

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **`tickets`, `users`, `organizations` and `articles` Walk Sorted List Endpoints Newest-First and Stop Themselves** -- Zendesk retired its Incremental Export APIs for integrations, so these streams read list endpoints sorted by the cursor descending and a paginator stop condition ends each sync; archived and deleted records are no longer returned, and the `tickets` cursor is `updated_at` with an automatic migration from `generated_timestamp`.
2. **StateDelegatingStream for Ticket Metrics — Two Completely Different Sync Paths** -- `ticket_metrics` bulk-reads everything when it has no state and reads one ticket at a time once it does, so performance depends on whether state exists.
3. **Enterprise-Only Streams Disabled at Manifest Level** -- Streams that need an Enterprise plan are commented out of the manifest because the CDK cannot yet hide streams based on endpoint availability.
4. **`ticket_events`, `ticket_comments` and `ticket_metric_events` Are Per-Ticket Substreams That Rebuild the Export Record Shape** -- Each costs one request per created or updated ticket, re-emits all of a changed ticket's records (its metric events, comments, events and side conversations; none of them is filtered on the saved cursor), and reshapes audits to look like the former export records, with documented differences in `ticket_events`; `ticket_metric_events` cursors on the parent ticket because Zendesk dates SLA breach events in the future.
5. **Per-Ticket Substreams Must Key Error Handling on the Status Code, Not the Response Body** -- Zendesk can refuse or lose single tickets with an empty body, so per-ticket streams ignore `403`/`404` by status code to keep the parent cursor advancing.
6. **`num_workers` Minimum Is 2 — One Thread Leaves No Sibling to Beat the Heartbeat** -- With one worker, a long `tickets` walk emits nothing and the platform cancels the sync, so the floor is enforced in the spec, a config migration and the concurrency clamp.
7. **`ticket_audits_per_ticket` Is Opt-In, Shares the Per-Ticket Audits Retriever, and No Longer Reaches Archived Tickets** -- The stream costs one request per updated ticket, so it is never suggested by default, and since 6.0.0 its parent list omits archived tickets.
8. **OAuth Completion Must Extract `expires_in` to Persist Token Expiry** -- Zendesk refresh tokens are single-use, so the OAuth flow must record the token expiry or every run burns a refresh token and the stored credentials stop working.

## Local testing notes

- Unit tests: `cd unit_tests && TZ=UTC poetry run pytest -q`. One `tickets_search` lookback test depends on the local time zone, so always set `TZ=UTC`.
- The OAuth integration-test credentials use single-use rotating refresh tokens. Running `check` or `read` locally with them consumes the shared refresh token; use the API-token credentials for local runs.
