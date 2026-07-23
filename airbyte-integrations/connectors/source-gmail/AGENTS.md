> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-gmail

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Gmail API uses a query-based filtering system (`q` parameter) that supports date ranges via `after:` and `before:` operators. However, these filter by internal date (similar to created_at), not by modification time. Messages and threads are mutable (labels change, read status), making `created_at`-style filtering insufficient. The `profile`, `drafts`, and `labels` streams are small config-style endpoints.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| drafts | small | top-level parent | none | none | deferred_no_api_support | No date filter; relatively small set per user |
| labels | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup, typically <100 labels |
| messages | xlarge | top-level parent | none | created_at_only | deferred_no_api_support | Gmail q parameter supports after:/before: but filters by internalDate (received), not modification time |
| profile | small | top-level parent | none | none | deferred_no_api_support | Singleton user profile endpoint |
| threads | xlarge | top-level parent | none | created_at_only | deferred_no_api_support | Same limitation as messages — q parameter filters by date received |
| labels_details | medium | child | none | none | deferred_child |  |
| messages_details | medium | child | none | none | deferred_child |  |
| threads_details | medium | child | none | none | deferred_child |  |

### Future incremental stream candidates

- **No API date filter (5 streams):** `drafts`, `labels`, `messages`, `profile`, `threads` — these streams do not have a documented date-based filter on their list endpoints. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
- **Child streams (3 streams):** `labels_details`, `messages_details`, `threads_details` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate whether these can be made incremental independently or via `incremental_dependency`.
