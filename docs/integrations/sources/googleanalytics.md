# Google Analytics

## Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |
| Custom Reports | Yes |

This Google Analytics source wraps the [Pipelinewise Singer Google Analytics Tap](https://github.com/transferwise/pipelinewise-tap-google-analytics).

## Supported Tables

* website_overview
* traffic_sources
* pages
* locations
* monthly_active_users
* four_weekly_active_users
* two_weekly_active_users
* weekly_active_users
* daily_active_users
* devices
* Any custom reports. See [below](googleanalytics.md#reading-custom-reports-from-google-analytics) for details on reading them.

## Getting Started (Airbyte Cloud)
Airbyte Cloud supports OAuth for the [GoogleAnalytics V4 connector](./google-analytics-v4.md), but not this one. If you can't use the V4 connector, just proceed with the open-source instructions below.

## Getting Started (Airbyte Open-Source)

#### Create a Service Account

We recommend creating a service account specifically for Airbyte so you can set granular permissions.

First, need to select or create a project in the Google Developers Console:

1. Sign in to the Google Account you are using for Google Analytics as an admin.
2. Go to the [Service accounts page](https://console.developers.google.com/iam-admin/serviceaccounts).
3. Click `Create service account`.
4. Create a JSON key file for the service user. The contents of this file will be provided as the `credentials_json` in the UI when authorizing GA after you grant permissions \(see below\).

#### Add service account to the Google Analytics account

Use the service account email address to [add a user](https://support.google.com/analytics/answer/1009702) to the Google analytics view you want to access via the API. You will need to grant [Read & Analyze permissions](https://support.google.com/analytics/answer/2884495).

#### Enable the APIs

1. Go to the [Google Analytics Reporting API dashboard](https://console.developers.google.com/apis/api/analyticsreporting.googleapis.com/overview) in the project for your service user. Enable the API for your account. You can set quotas and check usage.
2. Go to the [Google Analytics API dashboard](https://console.developers.google.com/apis/api/analytics.googleapis.com/overview) in the project for your service user. Enable the API for your account.

#### Reading custom reports from Google Analytics

You can replicate Google Analytics [Custom Reports](https://support.google.com/analytics/answer/1033013?hl=en) using this source. To do this, input a JSON object as a string in the "Custom Reports" field when setting up the connector. The JSON is an array of objects where each object has the following schema:

```text
{"name": string, "dimensions": [string], "metrics": [string]}
```

Here is an example input "Custom Reports" field:

```text
[{"name": "new_users_per_day", "dimensions": ["ga:date","ga:country","ga:region"], "metrics": ["ga:newUsers"]}, {"name": "users_per_city", "dimensions": ["ga:city"], "metrics": ["ga:users"]}]
```

To create a list of dimensions, you can use default GA dimensions \(listed below\) or custom dimensions if you have some defined. Each report can contain no more than 7 dimensions, and they must all be unique. The default GA dimensions are:

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

To create a list of metrics, use a default GA metric \(values from the list below\) or custom metrics if you have defined them.  
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


## Rate Limiting & Performance Considerations

The Google Analytics connector should not run into Google Analytics API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

[Analytics Reporting API v4](https://developers.google.com/analytics/devguides/reporting/core/v4/limits-quotas)

* Number of requests per day per project: 50,000
* Number of requests per view \(profile\) per day: 10,000 \(cannot be increased\)
* Number of requests per 100 seconds per project: 2,000
* Number of requests per 100 seconds per user per project: 100 \(can be increased in Google API Console to 1,000\).

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.2.5   | 2021-06-15 | [3648](https://github.com/airbytehq/airbyte/pull/3648) | Add filter to removed unused catalog |
| 0.2.4   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support |
| 0.2.3   | 2021-04-03 | [2726](https://github.com/airbytehq/airbyte/pull/2726) | Fix base connector versioning |
| 0.2.2   | 2021-03-11 | [2302](https://github.com/airbytehq/airbyte/pull/2302) | Support incremental sync |
| 0.2.0   | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238) | Protocol allows future/unknown properties |
| 0.1.9   | 2021-03-03 | [2151](https://github.com/airbytehq/airbyte/pull/2151) | Support chunked syncs to avoid sampling |
| 0.1.8   | 2021-02-18 | [2098](https://github.com/airbytehq/airbyte/pull/2098) | Implement `custom_reports` parameter |
| 0.1.7   | 2021-02-15 | [2053](https://github.com/airbytehq/airbyte/pull/2053) | Update SingerHelper read method |
| 0.1.6   | 2021-02-12 | [2056](https://github.com/airbytehq/airbyte/pull/2056) | Update requires fields in specification |
| 0.1.5   | 2020-12-16 | [1331](https://github.com/airbytehq/airbyte/pull/1331) | Refactor Python base connector |
| 0.1.4   | 2020-11-30 | [1046](https://github.com/airbytehq/airbyte/pull/1046) | Add connectors using an index YAML file |
