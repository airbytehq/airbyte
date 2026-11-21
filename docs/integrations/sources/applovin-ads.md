# AppLovin Ads

Syncs advertiser-side reporting from AppLovin: app campaigns ([Reporting API](https://support.applovin.com/en/growth/promoting-your-apps/api/reporting-api)),
web campaigns ([Web Reporting API](https://support.applovin.com/growth/promoting-your-websites/api/web-reporting-api)),
and creative assets ([Asset Reporting API](https://support.applovin.com/en/growth/promoting-your-websites/api/asset-reporting-api)).
MAX publisher/monetization reporting, campaign management, and the Conversions API are not covered.

## Setup

1. In the AppLovin dashboard, click your account name (top right) → **Keys** and copy your
   **Report Key**. Other keys (Management, Campaign Management, CAPI) do not work for reporting.
2. In Airbyte, create an **AppLovin Ads** source with the key and a `YYYY-MM-DD` start date.

## Configuration

| Input | Type | Description | Default |
|-------|------|-------------|---------|
| `api_key` | `string` | Report Key. | |
| `start_date` | `string` | UTC date to start replicating from (`YYYY-MM-DD`). | |
| `end_date` | `string` | UTC date to replicate up to, inclusive (`YYYY-MM-DD`). | today |
| `lookback_window` | `integer` | Days before the last synced date to re-request each sync. | `3` |
| `attribution_mode` | `string` | Web report streams: `click` or `click_and_view`. | `click` |
| `num_workers` | `integer` | Streams to sync concurrently. | `2` |

## Streams

All streams support full refresh and incremental sync, paginate by offset.

| Stream | Endpoint | Primary Key |
|--------|----------|-------------|
| advertiser_report_daily | `/report` | day + dimensions |
| advertiser_report_hourly | `/report` | day + hour + dimensions |
| web_report_daily | `/webReport` | day + dimensions |
| web_report_hourly | `/webReport` | day + hour + dimensions |
| asset_report_daily | `/assetAnalyticsReport` | date + asset_id + campaign_id + creative_set_id |

Advertiser streams cover app install campaigns; web streams cover website campaigns. Column
sets differ: only web reports expose checkout/new-customer metrics (`nc_d0_checkouts`,
`chka_usd_7d`, …), only app reports expose install metrics (`conversions`). Hourly streams
mirror their daily counterparts plus an `hour` column. (AppLovin's docs list `hour` only for
publisher reports, but the advertiser endpoints serve it too.)

### Incremental syncs and restated data

Streams request one day per slice and cursor on `day` (`asset_report_daily` has no day
column, so the connector stamps the slice date as `date`). AppLovin restates recent metrics
as attribution arrives; the `lookback_window` re-requests recent days, and the composite
primary keys let deduplicating sync modes overwrite restated rows. Yesterday's data is
stable after 06:00 UTC.

### Request windows

Dates outside AppLovin's serving window error rather than return empty, so the connector
clamps `start_date` to the oldest available day:

| Stream | Window |
|--------|--------|
| `advertiser_report_daily`, `asset_report_daily` | 45 days |
| `web_report_daily` | 90 days |
| hourly streams | 30 days |

### Requesting other columns

Each stream requests a fixed column set; AppLovin exposes more. Add them to the stream's
`columns` request parameter and schema in `manifest.yaml` — schemas allow additional
properties, so undeclared columns pass through.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                           | Subject                                                                             |
| :------ | :--------- | :----------------------------------------------------- | :---------------------------------------------------------------------------------- |
| 0.1.0   | 2026-06-29 | [81418](https://github.com/airbytehq/airbyte/pull/81418) | Initial release: `advertiser_report_daily`, `advertiser_report_hourly`, `web_report_daily`, `web_report_hourly`, `asset_report_daily` |

</details>
