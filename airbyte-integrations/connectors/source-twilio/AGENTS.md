> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-twilio

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Twilio REST API supports `DateCreated` filtering on many resource list endpoints. Every stream is declared in `manifest.yaml`; `components.py` only holds the schema-normalization type transformer and the state migrations.

**Connector type:** Manifest-only, with custom components in `components.py`

**Analysis status:** No stream-by-stream incremental analysis yet; build it from the stream definitions in `manifest.yaml`.

### Stale per-partition cursors

The per-partition incremental streams (`calls`, `conferences`, `messages`, `message_media`, `recordings`, `usage_records`) use per-partition state. The CDK only advances a partition's cursor from records it reads, so a partition (an account, or a message for `message_media`) with no new records keeps an old cursor while the global `state` cursor moves on, and that old cursor takes precedence on the next sync. `TwilioStalePartitionStateMigration` (last in each stream's `state_migrations`) drops partition cursors older than the global cursor so those partitions resume from the global cursor plus the CDK's runtime `lookback_window`. This relies on the CDK only advancing the global cursor after a completed sync.

### Future incremental stream candidates

None identified yet.

## Alerts request window splitting

The `alerts` stream handles Twilio's 10,000-result cap with a `SPLIT_REQUEST_WINDOW` response filter plus `request_window_splitting`:

- The SPLIT filter matches only the message "Invalid page and pageSize combination". Don't add `http_codes: [400]` to it: `HttpResponseFilter` ORs its conditions, so that would split every 400.
- Twilio returns that 400 only past the 10,000th record (`Page=10` at `PageSize=1000`), so every split replays up to 10,000 already-emitted records. Deduplicated sync modes drop them by `sid`; Append and Overwrite keep them.
- Each split halves the window at `PT1S` granularity and the CDK stops after 10 halvings, so the smallest window is the slice span / 1024: about 43 minutes with `P1M`, about 84 seconds with `P1D`.
- Exhausted splitting (depth 10, or a window that can't shrink) fails as `transient_error` with `failure_message` appended to the CDK message.
- Any other Alerts 400 hits the dedicated FAIL filter (`http_codes: [400]`, after the SPLIT filter) and fails as `system_error` with Twilio's own message.
