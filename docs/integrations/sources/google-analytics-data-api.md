# Google Analytics 4 (GA4)

This page contains the setup guide and reference information for the Google Analytics 4 source connector.

The Google Analytics 4 (GA4) connector represents the latest version of Google Analytics, introduced in 2020. It offers a new data model that emphasizes events and user properties, rather than pageviews and sessions. This updated model allows for more flexibility and customization in reporting, and provides more accurate measurement of user behavior across various devices and platforms.

:::note

The [Google Analytics Universal Analytics (UA) connector](https://docs.airbyte.com/integrations/sources/google-analytics-v4) utilizes the older version of Google Analytics, which was the standard for tracking website and app user behavior before the introduction of GA4. Please note that the UA connector is being deprecated in favor of this one. As of July 1, 2023, standard Universal Analytics properties no longer process hits. For further reading on the transition from UA to GA4, refer to [Google's official support page](https://support.google.com/analytics/answer/11583528).

:::

## Prerequisites

- A Google Analytics account with access to the GA4 property you want to sync

## Setup guide

### For Airbyte Cloud

<!-- env:cloud -->

For **Airbyte Cloud** users, we highly recommend using OAuth for authentication, as this significantly simplifies the setup process by allowing you to authenticate your Google Analytics account directly in the Airbyte UI. Please follow the steps below to set up the connector using this method.

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Google Analytics 4 (GA4)** from the list of available sources.
4. In the **Source name** field, enter a name to help you identify this source.
4. Select **Authenticate via Google (Oauth)** from the dropdown menu and click **Authenticate your Google Analytics 4 (GA4) account**. This will open a pop-up window where you can log in to your Google account and grant Airbyte access to your Google Analytics account. 
5. Enter the **Property ID** whose events are tracked. This ID should be a numeric value, such as `123456789`. If you are unsure where to find this value, refer to [Google's documentation](https://developers.google.com/analytics/devguides/reporting/data/v1/property-id#what_is_my_property_id).

:::note
If the Property Settings shows a "Tracking Id" such as "UA-123...-1", this denotes that the property is a Universal Analytics property, and the Analytics data for that property cannot be reported on in the Data API. You can create a new Google Analytics 4 property by following [these instructions](https://support.google.com/analytics/answer/9744165?hl=en).
:::

6. In the **Start Date** field, use the provided datepicker or enter a date programmatically in the format `YYYY-MM-DD`. All data added from this date onward will be replicated. Note that this setting is _not_ applied to custom Cohort reports.
8. (Optional) In the **Custom Reports** field, you may optionally provide a JSON array describing any custom reports you want to sync from Google Analytics. See the [Custom Reports](#custom-reports) section below for more information on formulating these reports.
9. (Optional) In the **Data request time increment in days** field, you can specify the interval used when requesting data from the Google Analytics API. The bigger this value is, the faster the sync will be, but the more likely that sampling will be applied to your data, potentially causing inaccuracies in the returned results. We recommend setting this to 1 unless you have a hard requirement to make the sync faster at the expense of accuracy. The minimum allowed value for this field is 1, and the maximum is 364. (Not applied to custom Cohort reports).
10. Click **Set up source** and wait for the tests to complete.

<!-- /env:cloud -->

<!-- env:oss -->

### For Airbyte Open Source

For **Airbyte Open Source** users, the simplest way to set up the Google Analytics 4 connector is to create a Service Account and set up a JSON key file for authentication. Please follow the steps below to set up the connector using this method.

#### Create a Service Account for authentication

1. Sign in to the Google Account you are using for Google Analytics as an admin.
2. Go to the [Service Accounts](https://console.developers.google.com/iam-admin/serviceaccounts) page in the Google Developers console.
3. Select the project you want to use and click **Continue**.
4. Click **+ Create Service Account** at the top of the page.
5. Enter a name for the service account, and optionally, a description. Click **Create and Continue**.
6. Choose the role for the service account. We reccomend the **Viewer** role (Read & Analyze permissions). Click **Continue**.
7. Select your new service account from the list, and open the **Keys** tab. Click **Add Key** > **Create New Key**. 
8. Select **JSON** as the Key type. This will generate and download the JSON key file that you'll use for authentication. Click **Continue**.

#### Enable the Google Analytics APIs

Before you can use the service account to access Google Analytics data, you need to enable the required APIs:

1. Go to the [Google Analytics Reporting API dashboard](https://console.developers.google.com/apis/api/analyticsreporting.googleapis.com/overview). Make sure you have selected the associated project for your service account, and enable the API. You can also set quotas and check usage.
2. Go to the [Google Analytics API dashboard](https://console.developers.google.com/apis/api/analytics.googleapis.com/overview). Make sure you have selected the associated project for your service account, and enable the API.

#### Step 2: Set up the Google Analytics connector in Airbyte

1. Navigate to the Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Google Analytics 4 (GA4)** from the list of available sources.
4. Select **Service Account Key Authenication** dropdown list and enter **Service Account JSON Key** from Step 1.
5. Enter the **Property ID** whose events are tracked. This ID should be a numeric value, such as `123456789`. If you are unsure where to find this value, refer to [Google's documentation](https://developers.google.com/analytics/devguides/reporting/data/v1/property-id#what_is_my_property_id).

:::note
If the Property Settings shows a "Tracking Id" such as "UA-123...-1", this denotes that the property is a Universal Analytics property, and the Analytics data for that property cannot be reported on in the Data API. You can create a new Google Analytics 4 property by following [these instructions](https://support.google.com/analytics/answer/9744165?hl=en).
:::

6. In the **Start Date** field, use the provided datepicker or enter a date programmatically in the format `YYYY-MM-DD`. All data added from this date onward will be replicated. Note that this setting is _not_ applied to custom Cohort reports.
8. (Optional) In the **Custom Reports** field, you may optionally provide a JSON array describing any custom reports you want to sync from Google Analytics. See the [Custom Reports](#custom-reports) section below for more information on formulating these reports.
9. (Optional) In the **Data request time increment in days** field, you can specify the interval used when requesting data from the Google Analytics API. The bigger this value is, the faster the sync will be, but the more likely that sampling will be applied to your data, potentially causing inaccuracies in the returned results. We recommend setting this to 1 unless you have a hard requirement to make the sync faster at the expense of accuracy. The minimum allowed value for this field is 1, and the maximum is 364. (Not applied to custom Cohort reports).
10. Click **Set up source** and wait for the tests to complete.
<!-- /env:oss -->

## Supported sync modes

The Google Analytics source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported streams

This connector outputs the following incremental streams:

- Preconfigured streams:
  - [daily_active_users](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
  - [devices](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
  - [four_weekly_active_users](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
  - [locations](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
  - [pages](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
  - [traffic_sources](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
  - [website_overview](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
  - [weekly_active_users](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
- [Custom stream\(s\)](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)

## Connector-specific features

### Custom Reports

Custom reports allow for flexibility in the reporting dimensions and metrics to meet your specific use case. We recommend using the [GA4 Query Explorer](https://ga-dev-tools.google/ga4/query-explorer/) to help build your report. To ensure your dimensions and metrics are compatible, you can also refer to the [GA4 Dimensions & Metrics Explorer](https://ga-dev-tools.google/ga4/dimensions-metrics-explorer/).

Custom reports should be constructed in the following format:

```json
[
  {
    "name": "<report-name>", 
    "dimensions": ["<dimension-name>", ...], 
    "metrics": ["<metric-name>", ...], 
    "cohortSpec": "<cohortSpec>", 
    "pivots": "<pivots>"
  }
]
```

- Both `pivots` and `cohortSpec` are optional properties. For detailed descriptions of the `cohortSpec` and the `pivots` objects, refer to the official documentation [here](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/CohortSpec) and [here](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/Pivot).
- To enable Incremental sync for Custom reports, you must include the `date` dimension (except for custom Cohort reports).

### Data Sampling and Data Request Time Increment

Data sampling in Google Analytics 4 refers to the process of estimating analytics data when the amount of data in an account exceeds Google's predefined compute thresholds. To mitigate the chances of data sampling being applied to the results, the **Data request time increment in days** field allows users to specify the interval used when requesting data from the Google Analytics API. By setting the time increment to 1 (one day increment), users can reduce the data processed per request, minimizing the likelihood of data sampling and ensuring more accurate results. While larger time increments can speed up the sync, choosing a smaller value (1) is recommended to prioritize data accuracy unless there is a specific need for faster synchronization at the expense of some potential inaccuracies. Please note that this field does not apply to custom Cohort reports.

## Performance Considerations

The Google Analytics connector is subject to Google Analytics Data API Quotas. For more information on these quotas, please refer to [the official Google docs](https://developers.google.com/analytics/devguides/reporting/data/v1/quotas).

## Data type map

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                       |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------------------|
| 1.1.2   | 2023-07-03 | [27909](https://github.com/airbytehq/airbyte/pull/27909) | Limit the page size of custom report streams                                  |
| 1.1.1   | 2023-06-26 | [27718](https://github.com/airbytehq/airbyte/pull/27718) | Limit the page size when calling `check()`                                    |
| 1.1.0   | 2023-06-26 | [27738](https://github.com/airbytehq/airbyte/pull/27738) | License Update: Elv2                                                          |
| 1.0.0   | 2023-06-22 | [26283](https://github.com/airbytehq/airbyte/pull/26283) | Added primary_key and lookback window                                         |
| 0.2.7   | 2023-06-21 | [27531](https://github.com/airbytehq/airbyte/pull/27531) | Fix formatting                                                                |
| 0.2.6   | 2023-06-09 | [27207](https://github.com/airbytehq/airbyte/pull/27207) | Improve api rate limit messages                                               |
| 0.2.5   | 2023-06-08 | [27175](https://github.com/airbytehq/airbyte/pull/27175) | Improve Error Messages                                                        |
| 0.2.4   | 2023-06-01 | [26887](https://github.com/airbytehq/airbyte/pull/26887) | Remove `authSpecification` from connector spec in favour of `advancedAuth`    |
| 0.2.3   | 2023-05-16 | [26126](https://github.com/airbytehq/airbyte/pull/26126) | Fix pagination                                                                |
| 0.2.2   | 2023-05-12 | [25987](https://github.com/airbytehq/airbyte/pull/25987) | Categorized Config Errors Accurately                                          |
| 0.2.1   | 2023-05-11 | [26008](https://github.com/airbytehq/airbyte/pull/26008) | Added handling for `429 - potentiallyThresholdedRequestsPerHour` error        |
| 0.2.0   | 2023-04-13 | [25179](https://github.com/airbytehq/airbyte/pull/25179) | Implement support for custom Cohort and Pivot reports                         |
| 0.1.3   | 2023-03-10 | [23872](https://github.com/airbytehq/airbyte/pull/23872) | Fix parse + cursor for custom reports                                         |
| 0.1.2   | 2023-03-07 | [23822](https://github.com/airbytehq/airbyte/pull/23822) | Improve `rate limits` customer faced error messages and retry logic for `429` |
| 0.1.1   | 2023-01-10 | [21169](https://github.com/airbytehq/airbyte/pull/21169) | Slicer updated, unit tests added                                              |
| 0.1.0   | 2023-01-08 | [20889](https://github.com/airbytehq/airbyte/pull/20889) | Improved config validation, SAT                                               |
| 0.0.3   | 2022-08-15 | [15229](https://github.com/airbytehq/airbyte/pull/15229) | Source Google Analytics Data Api: code refactoring                            |
| 0.0.2   | 2022-07-27 | [15087](https://github.com/airbytehq/airbyte/pull/15087) | fix documentationUrl                                                          |
| 0.0.1   | 2022-05-09 | [12701](https://github.com/airbytehq/airbyte/pull/12701) | Introduce Google Analytics Data API source                                    |
