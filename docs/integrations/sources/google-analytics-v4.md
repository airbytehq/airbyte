# Google Analytics 4 (GA4)

This page guides you through the process of setting up the Google Analytics source connector.

This connector supports GA4 properties through the [Analytics Data API v1](https://developers.google.com/analytics/devguides/reporting/data/v1).

## Prerequisites

* JSON credentials for the service account that has access to Google Analytics. For more details check [instructions](https://support.google.com/analytics/answer/1009702)
* OAuth 2.0 credentials for the service account that has access to Google Analytics
* Property ID
* Start Date
* Custom Reports (Optional)
* Data request time increment in days (Optional)

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

### Property ID

To determine a Google Analytics 4 [Property ID](https://developers.google.com/analytics/devguides/reporting/data/v1/property-id#what_is_my_property_id)

### Step 2: Set up the Google Analytics connector in Airbyte

**For Airbyte Cloud:**

1. [Login to your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Google Analytics 4 (GA4)** from the Source type dropdown and enter a name for this connector.
4. Click `Authenticate your account` by selecting Oauth or Service Account for Authentication.
5. Log in and Authorize the Google Analytics account.
6. Enter the **Property ID** whose events are tracked.
7. Enter the **Start Date** from which to replicate report data in the format YYYY-MM-DD.
8. Enter the **Custom Reports (Optional)** a JSON array describing the custom reports you want to sync from Google Analytics.
9. Enter the **Data request time increment in days (Optional)**. The bigger this value is, the faster the sync will be, but the more likely that sampling will be applied to your data, potentially causing inaccuracies in the returned results. We recommend setting this to 1 unless you have a hard requirement to make the sync faster at the expense of accuracy. The minimum allowed value for this field is 1, and the maximum is 364.

## Supported sync modes

The Google Analytics source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/glossary#full-refresh-sync)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

This connector outputs the following incremental streams:

* [daily_active_users](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [devices](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [four_weekly_active_users](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [locations](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [pages](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [traffic_sources](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [website_overview](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [weekly_active_users](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)

## Custom reports

* Support for multiple custom reports
* Custom reports in format `[{"name": "<report-name>", "dimensions": ["<dimension-name>", ...], "metrics": ["<metric-name>", ...]}]`
* Custom report format when using segments and / or filters `[{"name": "<report-name>", "dimensions": ["<dimension-name>", ...], "metrics": ["<metric-name>", ...], "segments":  ["<segment-id-or-dynamic-segment-v3-format]", filter: "<filter-definition-v3-format>"}]`
* When using segments, make sure you add the `ga:segment` dimension.
* Custom reports: [Dimensions and metrics explorer](https://ga-dev-tools.web.app/dimensions-metrics-explorer/)

## Rate Limits & Performance Considerations \(Airbyte Open-Source\)

[Google Analytics Data API](https://developers.google.com/analytics/devguides/reporting/data/v1/quotas)

* Number of requests per day per project: 50,000

# Reports

The reports are custom by setting the dimensions and metrics required. To support Incremental sync, the `date` dimension is
added by default to all reports. There are 8 default reports. To add more reports, you need to specify the `custom reports` field.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                            |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------------|
| 0.1.1   | 2023-01-10 | [21169](https://github.com/airbytehq/airbyte/pull/21169) | Slicer updated, unit tests added                   |
| 0.1.0   | 2023-01-08 | [20889](https://github.com/airbytehq/airbyte/pull/20889) | Improved config validation, SAT                    |
| 0.0.3   | 2022-08-15 | [15229](https://github.com/airbytehq/airbyte/pull/15229) | Source Google Analytics Data Api: code refactoring |
| 0.0.2   | 2022-07-27 | [15087](https://github.com/airbytehq/airbyte/pull/15087) | fix documentationUrl                               |
| 0.0.1   | 2022-05-09 | [12701](https://github.com/airbytehq/airbyte/pull/12701) | Introduce Google Analytics Data API source         |
