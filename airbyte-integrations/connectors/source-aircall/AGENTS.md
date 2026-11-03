# source-aircall: Unique Connector Behaviors

## 1. The 10,000-result cap requires date windows

Aircall limits list queries to 10,000 results. Calls and contacts are split into date windows to avoid this cap; `window_in_days` controls their size, defaulting to one day for calls and 30 days for contacts. The requests use the API's `from` and `to` parameters, and pagination is documented in [Aircall's API reference](https://developer.aircall.io/api-references/#pagination).

**Why this matters:** A large window can make Aircall reject a sync before pagination can retrieve the remaining results. Reduce `window_in_days` to keep each request below the result limit.

## 2. Cursor choices account for creation-date filters and edits

Aircall's `from` and `to` filters use creation date, not the record's update time. Calls use an incremental cursor on `started_at` with a three-day lookback so edits to tags, comments, and archived status are re-read. Contacts and users stay full refresh because a creation-date cursor would miss edits; numbers and teams keep incremental mode for compatibility but read all records so edits are not filtered by cursor state. `start_date` is unused. See the [calls](https://developer.aircall.io/api-references/#list-all-calls), [contacts](https://developer.aircall.io/api-references/#list-all-contacts), [numbers](https://developer.aircall.io/api-references/#list-all-numbers), and [users](https://developer.aircall.io/api-references/#list-all-users-v2) endpoints.

**Why this matters:** Applying a creation-date filter or an old cursor to these streams can permanently omit records that Aircall later edits.

## 3. Calls start within Aircall's six-month retention period

Aircall retains only six months of calls. Calls therefore start at `now - 186 days` rather than using `start_date`, which could exclude calls returned by earlier full-refresh syncs.

**Why this matters:** Using a configured historical start date can cause call data to disappear from subsequent syncs even though Aircall no longer retains that history.

## 4. Rate limits are shared across the company

Aircall allows 120 requests per minute per company. `X-AircallApi-Reset` is a UNIX timestamp, so throttled requests use `WaitUntilTimeFromHeader`; the shared API budget accounts for v1 and v2 requests. The configurable `num_workers` setting controls concurrency, but workers share this same company-wide limit. See [Aircall's rate-limit documentation](https://developer.aircall.io/api-references/#rate-limiting).

**Why this matters:** Increasing concurrency does not increase the company's quota and can cause all streams to be throttled together.

## 5. HTTP errors have distinct recovery behavior

| HTTP status                        | Connector behavior                                    |
| :--------------------------------- | :---------------------------------------------------- |
| 401 or 403                         | Configuration error; update the API ID and API token. |
| 400 with the 10,000-result message | Configuration error; lower `window_in_days`.          |
| 429                                | Rate limited; wait for Aircall's reset time.          |
| 500, 502, 503, or 504              | Retry the request.                                    |

See [Aircall's error documentation](https://developer.aircall.io/api-references/#errors).

**Why this matters:** The connector distinguishes credential or query-window problems that need configuration changes from rate limits and server errors that can recover on retry.

## 6. V1 page numbering starts at one

Aircall v1 list endpoints use 1-based page numbering. Their first request omits `page`, and subsequent requests use `page=2`, `page=3`, and so on; the shared paginator therefore starts at page 1.

**Why this matters:** Starting at page 0 or repeating page 1 can duplicate the first page and skip records.
