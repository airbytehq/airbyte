> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-recharge: Unique Connector Behaviors

## 1. The `events` Stream Is Hard-Capped to a Rolling 7-Day Window

Recharge's [`GET /events`](https://developer.rechargepayments.com/2021-11/events/events_list) endpoint is
documented as "limited to events that occurred in the last 7 days", and it rejects any request whose
`created_at_min` falls outside that window with a `422` carrying
`{"errors":{"_schema":["created_at_min must be less than 7 days ago"]}}`. Every other stream's
`updated_at_min` accepts an arbitrarily old date.

`base_incremental_events_stream` therefore puts a `min_datetime` floor of `day_delta(-7)` on its
`MinMaxDatetime` start date, so the value actually sent as `created_at_min` is never older than seven
days. The floor is evaluated per slice and applies to **both** inputs to the cursor: a `start_date`
from config *and* a saved state cursor restored on an incremental run. A connection configured with a
`start_date` of 2020 and a connection resuming `events` after a two-week pause therefore issue the
same request — `created_at_min = now - 7d`.

Two consequences follow from this being an API ceiling rather than a connector preference. The
endpoint cannot serve older events to any client, so the clamp does not drop records that were
otherwise retrievable. And because the stream then advances its cursor past the skipped interval and
reports success, a truncated resume is not distinguishable from a clean one in the sync log. `events`
has no `lookback_window`: a lookback cannot widen the window
past the floor, so `lookback_window_days` has no effect on this stream.

**Why this matters:** Removing the `min_datetime` floor, moving it past `-7`, or lifting it onto the
shared `base_incremental_stream` definition reintroduces the `422`. That failure surfaces as a
`config_error` and aborts the **entire sync** rather than just the `events` stream, so a change that
looks scoped to one stream takes down all of them. The `-7` value is itself deliberate: live testing
found the real enforced cutoff nearer 8 days, giving `-7` close to a day of margin against clock and
request-timing skew — but that margin is not part of Recharge's documented promise and must not be
spent by pushing the floor toward `-8`.

## 2. Cursor Pages Omit Sorting and Date Filters

Recharge's [cursor pagination](https://developer.rechargepayments.com/2021-11/) accepts only `cursor`
and `limit` on subsequent pages. Incremental streams using `updated_at` send
`sort_by=updated_at-asc` on their first page so records arrive in cursor order. The requester expression
`{{ 'updated_at-asc' if not next_page_token else '' }}` renders an empty value on cursor pages, which
the CDK drops from request parameters. Combined with
`ignore_stream_slicer_parameters_on_paginated_requests: true`, this removes both sorting and date
filters after the first page. Each new slice starts with its own filters and sorting again.

**Why this matters:** Making `sort_by` unconditional or retaining date filters on cursor pages sends
parameters Recharge rejects. Do not apply this omission to page-number pagination: the deprecated
orders API needs filters and sorting on every page.

## 3. Orders Switches API Versions and Keeps a Naive Cursor

Two `ConditionalStreams` entries select exactly one `orders` stream: `use_orders_deprecated_api: true`
uses `2021-01`, while false or a missing key uses `2021-11`. The setup form's spec default is true;
that does not change the missing-key runtime behavior. Each conditional child explicitly declares
`type: DeclarativeStream` so manifest schema validation succeeds.

Both variants use 30-day slices with one-second granularity and inclusive lower bounds. The
[2021-01 orders API](https://developer.rechargepayments.com/2021-01/orders) returns naive US-Eastern
`updated_at` values, so requests and state retain `%Y-%m-%d %H:%M:%S` rather than converting them to
UTC. Cursor parsing also accepts legacy ISO timestamps with `+00:00` offsets. Neither variant uses
`lookback_window_days`. The deprecated variant uses page numbers, restarting at page 1 (no `page`
parameter) in each slice and retaining date filters and sorting on every page; the modern variant
uses cursors and omits those parameters after the first page.

**Why this matters:** Collapsing the variants can change the API selected by existing configurations
or break pagination. Adding a second to the saved cursor skips boundary records; carrying page
numbers across slices skips orders. Treating naive US-Eastern timestamps as UTC shifts the requested
window rather than preserving the API's time convention.
