# Contributing to source-harvest

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Harvest API supports `updated_since` filtering on most high-volume endpoints (clients, invoices, projects, tasks, time_entries, etc.), which the connector already uses. The remaining FR parent streams are `company` (singleton config endpoint) and `project_budget` (summary endpoint) — neither supports date-based filtering.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| clients | medium | top-level parent | updated_at | updated_at | incremental |  |
| company | small | top-level parent | none | none | deferred_no_api_support | Singleton config endpoint, no date filter |
| contacts | medium | top-level parent | updated_at | updated_at | incremental |  |
| estimate_item_categories | medium | top-level parent | updated_at | updated_at | incremental |  |
| estimates | medium | top-level parent | updated_at | updated_at | incremental |  |
| expense_categories | medium | top-level parent | updated_at | updated_at | incremental |  |
| expenses | medium | top-level parent | updated_at | updated_at | incremental |  |
| expenses_categories | medium | top-level parent | to | to | incremental |  |
| expenses_clients | medium | top-level parent | to | to | incremental |  |
| expenses_projects | medium | top-level parent | to | to | incremental |  |
| expenses_team | medium | top-level parent | to | to | incremental |  |
| invoice_item_categories | medium | top-level parent | updated_at | updated_at | incremental |  |
| invoices | medium | top-level parent | updated_at | updated_at | incremental |  |
| project_budget | small | top-level parent | none | none | deferred_no_api_support | Summary/report endpoint, no date filter |
| projects | medium | top-level parent | updated_at | updated_at | incremental |  |
| roles | medium | top-level parent | updated_at | updated_at | incremental |  |
| task_assignments | medium | top-level parent | updated_at | updated_at | incremental |  |
| tasks | medium | top-level parent | updated_at | updated_at | incremental |  |
| time_clients | medium | top-level parent | to | to | incremental |  |
| time_entries | medium | top-level parent | updated_at | updated_at | incremental |  |
| time_projects | medium | top-level parent | to | to | incremental |  |
| time_tasks | medium | top-level parent | to | to | incremental |  |
| time_team | medium | top-level parent | to | to | incremental |  |
| uninvoiced | medium | top-level parent | to | to | incremental |  |
| user_assignments | medium | top-level parent | updated_at | updated_at | incremental |  |
| users | medium | top-level parent | updated_at | updated_at | incremental |  |
| billable_rates | medium | child | none | none | deferred_child |  |
| cost_rates | medium | child | none | none | deferred_child |  |
| estimate_messages | medium | child | updated_at | updated_at | incremental |  |
| invoice_messages | medium | child | updated_at | updated_at | incremental |  |
| invoice_payments | medium | child | updated_at | updated_at | incremental |  |
| project_assignments | medium | child | updated_at | updated_at | incremental |  |

### Deferred streams

- **No API date filter (2 streams):** `company`, `project_budget` — these streams do not have a documented date-based filter on their list endpoints. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
- **Child streams (2 streams):** `billable_rates`, `cost_rates` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate whether these can be made incremental independently or via `incremental_dependency`.
