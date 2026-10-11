> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

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
previously-working source are usually an expired JWT, not a revoked key.

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
`cursor_granularity: P1D`, with a user-configurable `lookback_window`). The four entity streams are
full refresh, even though `campaigns`, `adgroups`, `keywords`, and `ads` records all include a
`modificationTime` timestamp.

This is a deliberate deferral, not an API limitation, and it should be documented as such. Apple
exposes selector-condition endpoints (`POST /campaigns/find` and the equivalents for ad groups,
keywords, and ads) whose `Condition` objects accept `modificationTime` with operators such as
`GREATER_THAN`, so server-side incremental filtering is available in principle. Three reasons keep
the streams full refresh today:

- Volume is small. Campaigns, ad groups, keywords, and ads are configuration objects, not event
  data; a full refresh of an organization's campaign tree is cheap next to the daily report streams,
  and the streams already page at `limit=1000` with `default_concurrency` from `num_workers`.
- The `find` endpoints are a different request shape (`POST` with a selector body) than the `GET`
  list endpoints in use, so this is a rewrite of four streams rather than adding a cursor.
- Adding incremental sync to a stream that has none changes its state format from empty to a
  per-stream cursor and changes the sync mode users see in the catalog. That has to ship as its own
  reviewed change, not as a side effect of a documentation pass.

**Why this matters:** I-1 requires every stream with a viable cursor to be incremental, or a
documented reason why not. `modificationTime` is a viable cursor, so this connector does not pass
I-1 on the merits — it passes on a stated, revisitable deferral. Anyone picking this up should treat
it as scoped work (switch to `find`, add `DatetimeBasedCursor` on `modificationTime`, verify
substream partition routing still works) and not as a one-line manifest tweak.

## 5. No `api_budget`: the Campaign Management API publishes no numeric quota

The manifest configures no `api_budget`. The Rate Limits section of
[Calling the Apple Ads API](https://developer.apple.com/documentation/apple_ads/calling-the-apple-search-ads-api)
documents rate limiting only as retry guidance — "increase retry attempts exponentially by seconds",
with a suggested ceiling (2 → 4 → 8 → 16 seconds). It publishes no requests-per-second, no
requests-per-window, and no quota headers for this API version, so there is no published limit for
an `api_budget` to match.

Instead, every stream uses a `CompositeErrorHandler` with an `ExponentialBackoffStrategy` (report
streams take the multiplier from the optional `backoff_factor` config field) and retries `429` and
`500`; `401` maps to `REFRESH_TOKEN_THEN_RETRY`. That mirrors Apple's own prescription.

There is one forward-looking caveat. Apple's newer **Apple Ads Platform API** (a different API from
the Campaign Management API v5 this connector calls) _does_ return
[IETF `RateLimit-Limit` / `RateLimit-Remaining` / `RateLimit-Reset` headers](https://developer.apple.com/documentation/apple-ads-platform-api/rate-limits).
If this connector is ever migrated to that API, this justification no longer applies and the rate
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
