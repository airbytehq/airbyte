> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-clickup-api

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The ClickUp API v2 does not expose date-based filtering on the `user` or `team` endpoints. These are small config-style lookups. The connector's higher-volume data (tasks, comments, etc.) would be accessed through different endpoints not currently in this connector's manifest.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| team | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup; typically 1-5 teams |
| user | small | top-level parent | none | none | deferred_no_api_support | Singleton user endpoint |
| folder | medium | child | none | none | deferred_child |  |
| list | medium | child | none | none | deferred_child |  |
| list_comments | medium | child | none | none | deferred_child |  |
| list_custom_fields | medium | child | none | none | deferred_child |  |
| space | medium | child | none | none | deferred_child |  |
| space_tags | medium | child | none | none | deferred_child |  |
| task | medium | child | date_updated | none | deferred_child |  |
| team_custom_fields | medium | child | none | none | deferred_child |  |
| team_goals | medium | child | date_updated | none | deferred_child |  |
| time_tracking | medium | child | none | none | deferred_child |  |
| time_tracking_tags | medium | child | none | none | deferred_child |  |

### Future incremental stream candidates

- **No API date filter (2 streams):** `team`, `user` — these streams do not have a documented date-based filter on their list endpoints. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
- **Child streams (11 streams):** `folder`, `list`, `list_comments`, `list_custom_fields`, `space`, `space_tags`, `task`, `team_custom_fields`, `team_goals`, `time_tracking`, `time_tracking_tags` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate whether these can be made incremental independently or via `incremental_dependency`.
