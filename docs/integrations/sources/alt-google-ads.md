 Alternative Google Ads Source

This page contains the setup guide and reference information for the Alternative Google Ads source connector built in `low-code cdk`.

## Prerequisites

- A [Google Ads Account](https://support.google.com/google-ads/answer/6366720) [linked](https://support.google.com/google-ads/answer/7459601) to a [Google Ads Manager account](https://ads.google.com/home/tools/manager-accounts/)
- (For Airbyte Open Source) [A developer token](#step-1-for-airbyte-oss-apply-for-a-developer-token)

## Setup guide

### Step 1: (For Airbyte Open Source) Apply for a developer token

:::note
You'll need to create a [Google Ads Manager account](https://ads.google.com/home/tools/manager-accounts/) since Google Ads accounts cannot generate a developer token.
:::

To set up the Google Ads source connector with Airbyte Open Source, you'll need a developer token. This token allows you to access your data from the Google Ads API. However, Google is selective about which software and use cases can get a developer token. The Airbyte team has worked with the Google Ads team to allowlist Airbyte and make sure you can get a developer token (see [issue 1981](https://github.com/airbytehq/airbyte/issues/1981) for more information).

Follow [Google's instructions](https://developers.google.com/google-ads/api/docs/first-call/dev-token) to apply for the token. Note that you will _not_ be able to access your data via the Google Ads API until this token is approved. You cannot use a test developer token; it has to be at least a basic developer token. It usually takes Google 24 hours to respond to these applications.

When you apply for a token, make sure to mention:

- Why you need the token (example: Want to run some internal analytics)
- That you will be using the Airbyte Open Source project
- That you have full access to the code base (because we're open source)
- That you have full access to the server running the code (because you're self-hosting Airbyte)

### Step 2: Set up the Google Ads connector in Airbyte

#### For Airbyte Cloud

To set up Google Ads as a source in Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Google Ads** from the Source type dropdown.
4. Enter a **Name** for your source.
5. Click **Sign in with Google** to authenticate your Google Ads account.
6. Enter a comma-separated list of the [Customer ID(s)](https://support.google.com/google-ads/answer/1704344) for your account.
7. Enter the **Start Date** in YYYY-MM-DD format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
8. (Optional) Enter a custom [GAQL](#custom-query-understanding-google-ads-query-language) query.
9. (Optional) If the access to your account is through a [Google Ads Manager account](https://ads.google.com/home/tools/manager-accounts/), enter the [**Login Customer ID for Managed Accounts**](https://developers.google.com/google-ads/api/docs/concepts/call-structure#cid) of the Google Ads Manager account.
10. (Optional) Enter a [**Conversion Window**](https://support.google.com/google-ads/answer/3123169?hl=en).
11. (Optional) Enter the **End Date** in YYYY-MM-DD format. The data added after this date will not be replicated.
12. Click **Set up source**.

#### For Airbyte Open Source

To set up Google Ads as a source in Airbyte Open Source:

1. Log into your Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Google Ads** from the Source type dropdown.
4. Enter a **Name** for your source.
5. Enter the [**Developer Token**](#step-1-for-airbyte-oss-apply-for-a-developer-token).
6. To authenticate your Google account via OAuth, enter your Google application's [**Client ID**, **Client Secret**, **Refresh Token**, and optionally, the **Access Token**](https://developers.google.com/google-ads/api/docs/first-call/overview).
7. Enter a comma-separated list of the [Customer ID(s)](https://support.google.com/google-ads/answer/1704344) for your account.
8. Enter the **Start Date** in YYYY-MM-DD format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
9. (Optional) If the access to your account is through a [Google Ads Manager account](https://ads.google.com/home/tools/manager-accounts/), enter the [**Login Customer ID for Managed Accounts**](https://developers.google.com/google-ads/api/docs/concepts/call-structure#cid) of the Google Ads Manager account.
10. (Optional) Enter the **End Date** in YYYY-MM-DD format. The data added after this date will not be replicated.
11. Click **Set up source**.

## Supported sync modes

The Google Ads source connector supports the following[ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/glossary#full-refresh-sync)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental Sync - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

The Google Ads source connector can sync the following tables. It can also sync custom queries using GAQL.

### Main Tables

- [accounts](https://developers.google.com/google-ads/api/fields/v11/customer)
- [ad_group_ads](https://developers.google.com/google-ads/api/fields/v11/ad_group_ad)
- [ad_group_ad_labels](https://developers.google.com/google-ads/api/fields/v11/ad_group_ad_label)
- [ad_groups](https://developers.google.com/google-ads/api/fields/v11/ad_group)
- [ad_group_labels](https://developers.google.com/google-ads/api/fields/v11/ad_group_label)
- [campaign_labels](https://developers.google.com/google-ads/api/fields/v11/campaign_label)
- [click_view](https://developers.google.com/google-ads/api/reference/rpc/v11/ClickView)
- [keyword](https://developers.google.com/google-ads/api/fields/v11/keyword_view)
- [geographic](https://developers.google.com/google-ads/api/fields/v11/geographic_view)

Note that `ad_groups`, `ad_group_ads`, and `campaigns` contain a `labels` field, which should be joined against their respective `*_labels` streams if you want to view the actual labels. For example, the `ad_groups` stream contains an `ad_group.labels` field, which you would join against the `ad_group_labels` stream's `label.resource_name` field.

### Report Tables

- [campaigns](https://developers.google.com/google-ads/api/fields/v11/campaign)
- [account_performance_report](https://developers.google.com/google-ads/api/docs/migration/mapping#account_performance)
- [ad_group_ad_report](https://developers.google.com/google-ads/api/docs/migration/mapping#ad_performance)
- [display_keyword_report](https://developers.google.com/google-ads/api/docs/migration/mapping#display_keyword_performance)
- [display_topics_report](https://developers.google.com/google-ads/api/docs/migration/mapping#display_topics_performance)
- [user_location_report](https://developers.google.com/google-ads/api/fields/v11/user_location_view)

:::note
Due to Google Ads API constraints, the `click_view` stream retrieves data one day at a time and can only retrieve data newer than 90 days ago. Also, [metrics](https://developers.google.com/google-ads/api/fields/v11/metrics) cannot be requested for a Google Ads Manager account. Report streams are only available when pulling data from a non-manager account.
:::

For incremental streams, data is synced up to the previous day using your Google Ads account time zone since Google Ads can filter data only by [date](https://developers.google.com/google-ads/api/fields/v11/ad_group_ad#segments.date) without time. Also, some reports cannot load data real-time due to Google Ads [limitations](https://support.google.com/google-ads/answer/2544985?hl=en).


## Performance considerations

This source is constrained by the [Google Ads API limits](https://developers.google.com/google-ads/api/docs/best-practices/quotas)

Due to a limitation in the Google Ads API which does not allow getting performance data at a granularity level smaller than a day, the Google Ads connector usually pulls data up until the previous day. For example, if the sync runs on Wednesday at 5 PM, then data up until Tuesday midnight is pulled. Data for Wednesday is exported only if a sync runs after Wednesday (for example, 12:01 AM on Thursday) and so on. This avoids syncing partial performance data, only to have to resync it again once the full day's data has been recorded by Google. For example, without this functionality, a sync which runs on Wednesday at 5 PM would get ads performance data for Wednesday between 12:01 AM - 5 PM on Wednesday, then it would need to run again at the end of the day to get all of Wednesday's data.

## Changelog

| Version  | Date       | Pull Request                                             | Subject                                                                                                                              |
|:---------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------|                                                                                  |
| `0.1.0`  | 2022-10-26 | [4288](https://github.com/airbytehq/airbyte/pull/4288)   | `First Release`                                                                                      |
