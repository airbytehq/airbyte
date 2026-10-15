# Reddit Ads connector notes

## Authentication

The connector exchanges a refresh token for an access token at
`https://www.reddit.com/api/v1/access_token` using the OAuth refresh-token grant and
HTTP Basic client credentials. Every request requires the configured Reddit
`User-Agent`. If Reddit rotates the refresh token, `refresh_token_updater` saves
the replacement. Do not configure an access token: Reddit access tokens expire
after about an hour and the connector mints them as needed.

## Streams and incremental sync

`ad` and `ad_group` read their Reddit v3 list endpoints and apply `modified_at`
incremental filtering client-side. Those endpoints have no server-side
`modified_at` filter, so every sync pages through the complete list. `campaign`
uses the same incremental behavior. `ad_account` reads the configured account
details with full refresh.

`campaign_report`, `ad_account_report`, `ad_group_report`, and `ad_report` post
daily requests to `/reports`, broken down by campaign, account, ad group, and ad
respectively, with UTC `date` breakdowns. They request contiguous three-day
windows with day-aligned cursor boundaries and re-read a configurable whole-day
lookback (default 7 days, bounded to 0–30) on incremental syncs. `starts_at` and
`ends_at` are built in `request_body` (the day after the window end at 00:00Z,
capped at the current hour) because the CDK's inclusive slice end would drop
each window's last day, and the shared `record_filter` drops rows dated after
the window in case Reddit treats `ends_at` as inclusive. The current UTC day's
row stays partial until a sync runs after that day ends. Report history is
clamped to 24 months because Reddit only serves that period. Spend and cost
metrics stay in Reddit's micro-units and `conversion_*_total_value` stays
multiplied by 100; the connector does not convert them. Pagination uses
`pagination.next_url` and decodes `%3D` in `page.token` before sending the next
request.

## Not implemented

- `business_account`: requires business-level scope and an ID outside the configured ad account.
- Per-event conversion reports: use separate conversion endpoints and attribution semantics.
- Country/region breakdowns: are higher-cardinality and subject to Reddit's upcoming breakdown restrictions.

## Limits and errors

The API budget is configured to Reddit's documented per-policy quotas:
`ads-campaign-management-read` 400 requests per 60 seconds for the account,
`/ads`, `/ad_groups`, and `/campaigns` endpoints
(https://ads-api.reddit.com/docs/v3/api/list-campaigns) and
`ads-reporting` 60 requests per 60 seconds for `/reports`
(https://ads-api.reddit.com/docs/v3/api/get-a-report). The budget is per
connector process, so other clients using the same Reddit credentials are not
accounted for. Concurrency defaults to 3 workers, configurable with
`num_workers` up to 10.

| Response | Classification and handling |
| --- | --- |
| API 401 | Refresh the access token and retry |
| Token endpoint 400 "Bad Request" / 401 "Unauthorized" | `config_error`; re-authenticate the refresh token or check the client ID and secret |
| API 429 | `RATE_LIMITED` with backoff before classifying ad-account 400, 403, 404, or other 400 responses |
| API 500/502/503/504 | Retry with backoff before classifying ad-account 400, 403, 404, or other 400 responses |
| API 400 ad-account error | `config_error`; check the ad account ID |
| API 403 or 404 | `config_error`; permissions or ad account are incorrect |
| Other API 400 | `system_error`; the request was invalid |

Other token-endpoint failures use the CDK's generic handling; 429/5xx responses are retried.

## Deletions

Reddit v3 list endpoints expose neither hard-deleted entities nor an
include-deleted parameter, so the connector does not emit deletions. Entities
that change status remain in the listing with their status fields. Use a full
refresh when you need to detect removals.

## Verification note

Reddit's live API behavior has not been independently tested with a Reddit Ads
account; the connector behavior described above is covered by hermetic tests.
