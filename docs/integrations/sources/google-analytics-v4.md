# Google Analytics (v4)

This page guides you through the process of setting up the Google Analytics source connector.

This connector supports [Google Analytics v4](https://developers.google.com/analytics/devguides/collection/ga4).

## Prerequisites

* JSON credentials for the service account that has access to Google Analytics. For more details check [instructions](https://support.google.com/analytics/answer/1009702#zippy=%2Cin-this-article)
* Property ID
* Report name
* List of report dimensions comma separated
* List of report metrics comma separated
* Report start date
* Report end date

## Step 1: Set up Source

### Create a Service Account

First, you need to select existing or create a new project in the Google Developers Console:

1. Sign in to the Google Account you are using for Google Analytics as an admin.
2. Go to the [Service accounts page](https://console.developers.google.com/iam-admin/serviceaccounts).
3. Click `Create service account`.
4. Create a JSON key file for the service user. The contents of this file will be provided as the `credentials_json` in the UI when authorizing GA after you grant permissions \(see below\).

### Add service account to the Google Analytics account

Use the service account email address to [add a user](https://support.google.com/analytics/answer/1009702) to the Google analytics view you want to access via the API. You will need to grant [Read & Analyze permissions](https://support.google.com/analytics/answer/2884495).

### Enable the APIs

1. Go to the [Google Analytics Reporting API dashboard](https://console.developers.google.com/apis/api/analyticsreporting.googleapis.com/overview) in the project for your service user. Enable the API for your account. You can set quotas and check usage.
2. Go to the [Google Analytics API dashboard](https://console.developers.google.com/apis/api/analytics.googleapis.com/overview) in the project for your service user. Enable the API for your account.

### Property ID

Specify the Property ID as set [here](https://analytics.google.com/analytics/web/a54907729p153687530/admin/property/settings)

## Step 2: Set up the source connector in Airbyte

Set the required fields in the Google Analytics Data API connector page such as the JSON credentials, property ID,
report name, dimensions, metrics and start and end dates.

## Supported sync modes

The Google Analytics source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
 - Full Refresh
 - Incremental

## Rate Limits & Performance Considerations \(Airbyte Open-Source\)

[Google Analytics Data API](https://developers.google.com/analytics/devguides/reporting/data/v1/quotas)

* Number of requests per day per project: 50,000

# Reports

The reports are custom by setting the dimensions and metrics required. To support Incremental sync, the `date` dimension is
added by default to any report and no need to add it as a dimension. There is only 1 connector per report. To add more reports, you need to create 
a new connection.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                    |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------------------------|
| 0.0.2   | 2022-07-27 | [15087](https://github.com/airbytehq/airbyte/pull/15087) | fix documentationUrl                       |
| 0.0.1   | 2022-05-09 | [12701](https://github.com/airbytehq/airbyte/pull/12701) | Introduce Google Analytics Data API source |
