# Contributing to source-granola

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Granola API connector has 2 streams: `notes` (incremental with `created_at` cursor) and `detailed_notes` (child of notes via `SubstreamPartitionRouter`). No FR parent streams remain.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| notes | medium | top-level parent | created_at | created_at | incremental |  |
| detailed_notes | medium | child | none | none | deferred_child |  |

### Future incremental stream candidates

- **Child streams (1 streams):** `detailed_notes` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate incremental support.
