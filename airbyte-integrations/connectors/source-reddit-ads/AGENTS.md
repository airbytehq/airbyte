> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-reddit-ads: Unique Connector Behaviors

This connector is manifest-only; everything below lives in `manifest.yaml`. It reads Reddit's
[Ads API v3](https://ads-api.reddit.com/docs/v3/api/reddit-advertising-api) at
`https://ads-api.reddit.com/api/v3`, scoped to the configured `ad_account_id`. Reddit's
[OpenAPI spec](https://ads-api.reddit.com/api/v3/openapi.json) is the most reliable reference for
fields, filters and enums. `CONTRIBUTING.md` summarizes the same behaviors for people, and also
lists what is not implemented, how deletions behave and what has been verified live.

## 1. Token refresh needs HTTP Basic client credentials and a Reddit User-Agent, and only the refresh sends `user_agent`

The connector exchanges the refresh token for an access token at
`https://www.reddit.com/api/v1/access_token` with the OAuth refresh-token grant. Reddit
authenticates that request with HTTP Basic `client_id:client_secret`, so `refresh_request_headers`
builds the `Authorization: Basic …` header itself, and it also sends the
[User-Agent](https://ads-api.reddit.com/docs/v3/api/reddit-advertising-api#user-agents) Reddit
asks for: `{{ config.get('user_agent') or 'airbyte:source-reddit-ads:v1' }}`. That is the only
place the configured `user_agent` is used. The ads-api data requests set no `request_headers`, so
they never send it. The Cloud OAuth consent exchange (`advanced_auth`
`access_token_headers`) sends the fixed `airbyte:source-reddit-ads:v1`. If Reddit returns a new
refresh token, `refresh_token_updater` writes it back to `credentials.refresh_token`. A 400
`Bad Request` or 401 `Unauthorized` from the token endpoint is a `config_error`
(`refresh_token_error_*`). Don't configure an access token: Reddit access tokens are short-lived
and the connector mints them as needed.

**Why this matters:** Don't describe `user_agent` as affecting data-request throttling, and don't
move it into a data-request header without checking Reddit's limits first. Dropping the Basic header
or the `refresh_token_updater` breaks every sync at the token request, or after Reddit rotates the
refresh token.

## 2. Report parent IDs come from breakdowns, and Reddit allows at most three

`campaign_report`, `ad_account_report`, `ad_group_report` and `ad_report` post to
`/ad_accounts/{ad_account_id}/reports` with the shared `report_fields` list and a per-stream
`breakdowns` list, always ending in the date (`time_zone_id: GMT`). Parent IDs requested only as
`fields` did not appear in real `campaign_report` rows, so `ad_group_report` (`AD_GROUP_ID`,
`CAMPAIGN_ID`, `DATE`) and `ad_report` (`AD_ID`, `CAMPAIGN_ID`, `DATE`) add `CAMPAIGN_ID` as a
breakdown. Reddit allows at most three breakdowns, so `ad_report`'s `ad_group_id` still comes from
the `AD_GROUP_ID` field and may be empty. `ad_account_report` sets `account_id` from the configured
`ad_account_id` with `AddFields`, because the report URL is scoped to that account and the row key
of the `AD_ACCOUNT_ID` breakdown has not been observed. `campaign_report` keeps its original
lowercase breakdown values (`campaign_id`, `date`); the other three use Reddit's documented
uppercase values.

**Why this matters:** Adding a breakdown (country, region, community, keyword) changes the row grain
and the primary key, and can exceed Reddit's three-breakdown limit. Reddit also starts rejecting
some breakdown combinations on December 8, 2026
([upcoming reporting changes](https://ads-api.reddit.com/docs/v3/guides/programs/reporting/upcoming-reporting-api-changes)).
Changing `campaign_report`'s breakdown values to uppercase is untested against real rows.

## 3. Report windows are built in the request body so each window's last day isn't dropped

The report cursor (`report_incremental_sync`) slices contiguous three-day windows (`step: P3D`,
`cursor_granularity: P1D`) on day-aligned boundaries. `starts_at` is the window start at 00:00Z,
and `ends_at` is the day after the window end at 00:00Z, capped at the current hour; both are built
in `request_body` (`report_window`) instead of from the cursor's own request options, because the
CDK's inclusive slice end would drop each window's last day. The shared `report_record_filter` drops
rows dated after the window in case Reddit treats `ends_at` as inclusive. The current UTC day's row
stays partial until a sync runs after that day ends. `start_datetime` has `min_datetime` 24 months
before now, because Reddit only serves that period: an earlier `start_time` is clamped for the
report streams.

**Why this matters:** Before 0.3.0 the windows had gaps, which left dates missing in
`campaign_report`. Moving `starts_at`/`ends_at` back to cursor-driven options, or removing the
record filter, reintroduces gaps or double-counted days. Removing the 24-month clamp makes Reddit
reject the first report request of a sync with an old start date.

## 4. Report `date` is cut to `YYYY-MM-DD`, and rows without a string `date` are dropped

Each report stream sets `date` to its first ten characters with `AddFields`, so the emitted value
always matches its `format: date` and the primary key stays `YYYY-MM-DD` even if Reddit appends a
time. The record filter and the cursor's `cursor_datetime_formats` still accept a time suffix, and
legacy state values such as `2026-10-13T00:00:00Z` still parse. The record filter
(`record['date'] is string and record['date'][:10] <= stream_slice['end_time']`) also drops rows
whose `date` is null or not a string.

**Why this matters:** Rendering `[:10]` on a null fails, and the CDK would then emit the unrendered
template as `date` for every later row. Don't remove the `is string` guard, and keep the extra
`cursor_datetime_formats` so existing connections' state keeps parsing.

## 5. Spend, cost and conversion-value metrics stay in Reddit's units

Reddit returns `spend`, `cpc`, `cpv`, `ecpm` and the `conversion_*_ecpa` metrics in micro-units
(multiplied by 1,000,000), and the `conversion_*_total_value` metrics multiplied by 100. The
connector emits them unchanged. Count and micro-currency metrics are typed `integer`, and rate and
cost metrics `number`, as in Reddit's OpenAPI spec.

**Why this matters:** Converting the values in the connector would silently change every existing
row's meaning, and changing a metric's type is a breaking change (1.0.0 typed 26 report metrics and
`campaign.spend_cap` as integers).

## 6. Pagination decodes `%3D` in Reddit's page token

Every paginated stream reads `pagination.next_url`, takes its `page.token` query value and decodes
`%3D` to `=` before sending it back as the `page.token` request parameter. Pagination stops when
`next_url` is empty.

**Why this matters:** Reddit returns the token URL-encoded. Before 0.0.9 the connector passed it
back without decoding it, and every stream stopped after its first page without an error.

## 7. Two rate-limit groups with different quotas

`api_budget` mirrors Reddit's per-group [rate limits](https://ads-api.reddit.com/docs/v3/guides/quick-start/rate-limiting#rate-limit-endpoint-groups):
`ads-campaign-management-read` allows 400 requests per 60 seconds for the account, `/ads`,
`/ad_groups` and `/campaigns` endpoints
([list campaigns](https://ads-api.reddit.com/docs/v3/api/list-campaigns)), and `ads-reporting`
allows 60 requests per 60 seconds for `/reports`
([get a report](https://ads-api.reddit.com/docs/v3/api/get-a-report)). The budget is per connector
process, so other clients using the same Reddit credentials are not accounted for. Concurrency
defaults to 3 workers (`num_workers`, up to 10), and every worker shares the budget.

**Why this matters:** The report streams are bound by the 60-request quota: a first sync requests
one window per three days for 24 months, for each of the four report streams. A single budget for
every endpoint would let report requests run into 429s.

## 8. 400 responses are split by message into ad-account and request errors

The shared error handler refreshes the token and retries on 401, waits on 429 (`RATE_LIMITED`) and
retries 500, 502, 503 and 504. Only then does it classify the remaining responses:

| Response | Classification and handling |
| --- | --- |
| API 400 whose `error.message` or `error.explanation` mentions `ad_account` or `ad account` | `config_error`; check the ad account ID |
| API 403 | `config_error`; re-authorize with the `adsread` scope, as a user with access to the ad account |
| API 404 | `config_error`; the ad account ID is wrong |
| Other API 400 | `system_error`, with Reddit's message and per-field reasons |

**Why this matters:** The ad-account filter matches on message text, not a status code, so it must
stay before the generic 400 filter, and the retry filters must stay before both. Reordering them
turns a bad ad account ID into a system error, or turns a 429 into a failure.
