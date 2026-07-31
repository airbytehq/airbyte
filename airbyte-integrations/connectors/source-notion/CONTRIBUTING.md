# Contributing to source-notion

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

**Connector type:** Hybrid (manifest.yaml + Python custom components for record transformation, property flattening, and custom retriever)

**Analysis status:** Complete. 5 streams analyzed. All 5 use incremental sync via Notion's `filter.timestamp`/`last_edited_time` params. The connector is fully incremental.

### Incremental Streams

| Stream | Cursor Field | API Filter | Notes |
|--------|-------------|------------|-------|
| pages | last_edited_time | `filter.timestamp` = `last_edited_time` | Notion Search API with `last_edited_time` filter |
| databases | last_edited_time | `filter.timestamp` = `last_edited_time` | Notion Search API with `last_edited_time` filter |
| blocks | last_edited_time | Semi-incremental (client-side filtering) | Blocks retrieved per page; filtered client-side |
| comments | last_edited_time | Semi-incremental (client-side filtering) | Comments retrieved per block/page |
| users | (semi-incremental) | No server-side filter | Small dataset; fetches all and filters client-side |

### Full-Refresh Streams (Not Actionable)

No full-refresh-only streams. All streams support at least semi-incremental sync.
