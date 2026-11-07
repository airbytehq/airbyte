# AppLovin Ads

This source syncs reporting data from AppLovin. It covers both sides of the platform:
advertiser reporting (app campaigns, web campaigns, and asset/creative performance) and MAX
publisher reporting (mediation revenue plus install-cohort revenue, impressions, and
sessions). Every endpoint authenticates with the same Report Key.

The campaign management and Conversions APIs are not covered. They use different hosts
(`o.applovin.com`, `api.ads.axon.ai`, `b.applovin.com`), different credentials, header-based
auth, and they write data to AppLovin rather than read from it.

API documentation:

- [Reporting API](https://support.applovin.com/en/growth/promoting-your-apps/api/reporting-api) (app campaigns)
- [Web Reporting API](https://support.applovin.com/growth/promoting-your-websites/api/web-reporting-api) (web campaigns)
- [Asset Reporting API](https://support.applovin.com/en/growth/promoting-your-websites/api/asset-reporting-api)
- [Revenue Reporting API](https://support.applovin.com/en/max/reporting-apis/revenue-reporting-api) (MAX mediation)
- [Cohort API](https://support.applovin.com/en/max/reporting-apis/cohort-api) (MAX install cohorts)

## Prerequisites

- An AppLovin account with reporting access.
- A **Report Key**. In the AppLovin dashboard, click your account name in the top right and
  select **Keys**. The Management Key, Campaign Management Key, and CAPI Key are different
  credentials and do not work for reporting.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | Report Key. | |
| `start_date` | `string` | UTC date to start replicating from (`YYYY-MM-DD`). | |
| `end_date` | `string` | UTC date to replicate up to, inclusive (`YYYY-MM-DD`). | today |
| `lookback_window` | `integer` | Days before the last synced date to re-request on each incremental sync. | `3` |
| `cohort_lookback_window` | `integer` | Same, for the MAX cohort streams, whose metrics keep maturing for up to 45 days. | `45` |
| `attribution_mode` | `string` | Attribution mode for `web_report_daily`: `click` or `click_and_view`. | `click` |
| `num_workers` | `integer` | Number of streams to sync concurrently. | `2` |

## Streams

| Stream Name | Endpoint | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|----------|-------------|------------|---------------------|----------------------|
| advertiser_report_daily | `/report` | day.campaign_id_external.creative_set_id.country.platform.placement_type | Offset | ✅ | ✅ |
| web_report_daily | `/webReport` | day.campaign_id_external.creative_set_id.country.platform.placement_type | Offset | ✅ | ✅ |
| asset_report_daily | `/assetAnalyticsReport` | date.asset_id.campaign_id.creative_set_id | Offset | ✅ | ✅ |
| max_report_daily | `/maxReport` | day.package_name.max_ad_unit_id.network.network_placement.country.device_type.ad_format.platform | Offset | ✅ | ✅ |
| max_cohort_revenue_daily | `/maxCohort` | day.package_name.platform.country | Offset | ✅ | ✅ |
| max_cohort_impressions_daily | `/maxCohort/imp` | day.package_name.platform.country | Offset | ✅ | ✅ |
| max_cohort_sessions_daily | `/maxCohort/session` | day.package_name.platform.country | Offset | ✅ | ✅ |

The first three streams are advertiser-side: what you spend buying media. The `max_*`
streams are publisher-side: what you earn showing ads in apps you own. They are unrelated
data sets that happen to share a credential, and an account that only buys media returns no
rows for the MAX streams (and vice versa).

Use `advertiser_report_daily` for app install campaigns and `web_report_daily` for campaigns
driving traffic to a website. They are separate AppLovin endpoints with different column
sets: only the web report exposes checkout, ROAS, and new-customer metrics such as
`nc_d0_checkouts` and `chka_usd_7d`, and only the app report exposes install metrics such as
`conversions`.

### Incremental syncs and restated data

Every stream requests one day at a time, so each record belongs to a single date.
`advertiser_report_daily` and `web_report_daily` cursor on the API's native `day` column;
`asset_report_daily` has no day dimension, so the connector adds the requested date as
`date` and cursors on that.

AppLovin restates recent metrics as attribution data arrives, so the `lookback_window`
re-requests the most recent days on every sync. With a deduplicating sync mode, the
composite primary keys cause restated rows to overwrite the previously synced values.
Data for yesterday is stable after 06:00 UTC.

The cohort streams restate on a much longer horizon. Their metrics are suffixed with the
number of days since install (`pub_revenue_7`, `retention_30`, `imp_per_user_45`), so a
given install day's 45-day figures are not final until 45 days after that day. Those three
streams therefore use `cohort_lookback_window`, which defaults to 45 — the full window — so
that maturing cohorts are corrected in place. Lowering it cuts request volume but freezes
older cohorts at whatever value they had when first synced.

The cohort streams request a subset of the available day offsets (0, 1, 3, 7, 14, 30, and
45 for revenue; 0, 1, 7, 14, and 30 for impressions and sessions). AppLovin supports 0, 1,
2, 3, 4, 5, 6, 7, 10, 14, 18, 21, 24, 27, 30, and 45.

### Request windows

AppLovin serves a limited history, and dates outside the window return an error rather than
an empty result:

| Endpoint | Window |
|----------|--------|
| `/report` | 45 days |
| `/webReport` | 90 days |
| `/assetAnalyticsReport` | 45 days |
| `/maxReport` | 45 days |
| `/maxCohort`, `/maxCohort/imp`, `/maxCohort/session` | 45 days |

The connector clamps `start_date` to the oldest day each endpoint still serves, so a
`start_date` further back than the window syncs the available history instead of failing.
Backfilling more history than the window allows is not possible through this API.

### Asset report endpoints

AppLovin publishes the asset report under two base URLs that return the same report with
different time parameters: `/assetReport` takes a `range` (`yesterday`, `last_7d`, or
`last_month`) and `/assetAnalyticsReport` takes `start` and `end` dates. This connector uses
`/assetAnalyticsReport` because incremental syncs need per-day date ranges, which the
range-based variant cannot express.

### Requesting other columns

Each stream requests a fixed column set. AppLovin exposes many more columns, including
hourly and longer attribution windows. To add them, edit the stream's `columns` request
parameter and the corresponding schema in `manifest.yaml`; the schemas allow additional
properties, so extra columns pass through even if they are not declared.

Some MAX columns are mutually exclusive. `/maxReport` only returns `attempts`, `responses`,
and `fill_rate` when `network` or `network_placement` is also requested, and it cannot
return `requests` alongside either of those columns. `max_report_daily` requests `network`
and `network_placement`, so it omits `requests`.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.1.0 | 2026-07-30 | [83270](https://github.com/airbytehq/airbyte/pull/83270) | Initial release: advertiser reporting (`advertiser_report_daily`, `web_report_daily`, `asset_report_daily`) and MAX publisher reporting (`max_report_daily`, `max_cohort_revenue_daily`, `max_cohort_impressions_daily`, `max_cohort_sessions_daily`) |

</details>
