# source-aircall: Unique Connector Behaviors

## 1. The 10,000-result cap requires date windows

Aircall limits list queries to 10,000 results. Calls, contacts and conversations are split into date windows to avoid this cap; `window_in_days` controls their size, defaulting to one day for calls and 30 days for contacts and conversations. The requests use the API's `from` and `to` parameters, and pagination is documented in [Aircall's API reference](https://developer.aircall.io/api-references/#pagination). [List all Conversations](https://developer.aircall.io/api-references/#list-all-conversations) reports the cap as a 400 whose `troubleshoot` reads `page * per_page must not exceed 10000`, unlike the `limited to 10k results` message on calls and contacts.

**Why this matters:** A large window can make Aircall reject a sync before pagination can retrieve the remaining results. Reduce `window_in_days` to keep each request below the result limit.

## 2. Cursor choices account for creation-date filters and edits

Aircall's `from` and `to` filters use creation date, not the record's update time. Calls use an incremental cursor on `started_at` with a three-day lookback so edits to tags, comments, and archived status are re-read. Contacts and users stay full refresh because a creation-date cursor would miss edits; Numbers and teams are full refresh only since 1.0.0: neither endpoint filters by update time, so an incremental mode would re-emit every record on every sync and add duplicates in append mode. Conversations are the exception: their `from` and `to` filter on `last_engagement_at`, so they are incremental on that field with a three-day lookback, sorted with `order=asc` (the API defaults to `desc`), and start at 2014-01-01 because Aircall publishes no retention limit for them. `start_date` is unused. See the [calls](https://developer.aircall.io/api-references/#list-all-calls), [contacts](https://developer.aircall.io/api-references/#list-all-contacts), [numbers](https://developer.aircall.io/api-references/#list-all-numbers), and [users](https://developer.aircall.io/api-references/#list-all-users-v2) endpoints.

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
| 403 with a feature-gating body     | Skip the stream or partition; see section 7.          |
| 400 with the 10,000-result message | Configuration error; lower `window_in_days`.          |
| 429                                | Rate limited; wait for Aircall's reset time.          |
| 500, 502, 503, or 504              | Retry the request.                                    |

See [Aircall's error documentation](https://developer.aircall.io/api-references/#errors).

**Why this matters:** The connector distinguishes credential or query-window problems that need configuration changes from rate limits and server errors that can recover on retry.

## 6. Pagination differs by endpoint

Most Aircall v1 list endpoints use 1-based page numbering. Their first request omits `page`, and subsequent requests use `page=2`, `page=3`, and so on; the shared paginator therefore starts at page 1. `sms_templates` uses the same paginator with `per_page=100`, its documented maximum. Two other styles exist:

| Streams                          | Pagination                                                                                                                                                                  |
| :------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `campaigns`, `campaign_outcomes` | `cursor` request parameter from `meta.next_cursor`; no page numbers ([campaigns](https://developer.aircall.io/api-references/#list-all-campaigns)).                         |
| `whatsapp_templates`             | `token` request parameter from `pageInfo.nextToken`, one partition per number ([WhatsApp templates](https://developer.aircall.io/api-references/#list-whatsapp-templates)). |

**Why this matters:** Starting at page 0 or repeating page 1 can duplicate the first page and skip records, and sending `page` to a cursor endpoint returns the first page forever.

## 7. Add-on endpoints are gated by a 403 with a specific body

Several endpoints return 403 when the company lacks an add-on, but a revoked API key also returns a plain `{"message": "Forbidden"}` 403 on every endpoint. Each gated stream has its own `DefaultErrorHandler` whose stream filter matches only the documented body and runs before the shared filters, so gateway 403s still fail as configuration errors.

| Streams                                     | Documented 403 body                                         | Behavior                      |
| :------------------------------------------ | :---------------------------------------------------------- | :---------------------------- |
| `conversations`, `conversation_engagements` | `The Conversations API is not enabled for this Company.`    | Skip the stream.              |
| `trackers`                                  | `Forbidden access: company cannot access this feature.`     | Skip the stream (AI Assist).  |
| `whatsapp_templates`                        | `Forbidden access: line is not configured to use whatsapp.` | Skip that number's partition. |

See [List all Conversations](https://developer.aircall.io/api-references/#list-all-conversations), [List all Trackers](https://developer.aircall.io/api-references/#list-all-trackers) and [WhatsApp templates](https://developer.aircall.io/api-references/#list-whatsapp-templates).

**Why this matters:** Skipping on any 403 would hide a revoked key as an empty sync, while failing on the gated body would break every sync for companies without the add-on.

## 8. Primary keys follow Aircall's documented identifiers

`calls`, `contacts`, `numbers`, `teams` and `users` use `id`. `webhooks` uses `webhook_id`, the UUID Aircall documents as the webhook's identifier; Aircall describes the integer `id` as the legacy identifier. `company` has no primary key because `/company` returns one object with no identifier field ([company](https://developer.aircall.io/api-references/#company), [webhooks](https://developer.aircall.io/api-references/#webhook)).

**Why this matters:** Do not add a primary key to `company`; there is no field that identifies it, and it always has exactly one record.
