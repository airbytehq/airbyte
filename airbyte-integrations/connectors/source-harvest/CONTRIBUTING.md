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
