# Amazon Ads
This page contains the setup guide and reference information for the Amazon Ads source connector.

## Prerequisites

* Client ID
* Client Secret
* Refresh Token
* Region
* Start Date (Optional)
* Profile IDs (Optional)
* Marketplace IDs (Optional)

## Setup guide
### Step 1: Set up Amazon Ads
Create an [Amazon user](https://www.amazon.com) with access to [Amazon Ads account](https://advertising.amazon.com).

<!-- env:oss -->
**For Airbyte Open Source:**
To use the [Amazon Ads API](https://advertising.amazon.com/API/docs/en-us), you must first complete the [onboarding process](https://advertising.amazon.com/API/docs/en-us/setting-up/overview). The onboarding process has several steps and may take several days to complete. After completing all steps you will have to get Amazon client application `Client ID`, `Client Secret` and `Refresh Token`.
<!-- /env:oss -->

### Step 2: Set up the Amazon Ads connector in Airbyte

<!-- env:cloud -->
**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Amazon Ads** from the Source type dropdown and enter a name for this connector.
4. Click `Authenticate your Amazon Ads account`.
5. Log in and Authorize to the Amazon account.
6. Select **Region** to pull data from **North America (NA)**, **Europe (EU)**, **Far East (FE)**. See [docs](https://advertising.amazon.com/API/docs/en-us/info/api-overview#api-endpoints) for more details.
7. **Start Date (Optional)** is used for generating reports starting from the specified start date. Should be in YYYY-MM-DD format and not more than 60 days in the past. If not specified today's date is used. The date is treated in the timezone of the processed profile.
8. **Profile IDs (Optional)** you want to fetch data for. See [docs](https://advertising.amazon.com/API/docs/en-us/concepts/authorization/profiles) for more details.
9. **Marketplace IDs (Optional)** you want to fetch data for. _Note: If Profile IDs are also selected, profiles will be selected if they match the Profile ID **OR** the Marketplace ID._
10. Click `Set up source`.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. **Client ID** of your Amazon Ads developer application. See [onboarding process](https://advertising.amazon.com/API/docs/en-us/setting-up/overview) for more details.
2. **Client Secret** of your Amazon Ads developer application. See [onboarding process](https://advertising.amazon.com/API/docs/en-us/setting-up/overview) for more details.
3. **Refresh Token**. See [onboarding process](https://advertising.amazon.com/API/docs/en-us/setting-up/overview) for more details.
4. Select **Region** to pull data from **North America (NA)**, **Europe (EU)**, **Far East (FE)**. See [docs](https://advertising.amazon.com/API/docs/en-us/info/api-overview#api-endpoints) for more details.
5. **Start Date (Optional)** is used for generating reports starting from the specified start date. Should be in YYYY-MM-DD format and not more than 60 days in the past. If not specified today's date is used. The date is treated in the timezone of the processed profile.
6. **Profile IDs (Optional)** you want to fetch data for. See [docs](https://advertising.amazon.com/API/docs/en-us/concepts/authorization/profiles) for more details.
7. **Marketplace IDs (Optional)** you want to fetch data for. _Note: If Profile IDs are also selected, profiles will be selected if they match the Profile ID **OR** the Marketplace ID._
<!-- /env:oss -->

## Supported sync modes
The Amazon Ads source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-mode):
 - Full Refresh
 - Incremental

## Supported Streams
This source is capable of syncing the following streams:

* [Profiles](https://advertising.amazon.com/API/docs/en-us/reference/2/profiles#/Profiles)
* [Portfolios](https://advertising.amazon.com/API/docs/en-us/reference/2/portfolios#/Portfolios%20extended)
* [Sponsored Brands Campaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Campaigns)
* [Sponsored Brands Ad groups](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Ad%20groups)
* [Sponsored Brands Keywords](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Keywords)
* [Sponsored Display Campaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Campaigns)
* [Sponsored Display Ad groups](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Ad%20groups)
* [Sponsored Display Product Ads](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Product%20ads)
* [Sponsored Display Targetings](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Targeting)
* [Sponsored Display Budget Rules](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi/prod#/BudgetRules/GetSDBudgetRulesForAdvertiser)
* [Sponsored Products Campaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Campaigns)
* [Sponsored Products Ad groups](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Ad%20groups)
* [Sponsored Products Ad Group Bid Recommendations](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Bid%20recommendations/getAdGroupBidRecommendations)
* [Sponsored Products Ad Group Suggested Keywords](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Suggested%20keywords)
* [Sponsored Products Keywords](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Keywords)
* [Sponsored Products Negative keywords](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Negative%20keywords)
* [Sponsored Products Campaign Negative keywords](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Negative%20keywords)
* [Sponsored Products Ads](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Product%20ads)
* [Sponsored Products Targetings](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Product%20targeting)
* [Brands Reports](https://advertising.amazon.com/API/docs/en-us/reference/sponsored-brands/2/reports)
* [Brand Video Reports](https://advertising.amazon.com/API/docs/en-us/reference/sponsored-brands/2/reports)
* [Display Reports](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Reports) (Contextual targeting only)
* [Products Reports](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Reports)
* [Attribution Reports](https://advertising.amazon.com/API/docs/en-us/amazon-attribution-prod-3p/#/)

## Connector-specific features and highlights

All the reports are generated relative to the target profile' timezone.

Campaign reports may sometimes have no data or not presenting in records. This can occur when there are no clicks or views associated with the campaigns on the requested day - [details](https://advertising.amazon.com/API/docs/en-us/guides/reporting/v2/faq#why-is-my-report-empty).

Report data synchronization only cover the last 60 days - [details](https://advertising.amazon.com/API/docs/en-us/reference/1/reports#parameters).

## Performance considerations

Information about expected report generation waiting time you may find [here](https://advertising.amazon.com/API/docs/en-us/get-started/developer-notes).

### Data type mapping

| Integration Type         | Airbyte Type |
|:-------------------------|:-------------|
| `string`                 | `string`     |
| `int`, `float`, `number` | `number`     |
| `date`                   | `date`       |
| `datetime`               | `datetime`   |
| `array`                  | `array`      |
| `object`                 | `object`     |

## CHANGELOG

| Version | Date       | Pull Request                                             | Subject                                                                                                         |
|:--------|:-----------|:---------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------|
| 3.1.2   | 2023-08-16 | [29233](https://github.com/airbytehq/airbyte/pull/29233) | Add filter for Marketplace IDs                                                                                  |
| 3.1.1   | 2023-08-28 | [29900](https://github.com/airbytehq/airbyte/pull/29900) | Add 404 handling for no assotiated with bid ad groups                                                           |
| 3.1.0   | 2023-08-08 | [00000](https://github.com/airbytehq/airbyte/pull/00000) | Add `T00030` tactic support for `sponsored_display_report_stream`                                               |
| 3.0.0   | 2023-07-24 | [27868](https://github.com/airbytehq/airbyte/pull/27868) | Fix attribution report stream schemas                                                                           |
| 2.3.1   | 2023-07-11 | [28155](https://github.com/airbytehq/airbyte/pull/28155) | Bugfix: validation error when record values are missing                                                         |
| 2.3.0   | 2023-07-06 | [28002](https://github.com/airbytehq/airbyte/pull/28002) | Add sponsored_product_ad_group_suggested_keywords, sponsored_product_ad_group_bid_recommendations streams       |
| 2.2.0   | 2023-07-05 | [27607](https://github.com/airbytehq/airbyte/pull/27607) | Add stream for sponsored brands v3 purchased product reports                                                    |
| 2.1.0   | 2023-06-19 | [25412](https://github.com/airbytehq/airbyte/pull/25412) | Add sponsored_product_campaign_negative_keywords, sponsored_display_budget_rules streams                        |
| 2.0.0   | 2023-05-31 | [25874](https://github.com/airbytehq/airbyte/pull/25874) | Type `portfolioId` as integer                                                                                   |
| 1.1.0   | 2023-04-22 | [25412](https://github.com/airbytehq/airbyte/pull/25412) | Add missing reporting metrics                                                                                   |
| 1.0.6   | 2023-05-09 | [25913](https://github.com/airbytehq/airbyte/pull/25913) | Small schema fixes                                                                                              |
| 1.0.5   | 2023-05-08 | [25885](https://github.com/airbytehq/airbyte/pull/25885) | Improve error handling for attribution_report(s) streams                                                        |
| 1.0.4   | 2023-05-04 | [25792](https://github.com/airbytehq/airbyte/pull/25792) | Add availability strategy for basic streams (not including report streams)                                      |
| 1.0.3   | 2023-04-13 | [25146](https://github.com/airbytehq/airbyte/pull/25146) | Validate pk for reports when expected pk is not returned                                                        |
| 1.0.2   | 2023-02-03 | [22355](https://github.com/airbytehq/airbyte/pull/22355) | Migrate `products_report` stream to API v3                                                                      |
| 1.0.1   | 2022-11-01 | [18677](https://github.com/airbytehq/airbyte/pull/18677) | Add optional config report_record_types                                                                         |
| 1.0.0   | 2023-01-30 | [21677](https://github.com/airbytehq/airbyte/pull/21677) | Fix bug with non-unique primary keys in report streams. Add asins_keywords and asins_targets                    |
| 0.1.29  | 2023-01-27 | [22038](https://github.com/airbytehq/airbyte/pull/22038) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                     |
| 0.1.28  | 2023-01-18 | [19491](https://github.com/airbytehq/airbyte/pull/19491) | Add option to customize look back window value                                                                  |
| 0.1.27  | 2023-01-05 | [21082](https://github.com/airbytehq/airbyte/pull/21082) | Fix bug with handling: "Report date is too far in the past." - partial revert of #20662                         |
| 0.1.26  | 2022-12-19 | [20662](https://github.com/airbytehq/airbyte/pull/20662) | Fix bug with handling: "Report date is too far in the past."                                                    |
| 0.1.25  | 2022-11-08 | [18985](https://github.com/airbytehq/airbyte/pull/18985) | Remove "report_wait_timeout", "report_generation_max_retries" from config                                       |
| 0.1.24  | 2022-10-19 | [17475](https://github.com/airbytehq/airbyte/pull/17475) | Add filters for state on brand, product and display campaigns                                                   |
| 0.1.23  | 2022-09-06 | [16342](https://github.com/airbytehq/airbyte/pull/16342) | Add attribution reports                                                                                         |
| 0.1.22  | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304) | Migrate to per-stream state.                                                                                    |
| 0.1.21  | 2022-09-27 | [17202](https://github.com/airbytehq/airbyte/pull/17202) | Improved handling if known reporting errors                                                                     |
| 0.1.20  | 2022-09-08 | [16453](https://github.com/airbytehq/airbyte/pull/16453) | Increase `report_wait_timeout` 30 -> 60 minutes                                                                 |
| 0.1.19  | 2022-08-31 | [16191](https://github.com/airbytehq/airbyte/pull/16191) | Improved connector's input configuration validation                                                             |
| 0.1.18  | 2022-08-25 | [15951](https://github.com/airbytehq/airbyte/pull/15951) | Skip API error "Tactic T00020 is not supported for report API in marketplace A1C3SOZRARQ6R3."                   |
| 0.1.17  | 2022-08-24 | [15921](https://github.com/airbytehq/airbyte/pull/15921) | Skip API error "Report date is too far in the past."                                                            |
| 0.1.16  | 2022-08-23 | [15822](https://github.com/airbytehq/airbyte/pull/15822) | Set default value for `region` if needed                                                                        |
| 0.1.15  | 2022-08-20 | [15816](https://github.com/airbytehq/airbyte/pull/15816) | Update STATE of incremental sync if no records                                                                  |
| 0.1.14  | 2022-08-15 | [15637](https://github.com/airbytehq/airbyte/pull/15637) | Generate slices by lazy evaluation                                                                              |
| 0.1.12  | 2022-08-09 | [15469](https://github.com/airbytehq/airbyte/pull/15469) | Define primary_key for all report streams                                                                       |
| 0.1.11  | 2022-07-28 | [15031](https://github.com/airbytehq/airbyte/pull/15031) | Improve report streams date-range generation                                                                    |
| 0.1.10  | 2022-07-26 | [15042](https://github.com/airbytehq/airbyte/pull/15042) | Update `additionalProperties` field to true from schemas                                                        |
| 0.1.9   | 2022-05-08 | [12541](https://github.com/airbytehq/airbyte/pull/12541) | Improve documentation for Beta                                                                                  |
| 0.1.8   | 2022-05-04 | [12482](https://github.com/airbytehq/airbyte/pull/12482) | Update input configuration copy                                                                                 |
| 0.1.7   | 2022-04-27 | [11730](https://github.com/airbytehq/airbyte/pull/11730) | Update fields in source-connectors specifications                                                               |
| 0.1.6   | 2022-04-20 | [11659](https://github.com/airbytehq/airbyte/pull/11659) | Add adId to products report                                                                                     |
| 0.1.5   | 2022-04-08 | [11430](https://github.com/airbytehq/airbyte/pull/11430) | Add support OAuth2.0                                                                                            |
| 0.1.4   | 2022-02-21 | [10513](https://github.com/airbytehq/airbyte/pull/10513) | Increasing REPORT_WAIT_TIMEOUT for supporting report generation which takes longer time                         |
| 0.1.3   | 2021-12-28 | [8388](https://github.com/airbytehq/airbyte/pull/8388)   | Add retry if recoverable error  occured for reporting stream processing                                         |
| 0.1.2   | 2021-10-01 | [6367](https://github.com/airbytehq/airbyte/pull/6461)   | Add option to pull data for different regions. Add option to choose profiles we want to pull data. Add lookback |
| 0.1.1   | 2021-09-22 | [6367](https://github.com/airbytehq/airbyte/pull/6367)   | Add seller and vendor filters to profiles stream                                                                |
| 0.1.0   | 2021-08-13 | [5023](https://github.com/airbytehq/airbyte/pull/5023)   | Initial version                                                                                                 |
