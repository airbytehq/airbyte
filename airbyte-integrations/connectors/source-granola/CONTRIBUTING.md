# Contributing to source-granola

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Granola API connector has 2 streams: `notes` (incremental with `updated_at` cursor) and `detailed_notes` (child of notes via `SubstreamPartitionRouter`). No FR parent streams remain.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| notes | medium | top-level parent | updated_at | updated_after | incremental |  |
| detailed_notes | medium | child | none | none | full child re-read | `incremental_dependency` is not enabled because it could skip detail updates when a parent cursor does not advance; all parent notes are re-read to keep details complete. |
