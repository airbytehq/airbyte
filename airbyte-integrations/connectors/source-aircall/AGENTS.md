# source-aircall: Unique Connector Behaviors

## 1. The 10,000-result cap requires date windows

Aircall limits list queries to 10,000 results. Past that it answers page 201 with HTTP 400 and puts the reason in `errors` ("Your query is limited to 10k results ..."); `message` only says `BAD_REQUEST` (airbytehq/airbyte#76489), so the filters match `errors` with a predicate. Calls and contacts read date windows through the API's `from` and `to` parameters; `window_in_days` sets the calls window (default one day) and `contacts_window_in_days` the contacts window (default 30 days). See [pagination](https://developers.aircall.io/api-references/#pagination). [List all Conversations](https://developers.aircall.io/api-references/#list-all-conversations) reports the cap as a 400 whose `troubleshoot` reads `page * per_page must not exceed 10000`, unlike the `limited to 10k results` text on calls and contacts. Conversations never reach it: they come sorted by `last_engagement_at` ascending (`order=asc`), so after 10,000 records the retriever restarts from the last record's timestamp (`pagination_reset` with `SPLIT_USING_CURSOR`) instead of asking for page 201. Their windows are a fixed 30 days (`P30D`), which keeps first-sync checkpoints frequent for the engagements fan-out, and do not read `window_in_days`. 10,000 or more conversations sharing one `last_engagement_at` second cannot be read: the reset would repeat the same slice and the CDK fails the sync. Engagements have no date filter, so a conversation with more than 10,000 engagements keeps only its newest 10,000; that 400 is ignored with a message that names the conversation, matched by the number in the body because the engagements reference words it differently.

- `calls` splits a rejected window in two and reads each half (`request_window_splitting`). The CDK splits at most 10 times, so a one-day window ends at about 84 seconds. Aircall rejects only page 201, so the records of every rejected window are emitted again at each split level (a day with 15,000 calls emits 10,000 of them twice). Dedup on the primary key removes them once the stream has one (1.0.0).
- `contacts` is full refresh only, so it has no cursor to split. Its windows come from a `ListPartitionRouter`, and a rejected window fails as a config error that asks for a smaller `contacts_window_in_days` (default 30). It is a separate setting because a wider calls window means more splits and more replayed calls. A single day with more than 10,000 new contacts cannot be read.

**Why this matters:** Without windows a large company never reads past the first 10,000 calls or contacts.

## 2. Cursor choices account for creation-date filters and edits

Aircall's `from` and `to` filters use creation date, not the record's update time. Calls use an incremental cursor on `started_at` with a three-day lookback: each incremental sync re-reads the calls that started in the three days before the saved cursor, which catches calls that were still in progress and edits made soon after a call. Later edits to older calls (tags, comments, `archived`) arrive only with a full refresh. Contacts and users stay full refresh because a creation-date cursor would miss edits; numbers and teams are full refresh only since 1.0.0: neither endpoint filters by update time, so an incremental mode re-emitted every record on every sync and added duplicates in append mode. Contacts do not use `order_by=updated_at` either: it only sorts, `from` and `to` still filter on creation date, so a read sorted by update time has nothing that keeps it under the 10,000-result cap; only the creation-date windows bound it. `campaigns`, `campaign_outcomes`, `trackers`, `webhooks`, `whatsapp_templates`, `sms_templates` and `user_numbers` stay full refresh because their endpoints have no server-side update filter and the lists are small (a few pages, or one request per number or user). Conversations are the exception: their `from` and `to` filter on `last_engagement_at`, so they are incremental on that field with a three-day lookback, sorted with `order=asc` (the API defaults to `desc`), and start at 2014-01-01 because Aircall publishes no retention limit for them. Closing, reopening or assigning a conversation does not move `last_engagement_at`, so those changes reach an incremental sync only with the next call or message, or with a full refresh. `conversation_engagements` follows its parent (`incremental_dependency`): it reads the engagements of the conversations the parent's incremental read returns, including the ones inside the three-day lookback. Its own cursor (`global_substream_cursor`) sends no request filter and drops no record; its `created_at` state only bounds slices that are never sent, and a far `end_datetime` keeps an engagement dated in the future from emptying the slices of later syncs. Every engagement of a re-read conversation is emitted again, and dedup on `id` keeps one row. A conversation that gets new activity during a read moves to the end of the `last_engagement_at` order, so the offset pages skip one row behind it; the next sync's lookback repairs that for recent conversations, and a full refresh repairs it in any case. `start_date` is unused and hidden in the form; configs saved before 0.5.0 keep it. See the [calls](https://developers.aircall.io/api-references/#list-all-calls), [contacts](https://developers.aircall.io/api-references/#list-all-contacts), [numbers](https://developers.aircall.io/api-references/#list-all-numbers), and [users](https://developers.aircall.io/api-references/#list-all-users-v2) endpoints.

**Why this matters:** Applying a creation-date filter or an old cursor to these streams can permanently omit records that Aircall later edits.

## 3. Calls start a year back to cover Aircall's call history

Aircall retains six months of calls. A first sync or full refresh starts 365 days back, covering all the call history Aircall keeps, instead of using `start_date`; incremental syncs start three days before the saved cursor.

**Why this matters:** Honouring a recent `start_date` would drop calls that the 0.4.x full refreshes returned.

## 4. Rate limits are shared across the company

Aircall allows 120 requests per minute per company, shared with the company's other integrations, so the budget allows 100. The reference calls `X-AircallApi-Reset` a timestamp without a unit, so `WaitUntilTimeFromHeader` reads its first 10 digits, which are epoch seconds for both seconds and milliseconds. Waits are capped at 300 seconds; a later reset is treated as a bad header and fails the attempt. The shared API budget covers v1 and v2 requests and treats a 429 as a full bucket, so a 429 costs about one minute. The configurable `num_workers` setting controls concurrency, but workers share this same company-wide limit. See [Aircall's rate-limit documentation](https://developers.aircall.io/api-references/#rate-limiting).

**Why this matters:** Increasing concurrency does not increase the company's quota and can cause all streams to be throttled together.

## 5. HTTP errors have distinct recovery behavior

| HTTP status                                                                | Connector behavior                                                                                                          |
| :------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------- |
| 401 or 403                                                                 | Configuration error: re-authenticate OAuth or replace the API key. The 403 message names the URL in case the plan lacks it. |
| 400 with the 10,000-result text                                            | Calls split the window; contacts fail as a configuration error asking for a smaller `contacts_window_in_days`.              |
| 403 with a feature-gating body                                             | Ignored with a message that names the URL; see section 7.                                                                   |
| Engagements: 400 that mentions 10,000, or 404 "No Conversation exists"     | Ignored with the URL; the newest 10,000 engagements of a conversation stay.                                                 |
| Other 400                                                                  | CDK default: system error.                                                                                                  |
| 429                                                                        | CDK default (rate limited); waits until `X-AircallApi-Reset`.                                                               |
| 500, 502, 503, or 504                                                      | CDK default: retried with exponential backoff, or until `X-AircallApi-Reset` when the response has it.                      |
| Conversation intelligence: 404 `NotFound`, or 403 without the gateway body | 404 ignored with the URL; 403 is a configuration error that names the option; see section 10.                               |
| Any other status                                                           | CDK default mapping: for example 404 and 405 fail as system errors, 408 and unmapped codes are retried.                     |

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

Several endpoints return 403 when the company lacks an add-on, but a revoked API key also returns a plain `{"message": "Forbidden"}` 403 on every endpoint. Each gated stream has its own `DefaultErrorHandler` whose stream filter matches only the gating text and runs before the shared filters, so gateway 403s still fail as configuration errors. An ignored request still costs one call: a company without the Conversations API spends one request per 30-day window of history (157 in 2026) on every sync that selects `conversations`, twice with `conversation_engagements`.

| Streams                                     | Documented 403 body                                                                                                                                                                    | Behavior                        |
| :------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------ |
| `conversations`, `conversation_engagements` | `The Conversations API is not enabled for this Company.` (the filter matches `not enabled`; the reference shows no full body)                                                          | Ignore the request.             |
| `trackers`                                  | `Forbidden access: company cannot access this feature.`                                                                                                                                | Ignore the request (AI Assist). |
| `whatsapp_templates`                        | `Forbidden access: line is not configured to use whatsapp.`, `line does not belong to the company.`; live responses say `Line <id> doesn't have WhatsApp capability` (key `Forbidden`) | Ignore that number.             |

See [List all Conversations](https://developers.aircall.io/api-references/#list-all-conversations), [List all Trackers](https://developers.aircall.io/api-references/#list-all-trackers) and [WhatsApp templates](https://developers.aircall.io/api-references/#list-whatsapp-templates).

**Why this matters:** Ignoring any 403 would hide a revoked key as an empty sync, while failing on the gated body would break every sync for companies without the add-on.

## 8. Primary keys follow Aircall's documented identifiers

`calls`, `contacts`, `numbers`, `teams` and `users` use `id`. `webhooks` uses `webhook_id`, the UUID Aircall documents as the webhook's identifier; Aircall describes the integer `id` as the legacy identifier. `company` has no primary key because `/company` returns one object with no identifier field ([company](https://developers.aircall.io/api-references/#company), [webhooks](https://developers.aircall.io/api-references/#webhook)).

**Why this matters:** Do not add a primary key to `company`; there is no field that identifies it, and it always has exactly one record.

## 9. Ids and epoch times stay `number`

The reference calls ids and epoch fields (`calls.id`, `started_at`, `answered_at`, `ended_at`, `duration`, the v1 `id` fields) integers, but the manifest declares them `number`. Every value fits, Snowflake keys on `FLOAT` are exact below 2^53, and changing a declared type is breaking, so 1.0.0 changed only the fields whose declared type misrepresented the value: objects stored as text, the integer `priority`, and ISO timestamps declared as plain strings. `campaigns.calling_hours.slots` `from_time` and `to_time` stay plain strings: Aircall sends 24-hour `HH:MM` without seconds, which no Airbyte time type accepts.

**Why this matters:** Retyping these fields later needs another major release, and `started_at` is the `calls` cursor.

## 10. Conversation intelligence is opt-in and costs one request per call

The six AI streams (`call_transcriptions`, `call_sentiments`, `call_topics`, `call_summaries`, `call_action_items`, `call_playbook_results`) sit in a `ConditionalStreams` block on `include_conversation_intelligence` (default `false`), so they are not discovered unless the option is on. They need the AI Assist or AI Assist Pro package ([Conversation Intelligence](https://developers.aircall.io/api-references/#conversation-intelligence-overview)); playbook results need AI Assist Pro. Their requester has its own `DefaultErrorHandler`, filters in this order:

1. The gateway body `{"message": "Forbidden"}` that a revoked API key gets on every endpoint keeps the shared credentials message (`gateway_forbidden`, the shared `forbidden` filter matched by body instead of status).
2. Any other 403 fails as a configuration error (`conversation_intelligence_not_enabled`) that names the package, an active and verified company (the only 403s the reference documents for these endpoints), and the fixes: deselect the stream, or turn the option off and refresh the source schema. Turning the option off alone is not enough: a catalog that still selects the streams gets an `INCOMPLETE` status for each of them. `call_playbook_results` overrides this filter with `playbook_results_not_enabled`, which names AI Assist Pro and says to deselect that stream, since a company with AI Assist only can still read the other five. It fails rather than skips: the option is an explicit request for this data, and a skip would spend one request per call for nothing. The gateway carve-out is not verified live: if Aircall answers a company without the package with the bare gateway body, the credentials message still says to check the plan.
3. A 404 is ignored with the URL (`call_result_not_found`) only when it carries Aircall's body `{"error": "NotFound", "troubleshoot": "<result> not found"}`: all six routes answer that for a call without a result, such as a missed call (checked live on 2026-11-11). A 404 with any other body, such as a retired or renamed route, fails instead of skipping every call.

`call_id` is added from the partition: action items carry it only at the response root, and the reference types it as a string while its samples show integers. `call_action_items` is keyed on `call_id` and `id`, because the action item `id` looks unique only within a call (inferred from the reference sample, whose items on one call have ids 1 and 2).

**Why this matters:** Turning the option on without the package must fail with a message that says what to change, while a revoked key must still read as a credentials problem.

## 11. Conversation intelligence fans out over the calls read

Each AI stream is a `SubstreamPartitionRouter` child of `calls` with `incremental_dependency`, so it reads the calls of the calls stream's own window (365 days on a first sync or full refresh, three days before the saved cursor on an incremental sync) and makes one request per call. The parent's `started_at` comes through `extra_fields` and is added as `call_started_at`, the child cursor every result has (sentiments have no timestamp, and the other results do not share one). It has no `value_type`: with one, a call without `started_at` would get the string `"None"`; without it the field is left out. Like `conversation_engagements`, the child cursor is a `global_substream_cursor` that sends no request filter and drops no record, with a far `end_datetime` so a call dated in the future cannot empty later slices. Results edited after the call (action items carry `updated_at`) reach an incremental sync only while the call is inside the parent's three-day lookback. The CDK caches parent responses, so the calls pages are reused across the selected streams within a sync when their windows match. The cost is one request per call per stream on every sync, and all streams share one 100 requests per minute budget: a company with 1,000 calls a day and daily syncs spends about 4,000 requests per stream per sync (40 minutes), 4 hours for all six, and about 180 hours for all six on the first sync.

**Why this matters:** The fan-out shares the company's 120 requests per minute with every other integration, which is why the streams are opt-in and the docs spell out the cost.

## 12. Two authentication modes; OAuth needs a Technology Partner app

`credentials` is a `oneOf` with OAuth 2.0 first and the API key pair second, selected by `credentials.auth_type` through a `SelectiveAuthenticator`. Aircall issues OAuth client credentials only to [Technology Partner apps](https://developers.aircall.io/api-references/#oauth-technology-partners). The consent URL is `https://dashboard.aircall.io/oauth/authorize` with `scope=public_api`, and the code is exchanged at `POST https://api.aircall.io/v1/oauth/token` with a JSON body. The returned `access_token` does not expire and no refresh token is issued, so OAuth uses a `BearerAuthenticator` and `advanced_auth` extracts only `access_token`. The API key option uses HTTP Basic with `api_id` and `api_token`. The modes return the same data except `webhooks`: with OAuth, Aircall returns only the webhooks created with the OAuth token ([Webhook API overview](https://developers.aircall.io/api-references/#webhook-api-overview)), so the stream is usually empty. Every requester, including the conversation intelligence requester and `user_numbers` on `/v2`, `$ref`s the base requester and so inherits the `SelectiveAuthenticator`. A config migration moves the top-level `api_id` and `api_token` of configs saved before 1.2.0 into `credentials` with `auth_type: api_key`, and removes the top-level keys whenever `credentials.auth_type` is set.

**Why this matters:** Aircall answers an invalid bearer token with 403 and the token never expires, so a 401 or 403 under OAuth needs re-authentication, not a refresh. Removing the migration breaks every API key connection created before 1.2.0, and 1.1.0 and earlier cannot read a migrated config, so roll forward instead of pinning 1.1.0; `releases.unsafeDowngrades` in `metadata.yaml` records this for rollouts.
