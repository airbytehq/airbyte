# Google Analytics 4 (GA4)

This page contains the setup guide and reference information for the Google Analytics 4 source connector.

:::note

The [Google Analytics Universal Analytics (UA) connector](https://docs.airbyte.com/integrations/sources/google-analytics-v4) utilizes the older version of Google Analytics, which has been the standard for tracking website and app user behavior since 2012.

The Google Analytics 4 (GA4) connector represents the latest version of Google Analytics, introduced in 2020. It offers a new data model that emphasizes events and user properties, rather than pageviews and sessions. This updated model allows for more flexibility and customization in reporting, and provides more accurate measurement of user behavior across various devices and platforms.

:::

## Prerequisites

- A Google Analytics account with access to the property you want to track
- OAuth or JSON credentials for the service account that has access to Google Analytics.

## Step 1: Set up Source

### Create a Service Account

First, you need to select existing or create a new project in the Google Developers Console:

1. Sign in to the Google Account you are using for Google Analytics as an admin.
2. Go to the [Service Accounts](https://console.developers.google.com/iam-admin/serviceaccounts) page.
3. Click `Create service account`.
4. Create a JSON key file for the service user. The contents of this file will be provided as the `credentials_json` in the UI when authorizing GA after you grant permissions \(see below\).

### Add service account to the Google Analytics account

Use the service account email address to [add a user](https://support.google.com/analytics/answer/1009702) to the Google analytics view you want to access via the API. You will need to grant [Viewer permissions](https://support.google.com/analytics/answer/2884495).

### Enable the APIs

1. Go to the [Google Analytics Reporting API dashboard](https://console.developers.google.com/apis/api/analyticsreporting.googleapis.com/overview) in the project for your service user. Enable the API for your account. You can set quotas and check usage.
2. Go to the [Google Analytics API dashboard](https://console.developers.google.com/apis/api/analytics.googleapis.com/overview) in the project for your service user. Enable the API for your account.

### Step 2: Set up the Google Analytics connector in Airbyte

**For Airbyte Cloud:**

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Google Analytics 4 (GA4)** from the list of available sources.
4. Click **Authenticate your account** by selecting Oauth or Service Account for Authentication.
5. Log in and Authorize the Google Analytics account.
6. Enter the [**Property ID**](https://developers.google.com/analytics/devguides/reporting/data/v1/property-id#what_is_my_property_id) whose events are tracked. The property ID should be a numeric string
7. Enter the **Start Date** from which to replicate report data in the format YYYY-MM-DD. (Not applied to custom Cohort reports).
8. **Custom Reports (Optional)**: You may provide a JSON array describing the custom reports you want to sync from Google Analytics.
9. Enter the **Data request time increment in days (Optional)**. The bigger this value is, the faster the sync will be, but the more likely that sampling will be applied to your data, potentially causing inaccuracies in the returned results. We recommend setting this to 1 unless you have a hard requirement to make the sync faster at the expense of accuracy. The minimum allowed value for this field is 1, and the maximum is 364. (Not applied to custom Cohort reports).

**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Google Analytics 4 (GA4)** from the Source type dropdown and enter a name for this connector.
4. Select Service Account for Authentication in dropdown list and enter **Service Account JSON Key** from Step 1.
5. Enter the [**Property ID**](https://developers.google.com/analytics/devguides/reporting/data/v1/property-id#what_is_my_property_id) whose events are tracked.
6. Enter the **Start Date** from which to replicate report data in the format YYYY-MM-DD. (Not applied to custom Cohort reports).
7. Enter the **Custom Reports (Optional)** a JSON array describing the custom reports you want to sync from Google Analytics.
8. Enter the **Data request time increment in days (Optional)**. The bigger this value is, the faster the sync will be, but the more likely that sampling will be applied to your data, potentially causing inaccuracies in the returned results. We recommend setting this to 1 unless you have a hard requirement to make the sync faster at the expense of accuracy. The minimum allowed value for this field is 1, and the maximum is 364. (Not applied to custom Cohort reports).

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

Custom Reports allow for flexibility in the reporting dimensions and metrics to meet your specific use case. Use the [GA4 Query Explorer](https://ga-dev-tools.google/ga4/query-explorer/) to help build your report. To ensure your dimensions and metrics are compatible, you can also refer to the [GA4 Dimensions & Metrics Explorer](https://ga-dev-tools.google/ga4/dimensions-metrics-explorer/). Custom reports should be constructed in the following format: 

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
- Both `pivots` and `cohortSpec` are optional. For detailed descriptions of the `cohortSpec` and the `pivots` objects, refer to the official documentation [here](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/CohortSpec) and [here](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/Pivot).
- To enable Incremental sync for Custom reports, you must include the `date` dimension (except for custom Cohort reports).

## Performance Considerations

The Google Analytics connector is subject to Google Analytics Data API Quotas. For more information on these quotas, please refer to [the official docs](https://developers.google.com/analytics/devguides/reporting/data/v1/quotas).

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
