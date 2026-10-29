# source-apple-search-ads: Unique Connector Behaviors

This connector is manifest-only (`language:manifest-only`, `cdk:low-code`); all behavior described
below lives in `manifest.yaml`. It targets the Apple Ads (formerly Apple Search Ads) Campaign
Management API v5 at `https://api.searchads.apple.com/api/v5`, and every request except
`organization`'s `GET /acls` carries an `X-AP-Context: orgId={{ config.org_id }}` header, which the
API requires on campaign-management calls.

Streams: `campaigns`, `adgroups`, `keywords`, `ads`, `creatives`, `campaign_negative_keywords`,
`adgroup_negative_keywords`, `product_pages` (entity streams, `primary_key: [id]`, full refresh),
`organization` (`GET /acls`, `primary_key: [orgId]`, full refresh, no `X-AP-Context` header because
the ACL call lists every organization the API user can access) and `campaigns_report_daily`,
`adgroups_report_daily`, `keywords_report_daily`, `ads_report_daily`, `search_terms_report_daily`
(report streams, incremental on `date`).

`product_pages` is partitioned by the app (`adamId`) of each campaign through a deduplicating
`GroupingPartitionRouter` (`group_size: 1`), so an app advertised by several campaigns is requested
once.

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

## 2. The five `*_report_daily` streams are genuinely keyless

`campaigns_report_daily`, `adgroups_report_daily`, `keywords_report_daily`, `ads_report_daily`, and
`search_terms_report_daily` declare no `primary_key`. They are aggregate reporting streams: the request is a `POST` to
`/reports/campaigns[/{campaignId}/{adgroups|keywords|ads|searchterms}]` with `granularity: DAILY`,
`groupBy: ['countryOrRegion']`, and a `startTime`/`endTime` window; the API returns
`data.reportingDataResponse.row[]` where each row is a metric aggregation, not a stored object. No
row carries an API-assigned record identifier.

What actually identifies a row is a composite of fields the connector assembles itself with
`AddFields` transformations: the reporting entity id (`campaignId`, `adGroupId`, `keywordId`, or
`adId`, lifted out of the nested `record.metadata`; search-term rows also get `adGroupId`, `keywordId`,
and `searchTermText`, and `searchTermText` is null for Apple's low-volume rollup row), the `date` copied from
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
per stream with the reason. These five streams are the exception, and the reason is not "we did not
get around to it": the identifying tuple is derived from the connector's own request parameters
rather than from the API, so it is not a stable record identity. Users who need deduplicated
reporting rows should dedupe on `(<entity>Id, date, countryorregion)` (for `search_terms_report_daily`, on `campaignId`, `adGroupId`, `keywordId`, `searchTermText`, `date` and `countryorregion`) in the destination.

## 3. The `GET` list endpoints never return deleted entities

Apple soft-deletes campaign-management objects and documents a `deleted` boolean on `Campaign`,
`AdGroup`, `Keyword`, `Ad` and `NegativeKeyword`, and the schemas of `campaigns`, `adgroups`,
`keywords`, `ads`, `campaign_negative_keywords` and `adgroup_negative_keywords` declare it. But
Apple's [Selector](https://developer.apple.com/documentation/apple_ads/selector) reference says: "By
default, API fetch calls don't return deleted resources, with the exception of GET by a resource Id.
To retrieve deleted resources, you must explicitly request the call using the selector Condition".
The connector reads the plain `GET` list endpoints (`/campaigns`, `/campaigns/{campaignId}/adgroups`,
`/campaigns/{campaignId}/adgroups/{adgroupId}/targetingkeywords`,
`/campaigns/{campaignId}/adgroups/{adgroupId}/ads` and the negative keyword lists), so deleted
objects never arrive and `deleted` is always `false`.

Apple's find endpoints (`POST /campaigns/find` and the per-campaign `find` endpoints) accept the
condition `{"field": "deleted", "operator": "IN", "values": [true, false]}` and return deleted objects
too. They take a selector body with its own pagination, so moving to them rewrites the entity
streams. That work is planned together with the Campaign Management API v5 retirement on 2027-01-26
(airbytehq/oncall#13496), because the replacement API changes these endpoints anyway.

**Why this matters:** S-5 fails until deleted entities reach the primary streams; the fix is the
find endpoints with the `deleted` condition, not `deleted_*` streams. Until then a destination keeps
a deleted object as it was last seen, with `deleted: false`, and the user docs say so.

## 4. Entity streams are full refresh even though records carry `modificationTime`

Only the five report streams are incremental (`DatetimeBasedCursor` on `date`, `step: P1D`,
`cursor_granularity: P1D`, with a user-configurable `lookback_window`). The entity streams
(`campaigns`, `adgroups`, `keywords`, `ads`, `creatives`, `campaign_negative_keywords`,
`adgroup_negative_keywords`, `product_pages`, `organization`) are full refresh on purpose, even
though most of their records carry `modificationTime`:

- The newer entity streams read `GET` endpoints with no modification-time filter (only the separate Find Creatives endpoint filters on it): Get All Creatives
  and both negative keyword endpoints take only `limit` and `offset`, Get Product Pages takes only
  `name` and `states`, and Get User ACL takes no parameters.

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
keywords, ads, organization, creatives, campaign_negative_keywords, adgroup_negative_keywords and
product_pages use `error_handler`; campaigns_report_daily, adgroups_report_daily, ads_report_daily
and search_terms_report_daily use `report_error_handler`; keywords_report_daily uses
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

## 6. Stream coverage against the market (parity table)

The table compares the connector with the resources other Apple Ads connectors on the market sync,
normalized to Apple API resources (checked 2026-10-27).

| Resource | Verdict | Airbyte stream or field |
| --- | --- | --- |
| Campaigns | covered | `campaigns` |
| Countries or regions of a campaign | covered as a field | `campaigns.countriesOrRegions`, `campaigns.countryOrRegionServingStateReasons` |
| Ad groups | covered | `adgroups` |
| Targeting dimensions | covered as a field | `adgroups.targetingDimensions` |
| Keywords | covered | `keywords` |
| Negative keywords | covered | `campaign_negative_keywords`, `adgroup_negative_keywords` |
| Ads | covered | `ads` |
| Ad serving state reasons | covered as a field | `ads.servingStateReasons` |
| Creatives | covered | `creatives` |
| Creative state reasons | covered as a field | `creatives.stateReasons` |
| Product pages | covered | `product_pages` |
| Product page locales and their devices | missing | [`GET /apps/{adamId}/product-pages/{productPageId}/locale-details`](https://developer.apple.com/documentation/apple_ads/get-product-page-locales) |
| Organization | covered | `organization` ([`GET /acls`](https://developer.apple.com/documentation/apple_ads/get-user-acl)) |
| Campaign report | covered | `campaigns_report_daily` |
| Ad group report | covered | `adgroups_report_daily` |
| Keyword report | covered | `keywords_report_daily` |
| Ad report | covered | `ads_report_daily` |
| Search term report | covered | `search_terms_report_daily` |
| Impression share report | missing | asynchronous custom reports: create, poll, download, at most 10 reports per 24 hours and a 30-day range |

Market `*_history` tables are versioned snapshots; these streams replicate current state and leave
versioning to the destination sync mode. Report metrics stay in Apple's nested shape: metrics in the
`granularity` array, entity attributes in `metadata`.

**Why this matters:** V-1 passes only when no row is `missing` or each is justified. The two missing
resources are planned with the v5 retirement (airbytehq/oncall#13496), because the replacement API
changes their endpoints; adding them on v5 now would be rewritten within weeks. Update this table in
the same change as any new stream.

## 7. `search_terms_report_daily` always uses ORTZ and only Search Results campaigns

The stream sends `timeZone: ORTZ` whatever `timezone` says, because Apple states "Search term-level
reports only support a `timeZone` value of `ORTZ`"
([Get Search Term-Level Reports](https://developer.apple.com/documentation/apple_ads/get-search-term-level-reports)),
and it sends `returnRowTotals: false` and `returnGrandTotals: false`, which Apple requires when a
request sets `granularity` ([ReportingRequest](https://developer.apple.com/documentation/apple_ads/reportingrequest)).
It only requests campaigns whose `supplySources` include `APPSTORE_SEARCH_RESULTS` (a `RecordFilter`
on the parent `campaigns` stream), because search terms only exist for Search Results campaigns;
campaigns without `supplySources` are kept. Terms under Apple's 10-impression limit arrive in rows
with `other: true` and a null `searchTermText`. Each request covers one day (`endTime` equals the
slice start), so a row's `date` always matches its metrics. The CDK folds the last day into the
final slice, so the cursor ends one day after the End Date (or today) to give that day its own
request; `is_compare_strictly` keeps a start equal to that end from requesting a day past the range.
The first window starts at most 89 days back, because Apple serves `DAILY`
reports only when "the startTime is <= 90 days in the past"; a day of margin covers organization time
zones ahead of UTC. With that floor a `400` cannot come from the Start Date, so the stream's error
handler reports it as a system error.

**Why this matters:** with `timezone: UTC`, this stream's `date` is an organization-time-zone day
while the other report streams use UTC days, so joins by `date` can shift by one day. Do not make it
follow the `timezone` setting, and keep the 89-day floor: search terms are sparse, a sync without
rows does not move the cursor, and without the floor such a stream would restart from an old Start
Date that Apple rejects.

## Pagination notes

Every list and report stream pages with `limit`/`offset` and a page size of 1000, Apple's documented
maximum ([Pagination](https://developer.apple.com/documentation/apple_ads/pagination)); report streams
send them inside `selector.pagination`. Two streams have no paginator on purpose: `organization`,
because [Get User ACL](https://developer.apple.com/documentation/apple_ads/get-user-acl) takes no
parameters, and `product_pages`, because
[Get Product Pages](https://developer.apple.com/documentation/apple_ads/get-product-pages) takes only
`name` and `states`.

