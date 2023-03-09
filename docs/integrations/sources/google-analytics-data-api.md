# Google Analytics 4 (GA4)

This page guides you through the process of setting up the Google Analytics 4 source connector.

This connector supports GA4 properties through the [Analytics Data API v1](https://developers.google.com/analytics/devguides/reporting/data/v1).

## Prerequisites

A Google Cloud account with [Viewer permissions](https://support.google.com/analytics/answer/2884495) and [Google Analytics Reporting API](https://console.developers.google.com/apis/api/analyticsreporting.googleapis.com/overview) and [Google Analytics API](https://console.developers.google.com/apis/api/analytics.googleapis.com/overview) enabled.

## Setup guide

<!-- env:cloud -->
**For Airbyte Cloud:**

To set up Google Analytics 4 as a source in Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Google Analytics 4 (GA4)** from the Source type dropdown and enter a name for this connector.
4. Authenticate your Google account via OAuth or Service Account Key Authentication.
    - (Recommended) To authenticate your Google account via OAuth, click **Sign in with Google** and complete the authentication workflow.
    - To authenticate your Google account via Service Account Key Authentication, enter your [Google Cloud service account key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys) in JSON format. Use the service account email address to [add a user](https://support.google.com/analytics/answer/1009702) to the Google analytics view you want to access via the API and grant the [Viewer](https://support.google.com/analytics/answer/2884495) permission.
6. Enter the [**Property ID**](https://developers.google.com/analytics/devguides/reporting/data/v1/property-id#what_is_my_property_id).
7. Enter the **Start Date** from which to replicate report data in the format YYYY-MM-DD.
8. Optionally, to generate **Custom Reports**, enter a JSON array describing the [custom reports](#custom-reports) you want to sync from Google Analytics.
9. Leave **Data request time increment in days (Optional)** blank or set to 1. For faster syncs, set this value to more than 1 but that might result in inaccuracies in the returned results. The maximum allowed value is 364.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

To set up Google Analytics 4 as a source in Airbyte Open Source:

1. Go to the Airbyte UI, click **Sources**, and then click **+ New source**.
2. On the Set up the source page, select **Google Analytics 4 (GA4)** from the **Source type** dropdown.
3. Enter a name for the Google Analytics 4 connector.
4. Authenticate your Google account via OAuth or Service Account Key Authentication:
    - To authenticate your Google account via OAuth, enter your Google application's [client ID, client secret, and refresh token](https://developers.google.com/identity/protocols/oauth2).
    - To authenticate your Google account via Service Account Key Authentication, enter your [Google Cloud service account key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys) in JSON format. Use the service account email address to [add a user](https://support.google.com/analytics/answer/1009702) to the Google analytics view you want to access via the API and grant the [Viewer](https://support.google.com/analytics/answer/2884495) permission.
5. Enter the [**Property ID**](https://developers.google.com/analytics/devguides/reporting/data/v1/property-id#what_is_my_property_id).
6. Enter the **Start Date** from which to replicate report data in the format YYYY-MM-DD.
7. Optionally, to generate **Custom Reports**, enter a JSON array describing the [custom reports](#custom-reports) you want to sync from Google Analytics.
8. Leave **Data request time increment in days (Optional)** blank or set to 1. For faster syncs, set this value to more than 1 but that might result in inaccuracies in the returned results. The maximum allowed value is 364.
<!-- /env:oss -->

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

* Custom reports in format `[{"name": "<report-name>", "dimensions": ["<dimension-name>", ...], "metrics": ["<metric-name>", ...]}]`
* Custom report format when using segments and / or filters `[{"name": "<report-name>", "dimensions": ["<dimension-name>", ...], "metrics": ["<metric-name>", ...], "segments":  ["<segment-id-or-dynamic-segment-v3-format]", filter: "<filter-definition-v3-format>"}]`
* When using segments, make sure you add the `ga:segment` dimension.
* Custom reports: [Dimensions and metrics explorer](https://ga-dev-tools.web.app/dimensions-metrics-explorer/)

## Rate Limits & Performance Considerations \(Airbyte Open-Source\)

[Google Analytics Data API](https://developers.google.com/analytics/devguides/reporting/data/v1/quotas)

* Number of requests per day per project: 50,000

## Changelog

| Version | Date       | Pull Request                                             | Subject                                            |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------------|
| 0.1.1   | 2023-01-10 | [21169](https://github.com/airbytehq/airbyte/pull/21169) | Slicer updated, unit tests added                   |
| 0.1.0   | 2023-01-08 | [20889](https://github.com/airbytehq/airbyte/pull/20889) | Improved config validation, SAT                    |
| 0.0.3   | 2022-08-15 | [15229](https://github.com/airbytehq/airbyte/pull/15229) | Source Google Analytics Data Api: code refactoring |
| 0.0.2   | 2022-07-27 | [15087](https://github.com/airbytehq/airbyte/pull/15087) | fix documentationUrl                               |
| 0.0.1   | 2022-05-09 | [12701](https://github.com/airbytehq/airbyte/pull/12701) | Introduce Google Analytics Data API source         |
