# Bing Ads

<HideInUI>

This page contains the setup guide and reference information for the Bing Ads source connector.

</HideInUI>

## Prerequisites
- Microsoft Advertising account
- Microsoft Developer Token

## Setup guide

<!-- env:oss -->

For Airbyte Open Source set up your application to get **Client ID**, **Client Secret**, **Refresh Token** 

1. [Register your application](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-register?view=bingads-13) in the Azure portal.
2. [Request user consent](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-consent?view=bingads-13l) to get the authorization code.
3. Use the authorization code to [get a refresh token](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-get-tokens?view=bingads-13).

:::note

The refresh token expires in 90 days. Repeat the authorization process to get a new refresh token. The full authentication process described [here](https://docs.microsoft.com/en-us/advertising/guides/get-started?view=bingads-13#access-token).
Please be sure to authenticate with the email (personal or work) that you used to sign in to the Bing ads/Microsoft ads platform.
:::

<!-- /env:oss -->

### Step 1: Set up Bing Ads

1. Get your [Microsoft developer token](https://docs.microsoft.com/en-us/advertising/guides/get-started?view=bingads-13#get-developer-token). To use Bing Ads APIs, you must have a developer token and valid user credentials. See [Microsoft Advertising docs](https://docs.microsoft.com/en-us/advertising/guides/get-started?view=bingads-13#get-developer-token) for more info.
   1. Sign in with [Super Admin](https://learn.microsoft.com/en-us/advertising/guides/account-hierarchy-permissions?view=bingads-13#user-roles-permissions) credentials at the [Microsoft Advertising Developer Portal](https://developers.ads.microsoft.com/Account) account tab. 
   2. Choose the user that you want associated with the developer token. Typically an application only needs one universal token regardless how many users will be supported. 
   3. Click on the Request Token button.

2. If your OAuth app has a custom tenant, and you cannot use Microsoft’s recommended common tenant, use the custom tenant in the **Tenant ID** field when you set up the connector.

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
7. For **Reports Replication Start Date**,  enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data from previous and current calendar years.
8. For **Lookback window** (also known as attribution or conversion window) enter the number of **days** to look into the past. If your conversion window has an hours/minutes granularity, round it up to the number of days exceeding. If you're not using performance report streams in incremental mode and Reports Start Date is not provided, let it with 0 default value.
9. For *Custom Reports* - see [custom reports](#custom-reports) section, list of custom reports object:
   1. For *Report Name* enter the name that you want for your custom report.
   2. For *Reporting Data Object* add the Bing Ads Reporting Object that you want to sync in the custom report.
   3. For *Columns* add list columns of Reporting Data Object that you want to see in the custom report.
   4. For *Aggregation* add time aggregation. See [report aggregation](#report-aggregation) section.
10. Click **Authenticate your Bing Ads account**.
11. Log in and authorize the Bing Ads account.
12. Click **Set up source**.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Log in to your Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Bing Ads** from the **Source type** dropdown.
4. Enter a name for your source.
5. For **Tenant ID**, enter the custom tenant or use the common tenant.
6. Enter the **Client ID**, **Client Secret**, **Refresh Token**, and **Developer Token** from [Step 1](#step-1-set-up-bing-ads).
7. For **Reports Replication Start Date**, enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data from previous and current calendar years.
8. For **Lookback window** (also known as attribution or conversion window) enter the number of **days** to look into the past. If your conversion window has an hours/minutes granularity, round it up to the number of days exceeding. If you're not using performance report streams in incremental mode and Reports Start Date is not provided, let it with 0 default value.
9. For *Custom Reports* - see [custom reports](#custom-reports) section:
   1. For *Report Name* enter the name that you want for your custom report.
   2. For *Reporting Data Object* add the Bing Ads Reporting Object that you want to sync in the custom report.
   3. For *Columns* add columns of Reporting Data Object that you want to see in the custom report.
   4. For *Aggregation* select time aggregation. See [report aggregation](#report-aggregation) section.

10. Click **Set up source**.
<!-- /env:oss -->

<HideInUI>

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

- [Account Performance Report Hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
- [Account Performance Report Daily](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
- [Account Performance Report Weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
- [Account Performance Report Monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
- [Account Impression Performance Report Hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
- [Account Impression Performance Report Daily](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
- [Account Impression Performance Report Weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
- [Account Impression Performance Report Monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
- [Ad Group Performance Report Hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
- [Ad Group Performance Report Daily](https://docs.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
- [Ad Group Performance Report Weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
- [Ad Group Performance Report Monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
- [Ad Group Impression Performance Report Hourly](https://learn.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
- [Ad Group Impression Performance Report Daily](https://learn.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
- [Ad Group Impression Performance Report Weekly](https://learn.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
- [Ad Group Impression Performance Report Monthly](https://learn.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
- [Ad Performance Report Hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/adperformancereportrequest?view=bingads-13)
- [Ad Performance Report Daily](https://docs.microsoft.com/en-us/advertising/reporting-service/adperformancereportrequest?view=bingads-13)
- [Ad Performance Report Weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/adperformancereportrequest?view=bingads-13)
- [Ad Performance Report Monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/adperformancereportrequest?view=bingads-13)
- [Age Gender Audience Report Hourly](https://learn.microsoft.com/en-us/advertising/reporting-service/agegenderaudiencereportrequest?view=bingads-13)
- [Age Gender Audience Report Daily](https://learn.microsoft.com/en-us/advertising/reporting-service/agegenderaudiencereportrequest?view=bingads-13)
- [Age Gender Audience Report Weekly](https://learn.microsoft.com/en-us/advertising/reporting-service/agegenderaudiencereportrequest?view=bingads-13)
- [Age Gender Audience Report Monthly](https://learn.microsoft.com/en-us/advertising/reporting-service/agegenderaudiencereportrequest?view=bingads-13)
- [Geographic Performance Report Hourly](https://learn.microsoft.com/en-us/advertising/reporting-service/geographicperformancereportrequest?view=bingads-13)
- [Geographic Performance Report Daily](https://learn.microsoft.com/en-us/advertising/reporting-service/geographicperformancereportrequest?view=bingads-13)
- [Geographic Performance Report Weekly](https://learn.microsoft.com/en-us/advertising/reporting-service/geographicperformancereportrequest?view=bingads-13)
- [Geographic Performance Report Monthly](https://learn.microsoft.com/en-us/advertising/reporting-service/geographicperformancereportrequest?view=bingads-13)
- [Budget Summary Report](https://docs.microsoft.com/en-us/advertising/reporting-service/budgetsummaryreportrequest?view=bingads-13)
- [Campaign Performance Report Hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
- [Campaign Performance Report Daily](https://docs.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
- [Campaign Performance Report Weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
- [Campaign Performance Report Monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
- [Campaign Impression Performance Report Hourly](https://learn.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
- [Campaign Impression Performance Report Daily](https://learn.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
- [Campaign Impression Performance Report Weekly](https://learn.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
- [Campaign Impression Performance Report Monthly](https://learn.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
- [Keyword Performance Report Hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/keywordperformancereportrequest?view=bingads-13)
- [Keyword Performance Report Daily](https://docs.microsoft.com/en-us/advertising/reporting-service/keywordperformancereportrequest?view=bingads-13)
- [Keyword Performance Report Weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/keywordperformancereportrequest?view=bingads-13)
- [Keyword Performance Report Monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/keywordperformancereportrequest?view=bingads-13)
- [User Location Performance Report Hourly](https://learn.microsoft.com/en-us/advertising/reporting-service/userlocationperformancereportrequest?view=bingads-13)
- [User Location Performance Report Daily](https://learn.microsoft.com/en-us/advertising/reporting-service/userlocationperformancereportrequest?view=bingads-13)
- [User Location Performance Report Weekly](https://learn.microsoft.com/en-us/advertising/reporting-service/userlocationperformancereportrequest?view=bingads-13)
- [User Location Performance Report Monthly](https://learn.microsoft.com/en-us/advertising/reporting-service/userlocationperformancereportrequest?view=bingads-13)
- [Search Query Performance Report Hourly](https://learn.microsoft.com/en-us/advertising/reporting-service/searchqueryperformancereportrequest?view=bingads-13)
- [Search Query Performance Report Daily](https://learn.microsoft.com/en-us/advertising/reporting-service/searchqueryperformancereportrequest?view=bingads-13)
- [Search Query Performance Report Weekly](https://learn.microsoft.com/en-us/advertising/reporting-service/searchqueryperformancereportrequest?view=bingads-13)
- [Search Query Performance Report Monthly](https://learn.microsoft.com/en-us/advertising/reporting-service/searchqueryperformancereportrequest?view=bingads-13)

### Custom Reports
You can build your own report by providing:
- *Report Name* - name of the stream
- *Reporting Data Object* - Bing Ads reporting data object that you can find [here](https://learn.microsoft.com/en-us/advertising/reporting-service/reporting-data-objects?view=bingads-13). All data object with ending ReportRequest can be used as data object in custom reports.
- *Columns* - Reporting object columns that you want to sync. You can find it on ReportRequest data object page by clicking the ...ReportColumn link in [Bing Ads docs](https://learn.microsoft.com/en-us/advertising/reporting-service/reporting-value-sets?view=bingads-13). 
The report must include the Required Columns (you can find it under list of all columns of reporting object) at a minimum. As a general rule, each report must include at least one attribute column and at least one non-impression share performance statistics column. Be careful you can't add extra columns that not specified in Bing Ads docs and not all fields can be skipped.
- *Aggregation* - Hourly, Daily, Weekly, Monthly, DayOfWeek, HourOfDay, WeeklyStartingMonday, Summary. See [report aggregation](#report-aggregation).

### Report aggregation

All reports synced by this connector can be [aggregated](https://docs.microsoft.com/en-us/advertising/reporting-service/reportaggregation?view=bingads-13) using hourly, daily, weekly, or monthly time windows.

For example, if you select a report with daily aggregation, the report will contain a row for each day for the duration of the report. Each row will indicate the number of impressions recorded on that day.

A report's aggregation window is indicated in its name. For example, `account_performance_report_hourly` is the Account Performance Reported aggregated using an hourly window.

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about Bing Ads connector limitations and troubleshooting.
</summary>

### Connector limitations

#### Rate limiting

The Bing Ads API limits the number of requests for all Microsoft Advertising clients. You can find detailed info [here](https://docs.microsoft.com/en-us/advertising/guides/services-protocol?view=bingads-13#throttling).

### Troubleshooting

* Check out common troubleshooting issues for the Bing Ads source connector on our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions).

</details>

## Changelog

| Version | Date       | Pull Request                                                                                                                     | Subject                                                                                                                                         |
|:--------|:-----------|:---------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------|
| 2.0.1   | 2023-11-16 | [32597](https://github.com/airbytehq/airbyte/pull/32597)                                                                         | Fix start date parsing from stream state                                                                                                        |
| 2.0.0   | 2023-11-07 | [31995](https://github.com/airbytehq/airbyte/pull/31995)                                                                         | Schema update for Accounts, Campaigns and Search Query Performance Report streams.  Convert `date` and `date-time` fields to standard `RFC3339` |
| 1.13.0  | 2023-11-13 | [32306](https://github.com/airbytehq/airbyte/pull/32306)                                                                         | Add Custom reports and decrease backoff max tries number                                                                                        |
| 1.12.1  | 2023-11-10 | [32422](https://github.com/airbytehq/airbyte/pull/32422)                                                                         | Normalize numeric values in reports                                                                                                             |
| 1.12.0  | 2023-11-09 | [32340](https://github.com/airbytehq/airbyte/pull/32340)                                                                         | Remove default start date in favor of Time Period - Last Year and This Year, if start date is not provided                                      |
| 1.11.0  | 2023-11-06 | [32201](https://github.com/airbytehq/airbyte/pull/32201)                                                                         | Skip broken CSV report files                                                                                                                    |
| 1.10.0  | 2023-11-06 | [32148](https://github.com/airbytehq/airbyte/pull/32148)                                                                         | Add new fields to stream Ads: "BusinessName", "CallToAction", "Headline", "Images", "Videos", "Text"                                            |
| 1.9.0   | 2023-11-03 | [32131](https://github.com/airbytehq/airbyte/pull/32131)                                                                         | Add  "CampaignId", "AccountId", "CustomerId" fields to Ad Groups, Ads and Campaigns streams.                                                    |
| 1.8.0   | 2023-11-02 | [32059](https://github.com/airbytehq/airbyte/pull/32059)                                                                         | Add new streams `CampaignImpressionPerformanceReport` (daily, hourly, weekly, monthly)                                                          |
| 1.7.1   | 2023-11-02 | [32088](https://github.com/airbytehq/airbyte/pull/32088)                                                                         | Raise config error when user does not have accounts                                                                                             |
| 1.7.0   | 2023-11-01 | [32027](https://github.com/airbytehq/airbyte/pull/32027)                                                                         | Add new streams `AdGroupImpressionPerformanceReport`                                                                                            |
| 1.6.0   | 2023-10-31 | [32008](https://github.com/airbytehq/airbyte/pull/32008)                                                                         | Add new streams `Keywords`                                                                                                                      |
| 1.5.0   | 2023-10-30 | [31952](https://github.com/airbytehq/airbyte/pull/31952)                                                                         | Add new streams `Labels`,  `App install ads`, `Keyword Labels`, `Campaign Labels`, `App Install Ad Labels`, `Ad Group Labels`                   |
| 1.4.0   | 2023-10-27 | [31885](https://github.com/airbytehq/airbyte/pull/31885)                                                                         | Add new stream: `AccountImpressionPerformanceReport` (daily, hourly, weekly, monthly)                                                           |
| 1.3.0   | 2023-10-26 | [31837](https://github.com/airbytehq/airbyte/pull/31837)                                                                         | Add new stream: `UserLocationPerformanceReport` (daily, hourly, weekly, monthly)                                                                |
| 1.2.0   | 2023-10-24 | [31783](https://github.com/airbytehq/airbyte/pull/31783)                                                                         | Add new stream: `SearchQueryPerformanceReport` (daily, hourly, weekly, monthly)                                                                 |
| 1.1.0   | 2023-10-24 | [31712](https://github.com/airbytehq/airbyte/pull/31712)                                                                         | Add new stream: `AgeGenderAudienceReport` (daily, hourly, weekly, monthly)                                                                      |
| 1.0.2   | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599)                                                                         | Base image migration: remove Dockerfile and use the python-connector-base image                                                                 |
| 1.0.1   | 2023-10-16 | [31432](https://github.com/airbytehq/airbyte/pull/31432)                                                                         | Remove primary keys from the geographic performance reports - complete what was missed in version 1.0.0                                         |
| 1.0.0   | 2023-10-11 | [31277](https://github.com/airbytehq/airbyte/pull/31277)                                                                         | Remove primary keys from the geographic performance reports.                                                                                    |
| 0.2.3   | 2023-09-28 | [30834](https://github.com/airbytehq/airbyte/pull/30834)                                                                         | Wrap auth error with the config error.                                                                                                          |
| 0.2.2   | 2023-09-27 | [30791](https://github.com/airbytehq/airbyte/pull/30791)                                                                         | Fix missing fields for geographic performance reports.                                                                                          |
| 0.2.1   | 2023-09-04 | [30128](https://github.com/airbytehq/airbyte/pull/30128)                                                                         | Add increasing download timeout if ReportingDownloadException occurs                                                                            |
| 0.2.0   | 2023-08-17 | [27619](https://github.com/airbytehq/airbyte/pull/27619)                                                                         | Add Geographic Performance Report                                                                                                               |
| 0.1.24  | 2023-06-22 | [27619](https://github.com/airbytehq/airbyte/pull/27619)                                                                         | Retry request after facing temporary name resolution error.                                                                                     |
| 0.1.23  | 2023-05-11 | [25996](https://github.com/airbytehq/airbyte/pull/25996)                                                                         | Implement a retry logic if SSL certificate validation fails.                                                                                    |
| 0.1.22  | 2023-05-08 | [24223](https://github.com/airbytehq/airbyte/pull/24223)                                                                         | Add CampaignLabels report column in campaign performance report                                                                                 |
| 0.1.21  | 2023-04-28 | [25668](https://github.com/airbytehq/airbyte/pull/25668)                                                                         | Add undeclared fields to accounts, campaigns, campaign_performance_report, keyword_performance_report and account_performance_report streams    |
| 0.1.20  | 2023-03-09 | [23663](https://github.com/airbytehq/airbyte/pull/23663)                                                                         | Add lookback window for performance reports in incremental mode                                                                                 |
| 0.1.19  | 2023-03-08 | [23868](https://github.com/airbytehq/airbyte/pull/23868)                                                                         | Add dimensional-type columns for reports.                                                                                                       |
| 0.1.18  | 2023-01-30 | [22073](https://github.com/airbytehq/airbyte/pull/22073)                                                                         | Fix null values in the `Keyword` column of `keyword_performance_report` streams                                                                 |
| 0.1.17  | 2022-12-10 | [20005](https://github.com/airbytehq/airbyte/pull/20005)                                                                         | Add `Keyword` to `keyword_performance_report` stream                                                                                            |
| 0.1.16  | 2022-10-12 | [17873](https://github.com/airbytehq/airbyte/pull/17873)                                                                         | Fix: added missing campaign types in (Audience, Shopping and DynamicSearchAds) in campaigns stream                                              |
| 0.1.15  | 2022-10-03 | [17505](https://github.com/airbytehq/airbyte/pull/17505)                                                                         | Fix: limit cache size for ServiceClient instances                                                                                               |
| 0.1.14  | 2022-09-29 | [17403](https://github.com/airbytehq/airbyte/pull/17403)                                                                         | Fix: limit cache size for ReportingServiceManager instances                                                                                     |
| 0.1.13  | 2022-09-29 | [17386](https://github.com/airbytehq/airbyte/pull/17386)                                                                         | Migrate to per-stream states.                                                                                                                   |
| 0.1.12  | 2022-09-05 | [16335](https://github.com/airbytehq/airbyte/pull/16335)                                                                         | Added backoff for socket.timeout                                                                                                                |
| 0.1.11  | 2022-08-25 | [15684](https://github.com/airbytehq/airbyte/pull/15684) (published in [15987](https://github.com/airbytehq/airbyte/pull/15987)) | Fixed log messages being unreadable                                                                                                             |
| 0.1.10  | 2022-08-12 | [15602](https://github.com/airbytehq/airbyte/pull/15602)                                                                         | Fixed bug caused Hourly Reports to crash due to invalid fields set                                                                              |
| 0.1.9   | 2022-08-02 | [14862](https://github.com/airbytehq/airbyte/pull/14862)                                                                         | Added missing columns                                                                                                                           |
| 0.1.8   | 2022-06-15 | [13801](https://github.com/airbytehq/airbyte/pull/13801)                                                                         | All reports `hourly/daily/weekly/monthly` will be generated by default, these options are removed from input configuration                      |
| 0.1.7   | 2022-05-17 | [12937](https://github.com/airbytehq/airbyte/pull/12937)                                                                         | Added OAuth2.0 authentication method, removed `redirect_uri` from input configuration                                                           |
| 0.1.6   | 2022-04-30 | [12500](https://github.com/airbytehq/airbyte/pull/12500)                                                                         | Improve input configuration copy                                                                                                                |
| 0.1.5   | 2022-01-01 | [11652](https://github.com/airbytehq/airbyte/pull/11652)                                                                         | Rebump attempt after DockerHub failure at registring the 0.1.4                                                                                  |
| 0.1.4   | 2022-03-22 | [11311](https://github.com/airbytehq/airbyte/pull/11311)                                                                         | Added optional Redirect URI & Tenant ID to spec                                                                                                 |
| 0.1.3   | 2022-01-14 | [9510](https://github.com/airbytehq/airbyte/pull/9510)                                                                           | Fixed broken dependency that blocked connector's operations                                                                                     |
| 0.1.2   | 2021-12-14 | [8429](https://github.com/airbytehq/airbyte/pull/8429)                                                                           | Update titles and descriptions                                                                                                                  |
| 0.1.1   | 2021-08-31 | [5750](https://github.com/airbytehq/airbyte/pull/5750)                                                                           | Added reporting streams\)                                                                                                                       |
| 0.1.0   | 2021-07-22 | [4911](https://github.com/airbytehq/airbyte/pull/4911)                                                                           | Initial release supported core streams \(Accounts, Campaigns, Ads, AdGroups\)                                                                   |

</HideInUI>