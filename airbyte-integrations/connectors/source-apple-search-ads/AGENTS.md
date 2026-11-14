# source-apple-search-ads: Unique Connector Behaviors

This connector is manifest-only (`language:manifest-only`, `cdk:low-code`); all behavior described
below lives in `manifest.yaml`. It targets the Apple Ads (formerly Apple Search Ads) Campaign
Management API v5 at `https://api.searchads.apple.com/api/v5`, and every request carries an
`X-AP-Context: orgId={{ config.org_id }}` header, which the API requires on all campaign-management
calls.

Streams: `campaigns`, `adgroups`, `keywords`, `ads` (entity streams, `primary_key: [id]`,
full refresh) and `campaigns_report_daily`, `adgroups_report_daily`, `keywords_report_daily`,
`ads_report_daily` (report streams, incremental on `date`).

## 1. Authentication is two-legged only; there is no user-consent OAuth flow

The Apple Ads API implements OAuth 2 as a pure machine-to-machine (two-legged) flow. The API user
generates an ECDSA P-256 (`prime256v1`) key pair with `openssl`, uploads the public key in the Apple
Ads UI, and then signs a self-issued ES256 JWT that is used as the `client_secret`. Tokens are
obtained by posting `grant_type=client_credentials&scope=searchadsorg` to
`https://appleid.apple.com/auth/oauth2/token`. There is no authorization endpoint, no redirect URI,
no user-consent screen, and no refresh token — see
[Implementing OAuth for the Apple Ads API](https://developer.apple.com/documentation/apple_ads/implementing-oauth-for-the-apple-search-ads-api).

The manifest therefore uses a plain `OAuthAuthenticator` with `grant_type: client_credentials`,
`client_id` and `client_secret` taken from the connector config, and an overridable
`token_refresh_endpoint`. It intentionally declares **no** `advanced_auth` block and **no**
`oauth_connector_input_specification`: both describe a three-legged consent flow (Airbyte redirects
the user to the vendor, the user approves, Airbyte exchanges a code), which this API does not offer.
Declarative OAuth cannot be used for the same reason — there is no consent URL to declare.

One consequence worth knowing: the `client_secret` JWT that users paste into the config is
short-lived by Apple's own rules (Apple caps its `exp` at 180 days). Auth failures on a
previously-working source are usually an expired JWT, not a revoked key. The token endpoint answers
an expired or wrong secret with `400 {"error": "invalid_client"}`; `refresh_token_error_*` turns that
into a configuration error whose text comes from the CDK and talks about a "refresh token". For this
connector that message means: generate a new client secret. Token-endpoint failures with a non-JSON
body or an unlisted `error` still surface as a system error, because the CDK only classifies the
listed JSON shape on the initial and hourly token fetch (airbytehq/airbyte-python-cdk#1251). After an
API `401`, the CDK's forced refresh fails any non-429 `4xx` from the token endpoint as a
configuration error instead.

**Why this matters:** Certification criteria A-1 and A-2 expect OAuth to be implemented
declaratively and offered first in the UI _where the API supports it_. This API does not support a
user-consent flow at all, so the `client_id` / `client_secret` pair is the only possible credential
shape; adding `advanced_auth` would advertise a flow that cannot work. Anyone "fixing" this
connector by adding a declarative OAuth spec would produce a spec Apple cannot satisfy.

## 2. The four `*_report_daily` streams are genuinely keyless

`campaigns_report_daily`, `adgroups_report_daily`, `keywords_report_daily`, and `ads_report_daily`
declare no `primary_key`. They are aggregate reporting streams: the request is a `POST` to
`/reports/campaigns[/{campaignId}/{adgroups|keywords|ads}]` with `granularity: DAILY`,
`groupBy: ['countryOrRegion']`, and a `startTime`/`endTime` window; the API returns
`data.reportingDataResponse.row[]` where each row is a metric aggregation, not a stored object. No
row carries an API-assigned record identifier.

What actually identifies a row is a composite of fields the connector assembles itself with
`AddFields` transformations: the reporting entity id (`campaignId`, `adGroupId`, `keywordId`, or
`adId`, lifted out of the nested `record.metadata`), the `date` copied from
`stream_slice.start_time`, and `countryorregion` lifted from `record.metadata.countryOrRegion`
(the single `groupBy` dimension). Metrics are nested under the `granularity` array; entity
attributes stay under `metadata`.

That composite is not declared as a primary key because it is only unique as long as the request
shape stays exactly as it is today: the tuple is a function of the hard-coded `granularity: DAILY`
and `groupBy: ['countryOrRegion']` in the manifest, plus `step: P1D` on the cursor. Declaring it as
a PK would make any future change to `groupBy` (adding a dimension) or `granularity` (HOURLY,
WEEKLY, MONTHLY) a silently key-violating change rather than an additive one, and changing a
declared PK afterwards is a breaking change for every existing connection. Keyless append is the
honest description of what the API returns.

**Why this matters:** S-1 requires either a real primary key on every stream or a named exception
per stream with the reason. These four streams are the exception, and the reason is not "we did not
get around to it": the identifying tuple is derived from the connector's own request parameters
rather than from the API, so it is not a stable record identity. Users who need deduplicated
reporting rows should dedupe on `(<entity>Id, date, countryorregion)` in the destination.

## 3. Deletions are replicated as a `deleted` flag on the entity streams

The canonical deletion pattern for this connector is **a deletion flag field on the primary
streams**, not dedicated `deleted_*` streams. Apple soft-deletes campaign-management objects and
returns `deleted: true|false` on `Campaign`, `AdGroup`, `Keyword`, and `Ad`; the schemas of
`campaigns`, `adgroups`, `keywords`, and `ads` all include that boolean, so whatever Apple returns
is passed through to the destination unchanged. There are no `deleted_*` streams and none should be
added.

The important caveat is coverage, and it is not fully verified. The connector reads entities through
the plain `GET` list endpoints (`/campaigns`,
`/campaigns/{campaignId}/adgroups`, `/campaigns/{campaignId}/adgroups/{adgroupId}/targetingkeywords`,
`/campaigns/{campaignId}/adgroups/{adgroupId}/ads`), which take no "include deleted" parameter, and
Apple's reference pages for those endpoints do not state whether soft-deleted objects are included
in the response. Apple's selector-based counterparts — `POST /campaigns/find` and friends — do
accept a `deleted` [`Condition`](https://developer.apple.com/documentation/apple_ads/find-campaigns),
which is the only documented way to explicitly select or exclude deleted objects. So the accurate
statement is: the `deleted` flag is replicated when the API returns it, and the connector does not
request deleted records explicitly. Whether the `GET` endpoints emit soft-deleted rows at all has
not been confirmed against live data (this connector has no working sandbox; see
`acceptance-test-config.yml`, where the connection test is expected to fail and the data tests are
commented out).

Note that switching the entity streams to the `find` endpoints purely to guarantee deleted-record
coverage would not be a free change: `find` is `POST` with a selector body and its own pagination,
so it is a rewrite of four streams, and narrowing or widening the returned record set changes what
existing connections sync.

**Why this matters:** S-5 requires one canonical, documented deletion pattern per connector. This is
that declaration — flag field, not `deleted_*` streams — and it deliberately stops short of claiming
that every deletion reaches the destination, because the manifest does not implement anything that
guarantees it. A future agent verifying S-5 against live credentials should check whether
`GET /campaigns` returns rows with `deleted: true`, and only then decide whether the `find`
endpoints are needed.

## 4. Entity streams are full refresh even though records carry `modificationTime`

Only the four report streams are incremental (`DatetimeBasedCursor` on `date`, `step: P1D`,
`cursor_granularity: P1D`, with a user-configurable `lookback_window`). The four entity streams
(`campaigns`, `adgroups`, `keywords`, `ads`) are full refresh on purpose, even though their records
carry `modificationTime`:

- `modificationTime` does not move when the serving state changes. Apple documents it as "the date
  and time of the most recent modification of the object", while `servingStatus`,
  `servingStateReasons` and `displayStatus` are resolved by Apple from time, budget and billing
  events: campaigns list reasons such as `CAMPAIGN_END_DATE_REACHED`, `DAILY_CAP_EXHAUSTED`,
  `TOTAL_BUDGET_EXHAUSTED`, `CREDIT_CARD_DECLINED` and `PAUSED_BY_SYSTEM`
  ([Campaign](https://developer.apple.com/documentation/apple_ads/campaign)), and ad groups list
  `ADGROUP_END_DATE_REACHED` and `CAMPAIGN_NOT_RUNNING`
  ([AdGroup](https://developer.apple.com/documentation/apple_ads/adgroup)). A `modificationTime`
  cursor would leave these fields stale in the destination; a full refresh keeps them current.
- Only `Campaign` and `Ad` document range operators (`LESS_THAN`, `GREATER_THAN`) on
  `modificationTime`. `Keyword` documents `EQUALS` and `IN` only, and `AdGroup` documents no
  operator for it ([Keyword](https://developer.apple.com/documentation/apple_ads/keyword),
  [Ad](https://developer.apple.com/documentation/apple_ads/ad)), so two of the four streams have no
  server-side cursor at all.
- The range filters exist only on the `POST .../find` endpoints, a different request shape from the
  `GET` list endpoints in use. Entity volumes are small next to the daily report streams.

Keep these streams full refresh. Revisit only if Apple documents a cursor that also tracks serving
state changes.

**Why this matters:** I-1 accepts full refresh only with a documented reason. A `modificationTime`
cursor would freeze `servingStatus`, `servingStateReasons` and `displayStatus` in the destination
whenever Apple changes them on its own, and keywords and ad groups have no range filter at all.

## 5. No `api_budget`: the Campaign Management API publishes no numeric quota

The manifest configures no `api_budget`. The Rate Limits section of
[Calling the Apple Ads API](https://developer.apple.com/documentation/apple_ads/calling-the-apple-search-ads-api)
documents rate limiting only as retry guidance — "increase retry attempts exponentially by seconds",
with a suggested ceiling (2 → 4 → 8 → 16 seconds). It publishes no requests-per-second, no
requests-per-window, and no quota headers for this API version, so there is no published limit for
an `api_budget` to match.

Each stream resolves to one `DefaultErrorHandler` through shared definitions: campaigns, adgroups,
keywords, and ads use `error_handler`; campaigns_report_daily, adgroups_report_daily, and
ads_report_daily use `report_error_handler`; keywords_report_daily uses
`keywords_report_error_handler`, which first ignores Apple's `CAMPAIGN DOES NOT CONTAIN KEYWORD`
response. The filters follow the status tables on each endpoint page (for example
[Get All Ad Groups](https://developer.apple.com/documentation/apple_ads/get-all-ad-groups) and
[Get Campaign-Level Reports](https://developer.apple.com/documentation/apple_ads/get-campaign-level-reports)):

- `401`: refresh the access token and retry; a `401` that persists after the refresh fails as a
  configuration error.
- `403` ("Insufficient rights to the resource."): configuration error that asks for an API role,
  with Apple's first error message.
- `400` ("An invalid query or missing required parameters."): on the report streams a configuration
  error, because their requests carry the user's dates and Apple serves `DAILY` reports only when
  "the startTime is <= 90 days in the past"
  ([ReportingRequest](https://developer.apple.com/documentation/apple_ads/reportingrequest)). The spec
  cannot enforce that limit: a Start Date older than 90 days, or a cursor that has not moved for about
  60 days with the default 30-day lookback, crosses it. On the entity streams a `400` is a system
  error, since their list requests carry no user input.
- `404` ("The API can't locate the resource."): documented only on endpoints addressed by a parent
  id, so a campaign or ad group removed during the sync; system error naming the URL, with Apple's
  message.
- `429`, `500`-`504` and statuses Apple does not list fall back to the CDK default mapping (retry
  with backoff, or fail as a system error).

Entity handlers use an exponential backoff strategy with the default factor and 5 retries. Report
handlers take their factor from `backoff_factor` (default 5) and allow up to 10 retries, but the
CDK stops retrying after 600 seconds, which is 6 retries at the default factor.

Apple sunsets Campaign Management API v5 on 2027-01-26 (see the [API v5
changelog](https://developer.apple.com/documentation/apple_ads/apple-search-ads-campaign-management-api-5)).
The connector must migrate to the Apple Ads Platform API at `https://api.ads.apple.com/v1/` before
then.

There is one forward-looking caveat. Apple's newer **Apple Ads Platform API** (a different API from
the Campaign Management API v5 this connector calls) _does_ return
[IETF `RateLimit-Limit` / `RateLimit-Remaining` / `RateLimit-Reset` headers](https://developer.apple.com/documentation/apple-ads-platform-api/rate-limits).
When this connector migrates to that API, this justification no longer applies and the rate
limits should be honored, either via `api_budget` or by respecting `Retry-After` on `429`.

**Why this matters:** P-2 requires `api_budget` wherever the API publishes rate limits, and
otherwise a documented statement that none are published. For v5 the honest answer is that Apple
publishes backoff advice rather than a quota, so a hard-coded `api_budget` would be an invented
number. Keep this section in sync with the API version the manifest's `url_base` actually points at.

## 6. Stream coverage versus Fivetran (parity table)

The comparison below is against Fivetran's Apple Search Ads connector, the required V-1 source. Rows
are the tables Fivetran materializes, taken from
[`fivetran/dbt_apple_search_ads`](https://github.com/fivetran/dbt_apple_search_ads) (the source
package [`dbt_apple_search_ads_source`](https://github.com/fivetran/dbt_apple_search_ads_source) is
deprecated and folded into it) and the
[Fivetran connector schema/ERD](https://fivetran.com/docs/connectors/applications/apple-search-ads).

| Fivetran table       | Verdict | Airbyte stream / notes                                                                                                                                                                                                                               |
| -------------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `campaign_history`   | covered | `campaigns`                                                                                                                                                                                                                                          |
| `ad_group_history`   | covered | `adgroups`                                                                                                                                                                                                                                           |
| `keyword_history`    | covered | `keywords`                                                                                                                                                                                                                                           |
| `ad_history`         | covered | `ads`                                                                                                                                                                                                                                                |
| `campaign_report`    | covered | `campaigns_report_daily`                                                                                                                                                                                                                             |
| `ad_group_report`    | covered | `adgroups_report_daily`                                                                                                                                                                                                                              |
| `keyword_report`     | covered | `keywords_report_daily`                                                                                                                                                                                                                              |
| `ad_report`          | covered | `ads_report_daily`                                                                                                                                                                                                                                   |
| `organization`       | missing | Apple exposes [`GET /acls`](https://developer.apple.com/documentation/apple_ads/get-user-acl) (org id, name, currency, timezone, payment model) and `GET /me`; neither is implemented as a stream.                                                   |
| `search_term_report` | missing | Apple exposes `POST /reports/campaigns/{campaignId}/searchterms` and the [ad-group-scoped variant](https://developer.apple.com/documentation/apple_ads/get-search-term-level-within-ad-group-reports); no `search_terms_report_daily` stream exists. |

Two notes on the `covered` verdicts, so they are not read as more than they are. First, Fivetran's
`*_history` tables are versioned snapshots produced by Fivetran's history mode; the matching Airbyte
streams replicate current state, and versioning is left to the destination sync mode. Second,
Fivetran flattens report metrics into columns (`impressions`, `taps`, `local_spend_amount`, …) while
these streams keep Apple's nested response shape — metrics live in the `granularity` array and
entity attributes in `metadata`, so the data is present but not column-per-metric.

The two `missing` rows are real and are **not** justified here as out of scope: both endpoints exist
and both are ordinary reporting/reference resources. Implementing them belongs in its own sub-issue
of the certification epic (V-1 asks for a single sub-issue listing all missing streams), not in a
documentation change. Separately, Apple's v5 API also exposes resources neither Fivetran nor this
connector covers — impression-share reports, product pages, and app locale resources among them;
they are outside the V-1 comparison because V-1 is scored against competitor coverage, but they are
worth knowing about when scoping that sub-issue.

**Why this matters:** V-1 asks whether stream coverage matches the market, and passes only when
there are no `missing` rows or each is justified. This connector has two genuine gaps, so the table
is the record of that — deliberately not inflated to a clean sheet. Anyone adding streams here
should update this table in the same change.
