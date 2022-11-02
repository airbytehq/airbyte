# Google Ad Manager Connector

This pages guide you to the process of creating the source connector to the google ad manager api.
The connector is built using the [python google-ad-manager-api](https://github.com/googleads/googleads-python-lib/tree/master)


## How is google ad manager connector different from google ads connector?

There is actual little overlap between the two, google ads and ad manager are remnants of 2 different google products. Google Ads is a remnant of Google AdWords, which focuses on the ADVERTISERS and is a platform for managing advertising campaigns, so this can generate reports for someone who has created an advertisement - to show the reach of the ad, who saw it, etc.

On the flip side Google Ad Manager contains the remnants of google Doubleclick, and focuses on the PUBLISHERS, likewise, the generated reports focus on an individual who is running ads on their own site, and can be broken down by what platform they were shown on, the generated revenue, how often people on the site viewed an ad, etc.

They are two sides of the same coin but have very different applications and uses.
I hope this clears up the confusion between the two, Google has done a poor job on its end differentiating some of its products.


## Prerequisites

* JSON credentials for the service account that has access to Google Ad manager. For more details check [instructions](https://support.google.com/analytics/answer/1009702#zippy=%2Cin-this-article)
* OAuth 2.0 credentials for the service account that has access to Google Analytics
* Property ID
* customer name

## Custom reports

- For now the connector support only two custom reports: Ad Unit Per Hour Report, and Ad Unit per Referrer Report. You can create stream for your report by following the structure of the generated report.

## Step 1: Set up Source

### Create a Service Account

First, you need to select existing or create a new project in the Google Developers Console:

1. Sign in to the Google Account you are using for Google Analytics as an admin.
2. Go to the [Service accounts page](https://console.developers.google.com/iam-admin/serviceaccounts).
3. Click `Create service account`.
4. Create a JSON key file for the service user. The contents of this file will be provided as the `credentials_json` in the UI when authorizing GA after you grant permissions \(see below\).

### Add service account to the Google Analytics account

Use the service account email address to [add a user](https://support.google.com/analytics/answer/1009702) to the Google analytics view you want to access via the API. You will need to grant [Viewer permissions](https://support.google.com/analytics/answer/2884495).

### Enable the APIs

THIS NEED TO BE FILLED

### Property ID
## Step 2: Set up the source connector in Airbyte

Once you get your credentials, you can use them to setup the connector
## Supported sync modes

The Google Analytics source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
 - Full Refresh
 - Incremental

## Rate Limits & Performance Considerations \(Airbyte Open-Source\)

To be Filled

# Reports

To be filled

## Changelog

