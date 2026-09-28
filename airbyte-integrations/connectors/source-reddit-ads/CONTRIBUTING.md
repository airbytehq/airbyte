# Reddit Ads connector notes

## Authentication

The connector exchanges a refresh token for an access token at
`https://www.reddit.com/api/v1/access_token` using the OAuth refresh-token grant and
HTTP Basic client credentials. Every request requires the configured Reddit
`User-Agent`. If Reddit rotates the refresh token, `refresh_token_updater` saves
the replacement. Do not configure an access token: Reddit access tokens expire
after about an hour and the connector mints them as needed.

## Streams and incremental sync

`ad` and `campaign` read the full Reddit v3 list endpoints and apply
`modified_at` incremental filtering client-side. Those endpoints have no
server-side `modified_at` filter, so every sync pages through the complete list.

`campaign_report` posts campaign-level requests to `/reports`, with `campaign_id`
and `date` breakdowns in GMT. It requests P3D slices, uses a PT7H lookback and
P1D cursor granularity, and clamps report history to 24 months because Reddit
only serves that period. Metric money fields are kept in the micro-units Reddit
returns; the connector does not convert them. Pagination uses
`pagination.next_url` and decodes `%3D` in `page.token` before sending the next
request.

## Limits and errors

The API budget models Reddit's published per-process limits: 400 calls per
minute for ads/campaign reads and 60 calls per minute for reports. Concurrency
defaults to 3 workers, configurable with `num_workers` up to 10.

| Response | Classification and handling |
| --- | --- |
| API 401 | Refresh the access token and retry |
| Token 400 `invalid_grant` | `config_error`; the refresh token was rejected |
| API 400 ad-account error | `config_error`; check the ad account ID |
| Other API 400 | `system_error`; the request was invalid |
| API 403 or 404 | `config_error`; permissions or ad account are incorrect |
| API 429 or 5xx | Retry with backoff |

## Deletions

Reddit v3 list endpoints expose neither hard-deleted entities nor an
include-deleted parameter, so the connector does not emit deletions. Entities
that change status remain in the listing with their status fields. Use a full
refresh when you need to detect removals.

## Verification note

Reddit's live API behavior has not been independently tested with a Reddit Ads
account; the connector behavior described above is covered by hermetic tests.
