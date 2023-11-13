# TikTok Marketing

This page guides you through the process of setting up the TikTok Marketing source connector.

## Prerequisites

<!-- env:cloud -->

**For Airbyte Cloud:**

- A Tiktok Ads Business account with permission to access data from accounts you want to sync
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

For the Production environment:

- Access token
- Secret
- App ID

To access the Sandbox environment:

- Access token
- Advertiser ID
<!-- /env:oss -->

## Setup guide

### Step 1: Set up TikTok

1. Create a TikTok For Business account: [Link](https://business-api.tiktok.com/portal/docs?rid=fgvgaumno25&id=1738855099573250) <!-- env:oss -->
2. Create developer application: [Link](https://business-api.tiktok.com/portal/docs?rid=fgvgaumno25&id=1738855242728450)
3. For a sandbox environment: create a Sandbox Ad Account [Link](https://business-api.tiktok.com/portal/docs?rid=fgvgaumno25&id=1738855331457026)
<!-- /env:oss -->

### Step 2: Set up the source connector in Airbyte

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Tiktok Marketing** from the Source type dropdown and enter a name for this connector.
4. Select `OAuth2.0` Authorization method, then click `Authenticate your account`.
5. Log in and Authorize to the Tiktok account
6. Choose required Start date
7. click `Set up source`.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Go to local Airbyte page.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the Set up the source page, enter the name for the connector and select **Tiktok Marketing** from the Source type dropdown.
4. Select `Production Access Token` or `Sandbox Access Token` Authorization method, then copy and paste info from step 1.
5. Choose required Start date
6. Click `Set up source`.
<!-- /env:oss -->

## Supported streams and sync modes

| Stream                                    | Environment  | Key                                        | Incremental |
|:------------------------------------------| ------------ |--------------------------------------------| :---------- |
| Advertisers                               | Prod,Sandbox | advertiser_id                              | No          |
| AdGroups                                  | Prod,Sandbox | adgroup_id                                 | Yes         |
| Ads                                       | Prod,Sandbox | ad_id                                      | Yes         |
| Campaigns                                 | Prod,Sandbox | campaign_id                                | Yes         |
| AdsReportsHourly                          | Prod,Sandbox | ad_id, stat_time_hour                      | Yes         |
| AdsReportsDaily                           | Prod,Sandbox | ad_id, stat_time_day                       | Yes         |
| AdsReportsLifetime                        | Prod,Sandbox | ad_id                                      | No          |
| AdvertisersReportsHourly                  | Prod         | advertiser_id, stat_time_hour              | Yes         |
| AdvertisersReportsDaily                   | Prod         | advertiser_id, stat_time_day               | Yes         |
| AdvertisersReportsLifetime                | Prod         | advertiser_id                              | No          |
| AdGroupsReportsHourly                     | Prod,Sandbox | adgroup_id, stat_time_hour                 | Yes         |
| AdGroupsReportsDaily                      | Prod,Sandbox | adgroup_id, stat_time_day                  | Yes         |
| AdGroupsReportsLifetime                   | Prod,Sandbox | adgroup_id                                 | No          |
| Audiences                                 | Prod,Sandbox | audience_id                                | No          |
| CampaignsReportsHourly                    | Prod,Sandbox | campaign_id, stat_time_hour                | Yes         |
| CampaignsReportsDaily                     | Prod,Sandbox | campaign_id, stat_time_day                 | Yes         |
| CampaignsReportsLifetime                  | Prod,Sandbox | campaign_id                                | No          |
| CreativeAssetsImages                      | Prod,Sandbox | image_id                                   | Yes         |
| CreativeAssetsMusic                       | Prod,Sandbox | music_id                                   | Yes         |
| CreativeAssetsPortfolios                  | Prod,Sandbox | creative_portfolio_id                      | No          |
| CreativeAssetsVideos                      | Prod,Sandbox | video_id                                   | Yes         |
| AdvertiserIds                             | Prod         | advertiser_id                              | Yes         |
| AdvertisersAudienceReportsDaily           | Prod         | advertiser_id, stat_time_day, gender, age  | Yes         |
| AdvertisersAudienceReportsByCountryDaily  | Prod         | advertiser_id, stat_time_day, country_code | Yes         |
| AdvertisersAudienceReportsByPlatformDaily | Prod         | advertiser_id, stat_time_day, platform     | Yes         |
| AdvertisersAudienceReportsLifetime        | Prod         | advertiser_id, gender, age                 | No          |
| AdGroupAudienceReportsDaily               | Prod,Sandbox | adgroup_id, stat_time_day, gender, age     | Yes         |
| AdGroupAudienceReportsByCountryDaily      | Prod,Sandbox | adgroup_id, stat_time_day, country_code    | Yes         |
| AdGroupAudienceReportsByPlatformDaily     | Prod,Sandbox | adgroup_id, stat_time_day, platform        | Yes         |
| AdsAudienceReportsDaily                   | Prod,Sandbox | ad_id, stat_time_day, gender, age          | Yes         |
| AdsAudienceReportsByCountryDaily          | Prod,Sandbox | ad_id, stat_time_day, country_code         | Yes         |
| AdsAudienceReportsByPlatformDaily         | Prod,Sandbox | ad_id, stat_time_day, platform             | Yes         |
| AdsAudienceReportsByProvinceDaily         | Prod,Sandbox | ad_id, stat_time_day, province_id          | Yes         |
| CampaignsAudienceReportsDaily             | Prod,Sandbox | campaign_id, stat_time_day, gender, age    | Yes         |
| CampaignsAudienceReportsByCountryDaily    | Prod,Sandbox | campaign_id, stat_time_day, country_code   | Yes         |
| CampaignsAudienceReportsByPlatformDaily   | Prod,Sandbox | campaign_id, stat_time_day, platform       | Yes         |

:::info

TikTok Reporting API has some [Data Latency](https://ads.tiktok.com/marketing_api/docs?id=1738864894606337), usually of about 11 hours.
It is recommended to use higher values of attribution window (used in Incremental Syncs), at least 3 days, to ensure that the connector updates metrics in already presented records.

:::

### Report Aggregation

Reports synced by this connector can use either hourly, daily, or lifetime granularities for aggregating performance data. For example, if you select the daily-aggregation flavor of a report, the report will contain a row for each day for the duration of the report. Each row will indicate the number of impressions recorded on that day.

## Performance considerations

The connector is restricted by [requests limitation](https://business-api.tiktok.com/portal/docs?rid=fgvgaumno25&id=1740029171730433). This connector should not run into TikTok Marketing API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                     |
|:--------|:-----------| :------------------------------------------------------- |:------------------------------------------------------------------------------------------------------------|
| 3.9.2   | 2023-11-02 | [32091](https://github.com/airbytehq/airbyte/pull/32091) | Fix incremental syncs; update docs; fix field type of `preview_url_expire_time` to `date-time`.             |
| 3.9.1   | 2023-10-25 | [31812](https://github.com/airbytehq/airbyte/pull/31812) | Update `support level` in `metadata`, removed duplicated `tracking_pixel_id` field from `Ads` stream schema |
| 3.9.0   | 2023-10-23 | [31623](https://github.com/airbytehq/airbyte/pull/31623) | Add AdsAudienceReportsByProvince stream and expand base report metrics                                      |
| 3.8.0   | 2023-10-19 | [31610](https://github.com/airbytehq/airbyte/pull/31610) | Add Creative Assets and Audiences streams                                                                   |
| 3.7.1   | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image                             |
| 3.7.0   | 2023-10-19 | [31493](https://github.com/airbytehq/airbyte/pull/31493) | Add fields to Ads stream                                                                                    |
| 3.6.0   | 2023-10-18 | [31537](https://github.com/airbytehq/airbyte/pull/31537) | Use default availability strategy                                                                           |
| 3.5.0   | 2023-10-16 | [31445](https://github.com/airbytehq/airbyte/pull/31445) | Apply minimum date restrictions                                                                             |
| 3.4.1   | 2023-08-04 | [29083](https://github.com/airbytehq/airbyte/pull/29083) | Added new `is_smart_performance_campaign` property to `ad groups` stream schema                             |
| 3.4.0   | 2023-07-13 | [27910](https://github.com/airbytehq/airbyte/pull/27910) | Added `include_deleted` config param - include deleted `ad_groups`, `ad`, `campaigns` to reports            |
| 3.3.1   | 2023-07-06 | [25423](https://github.com/airbytehq/airbyte/pull/25423) | add new fields to ad reports streams                                                                        |
| 3.3.0   | 2023-07-05 | [27988](https://github.com/airbytehq/airbyte/pull/27988) | Add `category_exclusion_ids` field to `ad_groups` schema.                                                   |
| 3.2.1   | 2023-05-26 | [26569](https://github.com/airbytehq/airbyte/pull/26569) | Fixed syncs with `advertiser_id` provided in input configuration                                            |
| 3.2.0   | 2023-05-25 | [26565](https://github.com/airbytehq/airbyte/pull/26565) | Change default value for `attribution window` to 3 days; add min/max validation                             |
| 3.1.0   | 2023-05-12 | [26024](https://github.com/airbytehq/airbyte/pull/26024) | Updated the `Ads` stream schema                                                                             |
| 3.0.1   | 2023-04-07 | [24712](https://github.com/airbytehq/airbyte/pull/24712) | Added `attribution window` for \*-reports streams                                                           |
| 3.0.0   | 2023-03-29 | [24630](https://github.com/airbytehq/airbyte/pull/24630) | Migrate to v1.3 API                                                                                         |
| 2.0.6   | 2023-03-30 | [22134](https://github.com/airbytehq/airbyte/pull/22134) | Add `country_code` and `platform` audience reports.                                                         |
| 2.0.5   | 2023-03-29 | [22863](https://github.com/airbytehq/airbyte/pull/22863) | Specified date formatting in specification                                                                  |
| 2.0.4   | 2023-02-23 | [22309](https://github.com/airbytehq/airbyte/pull/22309) | Add Advertiser ID to filter reports and streams                                                             |
| 2.0.3   | 2023-02-15 | [23091](https://github.com/airbytehq/airbyte/pull/23091) | Add more clear log message for 504 error                                                                    |
| 2.0.2   | 2023-02-02 | [22309](https://github.com/airbytehq/airbyte/pull/22309) | Chunk Advertiser IDs                                                                                        |
| 2.0.1   | 2023-01-27 | [22044](https://github.com/airbytehq/airbyte/pull/22044) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                 |
| 2.0.0   | 2022-12-20 | [20415](https://github.com/airbytehq/airbyte/pull/20415) | Update schema types for `AudienceReports` and `BasicReports` streams.                                       |
| 1.0.1   | 2022-12-16 | [20598](https://github.com/airbytehq/airbyte/pull/20598) | Remove Audience Reports with Hourly granularity due to deprecated dimension.                                |
| 1.0.0   | 2022-12-05 | [19758](https://github.com/airbytehq/airbyte/pull/19758) | Convert `mobile_app_id` from integer to string in AudienceReport streams.                                   |
| 0.1.17  | 2022-10-04 | [17557](https://github.com/airbytehq/airbyte/pull/17557) | Retry error 50002                                                                                           |
| 0.1.16  | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream state                                                                                 |
| 0.1.15  | 2022-08-30 | [16137](https://github.com/airbytehq/airbyte/pull/16137) | Fixed bug with normalization caused by unsupported nested cursor field                                      |
| 0.1.14  | 2022-06-29 | [13890](https://github.com/airbytehq/airbyte/pull/13890) | Removed granularity config option                                                                           |
| 0.1.13  | 2022-06-28 | [13650](https://github.com/airbytehq/airbyte/pull/13650) | Added video metrics to report streams                                                                       |
| 0.1.12  | 2022-05-24 | [13127](https://github.com/airbytehq/airbyte/pull/13127) | Fixed integration test                                                                                      |
| 0.1.11  | 2022-04-27 | [12838](https://github.com/airbytehq/airbyte/pull/12838) | Added end date configuration for tiktok                                                                     |
| 0.1.10  | 2022-05-07 | [12545](https://github.com/airbytehq/airbyte/pull/12545) | Removed odd production authenication method                                                                 |
| 0.1.9   | 2022-04-30 | [12500](https://github.com/airbytehq/airbyte/pull/12500) | Improve input configuration copy                                                                            |
| 0.1.8   | 2022-04-28 | [12435](https://github.com/airbytehq/airbyte/pull/12435) | updated spec descriptions                                                                                   |
| 0.1.7   | 2022-04-27 | [12380](https://github.com/airbytehq/airbyte/pull/12380) | fixed spec descriptions and documentation                                                                   |
| 0.1.6   | 2022-04-19 | [11378](https://github.com/airbytehq/airbyte/pull/11378) | updated logic for stream initializations, fixed errors in schemas, updated SAT and unit tests               |
| 0.1.5   | 2022-02-17 | [10398](https://github.com/airbytehq/airbyte/pull/10398) | Add Audience reports                                                                                        |
| 0.1.4   | 2021-12-30 | [7636](https://github.com/airbytehq/airbyte/pull/7636)   | Add OAuth support                                                                                           |
| 0.1.3   | 2021-12-10 | [8425](https://github.com/airbytehq/airbyte/pull/8425)   | Update title, description fields in spec                                                                    |
| 0.1.2   | 2021-12-02 | [8292](https://github.com/airbytehq/airbyte/pull/8292)   | Support reports                                                                                             |
| 0.1.1   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)   | Remove base-python dependencies                                                                             |
| 0.1.0   | 2021-09-18 | [5887](https://github.com/airbytehq/airbyte/pull/5887)   | Release TikTok Marketing CDK Connector                                                                      |
