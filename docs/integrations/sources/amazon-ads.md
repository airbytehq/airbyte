# Amazon Ads
This page contains the setup guide and reference information for the Amazon Ads source connector.

## Prerequisites

* Client ID
* Client Secret
* Refresh Token
* Region
* Report Wait Timeout
* Report Generation Maximum Retries
* Start Date (Optional)
* Profile IDs (Optional)

## Setup guide
### Step 1: Set up Amazon Ads
Create an [Amazon user](https://www.amazon.com) with access to [Amazon Ads account](https://advertising.amazon.com).

### Airbyte Open Source additional setup steps
To use the [Amazon Ads API](https://advertising.amazon.com/API/docs/en-us), you must first complete the [onboarding process](https://advertising.amazon.com/API/docs/en-us/setting-up/overview). The onboarding process has several steps and may take several days to complete. After completing all steps you will have to get Amazon client application `Client ID`, `Client Secret` and `Refresh Token`.

### Step 2: Set up the Amazon Ads connector in Airbyte
**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Amazon Ads** from the Source type dropdown and enter a name for this connector.
4. Click `Authenticate your Amazon Ads account`.
5. Log in and Authorize to the Amazon account.
6. Select **Region** to pull data from **North America (NA)**, **Europe (EU)**, **Far East (FE)** or **Sandbox Environment**. See [docs](https://advertising.amazon.com/API/docs/en-us/info/api-overview#api-endpoints) for more details.
7. **Report Wait Timeout** is the maximum number of minutes the connector waits for the generation of a report for streams `Brands Reports`, `Brand Video Reports`, `Display Reports`, `Products Reports`.
8. **Report Generation Maximum Retries** is the maximum number of attempts the connector tries to generate a report for streams `Brands Reports`, `Brand Video Reports`, `Display Reports`, `Products Reports`.
9. **Start Date (Optional)** is used for generating reports starting from the specified start date. Should be in YYYY-MM-DD format and not more than 60 days in the past. If not specified today's date is used. The date for a specific profile is calculated according to its timezone, this parameter should be specified in the UTC timezone. Since it has no sense of generating report for the current day \(metrics could be changed\) it generates report for the day before \(e.g. if **Start Date** is 2021-10-11 it would use 20211010 as `reportDate` parameter for request\).
10. **Profile IDs (Optional)** you want to fetch data for. See [docs](https://advertising.amazon.com/API/docs/en-us/concepts/authorization/profiles) for more details.
11. Click `Set up source`.

**For Airbyte OSS:**

1. **Client ID** of your Amazon Ads developer application. See [onboarding process](https://advertising.amazon.com/API/docs/en-us/setting-up/overview) for more details.
2. **Client Secret** of your Amazon Ads developer application. See [onboarding process](https://advertising.amazon.com/API/docs/en-us/setting-up/overview) for more details.
3. **Refresh Token**. See [onboarding process](https://advertising.amazon.com/API/docs/en-us/setting-up/overview) for more details.

## Supported sync modes
The Amazon Ads source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-mode):
 - Full Refresh
 - Incremental

## Supported Streams
This source is capable of syncing the following streams:

* [Profiles](https://advertising.amazon.com/API/docs/en-us/reference/2/profiles#/Profiles)
* [Sponsored Brands Campaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Campaigns)
* [Sponsored Brands Ad groups](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Ad%20groups)
* [Sponsored Brands Keywords](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Keywords)
* [Sponsored Display Campaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Campaigns)
* [Sponsored Display Ad groups](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Ad%20groups)
* [Sponsored Display Product Ads](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Product%20ads)
* [Sponsored Display Targetings](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Targeting)
* [Sponsored Products Campaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Campaigns)
* [Sponsored Products Ad groups](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Ad%20groups)
* [Sponsored Products Keywords](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Keywords)
* [Sponsored Products Negative keywords](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Negative%20keywords)
* [Sponsored Products Ads](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Product%20ads)
* [Sponsored Products Targetings](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Product%20targeting)
* [Brands Reports](https://advertising.amazon.com/API/docs/en-us/reference/sponsored-brands/2/reports)
* [Brand Video Reports](https://advertising.amazon.com/API/docs/en-us/reference/sponsored-brands/2/reports)
* [Display Reports](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Reports)
* [Products Reports](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Reports)

## Connector-specific features and highlights

All the reports are generated for the day before relatively to the target profile' timezone

## Performance considerations

Information about expected report generation waiting time you may find [here](https://advertising.amazon.com/API/docs/en-us/get-started/developer-notes).

### Data type mapping

| Integration Type | Airbyte Type |
| :--- | :--- |
| `string` | `string` |
| `int`, `float`, `number` | `number` |
| `date` | `date` |
| `datetime` | `datetime` |
| `array` | `array` |
| `object` | `object` |

## CHANGELOG

| Version | Date       | Pull Request                                               | Subject                                                                                                           |
|:--------|:-----------|:-----------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------|
| `0.1.9` | 2022-05-08 | [\#12541](https://github.com/airbytehq/airbyte/pull/12541) | Improve documentation for Beta                                                                                    |
| `0.1.8` | 2022-05-04 | [\#12482](https://github.com/airbytehq/airbyte/pull/12482) | Update input configuration copy                                                                                   |
| `0.1.7` | 2022-04-27 | [\#11730](https://github.com/airbytehq/airbyte/pull/11730) | Update fields in source-connectors specifications                                                                 |
| `0.1.6` | 2022-04-20 | [\#11659](https://github.com/airbytehq/airbyte/pull/11659) | Add adId to products report                                                                                       |
| `0.1.5` | 2022-04-08 | [\#11430](https://github.com/airbytehq/airbyte/pull/11430) | `Added support OAuth2.0`                                                                                          |
| `0.1.4` | 2022-02-21 | [\#10513](https://github.com/airbytehq/airbyte/pull/10513) | `Increasing REPORT_WAIT_TIMEOUT for supporting report generation which takes longer time `                        |
| `0.1.3` | 2021-12-28 | [\#8388](https://github.com/airbytehq/airbyte/pull/8388)   | `Add retry if recoverable error  occured for reporting stream processing`                                         |
| `0.1.2` | 2021-10-01 | [\#6367](https://github.com/airbytehq/airbyte/pull/6461)   | `Add option to pull data for different regions. Add option to choose profiles we want to pull data. Add lookback` |
| `0.1.1` | 2021-09-22 | [\#6367](https://github.com/airbytehq/airbyte/pull/6367)   | `Add seller and vendor filters to profiles stream`                                                                |
| `0.1.0` | 2021-08-13 | [\#5023](https://github.com/airbytehq/airbyte/pull/5023)   | `Initial version`                                                                                                 |
