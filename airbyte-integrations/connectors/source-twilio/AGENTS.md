> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-twilio

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Twilio REST API supports `DateCreated` filtering on many resource list endpoints. Every stream is declared in `manifest.yaml`; `components.py` only holds the schema-normalization type transformer and the state migrations.

**Connector type:** Manifest-only, with custom components in `components.py`

**Analysis status:** No stream-by-stream incremental analysis yet; build it from the stream definitions in `manifest.yaml`.

### Future incremental stream candidates

None identified yet.

## Alerts request window splitting

The `alerts` stream handles Twilio's 10,000-result cap with a `SPLIT_REQUEST_WINDOW` response filter plus `request_window_splitting`:

- The SPLIT filter matches only the message "Invalid page and pageSize combination". Don't add `http_codes: [400]` to it: `HttpResponseFilter` ORs its conditions, so that would split every 400.
- Twilio returns that 400 only past the 10,000th record (`Page=10` at `PageSize=1000`), so every split replays up to 10,000 already-emitted records. Deduplicated sync modes drop them by `sid`; Append and Overwrite keep them.
- Each split halves the window at `PT1S` granularity and the CDK stops after 10 halvings, so the smallest window is the slice span / 1024: about 43 minutes with `P1M`, about 84 seconds with `P1D`.
- Exhausted splitting (depth 10, or a window that can't shrink) fails as `transient_error` with `failure_message` appended to the CDK message.
- Any other Alerts 400 hits the dedicated FAIL filter (`http_codes: [400]`, after the SPLIT filter) and fails as `system_error` with Twilio's own message.

## Cursor granularity must match the cursor format

`messages` and `recordings` format their cursor as `%Y-%m-%d %H:%M:%SZ` (whole seconds), so their `cursor_granularity` is `PT1S`. A finer granularity (e.g. `PT0.000001S`) leaves a gap between adjacent slices once the boundaries are formatted to seconds; the CDK then cannot merge the slices and the per-partition state only advances to the latest record of the first slice, so every multi-slice sync re-reads everything after it. Keep `cursor_granularity` equal to the smallest unit `datetime_format` can express.
