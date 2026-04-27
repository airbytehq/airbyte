# Contributing to source-granola

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Granola API connector has 2 streams: `meetings` (incremental with `updated_at` cursor) and `panels` (child of meetings via `SubstreamPartitionRouter`). No FR parent streams remain.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| notes | medium | top-level parent | created_at | created_at | incremental |  |
| detailed_notes | medium | child | none | none | deferred_child |  |

### Deferred streams

- **Child streams (1 streams):** `detailed_notes` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate incremental support.
