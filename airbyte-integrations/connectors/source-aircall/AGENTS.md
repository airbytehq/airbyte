# source-aircall: Unique Connector Behaviors

## 1. The 10,000-result cap requires date windows

Aircall limits list queries to 10,000 results. Past that it answers page 201 with HTTP 400 and puts the reason in `errors` ("Your query is limited to 10k results ..."); `message` only says `BAD_REQUEST` (airbytehq/airbyte#76489), so the filters match `errors` with a predicate. Calls and contacts read date windows through the API's `from` and `to` parameters; `window_in_days` sets the calls window (default one day) and `contacts_window_in_days` the contacts window (default 30 days). See [pagination](https://developers.aircall.io/api-references/#pagination). [List all Conversations](https://developers.aircall.io/api-references/#list-all-conversations) reports the cap as a 400 whose `troubleshoot` reads `page * per_page must not exceed 10000`, unlike the `limited to 10k results` text on calls and contacts.

- `calls` splits a rejected window in two and reads each half (`request_window_splitting`). The CDK splits at most 10 times, so a one-day window ends at about 84 seconds. Aircall rejects only page 201, so the records of every rejected window are emitted again at each split level (a day with 15,000 calls emits 10,000 of them twice). Dedup on the primary key removes them once the stream has one (1.0.0).
- `contacts` is full refresh only, so it has no cursor to split. Its windows come from a `ListPartitionRouter`, and a rejected window fails as a config error that asks for a smaller `contacts_window_in_days` (default 30). It is a separate setting because a wider calls window means more splits and more replayed calls. A single day with more than 10,000 new contacts cannot be read.

**Why this matters:** Without windows a large company never reads past the first 10,000 calls or contacts.

## 2. Cursor choices account for creation-date filters and edits

Aircall's `from` and `to` filters use creation date, not the record's update time. Calls use an incremental cursor on `started_at` with a three-day lookback: each incremental sync re-reads the calls that started in the three days before the saved cursor, which catches calls that were still in progress and edits made soon after a call. Later edits to older calls (tags, comments, `archived`) arrive only with a full refresh. Contacts and users stay full refresh because a creation-date cursor would miss edits; numbers and teams keep incremental mode for compatibility but read all records so edits are not filtered by cursor state. Conversations are the exception: their `from` and `to` filter on `last_engagement_at`, so they are incremental on that field with a three-day lookback, sorted with `order=asc` (the API defaults to `desc`), and start at 2014-01-01 because Aircall publishes no retention limit for them. `start_date` is unused and hidden in the form; configs saved before 0.5.0 keep it. See the [calls](https://developers.aircall.io/api-references/#list-all-calls), [contacts](https://developers.aircall.io/api-references/#list-all-contacts), [numbers](https://developers.aircall.io/api-references/#list-all-numbers), and [users](https://developers.aircall.io/api-references/#list-all-users-v2) endpoints.

**Why this matters:** Applying a creation-date filter or an old cursor to these streams can permanently omit records that Aircall later edits.

## 3. Calls start within Aircall's six-month retention period

Aircall retains only six months of calls. A first sync or a full refresh of calls starts at `now - 186 days` instead of `start_date`; incremental syncs start three days before the saved cursor.

**Why this matters:** Honouring a recent `start_date` would drop calls that the 0.4.x full refreshes returned.

## 4. Rate limits are shared across the company

Aircall allows 120 requests per minute per company, shared with the company's other integrations, so the budget allows 100. The reference calls `X-AircallApi-Reset` a timestamp without a unit, so `WaitUntilTimeFromHeader` reads its first 10 digits, which are epoch seconds for both seconds and milliseconds. Waits are capped at 300 seconds; a later reset is treated as a bad header and fails the attempt. The shared API budget covers v1 and v2 requests and treats a 429 as a full bucket, so a 429 costs about one minute. The configurable `num_workers` setting controls concurrency, but workers share this same company-wide limit. See [Aircall's rate-limit documentation](https://developers.aircall.io/api-references/#rate-limiting).

**Why this matters:** Increasing concurrency does not increase the company's quota and can cause all streams to be throttled together.

## 5. HTTP errors have distinct recovery behavior

| HTTP status                     | Connector behavior                                                                                             |
| :------------------------------ | :------------------------------------------------------------------------------------------------------------- |
| 401 or 403                      | Configuration error. Invalid keys answer 403; the 403 message names the URL in case the plan lacks it.         |
| 400 with the 10,000-result text | Calls split the window; contacts fail as a configuration error asking for a smaller `contacts_window_in_days`. |
| 403 with a feature-gating body  | Skip the stream or partition; see section 7.                                                                   |
| Other 400                       | CDK default: system error.                                                                                     |
| 429                             | CDK default (rate limited); waits until `X-AircallApi-Reset`.                                                  |
| 500, 502, 503, or 504           | CDK default: retried with exponential backoff, or until `X-AircallApi-Reset` when the response has it.         |

See [Aircall's error documentation](https://developers.aircall.io/api-references/#errors).

**Why this matters:** The connector distinguishes credential or query-window problems that need configuration changes from rate limits and server errors that can recover on retry.

## 6. Pagination differs by endpoint

Most Aircall v1 list endpoints use 1-based page numbering. Their first request omits `page`, and subsequent requests use `page=2`, `page=3`, and so on; the shared paginator therefore starts at page 1. `sms_templates` uses the same paginator with `per_page=100`, its documented maximum. Two other styles exist:

| Streams                          | Pagination                                                                                                                                                                   |
| :------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `campaigns`, `campaign_outcomes` | `cursor` request parameter from `meta.next_cursor`; no page numbers ([campaigns](https://developers.aircall.io/api-references/#list-all-campaigns)).                         |
| `whatsapp_templates`             | `token` request parameter from `pageInfo.nextToken`, one partition per number ([WhatsApp templates](https://developers.aircall.io/api-references/#list-whatsapp-templates)). |

**Why this matters:** Starting at page 0 sends `page=1` as the second request, which repeats the first page, and sending `page` to a cursor endpoint returns the first page forever.

## 7. Add-on endpoints are gated by a 403 with a specific body

Several endpoints return 403 when the company lacks an add-on, but a revoked API key also returns a plain `{"message": "Forbidden"}` 403 on every endpoint. Each gated stream has its own `DefaultErrorHandler` whose stream filter matches only the documented body and runs before the shared filters, so gateway 403s still fail as configuration errors.

| Streams                                     | Documented 403 body                                         | Behavior                      |
| :------------------------------------------ | :---------------------------------------------------------- | :---------------------------- |
| `conversations`, `conversation_engagements` | `The Conversations API is not enabled for this Company.`    | Skip the stream.              |
| `trackers`                                  | `Forbidden access: company cannot access this feature.`     | Skip the stream (AI Assist).  |
| `whatsapp_templates`                        | `Forbidden access: line is not configured to use whatsapp.` | Skip that number's partition. |

See [List all Conversations](https://developers.aircall.io/api-references/#list-all-conversations), [List all Trackers](https://developers.aircall.io/api-references/#list-all-trackers) and [WhatsApp templates](https://developers.aircall.io/api-references/#list-whatsapp-templates).

**Why this matters:** Skipping on any 403 would hide a revoked key as an empty sync, while failing on the gated body would break every sync for companies without the add-on.
