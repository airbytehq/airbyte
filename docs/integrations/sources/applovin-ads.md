# AppLovin Ads

This page contains the setup guide and reference information for the AppLovin Ads source connector.

It syncs advertiser-side reporting data from AppLovin: app campaign reporting, web campaign
reporting, and asset (creative) level reporting. MAX publisher and monetization reporting
(`/maxReport`, `/maxCohort`) is **not** covered by this connector, and neither are the campaign
management or Conversions APIs — those use different hosts and different credentials.

API documentation:

- [Reporting API](https://support.applovin.com/en/growth/promoting-your-apps/api/reporting-api) (app campaigns)
- [Web Reporting API](https://support.applovin.com/growth/promoting-your-websites/api/web-reporting-api) (web campaigns)
- [Asset Reporting API](https://support.applovin.com/en/growth/promoting-your-websites/api/asset-reporting-api)

## Prerequisites

- An AppLovin account with access to reporting.
- A **Report Key**. The Management Key, Campaign Management Key, and CAPI Key are different
  credentials and do not work for reporting.

## Setup guide

### Step 1: Get your Report Key

In the AppLovin dashboard, click your account name (top right) → **Keys** and copy your **Report Key**.

### Step 2: Set up the source in Airbyte

1. In Airbyte, click **Sources** → **+ New source** and select **AppLovin Ads**.
2. Enter your **Report Key**.
3. For **Start Date**, enter a `YYYY-MM-DD` date. Leave **End Date** blank to sync up to today.
4. Optionally adjust the **Lookback Window** and, for web campaigns, the **Web Attribution Mode**.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | Report Key. | |
| `start_date` | `string` | UTC date to start replicating from (`YYYY-MM-DD`). | |
| `end_date` | `string` | UTC date to replicate up to, inclusive (`YYYY-MM-DD`). | today |
| `lookback_window` | `integer` | Days before the last synced date to re-request on each incremental sync. | `3` |
| `attribution_mode` | `string` | Attribution mode for the web report streams: `click` or `click_and_view`. | `click` |
| `num_workers` | `integer` | Number of streams to sync concurrently. | `2` |

## Supported sync modes

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |

## Streams

| Stream Name | Endpoint | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|----------|-------------|------------|---------------------|----------------------|
| advertiser_report_daily | `/report` | day.campaign_id_external.creative_set_id.country.platform.placement_type | Offset | ✅ | ✅ |
| advertiser_report_hourly | `/report` | day.hour.campaign_id_external.creative_set_id.country.platform.placement_type | Offset | ✅ | ✅ |
| web_report_daily | `/webReport` | day.campaign_id_external.creative_set_id.country.platform.placement_type | Offset | ✅ | ✅ |
| web_report_hourly | `/webReport` | day.hour.campaign_id_external.creative_set_id.country.platform.placement_type | Offset | ✅ | ✅ |
| asset_report_daily | `/assetAnalyticsReport` | date.asset_id.campaign_id.creative_set_id | Offset | ✅ | ✅ |

Use `advertiser_report_daily` for app install campaigns and `web_report_daily` for campaigns
driving traffic to a website. They are separate AppLovin endpoints with different column
sets: only the web report exposes checkout, ROAS, and new-customer metrics such as
`nc_d0_checkouts` and `chka_usd_7d`, and only the app report exposes install metrics such as
`conversions`.

The `advertiser_report_hourly` and `web_report_hourly` streams add the `hour` column for a
per-day-and-hour breakdown of campaign spend and traffic metrics. Like the daily streams,
they request cohort mode (`day_column=day`), but they only pull base spend and traffic
metrics, not the `sales_0d`/`roas_7d`-style cohort attribution columns. Note that AppLovin's
documentation lists `hour` only for publisher reports, but the advertiser endpoints serve
it as well.

### Incremental syncs and restated data

Every stream requests one day at a time, so each record belongs to a single date.
All report streams except `asset_report_daily` cursor on the API's native `day` column
(hourly records stay day-sliced — each day's sync returns that day's 24 hourly rows);
`asset_report_daily` has no day dimension, so the connector adds the requested date as
`date` and cursors on that.

AppLovin restates recent metrics as attribution data arrives, so the `lookback_window`
re-requests the most recent days on every sync. With a deduplicating sync mode, the
composite primary keys cause restated rows to overwrite the previously synced values.
Data for yesterday is stable after 06:00 UTC.

### Request windows

AppLovin serves a limited history, and dates outside the window return an error rather than
an empty result:

| Endpoint | Window |
|----------|--------|
| `/report` | 45 days (30 days for the `hour` column, so `advertiser_report_hourly` clamps to 30) |
| `/webReport` | 90 days (30 days for the `hour` column, so `web_report_hourly` clamps to 30) |
| `/assetAnalyticsReport` | 45 days |

The connector clamps `start_date` to the oldest day each endpoint still serves, so a
`start_date` further back than the window syncs the available history instead of failing.
Backfilling more history than the window allows is not possible through this API.

### Requesting other columns

Each stream requests a fixed column set. AppLovin exposes many more columns, including
longer attribution windows. To add them, edit the stream's `columns` request parameter and
the corresponding schema in `manifest.yaml`; the schemas allow additional properties, so
extra columns pass through even if they are not declared.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                           | Subject                                                                             |
| :------ | :--------- | :----------------------------------------------------- | :---------------------------------------------------------------------------------- |
| 0.1.0   | 2026-06-29 | [81418](https://github.com/airbytehq/airbyte/pull/81418) | Initial release: `advertiser_report_daily`, `advertiser_report_hourly`, `web_report_daily`, `web_report_hourly`, `asset_report_daily` |

</details>
