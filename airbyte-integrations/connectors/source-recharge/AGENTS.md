> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-recharge: Unique Connector Behaviors

## 1. The `events` Stream Is Hard-Capped to a Rolling 7-Day Window

Recharge's [`GET /events`](https://developer.rechargepayments.com/2021-11/events/events_list) endpoint is
documented as "limited to events that occurred in the last 7 days", and it rejects any request whose
`created_at_min` falls outside that window with a `422` carrying
`{"errors":{"_schema":["created_at_min must be less than 7 days ago"]}}`. Every other stream's
`updated_at_min` accepts an arbitrarily old date.

`base_incremental_events_stream` therefore puts a `min_datetime` floor of `day_delta(-7)` on its
`MinMaxDatetime` start date and re-applies it in the requester's `created_at_min` expression, so the
value sent is never older than seven days at request time. SDM evaluates `start_datetime` once, when
it builds the streams at sync start, and `events` can be requested hours later. The floor applies to
**both** inputs to the cursor: a `start_date`
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
`system_error` after 11 requests with the manifest-only connector's CDK 7.46.0, failing `events`.
The deprecated orders validation handler deliberately does not apply to `events`.
The `-7` value is itself deliberate: live testing
found the real enforced cutoff nearer 8 days, giving `-7` close to a day of margin against clock and
request-timing skew — but that margin is not part of Recharge's documented promise and must not be
spent by pushing the floor toward `-8`.

## 2. Cursor Pages Omit Sorting and Date Filters

Recharge's [2021-01 cursor pagination docs](https://developer.rechargepayments.com/2021-01/cursor_pagination)
state that "the only compatible filter allowed to be used with cursors is limit"; the 2021-11 reference
pairs `cursor` only with `limit` in its examples. Incremental streams using `updated_at` send
`sort_by=updated_at-asc` on their first page so records arrive in cursor order. The requester expression
`{{ 'updated_at-asc' if not next_page_token else '' }}` renders an empty value on cursor pages, which
the CDK drops from request parameters. Combined with
`ignore_stream_slicer_parameters_on_paginated_requests: true`, this removes both sorting and date
filters after the first page. Each new slice starts with its own filters and sorting again.
The shared `updated_at` cursor re-reads `lookback_window_days` plus one hour before the saved cursor
to capture updates committed while the previous sync was running; orders and events do not use this margin.

**Why this matters:** Making `sort_by` unconditional or retaining date filters on cursor pages sends
parameters Recharge documents as incompatible with a cursor (whether it rejects or ignores them is not
documented). This also applies to the deprecated orders API, which follows cursor links to avoid
the 2021-01 API's 100-page limit. Other deprecated streams still use page-number pagination.

## 3. Orders Switches API Versions and Keeps a Naive Cursor

Two `ConditionalStreams` entries select exactly one `orders` stream: `use_orders_deprecated_api: true`
uses `2021-01`, while false or a missing key uses `2021-11`. The setup form's spec default is true;
that does not change the missing-key runtime behavior. Each conditional child explicitly declares
`type: DeclarativeStream` so manifest schema validation succeeds.

Both variants use 30-day slices with one-second granularity and resume with `updated_at_min` equal
to the saved cursor. Recharge documents only "updated after the given date", so treating that bound
as inclusive is the connector's assumption, not a documented contract. The
[2021-01 orders API](https://developer.rechargepayments.com/2021-01/orders) returns naive
`updated_at` values and documents no timezone; comparing the same orders across API versions, in
fixtures and in production state, shows they are US-Eastern wall-clock time. Requests and state
therefore retain `%Y-%m-%d %H:%M:%S` rather than converting them to UTC. Cursor parsing also accepts
legacy ISO timestamps with `+00:00` offsets. Neither variant uses
`lookback_window_days`. Both variants use cursor pagination and omit date filters and sorting after
the first page of each slice. The deprecated variant follows the response's `Link` next URL using
`page_info`, with a URL-encoded `next_cursor` body fallback. That URL already encodes the initial
filters; only `limit` is compatible with cursor requests. Each slice restarts without a cursor,
with its own date filters and sorting. Page-number pagination would fail above page 100 (25,000
orders per slice) with a 422 response.

**Why this matters:** Collapsing the variants can change the API selected by existing configurations
or break pagination. Adding a second to the saved cursor skips boundary records; carrying cursors
across slices skips orders. Treating naive US-Eastern timestamps as UTC shifts the requested
window rather than preserving the API's time convention.

## 4. Deprecated Orders Validation Errors Fail Fast

The 2021-01 `orders` requester fails on HTTP 422 without retrying. Recharge's known
`errors.page` message about exceeding 100 pages gets a fixed message naming that limit;
other 422 bodies get a fixed invalid-orders-request message. Both are `system_error`,
not configuration errors, and neither user-facing message includes the request URL or
raw response. This handler is scoped to deprecated orders, not the shared requester.

**Why this matters:** The shared handler has no 422 mapping, so CDK 7.46.0 otherwise retries
the same rejected request ten times and exposes the URL and response in the final error.
Keep the 429 retry filter when overriding the filter list, and do not broaden this override
to `events` or ignore rejected requests, which would hide incomplete data.
