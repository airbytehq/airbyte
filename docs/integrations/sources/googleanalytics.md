# Google Analytics

## Overview

The Google Analytics source supports Full Refresh syncs. That is, every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.

This Google Analytics source wraps the [Pipelinewise Singer Google Anaytics Tap](https://github.com/transferwise/pipelinewise-tap-google-analytics).

### Output streams

* `website_overview`
* `traffic_sources`
* `pages`
* `locations`
* `monthly_active_users`
* `four_weekly_active_users`
* `two_weekly_active_users`
* `weekly_active_users`
* `daily_active_users`
* `devices`

Please reach out to us on Slack or [create an issue](https://github.com/airbytehq/airbyte/issues) if you need to send custom Google Analytics report data with Airbyte.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |

### Performance considerations

The Google Analytics connector should not run into Google Analytics API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Create a Service Account
We recommend creating a service account specifically for Airbyte so you can set granular permissions. 

First, need to select or create a project in the Google Developers Console:

1. Sign in to the Google Account you are using for Google Analytics as an admin.
1. Go to the [Service accounts page](https://console.developers.google.com/iam-admin/serviceaccounts).
1. Click `Create service account`.
1. Create a JSON key file for the service user. The contents of this file will be provided as the `credentials_json` in the UI when authorizing GA after you grant permissions (see below).

### Add service account to the Google Analytics account
Use the service account email address to [add a user](https://support.google.com/analytics/answer/1009702) to the Google analytics view you want to access via the API. You will need to grant [Read & Analyze permissions](https://support.google.com/analytics/answer/2884495).

### Enable the APIs
1. Go to the [Google Analytics Reporting API dashboard](https://console.developers.google.com/apis/api/analyticsreporting.googleapis.com/overview) in the project for your service user. Enable the API for your account. You can set quotas and check usage.
1. Go to the [Google Analytics API dashboard](https://console.developers.google.com/apis/api/analytics.googleapis.com/overview) in the project for your service user. Enable the API for your account.
