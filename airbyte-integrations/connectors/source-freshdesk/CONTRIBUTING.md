# Contributing to source-freshdesk

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Freshdesk API supports `updated_since` filtering on a subset of its list endpoints — specifically `/api/v2/tickets`, `/api/v2/contacts`, and `/api/v2/companies` ([API Reference](https://developers.freshdesk.com/api/)). These endpoints accept an `updated_since` query parameter (mapped as `_updated_since` in the connector's request parameters). Most other list endpoints (agents, groups, roles, etc.) do not expose a date-based filter, so they remain full-refresh only despite having `updated_at` fields on their records.

The connector uses `DatetimeBasedCursor` with `cursor_field: updated_at` and `datetime_format: %Y-%m-%dT%H:%M:%SZ` for all incremental streams. Child streams (e.g. `canned_responses`, `conversations`, `discussion_comments`) are partitioned via `SubstreamPartitionRouter` and are handled separately from top-level parents.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| tickets | xlarge | top-level parent | updated_at | updated_since | incremental | Primary high-volume stream |
| contacts | xlarge | top-level parent | updated_at | updated_since | incremental | |
| companies | large | top-level parent | updated_at | updated_since | in_scope_this_pr | [API ref](https://developers.freshdesk.com/api/#list_all_companies) |
| satisfaction_ratings | medium | top-level parent | updated_at | updated_since | incremental | |
| agents | medium | top-level parent | updated_at | none | deferred_no_api_support | API only filters by email/state, not by date |
| business_hours | small | top-level parent | updated_at | none | deferred_no_api_support | No date filter on list endpoint |
| canned_response_folders | small | top-level parent | updated_at | none | deferred_no_api_support | No date filter on list endpoint |
| discussion_categories | small | top-level parent | updated_at | none | deferred_no_api_support | No date filter on list endpoint |
| email_configs | small | top-level parent | updated_at | none | deferred_no_api_support | No date filter on list endpoint |
| email_mailboxes | small | top-level parent | none | none | deferred_no_api_support | No updated_at field or date filter |
| groups | small | top-level parent | updated_at | none | deferred_no_api_support | No date filter on list endpoint |
| products | small | top-level parent | updated_at | none | deferred_no_api_support | No date filter on list endpoint |
| roles | small | top-level parent | updated_at | none | deferred_no_api_support | No date filter on list endpoint |
| scenario_automations | small | top-level parent | updated_at | none | deferred_no_api_support | No date filter on list endpoint |
| settings | small | top-level parent | none | none | not_applicable | Singleton config endpoint |
| skills | small | top-level parent | updated_at | none | deferred_no_api_support | No date filter on list endpoint |
| sla_policies | small | top-level parent | none | none | deferred_no_api_support | No updated_at field or date filter |
| solution_categories | small | top-level parent | updated_at | none | deferred_no_api_support | No date filter on list endpoint |
| surveys | small | top-level parent | updated_at | none | deferred_no_api_support | No date filter on list endpoint |
| ticket_fields | small | top-level parent | updated_at | none | deferred_no_api_support | No date filter on list endpoint |
| time_entries | large | top-level parent | updated_at | none | deferred_no_api_support | High volume but no date filter on list endpoint |
| canned_responses | small | child of canned_response_folders | none | none | deferred_child | |
| conversations | large | child of tickets | none | none | deferred_child | |
| discussion_comments | medium | child of discussion_topics | none | none | deferred_child | |
| discussion_forums | small | child of discussion_categories | none | none | deferred_child | |
| discussion_topics | medium | child of discussion_forums | none | none | deferred_child | |
| solution_articles | medium | child of solution_folders | none | none | deferred_child | |
| solution_folders | small | child of solution_categories | none | none | deferred_child | |

### Deferred streams

- **No API filter support (14 streams):** `agents`, `business_hours`, `canned_response_folders`, `discussion_categories`, `email_configs`, `groups`, `products`, `roles`, `scenario_automations`, `skills`, `solution_categories`, `surveys`, `ticket_fields`, `time_entries` — these streams have `updated_at` on the record but the Freshdesk API does not expose a date-based filter on their list endpoints. A future agent would need to verify via live API probing whether an undocumented `updated_since` parameter is accepted (some Freshdesk endpoints accept undocumented parameters).
- **No cursor field (3 streams):** `email_mailboxes`, `settings`, `sla_policies` — no `updated_at` field on the record, so incremental is not feasible without a different approach.
- **Child streams (7 streams):** `canned_responses`, `conversations`, `discussion_comments`, `discussion_forums`, `discussion_topics`, `solution_articles`, `solution_folders` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate whether these can be made incremental independently or via `incremental_dependency`.
