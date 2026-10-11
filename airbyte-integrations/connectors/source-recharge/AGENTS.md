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
is also the only incremental stream carrying no `lookback_window`: a lookback cannot widen the window
past the floor, so `lookback_window_days` has no effect on this stream.

**Why this matters:** Removing the `min_datetime` floor, moving it past `-7`, or lifting it onto the
shared `base_incremental_stream` definition reintroduces the `422`. That failure surfaces as a
`config_error` and aborts the **entire sync** rather than just the `events` stream, so a change that
looks scoped to one stream takes down all of them. The `-7` value is itself deliberate: live testing
found the real enforced cutoff nearer 8 days, giving `-7` close to a day of margin against clock and
request-timing skew — but that margin is not part of Recharge's documented promise and must not be
spent by pushing the floor toward `-8`.
