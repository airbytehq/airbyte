# Omnisend

## Sync overview

This source can sync data from the [Omnisend API](https://api-docs.omnisend.com/reference/intro). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- contacts
- campaigns
- carts
- orders
- products

### Features

| Feature           | Supported?\(Yes/No\) |
|:------------------|:---------------------|
| Full Refresh Sync | Yes                  |
| Incremental Sync  | No                   |

### Performance considerations

The five legacy streams keep their existing v3 API behavior. The new streams use
[Omnisend API version `2026-03-15`](https://api-docs.omnisend.com/docs/migrate-from-v3-to-v2026-03-15)
and are disabled until `enable_reporting` is set to `true`.

### Optional reporting streams

| Stream | Data |
|:-------|:-----|
| `brand` | Current brand metadata, including currency and timezone |
| `campaigns_v2026` | New-API campaign metadata; separate from legacy `campaigns` |
| `automations` | Automation workflow metadata |
| `forms` | Form metadata |
| `segments` | Segment metadata |
| `analytics_reports` | Send-date activity, channel, automation-message and overall performance |
| `analytics_statistics` | Event-date audience, sales, failure-reason and subscription-source statistics |
| `form_reports` | Periodic form performance, including views, interactions, submits and signups |
| `analytics_reports_daily` | Daily send-date performance by campaign/automation type for `lastMonth` |
| `analytics_statistics_daily` | Hourly event-date audience counts for explicit UTC windows |

The new API uses `Authorization: Omnisend-API-Key <key>` and the fixed
`Omnisend-Version: 2026-03-15` header. Set the optional secret `reporting_api_key`
to use a separate key for the new streams. Otherwise they use `api_key`.
Authentication, schemas and connection checks for the five legacy streams are
unchanged. The existing check validates legacy Contacts access; it does **not**
certify permission for the optional streams. Selected optional streams fail on
permission errors rather than silently returning no data.

The required `api_key` must retain Contacts read permission for the legacy
connection check, even when only optional streams are selected. A separate
`reporting_api_key` needs only the permissions for its selected new streams:
 `brands.read`, `campaigns.read`,
`automations.read`, `forms.read`, `segments.read` and `analytics.read`.
Do not grant write permissions for this connector.

### Reporting windows and semantics

- `reporting_periods` defaults to `["lastMonth"]` when reporting is enabled. Named
  intervals use the brand's timezone. Each period is one request containing four
  queries. These reports intentionally omit a timestamp dimension so the API
  calculates uniques and rates across the entire requested interval.
- `statistics_windows` is an optional array of `{ "from": "...", "to": "..." }`
  RFC3339 windows. `from` is inclusive and `to` exclusive. Use the same numerical
  timezone offset at both ends. Each window costs one request with four queries;
  it must span no more than 12 months. Omitted or empty means no requests.
- `form_report_windows` is a separate array with **both** boundaries inclusive.
  Use an end just before the next period starts. Each form/window pair is one
  request. Omnisend chooses granularity from the range and aligns buckets to the
  brand timezone. Omitted or empty means no form-report requests.
- `analytics_reports_daily` independently requests `lastMonth`, with daily
  timestamp buckets and marketing-activity type. It costs one analytics request.
- `daily_statistics_windows` is an optional array of explicit UTC windows (`Z` or
  `+00:00`). Each must be at most seven days. For a complete local calendar month,
  convert the true IANA-timezone boundaries to UTC, then split that interval into
  contiguous chunks of at most seven days. A 23/25-hour DST day is not a fixed
  24-hour day. The source emits hourly buckets; it does not aggregate them into
  local days. Omitted or empty means no requests.

Example event and form windows for one UTC month:

```json
{
  "enable_reporting": true,
  "statistics_windows": [
    {"from": "2026-09-01T00:00:00Z", "to": "2026-10-01T00:00:00Z"}
  ],
  "form_report_windows": [
    {"from": "2026-09-01T00:00:00Z", "to": "2026-09-30T23:59:59.999999Z"}
  ]
}
```

All reporting streams are full refresh. Date windows are reread on each sync;
there is no incremental high-water mark that would hide later attribution
corrections. Explicit windows do not advance automatically. Date-span and
metric/dimension compatibility errors are rejected by Omnisend and fail the
sync. The specification declares RFC3339 formats and enforces timestamp/UTC
syntax; calendar validity, date ordering and span validation remain the API's
responsibility. This manifest does not implement cross-field date validation.

[Reports](https://api-docs.omnisend.com/reference/reports) group opens, clicks and
attributed orders/revenue by **send date**, not purchase/event date.
[Statistics](https://api-docs.omnisend.com/reference/statistics) use **event date**.
Native NULLs and measured zero remain distinct. Rates and uniques are not
additive across dates, brands, activities or channels. Attributed revenue is
not interchangeable with total store revenue.

Report records retain the API's alias, metric/dimension metadata and `rows`
array, including an empty array. Added query-period/window fields explain which
request produced the envelope. Metadata streams emit individual entities;
empty metadata lists produce no records and are not deletion events. No
cross-stream atomic snapshot or complete-brand snapshot marker is promised.

### Reporting quotas

[Analytics limits](https://api-docs.omnisend.com/reference/rate-limit-timeouts-errors)
are 10 requests per minute and 55 per **rolling 24 hours**, shared by integrations
and keys for the same brand. The native in-process moving-window budget covers
both analytics endpoints. It cannot account for previous connector invocations
or other applications. Reporting disabled is the safe default; enabling it with
no explicit windows makes two analytics requests when both report streams are
selected (four-query interval report plus one daily report). Form requests use
the endpoint's default quota, not the 55-request analytics quota. Select only the streams needed and count all windows
before a historical backfill. Do not run overlapping reporting integrations.

On HTTP 429 the new streams fail without automatically retrying. The error
includes the provider's `retryAfter` seconds when present (or `Retry-After`
header), so an operator can wait for shared quota before restarting. CDK 6.48.10
cannot use a JSON-body `retryAfter` in a built-in backoff strategy. Server errors
have three bounded exponential retries. No permission/validation error is
ignored. A sufficiently large backfill can wait for the local sliding budget;
break it into bounded runs rather than assuming 55 requests reset at midnight.

This addition does not configure destination sync modes or migrate custom
connectors. In particular, entity records and generic report envelopes are not
a replacement for a custom Append pipeline's brand IDs, invocation UUIDs,
terminal-page snapshots or downstream deduplication/coverage contract.

## Getting started

### Requirements

- Omnisend API Key

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Development tests

Run the synthetic offline tests from the repository root with the connector's
pinned CDK. They do not require a real key or contact an Omnisend account:

```bash
uv run --python 3.11 --no-project --with airbyte-cdk==6.48.10 --with pytest --with requests-mock pytest airbyte-integrations/connectors/source-omnisend/unit_tests/test_reporting.py -q
```

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject        |
|:--------|:-----------| :------------------------------------------------------- | :------------- |
| 0.4.0 | 2026-10-10 | [88451](https://github.com/airbytehq/airbyte/pull/88451) | Add opt-in versioned metadata and bounded reporting streams |
| 0.3.11 | 2025-05-10 | [60078](https://github.com/airbytehq/airbyte/pull/60078) | Update dependencies |
| 0.3.10 | 2025-05-03 | [59470](https://github.com/airbytehq/airbyte/pull/59470) | Update dependencies |
| 0.3.9 | 2025-04-27 | [59086](https://github.com/airbytehq/airbyte/pull/59086) | Update dependencies |
| 0.3.8 | 2025-04-19 | [58483](https://github.com/airbytehq/airbyte/pull/58483) | Update dependencies |
| 0.3.7 | 2025-04-12 | [57871](https://github.com/airbytehq/airbyte/pull/57871) | Update dependencies |
| 0.3.6 | 2025-04-05 | [57341](https://github.com/airbytehq/airbyte/pull/57341) | Update dependencies |
| 0.3.5 | 2025-03-29 | [56802](https://github.com/airbytehq/airbyte/pull/56802) | Update dependencies |
| 0.3.4 | 2025-03-22 | [56170](https://github.com/airbytehq/airbyte/pull/56170) | Update dependencies |
| 0.3.3 | 2025-03-08 | [55057](https://github.com/airbytehq/airbyte/pull/55057) | Update dependencies |
| 0.3.2 | 2025-02-23 | [54561](https://github.com/airbytehq/airbyte/pull/54561) | Update dependencies |
| 0.3.1 | 2025-02-15 | [53999](https://github.com/airbytehq/airbyte/pull/53999) | Update dependencies |
| 0.3.0 | 2025-02-07 | [53208](https://github.com/airbytehq/airbyte/pull/53208) | update schemas and make dynamic |
| 0.2.11 | 2025-02-08 | [53487](https://github.com/airbytehq/airbyte/pull/53487) | Update dependencies |
| 0.2.10 | 2025-02-03 | [52699](https://github.com/airbytehq/airbyte/pull/52699) | Fix pagination |
| 0.2.9 | 2025-02-01 | [52987](https://github.com/airbytehq/airbyte/pull/52987) | Update dependencies |
| 0.2.8 | 2025-01-25 | [52478](https://github.com/airbytehq/airbyte/pull/52478) | Update dependencies |
| 0.2.7 | 2025-01-18 | [51859](https://github.com/airbytehq/airbyte/pull/51859) | Update dependencies |
| 0.2.6 | 2025-01-11 | [51205](https://github.com/airbytehq/airbyte/pull/51205) | Update dependencies |
| 0.2.5 | 2024-12-28 | [50291](https://github.com/airbytehq/airbyte/pull/50291) | Update dependencies |
| 0.2.4 | 2024-12-14 | [49674](https://github.com/airbytehq/airbyte/pull/49674) | Update dependencies |
| 0.2.3 | 2024-12-12 | [49365](https://github.com/airbytehq/airbyte/pull/49365) | Update dependencies |
| 0.2.2 | 2024-12-11 | [48284](https://github.com/airbytehq/airbyte/pull/48284) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.1 | 2024-10-29 | [47474](https://github.com/airbytehq/airbyte/pull/47474) | Update dependencies |
| 0.2.0 | 2024-08-19 | [44411](https://github.com/airbytehq/airbyte/pull/44411) | Refactor connector to manifest-only format |
| 0.1.13 | 2024-08-17 | [44307](https://github.com/airbytehq/airbyte/pull/44307) | Update dependencies |
| 0.1.12 | 2024-08-12 | [43727](https://github.com/airbytehq/airbyte/pull/43727) | Update dependencies |
| 0.1.11 | 2024-08-10 | [43581](https://github.com/airbytehq/airbyte/pull/43581) | Update dependencies |
| 0.1.10 | 2024-08-03 | [42745](https://github.com/airbytehq/airbyte/pull/42745) | Update dependencies |
| 0.1.9 | 2024-07-20 | [42325](https://github.com/airbytehq/airbyte/pull/42325) | Update dependencies |
| 0.1.8 | 2024-07-13 | [41697](https://github.com/airbytehq/airbyte/pull/41697) | Update dependencies |
| 0.1.7 | 2024-07-10 | [41454](https://github.com/airbytehq/airbyte/pull/41454) | Update dependencies |
| 0.1.6 | 2024-07-09 | [41319](https://github.com/airbytehq/airbyte/pull/41319) | Update dependencies |
| 0.1.5 | 2024-07-06 | [40969](https://github.com/airbytehq/airbyte/pull/40969) | Update dependencies |
| 0.1.4 | 2024-06-28 | [38664](https://github.com/airbytehq/airbyte/pull/38664) | Make connector compatible with Builder |
| 0.1.3 | 2024-06-25 | [40440](https://github.com/airbytehq/airbyte/pull/40440) | Update dependencies |
| 0.1.2 | 2024-06-22 | [40167](https://github.com/airbytehq/airbyte/pull/40167) | Update dependencies |
| 0.1.1 | 2024-05-30 | [38533](https://github.com/airbytehq/airbyte/pull/38533) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-25 | [18577](https://github.com/airbytehq/airbyte/pull/18577) | Initial commit |

</details>
