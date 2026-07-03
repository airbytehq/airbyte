# AppLovin Ads

This page contains the setup guide and reference information for the AppLovin Ads source connector.

It covers AppLovin's advertising (growth) side only — monetization (MAX) reporting is not implemented. It syncs advertising reporting data from AppLovin's [Reporting API](https://support.applovin.com/en/growth/promoting-your-websites/api/reporting-api) and [Asset Reporting API](https://support.applovin.com/en/growth/promoting-your-websites/api/asset-reporting-api).

## Prerequisites

- An AppLovin account with access to reporting.
- A **Report Key** (API key). Find it in the AppLovin dashboard: click your account in the top right and select **Keys**.

## Setup guide

### Step 1: Get your Report Key

In the AppLovin dashboard, click your account name (top right) → **Keys** and copy your **Report Key**.

### Step 2: Set up the source in Airbyte

1. In Airbyte, click **Sources** → **+ New source** and select **AppLovin Ads**.
2. Enter your **Report Key**.
3. For **Start Date**, enter a `YYYY-MM-DD` date. Leave **End Date** blank to sync up to today.
4. Optionally adjust the **Lookback Window** and the column lists for each report.

## Supported sync modes

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |

Both streams progress one day per request. `advertiser_report_daily` cursors on the Reporting API's native `day` column; `asset_report_daily` injects a `date` field (the requested day) since the Asset Analytics report has no day dimension. The **Lookback Window** re-pulls the configured number of prior days on each incremental sync to capture late-attributed data.

## Streams

| Stream                    | Endpoint                | Description                                          |
| :------------------------ | :---------------------- | :--------------------------------------------------- |
| `advertiser_report_daily` | `/report`               | Advertiser performance report (Reporting API).       |
| `asset_report_daily`      | `/assetAnalyticsReport` | Asset-level performance report (Asset Reporting API).|

The full set of documented columns is requested and typed in each stream's schema. Schemas are also permissive (`additionalProperties: true`), so any column not explicitly typed still passes through.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject         |
| :------ | :--------- | :----------- | :-------------- |
| 0.1.0   | 2026-06-29 |              | Initial release |

</details>
