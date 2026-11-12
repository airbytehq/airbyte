# Contributing to source-twilio

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Twilio REST API supports `DateCreated` filtering on many resource list endpoints. Every stream is declared in `manifest.yaml`; `components.py` only holds the schema-normalization type transformer and the state migrations.

**Connector type:** Manifest-only, with custom components in `components.py`

**Analysis status:** No stream-by-stream incremental analysis yet; build it from the stream definitions in `manifest.yaml`.

### Stale per-partition cursors

When an account's saved cursor is older than the stream's global cursor, the per-partition incremental streams resume that account from the global cursor instead of re-reading its history. See `AGENTS.md` for how `TwilioStalePartitionStateMigration` decides which entries are stale.

### Future incremental stream candidates

None identified yet.

## Alerts request window splitting

When an Alerts request window holds more than Twilio's 10,000-result limit, the `alerts` stream splits it in half and re-reads each half (up to 10 times), re-emitting up to 10,000 records per split. See `AGENTS.md` for the filter setup, duplicate handling, smallest window, and failure behavior.
