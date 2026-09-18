# Contributing to source-slack

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

**Connector type:** Hybrid (manifest.yaml + Python custom components for channel joining, member extraction, custom retriever, and state migration)

**Analysis status:** Complete. 5 streams analyzed. 2 use incremental sync with timestamp cursors. 3 are full-refresh.

### Incremental Streams

| Stream | Cursor Field | API Filter | Notes |
|--------|-------------|------------|-------|
| channel_messages | float_ts | `oldest`/`latest` params | Slack `conversations.history` with timestamp range |
| threads | float_ts | `oldest`/`latest` params | Slack `conversations.replies` with timestamp range |

### Full-Refresh Streams (Not Actionable)

| Stream | Reason | Evidence |
|--------|--------|----------|
| users | No date filtering | Slack `users.list` API has no `updated_since` or date filter |
| channels | No date filtering | Slack `conversations.list` API has no `updated_since` or date filter |
| channel_members | Substream of channels; no date filter | Slack `conversations.members` per-channel; no date param |
