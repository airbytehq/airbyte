# Bing Ads

This page guides you through the process of setting up the Bing Ads source connector.

## Prerequisites (Airbyte Cloud)
* A Bing Ads account with permission to access data from accounts you want to sync 

## Prerequisites (Airbyte Open Source)
* Tenant ID 
* Developer Token
* Client ID
* Client Secret
* Refresh Token
* Reports replication start date

## Step 1: Set up Bing Ads

1. Create a developer application using the instructions for [registering an application](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-register?view=bingads-13) in Azure portal
2. Perform [these steps](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-consent?view=bingads-13l) to get auth code, and use that to [get a refresh token](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-get-tokens?view=bingads-13). For reference, the full authentication process described [here](https://docs.microsoft.com/en-us/advertising/guides/get-started?view=bingads-13#access-token). Be aware that the refresh token will expire in 90 days. You need to repeat the auth process to get a new refresh token.
3. Find your Microsoft developer token by following [these instructions](https://docs.microsoft.com/en-us/advertising/guides/get-started?view=bingads-13#get-developer-token)
4. Optionally, if your oauth app lives under a custom tenant which cannot use Microsoft's recommended `common` tenant, make sure to get the tenant ID ready for input when configuring the connector. The tenant will be used in the auth URL e.g: `https://login.microsoftonline.com/<tenant>/oauth2/v2.0/authorize`.

## Step 2: Set up the source connector in Airbyte

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Bing Ads** from the Source type dropdown and enter a name for this connector.
4. Add Tenant ID
5. Click `Authenticate your account`.
6. Log in and Authorize to the BingAds account
7. Choose required Start date
8. click `Set up source`.

**For Airbyte OSS:**

1. Go to local Airbyte page.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**. 
3. On the Set up the source page, enter the name for the connector and select **Bing Ads** from the Source type dropdown. 
4. Add Tenant ID
5. Copy and paste info from step 1:
   * client ID 
   * client secret 
   * refresh_token
   * A developer token
7. Choose required Start date and type of aggregation report
8. Click `Set up source`.

## Supported sync modes

The Bing Ads source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
 - Full Refresh
 - Incremental

## Supported Streams
Basic streams:
* [accounts](https://docs.microsoft.com/en-us/advertising/customer-management-service/searchaccounts?view=bingads-13)
* [campaigns](https://docs.microsoft.com/en-us/advertising/campaign-management-service/getcampaignsbyaccountid?view=bingads-13)
* [ad_groups](https://docs.microsoft.com/en-us/advertising/campaign-management-service/getadgroupsbycampaignid?view=bingads-13)
* [ads](https://docs.microsoft.com/en-us/advertising/campaign-management-service/getadsbyadgroupid?view=bingads-13)

Report Streams:
* [budget_summary_report](https://docs.microsoft.com/en-us/advertising/reporting-service/budgetsummaryreportrequest?view=bingads-13)
* [account_performance_report_hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
* [account_performance_report_daily](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
* [account_performance_report_weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
* [account_performance_report_monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
* [ad_group_performance_report_hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
* [ad_group_performance_report_daily](https://docs.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
* [ad_group_performance_report_weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
* [ad_group_performance_report_monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
* [ad_performance_report_hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/adperformancereportrequest?view=bingads-13)
* [ad_performance_report_daily](https://docs.microsoft.com/en-us/advertising/reporting-service/adperformancereportrequest?view=bingads-13)
* [ad_performance_report_weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/adperformancereportrequest?view=bingads-13)
* [ad_performance_report_monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/adperformancereportrequest?view=bingads-13)
* [campaign_performance_report_hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
* [campaign_performance_report_daily](https://docs.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
* [campaign_performance_report_weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
* [campaign_performance_report_monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
* [keyword_performance_report_hourly](https://docs.microsoft.com/en-us/advertising/reporting-service/keywordperformancereportrequest?view=bingads-13)
* [keyword_performance_report_daily](https://docs.microsoft.com/en-us/advertising/reporting-service/keywordperformancereportrequest?view=bingads-13)
* [keyword_performance_report_weekly](https://docs.microsoft.com/en-us/advertising/reporting-service/keywordperformancereportrequest?view=bingads-13)
* [keyword_performance_report_monthly](https://docs.microsoft.com/en-us/advertising/reporting-service/keywordperformancereportrequest?view=bingads-13)

For more information, see the [Bing Ads API](https://docs.microsoft.com/en-us/advertising/guides/?view=bingads-13).

### Report Aggregation
All reports synced by this connector can be aggregated using hourly, daily, weekly, or monthly windows. Performance data is aggregated using the selected window. For example, if you select the daily-aggregation flavor of a report, the report will contain a row for each day for the duration of the report. Each row will indicate the number of impressions recorded on that day.   

A report's aggregation window is indicated in its name e.g: `account_performance_report_hourly` is the Account Performance Reported aggregated using an hourly window.

### Performance considerations

API limits number of requests for all Microsoft Advertising clients. You can find detailied info [here](https://docs.microsoft.com/en-us/advertising/guides/services-protocol?view=bingads-13#throttling)

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                                    |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------|
| 0.1.8   | 2022-06-15 | [13801](https://github.com/airbytehq/airbyte/pull/13801) | All reports `hourly/daily/weekly/monthly` will be generated by default, these options are removed from input configuration |
| 0.1.7   | 2022-05-17 | [12937](https://github.com/airbytehq/airbyte/pull/12937) | Added OAuth2.0 authentication method, removed `redirect_uri` from input configuration                                      |
| 0.1.6   | 2022-04-30 | [12500](https://github.com/airbytehq/airbyte/pull/12500) | Improve input configuration copy                                                                                           |
| 0.1.5   | 2022-01-01 | [11652](https://github.com/airbytehq/airbyte/pull/11652) | Rebump attempt after DockerHub failure at registring the 0.1.4                                                             |
| 0.1.4   | 2022-03-22 | [11311](https://github.com/airbytehq/airbyte/pull/11311) | Added optional Redirect URI & Tenant ID to spec                                                                            |
| 0.1.3   | 2022-01-14 | [9510](https://github.com/airbytehq/airbyte/pull/9510)   | Fixed broken dependency that blocked connector's operations                                                                |
| 0.1.2   | 2021-12-14 | [8429](https://github.com/airbytehq/airbyte/pull/8429)   | Update titles and descriptions                                                                                             |
| 0.1.1   | 2021-08-31 | [5750](https://github.com/airbytehq/airbyte/pull/5750)   | Added reporting streams\)                                                                                                  |
| 0.1.0   | 2021-07-22 | [4911](https://github.com/airbytehq/airbyte/pull/4911)   | Initial release supported core streams \(Accounts, Campaigns, Ads, AdGroups\)                                              |

