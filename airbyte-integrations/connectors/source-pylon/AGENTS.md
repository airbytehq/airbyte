> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-pylon

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Pylon API supports cursor-based pagination on some list endpoints. The `issues` stream already uses `DatetimeBasedCursor` with `updated_at` filtering. The remaining parent streams use full refresh: config-style lookups do not expose date-based filtering, and audit logs defer incremental support until write lag is understood.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| accounts | small | top-level parent | none | none | deferred_no_api_support | Config-style; no date filter |
| activity_types | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| audit_logs | growing | top-level parent | none | action_happened_at search filter | deferred_write_lag | Full refresh; separate created_at means late-written records could be missed |
| contacts | medium | top-level parent | none | none | deferred_no_api_support | No documented date filter on list endpoint |
| custom_fields | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| issue_statuses | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| issues | medium | top-level parent | updated_at | updated_at | incremental | Uses `DatetimeBasedCursor`; state migrated from `created_at` to `updated_at` |
| knowledge_bases | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| macro_groups | small | top-level parent | none | none | deferred_no_api_support | Full refresh; no time filter or pagination |
| surveys | small | top-level parent | none | none | deferred_no_api_support | Full refresh; no time filter or pagination |
| tags | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| teams | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| ticket_forms | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| training_data | small | top-level parent | none | none | deferred_no_api_support | Full refresh; no time filter or pagination |
| user_roles | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| users | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| issue_messages | medium | child | none | none | deferred_child |  |
| issue_threads | medium | child | none | none | deferred_child |  |
| knowledge_base_articles | medium | child | none | none | deferred_child |  |

### Future incremental stream candidates

- **Audit logs:** `POST /audit-logs/search` supports an `action_happened_at` filter, but records carry a separate `created_at`. Late-written records could fall behind a saved action-time cursor and be missed. Keep `audit_logs` full refresh until write lag can be shown to be bounded.
- **Unpaginated lookups (3 streams):** `macro_groups`, `surveys`, and `training_data` have no time filter and no pagination, so they remain full refresh.
- **No API date filter (11 streams):** `accounts`, `activity_types`, `contacts`, `custom_fields`, `issue_statuses`, `knowledge_bases`, `tags`, `teams`, `ticket_forms`, `user_roles`, `users` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
- **Child streams (3 streams):** `issue_messages`, `issue_threads`, `knowledge_base_articles` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate incremental support.
