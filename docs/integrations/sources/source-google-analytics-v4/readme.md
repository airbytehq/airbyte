# Google Analytics (Universal Analytics)

This page contains the setup guide and reference information for the Google Analytics (Universal Analytics) source connector.

This connector supports Universal Analytics properties through the [Reporting API v4](https://developers.google.com/analytics/devguides/reporting/core/v4).

:::caution

**The Google Analytics (Universal Analytics) connector will be deprecated soon.**

Google is phasing out Universal Analytics in favor of Google Analytics 4 (GA4). In consequence, we are deprecating the Google Analytics (Universal Analytics) connector and recommend that you migrate to the [Google Analytics 4 (GA4) connector](https://docs.airbyte.com/integrations/sources/google-analytics-data-api) as soon as possible to ensure your syncs are not affected.

Due to this deprecation, we will not be accepting new contributions for this source, and OAuth is no longer supported as an authentication method for new connections in Airbyte Cloud.

For more information, see ["Universal Analytics is going away"](https://support.google.com/analytics/answer/11583528).

:::

:::note

Google Analytics Universal Analytics (UA) connector, uses the older version of Google Analytics, which has been the standard for tracking website and app user behavior since 2012. 

[Google Analytics 4 (GA4) connector](https://docs.airbyte.com/integrations/sources/google-analytics-data-api) is the latest version of Google Analytics, which was introduced in 2020. It offers a new data model that emphasizes events and user properties, rather than pageviews and sessions. This new model allows for more flexible and customizable reporting, as well as more accurate measurement of user behavior across devices and platforms.

:::

## Prerequisites

A Google Cloud account with [Viewer permissions](https://support.google.com/analytics/answer/2884495) and [Google Analytics Reporting API](https://console.developers.google.com/apis/api/analyticsreporting.googleapis.com/overview) and [Google Analytics API](https://console.developers.google.com/apis/api/analytics.googleapis.com/overview) enabled.

## Setup guide

<!-- env:cloud -->
**For Airbyte Cloud:**

To set up Google Analytics as a source in Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, select **Google Analytics** from the **Source type** dropdown.
4. For Name, enter a name for the Google Analytics connector.
5. Authenticate your Google account via OAuth or Service Account Key Authentication.
    - To authenticate your Google account via OAuth, click **Sign in with Google** and complete the authentication workflow.
    - To authenticate your Google account via Service Account Key Authentication, enter your [Google Cloud service account key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys) in JSON format. Make sure the Service Account has the Project Viewer permission.
6. Enter the **Replication Start Date** in YYYY-MM-DD format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
7. Enter the [**View ID**](https://ga-dev-tools.appspot.com/account-explorer/) for the Google Analytics View you want to fetch data from.
8. Leave **Data request time increment in days (Optional)** blank or set to 1. For faster syncs, set this value to more than 1 but that might result in the Google Analytics API returning [sampled data](#sampled-data-in-reports), potentially causing inaccuracies in the returned results. The maximum allowed value is 364.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

To set up Google Analytics as a source in Airbyte Open Source:

1. Go to the Airbyte UI and click **Sources** and then click **+ New source**.
2. On the Set up the source page, select **Google Analytics** from the **Source type** dropdown.
3. Enter a name for the Google Analytics connector.
4. Authenticate your Google account via OAuth or Service Account Key Authentication:
    - To authenticate your Google account via OAuth, enter your Google application's [client ID, client secret, and refresh token](https://developers.google.com/identity/protocols/oauth2).
    - To authenticate your Google account via Service Account Key Authentication, enter your [Google Cloud service account key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys) in JSON format. Use the service account email address to [add a user](https://support.google.com/analytics/answer/1009702) to the Google analytics view you want to access via the API and grant [Read and Analyze permissions](https://support.google.com/analytics/answer/2884495).
5. Enter the **Replication Start Date** in YYYY-MM-DD format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
6. Enter the [**View ID**](https://ga-dev-tools.appspot.com/account-explorer/) for the Google Analytics View you want to fetch data from.
7. Optionally, enter a JSON object as a string in the **Custom Reports** field. For details, refer to [Requesting custom reports](#requesting-custom-reports)
8. Leave **Data request time increment in days (Optional)** blank or set to 1. For faster syncs, set this value to more than 1 but that might result in the Google Analytics API returning [sampled data](#sampled-data-in-reports), potentially causing inaccuracies in the returned results. The maximum allowed value is 364.
<!-- /env:oss -->

## Supported sync modes

The Google Analytics source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental Sync - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

:::caution

You need to add the service account email address on the account level, not the property level. Otherwise, an 403 error will be returned.

:::


## Supported streams

The Google Analytics (Universal Analytics) source connector can sync the following tables:

| Stream name              | Schema                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| :----------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| website_overview         | `{"ga_date":"2021-02-11","ga_users":1,"ga_newUsers":0,"ga_sessions":9,"ga_sessionsPerUser":9.0,"ga_avgSessionDuration":28.77777777777778,"ga_pageviews":63,"ga_pageviewsPerSession":7.0,"ga_avgTimeOnPage":4.685185185185185,"ga_bounceRate":0.0,"ga_exitRate":14.285714285714285,"view_id":"211669975"}`                                                                                                                                                         |
| traffic_sources          | `{"ga_date":"2021-02-11","ga_source":"(direct)","ga_medium":"(none)","ga_socialNetwork":"(not set)","ga_users":1,"ga_newUsers":0,"ga_sessions":9,"ga_sessionsPerUser":9.0,"ga_avgSessionDuration":28.77777777777778,"ga_pageviews":63,"ga_pageviewsPerSession":7.0,"ga_avgTimeOnPage":4.685185185185185,"ga_bounceRate":0.0,"ga_exitRate":14.285714285714285,"view_id":"211669975"}`                                                                              |
| pages                    | `{"ga_date":"2021-02-11","ga_hostname":"mydemo.com","ga_pagePath":"/home5","ga_pageviews":63,"ga_uniquePageviews":9,"ga_avgTimeOnPage":4.685185185185185,"ga_entrances":9,"ga_entranceRate":14.285714285714285,"ga_bounceRate":0.0,"ga_exits":9,"ga_exitRate":14.285714285714285,"view_id":"211669975"}`                                                                                                                                                          |
| locations                | `{"ga_date":"2021-02-11","ga_continent":"Americas","ga_subContinent":"Northern America","ga_country":"United States","ga_region":"Iowa","ga_metro":"Des Moines-Ames IA","ga_city":"Des Moines","ga_users":1,"ga_newUsers":0,"ga_sessions":1,"ga_sessionsPerUser":1.0,"ga_avgSessionDuration":29.0,"ga_pageviews":7,"ga_pageviewsPerSession":7.0,"ga_avgTimeOnPage":4.666666666666667,"ga_bounceRate":0.0,"ga_exitRate":14.285714285714285,"view_id":"211669975"}` |
| monthly_active_users     | `{"ga_date":"2021-02-11","ga_30dayUsers":1,"view_id":"211669975"}`                                                                                                                                                                                                                                                                                                                                                                                                |
| four_weekly_active_users | `{"ga_date":"2021-02-11","ga_28dayUsers":1,"view_id":"211669975"}`                                                                                                                                                                                                                                                                                                                                                                                                |
| two_weekly_active_users  | `{"ga_date":"2021-02-11","ga_14dayUsers":1,"view_id":"211669975"}`                                                                                                                                                                                                                                                                                                                                                                                                |
| weekly_active_users      | `{"ga_date":"2021-02-11","ga_7dayUsers":1,"view_id":"211669975"}`                                                                                                                                                                                                                                                                                                                                                                                                 |
| daily_active_users       | `{"ga_date":"2021-02-11","ga_1dayUsers":1,"view_id":"211669975"}`                                                                                                                                                                                                                                                                                                                                                                                                 |
| devices                  | `{"ga_date":"2021-02-11","ga_deviceCategory":"desktop","ga_operatingSystem":"Macintosh","ga_browser":"Chrome","ga_users":1,"ga_newUsers":0,"ga_sessions":9,"ga_sessionsPerUser":9.0,"ga_avgSessionDuration":28.77777777777778,"ga_pageviews":63,"ga_pageviewsPerSession":7.0,"ga_avgTimeOnPage":4.685185185185185,"ga_bounceRate":0.0,"ga_exitRate":14.285714285714285,"view_id":"211669975"}`                                                                    |
| Any custom reports       | See [below](https://docs.airbyte.com/integrations/sources/google-analytics-v4#reading-custom-reports) for details.                                                                                                                                                                                                                                                                                                                                                |

Reach out to us on Slack or [create an issue](https://github.com/airbytehq/airbyte/issues) if you need to send custom Google Analytics report data with Airbyte.

## Rate Limits and Performance Considerations \(Airbyte Open-Source\)

[Analytics Reporting API v4](https://developers.google.com/analytics/devguides/reporting/core/v4/limits-quotas)

* Number of requests per day per project: 50,000
* Number of requests per view (profile) per day: 10,000 (cannot be increased)
* Number of requests per 100 seconds per project: 2,000
* Number of requests per 100 seconds per user per project: 100 (can be increased in Google API Console to 1,000).

The Google Analytics connector should not run into the "requests per 100 seconds" limitation under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully and try increasing the `window_in_days` value.

## Sampled data in reports

If you are not on the Google Analytics 360 tier, the Google Analytics API may return sampled data if the amount of data in your Google Analytics account exceeds Google's [pre-determined compute thresholds](https://support.google.com/analytics/answer/2637192?hl=en&ref_topic=2601030&visit_id=637868645346124317-2833523666&rd=1#thresholds&zippy=%2Cin-this-article). This means the data returned in the report is an estimate which may have some inaccuracy. This [Google page](https://support.google.com/analytics/answer/2637192) provides a comprehensive overview of how Google applies sampling to your data.  

In order to minimize the chances of sampling being applied to your data, Airbyte makes data requests to Google in one day increments (the smallest allowed date increment). This reduces the amount of data the Google API processes per request, thus minimizing the chances of sampling being applied. The downside of requesting data in one day increments is that it increases the time it takes to export your Google Analytics data. If sampling is not a concern, you can override this behavior by setting the optional `window_in_day` parameter to specify the number of days to look back and avoid sampling.
When sampling occurs, a warning is logged to the sync log.

## Data processing latency

According to the [Google Analytics API documentation](https://support.google.com/analytics/answer/1070983?hl=en#DataProcessingLatency&zippy=%2Cin-this-article), all report data may continue to be updated 48 hours after it appears in the Google Analytics API. This means if you request the same report twice within 48 hours of that data being sent to Google Analytics, the report data might be different across the two requests. This happens when Google Analytics is still processing all events it received.

When this occurs, the returned data will set the flag `isDataGolden` to false. As mentioned in the [Google Analytics API docs](https://developers.google.com/analytics/devguides/reporting/core/v4/rest/v4/reports/batchGet#reportdata), the `isDataGolden` flag indicates if [data] is golden or not. Data is golden when the exact same request [for a report] will not produce any new results if asked at a later point in time.

To address this issue, the connector adds a lookback window of 2 days to ensure any previously synced non-golden data is re-synced with its potential updates. For example: If your last sync occurred 5 days ago and a sync is initiated today, the connector will attempt to sync data from 7 days ago up to the latest data available.

To determine whether data is finished processing or not, the `isDataGolden` flag is exposed and should be used.

## Requesting Custom Reports

To replicate Google Analytics [Custom Reports](https://support.google.com/analytics/answer/1033013?hl=en) using this connector, input a JSON object as a string in the **Custom Reports** field when setting up the connector. The JSON is an array of objects where each object has the following schema:

```text
{"name": string, "dimensions": [string], "metrics": [string]}
```

Here is an example input "Custom Reports" field:

```text
[{"name": "new_users_per_day", "dimensions": ["ga:date","ga:country","ga:region"], "metrics": ["ga:newUsers"]}, {"name": "users_per_city", "dimensions": ["ga:city"], "metrics": ["ga:users"]}]
```

To create a list of dimensions, you can use default Google Analytics dimensions (listed below) or custom dimensions if you have some defined. Each report can contain no more than 7 dimensions, and they must all be unique. The default Google Analytics dimensions are:

* `ga:browser`
* `ga:city`
* `ga:continent`
* `ga:country`
* `ga:date`
* `ga:deviceCategory`
* `ga:hostname`
* `ga:medium`
* `ga:metro`
* `ga:operatingSystem`
* `ga:pagePath`
* `ga:region`
* `ga:socialNetwork`
* `ga:source`
* `ga:subContinent`

To create a list of metrics, use a default Google Analytics metric (values from the list below) or custom metrics if you have defined them.  
A custom report can contain no more than 10 unique metrics. The default available Google Analytics metrics are:

* `ga:14dayUsers`
* `ga:1dayUsers`
* `ga:28dayUsers`
* `ga:30dayUsers`
* `ga:7dayUsers`
* `ga:avgSessionDuration`
* `ga:avgTimeOnPage`
* `ga:bounceRate`
* `ga:entranceRate`
* `ga:entrances`
* `ga:exitRate`
* `ga:exits`
* `ga:newUsers`
* `ga:pageviews`
* `ga:pageviewsPerSession`
* `ga:sessions`
* `ga:sessionsPerUser`
* `ga:uniquePageviews`
* `ga:users`

Incremental sync is supported only if you add `ga:date` dimension to your custom report.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                      |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------------------------------------------------------|
| 0.1.35  | 2023-05-31 | [26885](https://github.com/airbytehq/airbyte/pull/26885) | Remove `authSpecification` from spec in favour of `advancedAuth`                             |
| 0.1.34  | 2023-01-27 | [22006](https://github.com/airbytehq/airbyte/pull/22006) | Set `AvailabilityStrategy` for streams explicitly to `None`                                  |
| 0.1.33  | 2022-12-23 | [20858](https://github.com/airbytehq/airbyte/pull/20858) | Fix check connection                                                                         |  
| 0.1.32  | 2022-11-04 | [18965](https://github.com/airbytehq/airbyte/pull/18965) | Fix for `discovery` stage, when `custom_reports` are provided with single stream as `dict`   |  
| 0.1.31  | 2022-10-30 | [18670](https://github.com/airbytehq/airbyte/pull/18670) | Add `Custom Reports` schema validation on `check connection`                                 |
| 0.1.30  | 2022-10-13 | [17943](https://github.com/airbytehq/airbyte/pull/17943) | Fix pagination                                                                               |
| 0.1.29  | 2022-10-12 | [17905](https://github.com/airbytehq/airbyte/pull/17905) | Handle exceeded daily quota gracefully                                                       |
| 0.1.28  | 2022-09-24 | [16920](https://github.com/airbytehq/airbyte/pull/16920) | Added segments and filters to custom reports                                                 |
| 0.1.27  | 2022-10-07 | [17717](https://github.com/airbytehq/airbyte/pull/17717) | Improve CHECK by using `ga:hits` metric.                                                     |
| 0.1.26  | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/15087) | Migrate to per-stream states.                                                                |
| 0.1.25  | 2022-07-27 | [15087](https://github.com/airbytehq/airbyte/pull/15087) | Fix documentationUrl                                                                         |
| 0.1.24  | 2022-07-26 | [15042](https://github.com/airbytehq/airbyte/pull/15042) | Update `additionalProperties` field to true from schemas                                     |
| 0.1.23  | 2022-07-22 | [14949](https://github.com/airbytehq/airbyte/pull/14949) | Add handle request daily quota error                                                         |
| 0.1.22  | 2022-06-30 | [14298](https://github.com/airbytehq/airbyte/pull/14298) | Specify integer type for ga:dateHourMinute dimension                                         |
| 0.1.21  | 2022-04-30 | [12500](https://github.com/airbytehq/airbyte/pull/12500) | Improve input configuration copy                                                             |
| 0.1.20  | 2022-04-28 | [12426](https://github.com/airbytehq/airbyte/pull/12426) | Expose `isDataGOlden` field and always resync data two days back to make sure it is golden   |
| 0.1.19  | 2022-04-19 | [12150](https://github.com/airbytehq/airbyte/pull/12150) | Minor changes to documentation                                                               |
| 0.1.18  | 2022-04-07 | [11803](https://github.com/airbytehq/airbyte/pull/11803) | Improved documentation                                                                       |
| 0.1.17  | 2022-03-31 | [11512](https://github.com/airbytehq/airbyte/pull/11512) | Improved Unit and Acceptance tests coverage, fixed `read` with abnormally large state values |
| 0.1.16  | 2022-01-26 | [9480](https://github.com/airbytehq/airbyte/pull/9480)   | Reintroduce `window_in_days` and log warning when sampling occurs                            |
| 0.1.15  | 2021-12-28 | [9165](https://github.com/airbytehq/airbyte/pull/9165)   | Update titles and descriptions                                                               |
| 0.1.14  | 2021-12-09 | [8656](https://github.com/airbytehq/airbyte/pull/8656)   | Fix date format in schemas                                                                   |
| 0.1.13  | 2021-12-09 | [8676](https://github.com/airbytehq/airbyte/pull/8676)   | Fix `window_in_days` validation issue                                                        |
| 0.1.12  | 2021-12-03 | [8175](https://github.com/airbytehq/airbyte/pull/8175)   | Fix validation of unknown metric(s) or dimension(s) error                                    |
| 0.1.11  | 2021-11-30 | [8264](https://github.com/airbytehq/airbyte/pull/8264)   | Corrected date range                                                                         |
| 0.1.10  | 2021-11-19 | [8087](https://github.com/airbytehq/airbyte/pull/8087)   | Support `start_date` before the account has any data                                         |
| 0.1.9   | 2021-10-27 | [7410](https://github.com/airbytehq/airbyte/pull/7410)   | Add check for correct permission for requested `view_id`                                     |
| 0.1.8   | 2021-10-13 | [7020](https://github.com/airbytehq/airbyte/pull/7020)   | Add intermediary auth config support                                                         |
| 0.1.7   | 2021-10-07 | [6414](https://github.com/airbytehq/airbyte/pull/6414)   | Declare OAuth parameters in Google sources                                                   |
| 0.1.6   | 2021-09-27 | [6459](https://github.com/airbytehq/airbyte/pull/6459)   | Update OAuth Spec File                                                                       |
| 0.1.3   | 2021-09-21 | [6357](https://github.com/airbytehq/airbyte/pull/6357)   | Fix OAuth workflow parameters                                                                |
| 0.1.2   | 2021-09-20 | [6306](https://github.com/airbytehq/airbyte/pull/6306)   | Support of Airbyte OAuth initialization flow                                                 |
| 0.1.1   | 2021-08-25 | [5655](https://github.com/airbytehq/airbyte/pull/5655)   | Corrected validation of empty custom report                                                  |
| 0.1.0   | 2021-08-10 | [5290](https://github.com/airbytehq/airbyte/pull/5290)   | Initial Release                                                                              |
