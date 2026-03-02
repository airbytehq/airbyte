# source-harvest: Unique Connector Behaviors

This document describes the biggest non-obvious gotchas in `source-harvest` that deviate from standard
declarative connector patterns. Read this before making changes to the connector.

---

## 1. Harvest-Account-Id Header Required on Every Request

Every API request to Harvest requires a `Harvest-Account-Id` header containing the customer's account
ID. This is not part of authentication -- it is a separate routing header that Harvest uses to identify
which account's data to return. The header is injected on every stream's requester via
`request_headers: Harvest-Account-Id: "{{ config['account_id'] }}"`.

**Why this matters:** If you add a new stream and forget the `Harvest-Account-Id` header, the API will
return a 404 or data from the wrong account context. This header must be present on every single
request, even though it looks like it should be part of the authenticator. It is separate from auth
because a single OAuth token can have access to multiple Harvest accounts.

---

## 2. Link-Based Cursor Pagination

Harvest uses a non-standard pagination approach where the next page URL is embedded in the response
body under `links.next` rather than using standard offset/page parameters or response headers. The
paginator is configured as `CursorPagination` with `RequestPath` as the page token option, meaning the
entire next-page URL from `response.links.next` replaces the request path on subsequent pages.

**Why this matters:** This is not offset-based or token-based pagination in the usual sense. The
`cursor_value` extracts a full URL from `response.get("links", {}).get("next", {})`, and the
`stop_condition` checks for its absence. If you try to switch to `OffsetIncrement` or standard cursor
pagination, it will break because Harvest's API does not support `page` or `offset` parameters on most
endpoints.

---

## 3. Graceful Degradation on 401/403/404

Every stream in source-harvest uses a `CompositeErrorHandler` that **ignores** (rather than fails on)
HTTP 401, 403, and 404 responses. This means if a user's credentials lack permission to access a
specific stream, or the account ID is incorrect for a particular resource, that stream silently produces
zero records instead of failing the entire sync.

**Why this matters:** This is an intentional design choice because Harvest's permission model is
granular -- a user may have access to time entries but not invoices, for example. However, it also means
that misconfigured credentials or an incorrect account ID will not produce an error; the sync will
succeed with empty streams, which can be confusing to diagnose.

---

## 4. Report Streams Use Date-Range Slicing with Different Cursor Format

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

---

## 5. WaitTimeFromHeader Backoff Strategy

Harvest's API returns a `Retry-After` header on rate-limited responses, and the connector uses
`WaitTimeFromHeader` as its primary backoff strategy rather than exponential backoff. This is the first
handler in the `CompositeErrorHandler` chain, meaning it takes precedence over the 401/403/404 IGNORE
handlers.

Harvest documents a rate limit of 100 requests per 15 seconds per token
(https://help.getharvest.com/api-v2/introduction/overview/general/#rate-limiting).

**Why this matters:** The `Retry-After` header tells the connector exactly how long to wait, so the
connector will pause for precisely the time Harvest specifies. If you add a second backoff strategy
(like `ExponentialBackoffStrategy`), make sure it comes after `WaitTimeFromHeader` in the chain so the
API-specified wait time is honored first.

---

## 6. Substream Patterns for Messages, Payments, and Rates

Several streams are implemented as substreams that partition by parent entity ID:
- `estimate_messages` partitions by estimate ID
- `invoice_messages` and `invoice_payments` partition by invoice ID
- `project_assignments` and `billable_rates`/`cost_rates` partition by user or project ID

Each substream injects the parent ID into records via `AddFields` transformations (e.g.,
`parent_id: "{{stream_partition.id}}"`).

**Why this matters:** These substreams make one API call per parent entity, so the total number of
requests scales linearly with the number of parent records. A Harvest account with 10,000 invoices will
generate 10,000 additional API calls just for `invoice_messages`. Combined with the `Retry-After`
backoff, large accounts may experience very slow syncs for substreams.
