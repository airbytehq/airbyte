> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-twilio

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Twilio REST API supports `DateCreated` filtering on many resource list endpoints. Every stream is declared in `manifest.yaml`; `components.py` only holds the schema-normalization type transformer and the state migrations.

**Connector type:** Manifest-only, with custom components in `components.py`

`conversations` and `executions` filter on creation date only. Later updates (and steps added to long-running executions) are revisited only within the Lookback window; use full refresh for complete current state.

Both cursors use a fixed 2010-01-01 floor rather than Replication Start Date, preserving existing full-refresh data scope. Neither uses Slice Step Duration. Conversations have no step or cursor_granularity, preserving a single request window, with inclusive whole-day StartDate/EndDate filters and date-only state. Executions use DateCreatedFrom/DateCreatedTo and per-flow state, with a fixed P28D step and PT1S granularity because Studio limits date ranges to one calendar month. This slicing also applies when executions is the parent of step, including after lookback is applied.

`step` uses incremental_dependency on executions, retaining flow_sid as an extra field. Its global child cursor has a far-future end, no request options, and no client-side filtering; nested parent_state resumes executions per flow. Conversation children intentionally use base_conversations_stream without an incremental cursor or dependency so they still enumerate all conversations.

### Future incremental stream candidates

None identified yet.

## Alerts request window splitting

The `alerts` stream handles Twilio's 10,000-result cap with a `SPLIT_REQUEST_WINDOW` response filter plus `request_window_splitting`:

- The SPLIT filter matches only the message "Invalid page and pageSize combination". Don't add `http_codes: [400]` to it: `HttpResponseFilter` ORs its conditions, so that would split every 400.
- Twilio returns that 400 only past the 10,000th record (`Page=10` at `PageSize=1000`), so every split replays up to 10,000 already-emitted records. Deduplicated sync modes drop them by `sid`; Append and Overwrite keep them.
- Each split halves the window at `PT1S` granularity and the CDK stops after 10 halvings, so the smallest window is the slice span / 1024: about 43 minutes with `P1M`, about 84 seconds with `P1D`.
- Exhausted splitting (depth 10, or a window that can't shrink) fails as `transient_error` with `failure_message` appended to the CDK message.
- Any other Alerts 400 hits the dedicated FAIL filter (`http_codes: [400]`, after the SPLIT filter) and fails as `system_error` with Twilio's own message.
