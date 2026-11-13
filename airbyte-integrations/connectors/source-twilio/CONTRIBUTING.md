# Contributing to source-twilio

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Twilio REST API supports `DateCreated` filtering on many resource list endpoints. Every stream is declared in `manifest.yaml`; `components.py` only holds the schema-normalization type transformer and the state migrations.

**Connector type:** Manifest-only, with custom components in `components.py`

**Analysis status:** No stream-by-stream incremental analysis yet; build it from the stream definitions in `manifest.yaml`.

### Future incremental stream candidates

None identified yet.

## Messages global cursor

The `messages` stream uses one global `date_sent` cursor for all accounts (`global_substream_cursor: true`), not one cursor per account:

- With per-account state, an account that returned no messages kept its old cursor, so every sync re-read that account from the old date even when the stream-level `state.date_sent` was recent.
- `TwilioMessagesGlobalCursorStateMigration` converts per-account state to the global shape. It uses the stream-level `state.date_sent`, which the CDK only advances after every account finished reading. Legacy state without it falls back to the oldest account cursor so no account skips messages.
- `message_media` still uses per-message-partition state; its partitions are unchanged.

## Alerts request window splitting

When an Alerts request window holds more than Twilio's 10,000-result limit, the `alerts` stream splits it in half and re-reads each half (up to 10 times), re-emitting up to 10,000 records per split. See `AGENTS.md` for the filter setup, duplicate handling, smallest window, and failure behavior.
