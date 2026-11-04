# Contributing to source-pylon

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Pylon API supports cursor-based pagination on list endpoints. The `issues` stream already uses `DatetimeBasedCursor` with `updated_at` filtering. The remaining FR parent streams are config-style lookups (accounts, contacts, tags, teams, users, custom_fields, etc.) that do not expose date-based filtering parameters.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| accounts | small | top-level parent | none | none | deferred_no_api_support | Config-style; no date filter |
| activity_types | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| contacts | medium | top-level parent | none | none | deferred_no_api_support | No documented date filter on list endpoint |
| custom_fields | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| issue_statuses | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| issues | medium | top-level parent | updated_at | updated_at | incremental | Uses `DatetimeBasedCursor`; state migrated from `created_at` to `updated_at` |
| knowledge_bases | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| tags | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| teams | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| ticket_forms | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| user_roles | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| users | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| issue_messages | medium | child | none | none | deferred_child |  |
| issue_threads | medium | child | none | none | deferred_child |  |
| knowledge_base_articles | medium | child | none | none | deferred_child |  |

### Future incremental stream candidates

- **No API date filter (11 streams):** `accounts`, `activity_types`, `contacts`, `custom_fields`, `issue_statuses`, `knowledge_bases`, `tags`, `teams`, `ticket_forms`, `user_roles`, `users` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
- **Child streams (3 streams):** `issue_messages`, `issue_threads`, `knowledge_base_articles` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate incremental support.
