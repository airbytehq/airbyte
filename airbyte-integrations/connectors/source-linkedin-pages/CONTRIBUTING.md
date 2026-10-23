# Contributing to source-linkedin-pages

Follow the connector-specific behavior and maintenance guidance in [AGENTS.md](AGENTS.md).

## 1. Pinned LinkedIn API version

Keep every requester on the same current `Linkedin-Version`; LinkedIn sunsets versions on an approximately annual cadence. See [AGENTS.md](AGENTS.md#1-pinned-linkedin-api-version) and the versioning link there.

## 2. Time-bound statistics windows and cursors

Preserve the 12-month/2-day UTC availability window and midnight-aligned `DAY` windows for both time-bound streams. See [AGENTS.md](AGENTS.md#2-time-bound-statistics-windows-and-cursors).

## 3. LinkedIn rate limits

LinkedIn does not publish a fixed daily per-application limit, so this connector intentionally has no `api_budget`; `429` responses retry with bounded backoff. See [AGENTS.md](AGENTS.md#3-linkedin-rate-limits).

## 4. Lifetime aggregate streams

Keep the four cursorless lifetime aggregate streams full refresh. See [AGENTS.md](AGENTS.md#4-lifetime-aggregate-streams).
