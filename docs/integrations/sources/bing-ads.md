# Bing Ads

## Overview

The Bing Ads connector syncs data from the [Bing Ads API](https://docs.microsoft.com/en-us/advertising/guides/?view=bingads-13).

## Output schema

This Source is capable of syncing the following resources:

* [Accounts](https://docs.microsoft.com/en-us/advertising/customer-management-service/searchaccounts?view=bingads-13)
* [Campaigns](https://docs.microsoft.com/en-us/advertising/campaign-management-service/getcampaignsbyaccountid?view=bingads-13)
* [AdGroups](https://docs.microsoft.com/en-us/advertising/campaign-management-service/getadgroupsbycampaignid?view=bingads-13)
* [Ads](https://docs.microsoft.com/en-us/advertising/campaign-management-service/getadsbyadgroupid?view=bingads-13)

It can also sync the following reports:

* [AccountPerformanceReport](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
* [AdPerformanceReport](https://docs.microsoft.com/en-us/advertising/reporting-service/adperformancereportrequest?view=bingads-13)
* [AdGroupPerformanceReport](https://docs.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
* [CampaignPerformanceReport](https://docs.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
* [BudgetSummaryReport](https://docs.microsoft.com/en-us/advertising/reporting-service/budgetsummaryreportrequest?view=bingads-13)
* [KeywordPerformanceReport](https://docs.microsoft.com/en-us/advertising/reporting-service/keywordperformancereportrequest?view=bingads-13)

### Report Aggregation
All reports synced by this connector can be aggregated using hourly, daily, weekly, or monthly windows. Performance data is aggregated using the selected window. For example, if you select the daily-aggregation flavor of a report, the report will contain a row for each day for the duration of the report. Each row will indicate the number of impressions recorded on that day.   

A report's aggregation window is indicated in its name e.g: `account_performance_report_hourly` is the Account Performance Reported aggregated using an hourly window. 

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- |:---------------------| :--- |
| Full Refresh Sync | Yes                  |  |
| Incremental Sync | Yes                  |  |
| Namespaces | No                   |  |

### Performance considerations

API limits number of requests for all Microsoft Advertising clients. You can find detailied info [here](https://docs.microsoft.com/en-us/advertising/guides/services-protocol?view=bingads-13#throttling)

## Getting started (Airbyte Open Source)
### Requirements 
* A Microsoft User account with access to at least one Microsoft Advertising account
* A Microsoft Ads Customer ID
* Your Microsoft User ID
* A developer application with access to: 
  * client ID 
  * client secret 
  * A developer token 
  * Optionally, a tenant ID
* A refresh token generated using the above developer application credentials
* (Optional) Ad Account IDs you want to access, if you want to limit replication to specific ad accounts

### Setup Guide
* Create a developer application using the instructions for [registering an application](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-register?view=bingads-13) in Azure portal
* Perform [these steps](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-consent?view=bingads-13l) to get auth code, and use that to [get a refresh token](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-get-tokens?view=bingads-13). For reference, the full authentication process described [here](https://docs.microsoft.com/en-us/advertising/guides/get-started?view=bingads-13#access-token). Be aware that the refresh token will expire in 90 days. You need to repeat the auth process to get a new refresh token.
* Find your Microsoft developer token by following [these instructions](https://docs.microsoft.com/en-us/advertising/guides/get-started?view=bingads-13#get-developer-token)
* Find your customer ID and User ID by visiting the following URL: https://ui.ads.microsoft.com/campaign/Campaigns.m then copying the CID & UID parameters from the URL in the address bar. For example, once you visit the URL above, you'll notice it will have changed to an address of the form https://ui.ads.microsoft.com/campaign/vnext/overview?uid=USER_ID&cid=CUSTOMER_ID&aid=180534868 -- the customer ID is the value in the part of the URL that looks like `cid=THIS_IS_THE_CUSTOMER_ID&`, and the user ID is the value in front of `uid` e.g: `uid=THIS_IS_THE_USER_ID&`. 
* Optionally, if you want to replicate data from specific ad account IDs (you can configure the Bing Ads connector to replicate data from all accounts you have access to, or only from some), then also grab the account IDs you want by visiting the [Accounts Summary](https://ui.ads.microsoft.com/campaign/vnext/accounts/performance) page, clicking on each of the accounts you want under the `Account name` column, then repeating the process described earlier to get the `aid` parameter in the URL that looks like `aid=ACCOUNT_ID&`. You'll need to do this process once for each account from which you want to replicate data. 
* Optionally, if your oauth app lives under a custom tenant which cannot use Microsoft's recommended `common` tenant, make sure to get the tenant ID ready for input when configuring the connector. The tenant will be used in the auth URL e.g: `https://login.microsoftonline.com/<tenant>/oauth2/v2.0/authorize`.



## Changelog

| Version | Date | Pull Request                                             | Subject |
|:--------| :--- |:---------------------------------------------------------| :--- |
| 0.1.6   | 2022-04-30 | [12500](https://github.com/airbytehq/airbyte/pull/12500) | Improve input configuration copy                                                             |
| 0.1.5   | 2022-01-01 | [11652](https://github.com/airbytehq/airbyte/pull/11652) | Rebump attempt after DockerHub failure at registring the 0.1.4 |
| 0.1.4   | 2022-03-22 | [11311](https://github.com/airbytehq/airbyte/pull/11311) | Added optional Redirect URI & Tenant ID to spec |
| 0.1.3   | 2022-01-14 | [9510](https://github.com/airbytehq/airbyte/pull/9510)   | Fixed broken dependency that blocked connector's operations |
| 0.1.2   | 2021-12-14 | [8429](https://github.com/airbytehq/airbyte/pull/8429)   | Update titles and descriptions |
| 0.1.1   | 2021-08-31 | [5750](https://github.com/airbytehq/airbyte/pull/5750)   | Added reporting streams\) |
| 0.1.0   | 2021-07-22 | [4911](https://github.com/airbytehq/airbyte/pull/4911)   | Initial release supported core streams \(Accounts, Campaigns, Ads, AdGroups\) |

