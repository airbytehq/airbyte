# Bing Ads
This page contains the setup guide and reference information for the Bing Ads source connector.

## Setup guide
### Step 1: Set up Bing Ads
1. [Register your application](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-register?view=bingads-13) in the Azure portal.
2. [Request user consent](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-consent?view=bingads-13l) to get the authorization code.
3. Use the authorization code to [get a refresh token](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-get-tokens?view=bingads-13).

:::note

The refresh token expires in 90 days. Repeat the authorization process to get a new refresh token. The full authentication process described [here](https://docs.microsoft.com/en-us/advertising/guides/get-started?view=bingads-13#access-token).

:::

4. Get your [Microsoft developer token](https://docs.microsoft.com/en-us/advertising/guides/get-started?view=bingads-13#get-developer-token).
5. If your OAuth app has a custom tenant and you cannot use Microsoft’s recommended common tenant, use the custom tenant in the **Tenant ID** field when you set up the connector.

:::info

The tenant is used in the authentication URL, for example: `https://login.microsoftonline.com/<tenant>/oauth2/v2.0/authorize`

:::

### Step 2: Set up the source connector in Airbyte

<!-- env:cloud -->
**For Airbyte Cloud:**
1. Log in to your [Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Bing Ads** from the **Source type** dropdown.
4. Enter a name for your source.
5. For **Tenant ID**, enter the custom tenant or use the common tenant.
6. Add the developer token from [Step 1](#step-1-set-up-bing-ads).
7. For **Replication Start Date**, enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
8. Click **Authenticate your Bing Ads account**.
9. Log in and authorize the Bing Ads account.
10. Click **Set up source**.  
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
8. Click **Set up source**.
<!-- /env:oss -->

## Supported sync modes
The Bing Ads source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/glossary#full-refresh-sync)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams
The Bing Ads source connector supports the following streams. For more information, see the [Bing Ads API](https://docs.microsoft.com/en-us/advertising/guides/?view=bingads-13).

### Basic streams
- [accounts](https://docs.microsoft.com/en-us/advertising/customer-management-service/searchaccounts?view=bingads-13)
- [ad_groups](https://docs.microsoft.com/en-us/advertising/campaign-management-service/getadgroupsbycampaignid?view=bingads-13)
- [ads](https://docs.microsoft.com/en-us/advertising/campaign-management-service/getadsbyadgroupid?view=bingads-13)
- [campaigns](https://docs.microsoft.com/en-us/advertising/campaign-management-service/getcampaignsbyaccountid?view=bingads-13)

### Report Streams
- [account_performance_report_hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
- [account_performance_report_daily](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
- [account_performance_report_weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
- [account_performance_report_monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
- [ad_group_performance_report_hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
- [ad_group_performance_report_daily](https://docs.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
- [ad_group_performance_report_weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
- [ad_group_performance_report_monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
- [ad_performance_report_hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/adperformancereportrequest?view=bingads-13)
- [ad_performance_report_daily](https://docs.microsoft.com/en-us/advertising/reporting-service/adperformancereportrequest?view=bingads-13)
- [ad_performance_report_weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/adperformancereportrequest?view=bingads-13)
- [ad_performance_report_monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/adperformancereportrequest?view=bingads-13)
- [budget_summary_report](https://docs.microsoft.com/en-us/advertising/reporting-service/budgetsummaryreportrequest?view=bingads-13)
- [campaign_performance_report_hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
- [campaign_performance_report_daily](https://docs.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
- [campaign_performance_report_weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
- [campaign_performance_report_monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
- [keyword_performance_report_hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/keywordperformancereportrequest?view=bingads-13)
- [keyword_performance_report_daily](https://docs.microsoft.com/en-us/advertising/reporting-service/keywordperformancereportrequest?view=bingads-13)
- [keyword_performance_report_weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/keywordperformancereportrequest?view=bingads-13)
- [keyword_performance_report_monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/keywordperformancereportrequest?view=bingads-13)

### Report aggregation
All reports synced by this connector can be [aggregated](https://docs.microsoft.com/en-us/advertising/reporting-service/reportaggregation?view=bingads-13) using hourly, daily, weekly, or monthly time windows.

For example, if you select a report with daily aggregation, the report will contain a row for each day for the duration of the report. Each row will indicate the number of impressions recorded on that day.

A report's aggregation window is indicated in its name. For example, `account_performance_report_hourly` is the Account Performance Reported aggregated using an hourly window.

## Performance considerations
The Bing Ads API limits the number of requests for all Microsoft Advertising clients. You can find detailed info [here](https://docs.microsoft.com/en-us/advertising/guides/services-protocol?view=bingads-13#throttling).

## Changelog
| Version | Date       | Pull Request                                                                                                                     | Subject                                                                                                                    |
|:--------|:-----------|:---------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------|
| 0.1.18  | 2023-01-30 | [22073](https://github.com/airbytehq/airbyte/pull/22073)                                                                         | Fix null values in the `Keyword` column of `keyword_performance_report` streams                                            |
| 0.1.17  | 2022-12-10 | [20005](https://github.com/airbytehq/airbyte/pull/20005)                                                                         | Add `Keyword` to `keyword_performance_report` stream                                                                       |
| 0.1.16  | 2022-10-12 | [17873](https://github.com/airbytehq/airbyte/pull/17873)                                                                         | Fix: added missing campaign types in (Audience, Shopping and DynamicSearchAds) in campaigns stream                         |
| 0.1.15  | 2022-10-03 | [17505](https://github.com/airbytehq/airbyte/pull/17505)                                                                         | Fix: limit cache size for ServiceClient instances                                                                          |
| 0.1.14  | 2022-09-29 | [17403](https://github.com/airbytehq/airbyte/pull/17403)                                                                         | Fix: limit cache size for ReportingServiceManager instances                                                                |
| 0.1.13  | 2022-09-29 | [17386](https://github.com/airbytehq/airbyte/pull/17386)                                                                         | Migrate to per-stream states.                                                                                              |
| 0.1.12  | 2022-09-05 | [16335](https://github.com/airbytehq/airbyte/pull/16335)                                                                         | Added backoff for socket.timeout                                                                                           |
| 0.1.11  | 2022-08-25 | [15684](https://github.com/airbytehq/airbyte/pull/15684) (published in [15987](https://github.com/airbytehq/airbyte/pull/15987)) | Fixed log messages being unreadable                                                                                        |
| 0.1.10  | 2022-08-12 | [15602](https://github.com/airbytehq/airbyte/pull/15602)                                                                         | Fixed bug caused Hourly Reports to crash due to invalid fields set                                                         |
| 0.1.9   | 2022-08-02 | [14862](https://github.com/airbytehq/airbyte/pull/14862)                                                                         | Added missing columns                                                                                                      |
| 0.1.8   | 2022-06-15 | [13801](https://github.com/airbytehq/airbyte/pull/13801)                                                                         | All reports `hourly/daily/weekly/monthly` will be generated by default, these options are removed from input configuration |
| 0.1.7   | 2022-05-17 | [12937](https://github.com/airbytehq/airbyte/pull/12937)                                                                         | Added OAuth2.0 authentication method, removed `redirect_uri` from input configuration                                      |
| 0.1.6   | 2022-04-30 | [12500](https://github.com/airbytehq/airbyte/pull/12500)                                                                         | Improve input configuration copy                                                                                           |
| 0.1.5   | 2022-01-01 | [11652](https://github.com/airbytehq/airbyte/pull/11652)                                                                         | Rebump attempt after DockerHub failure at registring the 0.1.4                                                             |
| 0.1.4   | 2022-03-22 | [11311](https://github.com/airbytehq/airbyte/pull/11311)                                                                         | Added optional Redirect URI & Tenant ID to spec                                                                            |
| 0.1.3   | 2022-01-14 | [9510](https://github.com/airbytehq/airbyte/pull/9510)                                                                           | Fixed broken dependency that blocked connector's operations                                                                |
| 0.1.2   | 2021-12-14 | [8429](https://github.com/airbytehq/airbyte/pull/8429)                                                                           | Update titles and descriptions                                                                                             |
| 0.1.1   | 2021-08-31 | [5750](https://github.com/airbytehq/airbyte/pull/5750)                                                                           | Added reporting streams\)                                                                                                  |
| 0.1.0   | 2021-07-22 | [4911](https://github.com/airbytehq/airbyte/pull/4911)                                                                           | Initial release supported core streams \(Accounts, Campaigns, Ads, AdGroups\)                                              |
