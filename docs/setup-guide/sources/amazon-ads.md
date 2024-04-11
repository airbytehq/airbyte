# Amazon Ads

This page contains the setup guide and reference information for Amazon Ads.

## Prerequisites

* Amazon Ads account login (username and password)
* Region

## Setup guide

### Step 1: Set up Amazon Ads

Create an Amazon user with access to [Amazon Ads account](https://advertising.amazon.com/).

### Step 2: Set up the Amazon Ads data source in Daspire

1. Select **Amazon Ads** from the Source list.

2. Enter a **Source Name**.

3. **Authenticate your Amazon Ads account**.

4. Select **Region** to pull data from **North America (NA)**, **Europe (EU)** or **Far East (FE)**. See [Amazon docs](https://advertising.amazon.com/API/docs/en-us/info/api-overview#api-endpoints) for more details.

5. **Report Wait Timeout** is the maximum number of minutes the connector waits for the generation of a report for streams.

6. **Report Generation Maximum Retries** is the maximum number of attempts the connector tries to generate a report for streams.

7. **Start Date (optional)** is used for generating reports starting from the specified start date. Should be in YYYY-MM-DD format and not more than 60 days in the past. If not specified today's date is used. The date for a specific profile is calculated according to its timezone, this parameter should be specified in the UTC timezone. Since it doesn't make sense to generate reports for the current day (metrics could be changed), it generates reports for the day before (e.g. if **Start Date** is 2022-10-11 it would use 20221010 as reportDate parameter for request).

8. **Profile IDs (optional)** you want to fetch data for. See [Amazon docs](https://advertising.amazon.com/API/docs/en-us/concepts/authorization/profiles) for more details.

9. Click **Save & Test**.

## Supported sync modes

The Amazon Ads data source supports the following sync modes:

* Full Refresh
* Incremental

## Supported streams

This source is capable of syncing the following streams:

* [Profiles](https://advertising.amazon.com/API/docs/en-us/reference/2/profiles#/Profiles)
* [Sponsored Brands Campaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Campaigns)
* [Sponsored Brands Ad groups](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Ad%20groups)
* [Sponsored Brands Keywords](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Keywords)
* [Sponsored Brands Reports](https://advertising.amazon.com/API/docs/en-us/reference/sponsored-brands/2/reports)
* [Sponsored Display Campaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Campaigns)
* [Sponsored Display Ad groups](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Ad%20groups)
* [Sponsored Display Product Ads](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Product%20ads)
* [Sponsored Display Targetings](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Targeting)
* [Sponsored Display Reports](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Reports)
* [Sponsored Products Campaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#/Campaigns)
* [Sponsored Products Ad groups](https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#/AdGroups)
* [Sponsored Products Keywords](https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#/Keywords)
* [Sponsored Products Negative keywords](https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#/NegativeKeywords)
* [Sponsored Products Ads](https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#/ProductAds)
* [Sponsored Products Targetings](https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#/Product%20Targeting)
* [Sponsored Products Reports](https://advertising.amazon.com/API/docs/en-us/reporting/v3/overview)

## Specific features and highlights

All the reports are generated for the day before relatively to the target profile' timezone.

## Performance considerations

Information about expected report generation waiting time you may find [here](https://advertising.amazon.com/API/docs/en-us/get-started/developer-notes).

## Troubleshooting

Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.

## Data type mapping

| Integration Type | Daspire Type |
| --- | --- |
| `string` | `string` |
| `int`, `float`, `number` | `number` |
| `date` | `date` |
| `datetime` | `datetime` |
| `array` | `array` |
| `object` | `object` |