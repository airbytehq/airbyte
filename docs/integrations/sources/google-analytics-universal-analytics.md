# Google Analytics (Universal Analytics)

This page guides you through the process of setting up the Google Analytics source connector.

This connector supports [Google Analytics v4](https://developers.google.com/analytics/devguides/collection/ga4).

## Prerequisites

* A [Google Analytics](https://analytics.google.com/analytics/web/provision/#/provision) Account
* View ID
* Start date

## Step 1: Set up Source

Decide which Views you'd like to sync, prepare View IDs. Decide what date you'd like to start your data sync from.

## Step 2: Set up the source connector in Airbyte

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Google Analytics connector and select **Google Analytics** from the Source type dropdown.
4. Click `OAuth2.0 authorization` then `Authenticate your Google Analytics account`.
5. Find your View ID for the view you want to fetch data from. Find it [here](https://ga-dev-tools.web.app/account-explorer/).
6. Enter a start date, and custom report information.

**For Airbyte Open Source:**

There are 2 options of setting up authorization for this source:

* Create service account specifically for Airbyte and authorize with JWT. Select `JWT authorization` from the `Authentication mechanism` dropdown list.
* Use your Google account and authorize over Google's OAuth on connection setup. Select `Default OAuth2.0 authorization` from dropdown list.

#### Create a Service Account

First, you need to select existing or create a new project in the Google Developers Console:

1. Sign in to the Google Account you are using for Google Analytics as an admin.
2. Go to the [Service accounts page](https://console.developers.google.com/iam-admin/serviceaccounts).
3. Click `Create service account`.
4. Create a JSON key file for the service user. The contents of this file will be provided as the `credentials_json` in the UI when authorizing GA after you grant permissions \(see below\).

#### Add service account to the Google Analytics account

Use the service account email address to [add a user](https://support.google.com/analytics/answer/1009702) to the Google analytics view you want to access via the API. You will need to grant [Read & Analyze permissions](https://support.google.com/analytics/answer/2884495).

#### Enable the APIs

1. Go to the [Google Analytics Reporting API dashboard](https://console.developers.google.com/apis/api/analyticsreporting.googleapis.com/overview) in the project for your service user. Enable the API for your account. You can set quotas and check usage.
2. Go to the [Google Analytics API dashboard](https://console.developers.google.com/apis/api/analytics.googleapis.com/overview) in the project for your service user. Enable the API for your account.

## Supported sync modes

The Google Analytics source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
 - Full Refresh
 - Incremental

## Rate Limits & Performance Considerations \(Airbyte Open-Source\)

[Analytics Reporting API v4](https://developers.google.com/analytics/devguides/reporting/core/v4/limits-quotas)

* Number of requests per day per project: 50,000
* Number of requests per view \(profile\) per day: 10,000 \(cannot be increased\)
* Number of requests per 100 seconds per project: 2,000
* Number of requests per 100 seconds per user per project: 100 \(can be increased in Google API Console to 1,000\).

Talking about "requests per 100 seconds" limitations, the Google Analytics connector should not run into these limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.
In order not to meet the "requests per day" limitation, try increasing the `window_in_days` value. Unfortunately, it can not be overcome programmatically.

## Supported streams

This source is capable of syncing the following tables and their data:

| Stream name                  | Schema                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|:-----------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| website_overview             | `{"ga_date":"2021-02-11","ga_users":1,"ga_newUsers":0,"ga_sessions":9,"ga_sessionsPerUser":9.0,"ga_avgSessionDuration":28.77777777777778,"ga_pageviews":63,"ga_pageviewsPerSession":7.0,"ga_avgTimeOnPage":4.685185185185185,"ga_bounceRate":0.0,"ga_exitRate":14.285714285714285,"view_id":"211669975"}`                                                                                                                                                         |
| traffic_sources              | `{"ga_date":"2021-02-11","ga_source":"(direct)","ga_medium":"(none)","ga_socialNetwork":"(not set)","ga_users":1,"ga_newUsers":0,"ga_sessions":9,"ga_sessionsPerUser":9.0,"ga_avgSessionDuration":28.77777777777778,"ga_pageviews":63,"ga_pageviewsPerSession":7.0,"ga_avgTimeOnPage":4.685185185185185,"ga_bounceRate":0.0,"ga_exitRate":14.285714285714285,"view_id":"211669975"}`                                                                              |
| pages                        | `{"ga_date":"2021-02-11","ga_hostname":"mydemo.com","ga_pagePath":"/home5","ga_pageviews":63,"ga_uniquePageviews":9,"ga_avgTimeOnPage":4.685185185185185,"ga_entrances":9,"ga_entranceRate":14.285714285714285,"ga_bounceRate":0.0,"ga_exits":9,"ga_exitRate":14.285714285714285,"view_id":"211669975"}`                                                                                                                                                          |
| locations                    | `{"ga_date":"2021-02-11","ga_continent":"Americas","ga_subContinent":"Northern America","ga_country":"United States","ga_region":"Iowa","ga_metro":"Des Moines-Ames IA","ga_city":"Des Moines","ga_users":1,"ga_newUsers":0,"ga_sessions":1,"ga_sessionsPerUser":1.0,"ga_avgSessionDuration":29.0,"ga_pageviews":7,"ga_pageviewsPerSession":7.0,"ga_avgTimeOnPage":4.666666666666667,"ga_bounceRate":0.0,"ga_exitRate":14.285714285714285,"view_id":"211669975"}` |
| monthly_active_users         | `{"ga_date":"2021-02-11","ga_30dayUsers":1,"view_id":"211669975"}`                                                                                                                                                                                                                                                                                                                                                                                                |
| four_weekly_active_users     | `{"ga_date":"2021-02-11","ga_28dayUsers":1,"view_id":"211669975"}`                                                                                                                                                                                                                                                                                                                                                                                                |
| two_weekly_active_users      | `{"ga_date":"2021-02-11","ga_14dayUsers":1,"view_id":"211669975"}`                                                                                                                                                                                                                                                                                                                                                                                                |
| weekly_active_users          | `{"ga_date":"2021-02-11","ga_7dayUsers":1,"view_id":"211669975"}`                                                                                                                                                                                                                                                                                                                                                                                                 |
| daily_active_users           | `{"ga_date":"2021-02-11","ga_1dayUsers":1,"view_id":"211669975"}`                                                                                                                                                                                                                                                                                                                                                                                                 |
| devices                      | `{"ga_date":"2021-02-11","ga_deviceCategory":"desktop","ga_operatingSystem":"Macintosh","ga_browser":"Chrome","ga_users":1,"ga_newUsers":0,"ga_sessions":9,"ga_sessionsPerUser":9.0,"ga_avgSessionDuration":28.77777777777778,"ga_pageviews":63,"ga_pageviewsPerSession":7.0,"ga_avgTimeOnPage":4.685185185185185,"ga_bounceRate":0.0,"ga_exitRate":14.285714285714285,"view_id":"211669975"}`                                                                    |
| Any custom reports           | See [below](https://docs.airbyte.com/integrations/sources/google-analytics-v4#reading-custom-reports) for details.                                                                                                                                                                                                                                                                                                                                                |

Please reach out to us on Slack or [create an issue](https://github.com/airbytehq/airbyte/issues) if you need to send custom Google Analytics report data with Airbyte.

## Sampling in reports 

For users who are not on the Google Analytics 360 tier, the Google Analytics API may return sampled data if the amount of data in the user's Google Analytics account exceeds Google's [pre-determined compute thresholds](https://support.google.com/analytics/answer/2637192?hl=en&ref_topic=2601030&visit_id=637868645346124317-2833523666&rd=1#thresholds&zippy=%2Cin-this-article). Concretely, this means the data returned in the report is an estimate which may have some inaccuracy. This [Google page](https://support.google.com/analytics/answer/2637192) provides a comprehensive overview of how Google applies sampling to your data.  

In order to minimize the chances of sampling being applied to your data, Airbyte makes data requests to Google in one day increments (the smallest allowed date increment). This reduces the amount of data the Google API processes per request, thus minimizing the chances of sampling being applied. The downside of requesting data in one day increments is that it increases the time it takes to export your Google Analytics data. If sampling is not a concern, users can override this behavior by setting the optional `window_in_day` parameter is used to specify the number of days to look back and can be used to avoid sampling.
When sampling occurs, a warning is logged to the sync log.

## Data processing latency

According to the [Google Analytics API documentation in the "Data Processing Latency" section](https://support.google.com/analytics/answer/1070983?hl=en#DataProcessingLatency&zippy=%2Cin-this-article), all report data may continue to be updated 48 hours after it appears in the Google Analytics API. This means that if you request the same report twice within 48 hours of that data being sent to Google Analytics, the report data might be different across the two requests. This happens when Google Analytics is still processing all events it received. 

When this occurs, the returned data will set the flag `isDataGolden` to false. Like mentioned in the [Google Analytics API docs](https://developers.google.com/analytics/devguides/reporting/core/v4/rest/v4/reports/batchGet#reportdata):
> the `isDataGolden` flag indicates if [data] is golden or not. Data is golden when the exact same request [for a report] will not produce any new results if asked at a later point in time. 

To address this issue, the connector adds a lookback window of 2 days to ensure any previously synced non-golden data is re-synced with its potential updates. For example: If your last sync occurred 5 days ago and a sync kicks off today, it will attempt to sync data from 7 days ago up to the latest data available.

To determine whether data is finished processing or not, the `isDataGolden` flag is exposed and should be used.

## Requesting Custom Reports

You can replicate Google Analytics [Custom Reports](https://support.google.com/analytics/answer/1033013?hl=en) using this connector. To do this, input a JSON object as a string in the "Custom Reports" field when setting up the connector. The JSON is an array of objects where each object has the following schema:

```text
{"name": string, "dimensions": [string], "metrics": [string]}
```

Here is an example input "Custom Reports" field:

```text
[{"name": "new_users_per_day", "dimensions": ["ga:date","ga:country","ga:region"], "metrics": ["ga:newUsers"]}, {"name": "users_per_city", "dimensions": ["ga:city"], "metrics": ["ga:users"]}]
```

To create a list of dimensions, you can use default GA dimensions (listed below) or custom dimensions if you have some defined. Each report can contain no more than 7 dimensions, and they must all be unique. The default GA dimensions are:

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

To create a list of metrics, use a default GA metric (values from the list below) or custom metrics if you have defined them.  
A custom report can contain no more than 10 unique metrics. The default available GA metrics are:

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
| 0.1.25  | 2022-07-27  | [15087](https://github.com/airbytehq/airbyte/pull/15087) | Fix documentationUrl                                                                         |
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
