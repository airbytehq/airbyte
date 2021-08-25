# Google Analytics

## Overview

The Google Analytics source supports Full Refresh syncs. That is, every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.

This Source Connector is based on a [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

### Output streams

* `website_overview` \(Incremental\)
* `traffic_sources` \(Incremental\)
* `pages` \(Incremental\)
* `locations` \(Incremental\)
* `monthly_active_users` \(Incremental\)
* `four_weekly_active_users` \(Incremental\)
* `two_weekly_active_users` \(Incremental\)
* `weekly_active_users` \(Incremental\)
* `daily_active_users` \(Incremental\)
* `devices` \(Incremental\)
* Any custom reports you configure. See the section below on custom reports. 

Please reach out to us on Slack or [create an issue](https://github.com/airbytehq/airbyte/issues) if you need to send custom Google Analytics report data with Airbyte.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The Google Analytics connector should not run into Google Analytics API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Create a Service Account

We recommend creating a service account specifically for Airbyte so you can set granular permissions.

First, need to select or create a project in the Google Developers Console:

1. Sign in to the Google Account you are using for Google Analytics as an admin.
2. Go to the [Service accounts page](https://console.developers.google.com/iam-admin/serviceaccounts).
3. Click `Create service account`.
4. Create a JSON key file for the service user. The contents of this file will be provided as the `credentials_json` in the UI when authorizing GA after you grant permissions \(see below\).

### Add service account to the Google Analytics account

Use the service account email address to [add a user](https://support.google.com/analytics/answer/1009702) to the Google analytics view you want to access via the API. You will need to grant [Read & Analyze permissions](https://support.google.com/analytics/answer/2884495).

### Enable the APIs

1. Go to the [Google Analytics Reporting API dashboard](https://console.developers.google.com/apis/api/analyticsreporting.googleapis.com/overview) in the project for your service user. Enable the API for your account. You can set quotas and check usage.
2. Go to the [Google Analytics API dashboard](https://console.developers.google.com/apis/api/analytics.googleapis.com/overview) in the project for your service user. Enable the API for your account.

### Reading custom reports from Google Analytics

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

Incremental sync supports only if you add `ga:date` dimension to your custom report.

### Limits and Quotas on API Requests

[Analytics Reporting API v4](https://developers.google.com/analytics/devguides/reporting/core/v4/limits-quotas)

* Number of requests per day per project: 50,000
* Number of requests per view \(profile\) per day: 10,000 \(cannot be increased\)
* Number of requests per 100 seconds per project: 2,000
* Number of requests per 100 seconds per user per project: 100 \(can be increased in Google API Console to 1,000\).

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.0   | 2021-08-10 | [5290](https://github.com/airbytehq/airbyte/pull/5290) | Initial Release|
