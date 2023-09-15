# Amazon Ads v3
This page contains the setup guide and reference information for the Amazon Ads source connector.

## Prerequisites

* Client ID
* Client Secret
* Refresh Token
* Region
* Start Date (Optional)
* End Date (Optional)
* Profile IDs (Optional)

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
9. Click `Set up source`.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. **Client ID** of your Amazon Ads developer application. See [onboarding process](https://advertising.amazon.com/API/docs/en-us/setting-up/overview) for more details.
2. **Client Secret** of your Amazon Ads developer application. See [onboarding process](https://advertising.amazon.com/API/docs/en-us/setting-up/overview) for more details.
3. **Refresh Token**. See [onboarding process](https://advertising.amazon.com/API/docs/en-us/setting-up/overview) for more details.
<!-- /env:oss -->

## Supported sync modes
The Amazon Ads source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-mode):
 - Full Refresh
 - Incremental

## Supported Streams
This source is capable of syncing the following streams:

* [Profiles](https://advertising.amazon.com/API/docs/en-us/reference/2/profiles#/Profiles)
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
* [Attribution Reports](https://advertising.amazon.com/API/docs/en-us/amazon-attribution-prod-3p/#/)

## Connector-specific features and highlights

All the reports are generated relative to the target profile' timezone.

## Performance considerations

Information about expected report generation waiting time you may find [here](https://advertising.amazon.com/API/docs/en-us/get-started/developer-notes).

### Data type mapping

| Integration Type         | Airbyte Type |
| :----------------------- | :----------- |
| `string`                 | `string`     |
| `int`, `float`, `number` | `number`     |
| `date`                   | `date`       |
| `datetime`               | `datetime`   |
| `array`                  | `array`      |
| `object`                 | `object`     |

## CHANGELOG
