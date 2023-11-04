# Bing Ads

This page contains the setup guide and reference information for the Bing Ads source connector.

## Setup guide

### Step 1: Set up Bing Ads

1. [Register your application](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-register?view=bingads-13) in the Azure portal.
2. [Request user consent](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-consent?view=bingads-13l) to get the authorization code.
3. Use the authorization code to [get a refresh token](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-get-tokens?view=bingads-13).

:::note

The refresh token expires in 90 days. Repeat the authorization process to get a new refresh token. The full authentication process described [here](https://docs.microsoft.com/en-us/advertising/guides/get-started?view=bingads-13#access-token).
Please be sure to authenticate with the email (personal or work) that you used to sign in to the Bing ads/Microsoft ads platform.
:::

4. Get your [Microsoft developer token](https://docs.microsoft.com/en-us/advertising/guides/get-started?view=bingads-13#get-developer-token).
5. If your OAuth app has a custom tenant and you cannot use Microsoft’s recommended common tenant, use the custom tenant in the **Tenant ID** field when you set up the connector.

:::info

The tenant is used in the authentication URL, for example: `https://login.microsoftonline.com/<tenant>/oauth2/v2.0/authorize`

:::

### Step 2: Set up the source connector in Airbyte

<!-- env:cloud -->

**For Airbyte Cloud:**

1. Log in to your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Bing Ads** from the **Source type** dropdown.
4. Enter a name for your source.
5. For **Tenant ID**, enter the custom tenant or use the common tenant.
6. Add the developer token from [Step 1](#step-1-set-up-bing-ads).
7. For **Replication Start Date**, enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
8. For **Lookback window** (also known as attribution or conversion window) enter the number of **days** to look into the past. If your conversion window has an hours/minutes granularity, round it up to the number of days exceeding. If you're not using performance report streams in incremental mode, let it with 0 default value.
9. Click **Authenticate your Bing Ads account**.
10. Log in and authorize the Bing Ads account.
11. Click **Set up source**.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Log in to your Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Bing Ads** from the **Source type** dropdown.
4. Enter a name for your source.
5. For **Tenant ID**, enter the custom tenant or use the common tenant.
6. Enter the **Client ID**, **Client Secret**, **Refresh Token**, and **Developer Token** from [Step 1](#step-1-set-up-bing-ads).
7. For **Replication Start Date**, enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
8. For **Lookback window** (also known as attribution or conversion window) enter the number of **days** to look into the past. If your conversion window has an hours/minutes granularity, round it up to the number of days exceeding. If you're not using performance report streams in incremental mode, let it with 0 default value.
9. Click **Set up source**.
<!-- /env:oss -->

## Supported sync modes

The Bing Ads source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

The Bing Ads source connector supports the following streams. For more information, see the [Bing Ads API](https://docs.microsoft.com/en-us/advertising/guides/?view=bingads-13).

### Basic streams

- [Accounts](https://docs.microsoft.com/en-us/advertising/customer-management-service/searchaccounts?view=bingads-13)
- [Ad Groups](https://docs.microsoft.com/en-us/advertising/campaign-management-service/getadgroupsbycampaignid?view=bingads-13)
- [Ad Group Labels](https://learn.microsoft.com/en-us/advertising/bulk-service/ad-group-label?view=bingads-13)
- [Ads](https://docs.microsoft.com/en-us/advertising/campaign-management-service/getadsbyadgroupid?view=bingads-13)
- [App Install Ads](https://learn.microsoft.com/en-us/advertising/bulk-service/app-install-ad?view=bingads-13)
- [App Install Ad Labels](https://learn.microsoft.com/en-us/advertising/bulk-service/app-install-ad-label?view=bingads-13)
- [Campaigns](https://docs.microsoft.com/en-us/advertising/campaign-management-service/getcampaignsbyaccountid?view=bingads-13)
- [Campaign Labels](https://learn.microsoft.com/en-us/advertising/bulk-service/campaign-label?view=bingads-13)
- [Keywords](https://learn.microsoft.com/en-us/advertising/bulk-service/keyword?view=bingads-13)
- [Keyword Labels](https://learn.microsoft.com/en-us/advertising/bulk-service/keyword-label?view=bingads-13)
- [Labels](https://learn.microsoft.com/en-us/advertising/bulk-service/label?view=bingads-13)

### Report Streams

- [account_performance_report_hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
- [account_performance_report_daily](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
- [account_performance_report_weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
- [account_performance_report_monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
- [account_impression_performance_report_hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
- [account_impression_performance_report_daily](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
- [account_impression_performance_report_weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
- [account_impression_performance_report_monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
- [ad_group_performance_report_hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
- [ad_group_performance_report_daily](https://docs.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
- [ad_group_performance_report_weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
- [ad_group_performance_report_monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
- [ad_group_impression_performance_report_hourly](https://learn.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
- [ad_group_impression_performance_report_daily](https://learn.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
- [ad_group_impression_performance_report_weekly](https://learn.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
- [ad_group_impression_performance_report_monthly](https://learn.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
- [ad_performance_report_hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/adperformancereportrequest?view=bingads-13)
- [ad_performance_report_daily](https://docs.microsoft.com/en-us/advertising/reporting-service/adperformancereportrequest?view=bingads-13)
- [ad_performance_report_weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/adperformancereportrequest?view=bingads-13)
- [ad_performance_report_monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/adperformancereportrequest?view=bingads-13)
- [age_gender_audience_report_hourly](https://learn.microsoft.com/en-us/advertising/reporting-service/agegenderaudiencereportrequest?view=bingads-13)
- [age_gender_audience_report_daily](https://learn.microsoft.com/en-us/advertising/reporting-service/agegenderaudiencereportrequest?view=bingads-13)
- [age_gender_audience_report_weekly](https://learn.microsoft.com/en-us/advertising/reporting-service/agegenderaudiencereportrequest?view=bingads-13)
- [age_gender_audience_report_monthly](https://learn.microsoft.com/en-us/advertising/reporting-service/agegenderaudiencereportrequest?view=bingads-13)
- [geographic_performance_report_hourly](https://learn.microsoft.com/en-us/advertising/reporting-service/geographicperformancereportrequest?view=bingads-13)
- [geographic_performance_report_daily](https://learn.microsoft.com/en-us/advertising/reporting-service/geographicperformancereportrequest?view=bingads-13)
- [geographic_performance_report_weekly](https://learn.microsoft.com/en-us/advertising/reporting-service/geographicperformancereportrequest?view=bingads-13)
- [geographic_performance_report_monthly](https://learn.microsoft.com/en-us/advertising/reporting-service/geographicperformancereportrequest?view=bingads-13)
- [budget_summary_report](https://docs.microsoft.com/en-us/advertising/reporting-service/budgetsummaryreportrequest?view=bingads-13)
- [campaign_performance_report_hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
- [campaign_performance_report_daily](https://docs.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
- [campaign_performance_report_weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
- [campaign_performance_report_monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
- [campaign_impression_performance_report_hourly](https://learn.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
- [campaign_impression_performance_report_daily](https://learn.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
- [campaign_impression_performance_report_weekly](https://learn.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
- [campaign_impression_performance_report_monthly](https://learn.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
- [keyword_performance_report_hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/keywordperformancereportrequest?view=bingads-13)
- [keyword_performance_report_daily](https://docs.microsoft.com/en-us/advertising/reporting-service/keywordperformancereportrequest?view=bingads-13)
- [keyword_performance_report_weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/keywordperformancereportrequest?view=bingads-13)
- [keyword_performance_report_monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/keywordperformancereportrequest?view=bingads-13)
- [user_location_performance_report_hourly](https://learn.microsoft.com/en-us/advertising/reporting-service/userlocationperformancereportrequest?view=bingads-13)
- [user_location_performance_report_daily](https://learn.microsoft.com/en-us/advertising/reporting-service/userlocationperformancereportrequest?view=bingads-13)
- [user_location_performance_report_weekly](https://learn.microsoft.com/en-us/advertising/reporting-service/userlocationperformancereportrequest?view=bingads-13)
- [user_location_performance_report_monthly](https://learn.microsoft.com/en-us/advertising/reporting-service/userlocationperformancereportrequest?view=bingads-13)

### Report aggregation

All reports synced by this connector can be [aggregated](https://docs.microsoft.com/en-us/advertising/reporting-service/reportaggregation?view=bingads-13) using hourly, daily, weekly, or monthly time windows.

For example, if you select a report with daily aggregation, the report will contain a row for each day for the duration of the report. Each row will indicate the number of impressions recorded on that day.

A report's aggregation window is indicated in its name. For example, `account_performance_report_hourly` is the Account Performance Reported aggregated using an hourly window.

## Performance considerations

The Bing Ads API limits the number of requests for all Microsoft Advertising clients. You can find detailed info [here](https://docs.microsoft.com/en-us/advertising/guides/services-protocol?view=bingads-13#throttling).

## Changelog

| Version | Date       | Pull Request                                                                                                                     | Subject                                                                                                                                      |
|:--------|:-----------|:---------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------|
| 1.8.0   | 2023-11-02 | [32059](https://github.com/airbytehq/airbyte/pull/32059)                                                                         | Add new streams `CampaignImpressionPerformanceReport` (daily, hourly, weekly, monthly)                                                       |
| 1.7.1   | 2023-11-02 | [32088](https://github.com/airbytehq/airbyte/pull/32088)                                                                         | Raise config error when user does not have accounts                                                                                          |
| 1.7.0   | 2023-11-01 | [32027](https://github.com/airbytehq/airbyte/pull/32027)                                                                         | Add new streams `AdGroupImpressionPerformanceReport`                                                                                         |
| 1.6.0   | 2023-10-31 | [32008](https://github.com/airbytehq/airbyte/pull/32008)                                                                         | Add new streams `Keywords`                                                                                                                   |
| 1.5.0   | 2023-10-30 | [31952](https://github.com/airbytehq/airbyte/pull/31952)                                                                         | Add new streams `Labels`,  `App install ads`, `Keyword Labels`, `Campaign Labels`, `App Install Ad Labels`, `Ad Group Labels`                |
| 1.4.0   | 2023-10-27 | [31885](https://github.com/airbytehq/airbyte/pull/31885)                                                                         | Add new stream: `AccountImpressionPerformanceReport` (daily, hourly, weekly, monthly)                                                        |
| 1.3.0   | 2023-10-26 | [31837](https://github.com/airbytehq/airbyte/pull/31837)                                                                         | Add new stream: `UserLocationPerformanceReport` (daily, hourly, weekly, monthly)                                                             |
| 1.2.0   | 2023-10-24 | [31783](https://github.com/airbytehq/airbyte/pull/31783)                                                                         | Add new stream: `SearchQueryPerformanceReport` (daily, hourly, weekly, monthly)                                                              |
| 1.1.0   | 2023-10-24 | [31712](https://github.com/airbytehq/airbyte/pull/31712)                                                                         | Add new stream: `AgeGenderAudienceReport` (daily, hourly, weekly, monthly)                                                                   |
| 1.0.2   | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599)                                                                         | Base image migration: remove Dockerfile and use the python-connector-base image                                                              |
| 1.0.1   | 2023-10-16 | [31432](https://github.com/airbytehq/airbyte/pull/31432)                                                                         | Remove primary keys from the geographic performance reports - complete what was missed in version 1.0.0                                      |
| 1.0.0   | 2023-10-11 | [31277](https://github.com/airbytehq/airbyte/pull/31277)                                                                         | Remove primary keys from the geographic performance reports.                                                                                 |
| 0.2.3   | 2023-09-28 | [30834](https://github.com/airbytehq/airbyte/pull/30834)                                                                         | Wrap auth error with the config error.                                                                                                       |
| 0.2.2   | 2023-09-27 | [30791](https://github.com/airbytehq/airbyte/pull/30791)                                                                         | Fix missing fields for geographic performance reports.                                                                                       |
| 0.2.1   | 2023-09-04 | [30128](https://github.com/airbytehq/airbyte/pull/30128)                                                                         | Add increasing download timeout if ReportingDownloadException occurs                                                                         |
| 0.2.0   | 2023-08-17 | [27619](https://github.com/airbytehq/airbyte/pull/27619)                                                                         | Add Geographic Performance Report                                                                                                            |
| 0.1.24  | 2023-06-22 | [27619](https://github.com/airbytehq/airbyte/pull/27619)                                                                         | Retry request after facing temporary name resolution error.                                                                                  |
| 0.1.23  | 2023-05-11 | [25996](https://github.com/airbytehq/airbyte/pull/25996)                                                                         | Implement a retry logic if SSL certificate validation fails.                                                                                 |
| 0.1.22  | 2023-05-08 | [24223](https://github.com/airbytehq/airbyte/pull/24223)                                                                         | Add CampaignLabels report column in campaign performance report                                                                              |
| 0.1.21  | 2023-04-28 | [25668](https://github.com/airbytehq/airbyte/pull/25668)                                                                         | Add undeclared fields to accounts, campaigns, campaign_performance_report, keyword_performance_report and account_performance_report streams |
| 0.1.20  | 2023-03-09 | [23663](https://github.com/airbytehq/airbyte/pull/23663)                                                                         | Add lookback window for performance reports in incremental mode                                                                              |
| 0.1.19  | 2023-03-08 | [23868](https://github.com/airbytehq/airbyte/pull/23868)                                                                         | Add dimensional-type columns for reports.                                                                                                    |
| 0.1.18  | 2023-01-30 | [22073](https://github.com/airbytehq/airbyte/pull/22073)                                                                         | Fix null values in the `Keyword` column of `keyword_performance_report` streams                                                              |
| 0.1.17  | 2022-12-10 | [20005](https://github.com/airbytehq/airbyte/pull/20005)                                                                         | Add `Keyword` to `keyword_performance_report` stream                                                                                         |
| 0.1.16  | 2022-10-12 | [17873](https://github.com/airbytehq/airbyte/pull/17873)                                                                         | Fix: added missing campaign types in (Audience, Shopping and DynamicSearchAds) in campaigns stream                                           |
| 0.1.15  | 2022-10-03 | [17505](https://github.com/airbytehq/airbyte/pull/17505)                                                                         | Fix: limit cache size for ServiceClient instances                                                                                            |
| 0.1.14  | 2022-09-29 | [17403](https://github.com/airbytehq/airbyte/pull/17403)                                                                         | Fix: limit cache size for ReportingServiceManager instances                                                                                  |
| 0.1.13  | 2022-09-29 | [17386](https://github.com/airbytehq/airbyte/pull/17386)                                                                         | Migrate to per-stream states.                                                                                                                |
| 0.1.12  | 2022-09-05 | [16335](https://github.com/airbytehq/airbyte/pull/16335)                                                                         | Added backoff for socket.timeout                                                                                                             |
| 0.1.11  | 2022-08-25 | [15684](https://github.com/airbytehq/airbyte/pull/15684) (published in [15987](https://github.com/airbytehq/airbyte/pull/15987)) | Fixed log messages being unreadable                                                                                                          |
| 0.1.10  | 2022-08-12 | [15602](https://github.com/airbytehq/airbyte/pull/15602)                                                                         | Fixed bug caused Hourly Reports to crash due to invalid fields set                                                                           |
| 0.1.9   | 2022-08-02 | [14862](https://github.com/airbytehq/airbyte/pull/14862)                                                                         | Added missing columns                                                                                                                        |
| 0.1.8   | 2022-06-15 | [13801](https://github.com/airbytehq/airbyte/pull/13801)                                                                         | All reports `hourly/daily/weekly/monthly` will be generated by default, these options are removed from input configuration                   |
| 0.1.7   | 2022-05-17 | [12937](https://github.com/airbytehq/airbyte/pull/12937)                                                                         | Added OAuth2.0 authentication method, removed `redirect_uri` from input configuration                                                        |
| 0.1.6   | 2022-04-30 | [12500](https://github.com/airbytehq/airbyte/pull/12500)                                                                         | Improve input configuration copy                                                                                                             |
| 0.1.5   | 2022-01-01 | [11652](https://github.com/airbytehq/airbyte/pull/11652)                                                                         | Rebump attempt after DockerHub failure at registring the 0.1.4                                                                               |
| 0.1.4   | 2022-03-22 | [11311](https://github.com/airbytehq/airbyte/pull/11311)                                                                         | Added optional Redirect URI & Tenant ID to spec                                                                                              |
| 0.1.3   | 2022-01-14 | [9510](https://github.com/airbytehq/airbyte/pull/9510)                                                                           | Fixed broken dependency that blocked connector's operations                                                                                  |
| 0.1.2   | 2021-12-14 | [8429](https://github.com/airbytehq/airbyte/pull/8429)                                                                           | Update titles and descriptions                                                                                                               |
| 0.1.1   | 2021-08-31 | [5750](https://github.com/airbytehq/airbyte/pull/5750)                                                                           | Added reporting streams\)                                                                                                                    |
| 0.1.0   | 2021-07-22 | [4911](https://github.com/airbytehq/airbyte/pull/4911)                                                                           | Initial release supported core streams \(Accounts, Campaigns, Ads, AdGroups\)                                                                |