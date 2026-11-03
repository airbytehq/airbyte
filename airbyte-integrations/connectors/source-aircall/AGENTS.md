# source-aircall: Unique Connector Behaviors

## 1. The 10,000-result cap requires date windows

Aircall limits list queries to 10,000 results. Past that it answers page 201 with HTTP 400 and puts the reason in `errors` ("Your query is limited to 10k results ..."); `message` only says `BAD_REQUEST` (airbytehq/airbyte#76489), so the filters match `errors` with a predicate. Calls and contacts read date windows through the API's `from` and `to` parameters; `window_in_days` sets their size, defaulting to one day for calls and 30 days for contacts. See [pagination](https://developers.aircall.io/api-references/#pagination).

- `calls` splits a rejected window in two and reads each half (`request_window_splitting`). The CDK splits at most 10 times, so a one-day window ends at about 84 seconds. Records the oversized window emitted before the rejection are emitted again; dedup on the primary key removes them once the stream has one.
- `contacts` is full refresh only, so it has no cursor to split. Its windows come from a `ListPartitionRouter`, and a rejected window fails as a config error that asks for a smaller `window_in_days`. A single day with more than 10,000 new contacts cannot be read.

**Why this matters:** Without windows a large company never reads past the first 10,000 calls or contacts.

## 2. Cursor choices account for creation-date filters and edits

Aircall's `from` and `to` filters use creation date, not the record's update time. Calls use an incremental cursor on `started_at` with a three-day lookback: each incremental sync re-reads the calls that started in the three days before the saved cursor, which catches calls that were still in progress and edits made soon after a call. Later edits to older calls (tags, comments, `archived`) arrive only with a full refresh. Contacts and users stay full refresh because a creation-date cursor would miss edits; numbers and teams keep incremental mode for compatibility but read all records so edits are not filtered by cursor state. `start_date` is unused and hidden in the form; configs saved before 0.5.0 keep it. See the [calls](https://developers.aircall.io/api-references/#list-all-calls), [contacts](https://developers.aircall.io/api-references/#list-all-contacts), [numbers](https://developers.aircall.io/api-references/#list-all-numbers), and [users](https://developers.aircall.io/api-references/#list-all-users-v2) endpoints.

**Why this matters:** Applying a creation-date filter or an old cursor to these streams can permanently omit records that Aircall later edits.

## 3. Calls start within Aircall's six-month retention period

Aircall retains only six months of calls. A first sync or a full refresh of calls starts at `now - 186 days` instead of `start_date`; incremental syncs start three days before the saved cursor.

**Why this matters:** Honouring a recent `start_date` would drop calls that the 0.4.x full refreshes returned.

## 4. Rate limits are shared across the company

Aircall allows 120 requests per minute per company. The reference calls `X-AircallApi-Reset` a timestamp without a unit, so `WaitUntilTimeFromHeader` reads its first 10 digits, which are epoch seconds for both seconds and milliseconds. The shared API budget covers v1 and v2 requests and treats a 429 as a full bucket, so a 429 costs about one minute. The configurable `num_workers` setting controls concurrency, but workers share this same company-wide limit. See [Aircall's rate-limit documentation](https://developers.aircall.io/api-references/#rate-limiting).

**Why this matters:** Increasing concurrency does not increase the company's quota and can cause all streams to be throttled together.

## 5. HTTP errors have distinct recovery behavior

| HTTP status                     | Connector behavior                                                                                     |
| :------------------------------ | :----------------------------------------------------------------------------------------------------- |
| 401 or 403                      | Configuration error. Invalid keys answer 403; the 403 message names the URL in case the plan lacks it. |
| 400 with the 10,000-result text | Calls split the window; contacts fail as a configuration error asking for a smaller `window_in_days`.  |
| Other 400                       | CDK default: system error.                                                                             |
| 429                             | CDK default (rate limited); waits until `X-AircallApi-Reset`.                                          |
| 500, 502, 503, or 504           | CDK default: retried with exponential backoff.                                                         |

See [Aircall's error documentation](https://developers.aircall.io/api-references/#errors).

**Why this matters:** The connector distinguishes credential or query-window problems that need configuration changes from rate limits and server errors that can recover on retry.

## 6. V1 page numbering starts at one

Aircall v1 list endpoints use 1-based page numbering. Their first request omits `page`, and subsequent requests use `page=2`, `page=3`, and so on; the shared paginator therefore starts at page 1.

**Why this matters:** Starting at page 0 sends `page=1` as the second request, which repeats the first page.
