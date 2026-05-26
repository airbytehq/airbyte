# source-harvest: Unique Connector Behaviors

This document describes the biggest non-obvious gotchas in `source-harvest` that deviate from standard
declarative connector patterns. Read this before making changes to the connector.

---

## 1. Graceful Degradation on 401/403/404

Every stream in source-harvest uses a `CompositeErrorHandler` that **ignores** (rather than fails on)
HTTP 401, 403, and 404 responses. This means if a user's credentials lack permission to access a
specific stream, or the account ID is incorrect for a particular resource, that stream silently produces
zero records instead of failing the entire sync.

**Why this matters:** This is an intentional design choice because Harvest's permission model is
granular -- a user may have access to time entries but not invoices, for example. However, it also means
that misconfigured credentials or an incorrect account ID will not produce an error; the sync will
succeed with empty streams, which can be confusing to diagnose.

---

## 2. Report Streams Use Date-Range Slicing with Different Cursor Format

The report streams (expenses_categories, expenses_clients, expenses_projects, expenses_team,
project_budget, time_clients, time_projects, time_tasks, time_team, uninvoiced) use a fundamentally
different incremental sync pattern than the entity streams. Entity streams use `updated_since` with
ISO 8601 format (`%Y-%m-%dT%H:%M:%SZ`), while report streams use `from`/`to` date parameters with a
compact date format (`%Y%m%d`) and 365-day steps.

Report streams also inject `from` and `to` as `stream_partition.start_time` and
`stream_partition.end_time` into each record via `AddFields` transformations, since the API response
does not include the date range in the data itself.

**Why this matters:** Entity streams and report streams have incompatible cursor formats and pagination
patterns. If you copy an entity stream's incremental sync config to a report stream (or vice versa),
the date filtering will silently break. Report streams cursor on `to` (end of range), not `updated_at`.

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

### Future incremental stream candidates

- **No API date filter (2 streams):** `company`, `project_budget` — these streams do not have a documented date-based filter on their list endpoints. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
- **Child streams (2 streams):** `billable_rates`, `cost_rates` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate whether these can be made incremental independently or via `incremental_dependency`.
