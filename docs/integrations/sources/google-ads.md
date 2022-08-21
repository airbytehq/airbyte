# Google Ads

This page contains the setup guide and reference information for the Google Ads source connector.

## Prerequisites

- A [Google Ads Account](https://support.google.com/google-ads/answer/6366720) [linked](https://support.google.com/google-ads/answer/7459601) to a [Google Ads Manager account](https://ads.google.com/home/tools/manager-accounts/)
- (For Airbyte OSS) [A developer token](#step-1-for-airbyte-oss-apply-for-a-developer-token)

## Setup guide

### Step 1: (For Airbyte OSS) Apply for a developer token

:::note
You'll need to create a [Google Ads Manager account](https://ads.google.com/home/tools/manager-accounts/) since Google Ads accounts cannot generate a developer token.
::: 

To set up the Google Ads source connector with Airbyte OSS, you'll need a developer token. This token allows you to access your data from the Google Ads API. However, Google is selective about which software and use cases can get a developer token. The Airbyte team has worked with the Google Ads team to allowlist Airbyte and make sure you can get a developer token (see [issue 1981](https://github.com/airbytehq/airbyte/issues/1981) for more information).

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

#### For Airbyte OSS

To set up Google Ads as a source in Airbyte OSS:

1. Log into your Airbyte OSS account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Google Ads** from the Source type dropdown.
4. Enter a **Name** for your source.
5. Enter the [**Developer Token**](#step-1-for-airbyte-oss-apply-for-a-developer-token).
6. To authenticate your Google account via OAuth, enter your Google application's [**Client ID**, **Client Secret**, **Refresh Token**, and optionally, the **Access Token**](https://developers.google.com/google-ads/api/docs/first-call/overview).
7. Enter a comma-separated list of the [Customer ID(s)](https://support.google.com/google-ads/answer/1704344) for your account.
8. Enter the **Start Date** in YYYY-MM-DD format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
9. (Optional) Enter a custom [GAQL](#custom-query-understanding-google-ads-query-language) query.
10. (Optional) If the access to your account is through a [Google Ads Manager account](https://ads.google.com/home/tools/manager-accounts/), enter the [**Login Customer ID for Managed Accounts**](https://developers.google.com/google-ads/api/docs/concepts/call-structure#cid) of the Google Ads Manager account.
11. (Optional) Enter a [**Conversion Window**](https://support.google.com/google-ads/answer/3123169?hl=en).
12. (Optional) Enter the **End Date** in YYYY-MM-DD format. The data added after this date will not be replicated. 
13. Click **Set up source**.

## Supported sync modes

The Google Ads source connector supports the following[ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/glossary#full-refresh-sync)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental Sync - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

The Google Ads source connector can sync the following tables. It can also sync custom queries using GAQL.

### Main Tables

- [accounts](https://developers.google.com/google-ads/api/fields/v9/customer)
- [ad_group_ads](https://developers.google.com/google-ads/api/fields/v9/ad_group_ad)
- [ad_group_ad_labels](https://developers.google.com/google-ads/api/fields/v9/ad_group_ad_label)
- [ad_groups](https://developers.google.com/google-ads/api/fields/v9/ad_group)
- [ad_group_labels](https://developers.google.com/google-ads/api/fields/v9/ad_group_label)
- [campaign_labels](https://developers.google.com/google-ads/api/fields/v9/campaign_label)
- [click_view](https://developers.google.com/google-ads/api/reference/rpc/v9/ClickView)
- [keyword](https://developers.google.com/google-ads/api/fields/v9/keyword_view)
- [geographic](https://developers.google.com/google-ads/api/fields/v9/geographic_view)

Note that `ad_groups`, `ad_group_ads`, and `campaigns` contain a `labels` field, which should be joined against their respective `*_labels` streams if you want to view the actual labels. For example, the `ad_groups` stream contains an `ad_group.labels` field, which you would join against the `ad_group_labels` stream's `label.resource_name` field.

### Report Tables

- [campaigns](https://developers.google.com/google-ads/api/fields/v9/campaign)
- [account_performance_report](https://developers.google.com/google-ads/api/docs/migration/mapping#account_performance)
- [ad_group_ad_report](https://developers.google.com/google-ads/api/docs/migration/mapping#ad_performance)
- [display_keyword_report](https://developers.google.com/google-ads/api/docs/migration/mapping#display_keyword_performance)
- [display_topics_report](https://developers.google.com/google-ads/api/docs/migration/mapping#display_topics_performance)
- [shopping_performance_report](https://developers.google.com/google-ads/api/docs/migration/mapping#shopping_performance)
- [user_location_report](https://developers.google.com/google-ads/api/fields/v9/user_location_view)

:::note
Due to Google Ads API constraints, the `click_view` stream retrieves data one day at a time and can only retrieve data newer than 90 days ago. Also, [metrics](https://developers.google.com/google-ads/api/fields/v9/metrics) cannot be requested for a Google Ads Manager account. Report streams are only available when pulling data from a non-manager account.
:::

For incremental streams, data is synced up to the previous day using your Google Ads account time zone since Google Ads can filter data only by [date](https://developers.google.com/google-ads/api/fields/v9/ad_group_ad#segments.date) without time. Also, some reports cannot load data real-time due to Google Ads [limitations](https://support.google.com/google-ads/answer/2544985?hl=en).

## Custom Query: Understanding Google Ads Query Language

The Google Ads Query Language can query the Google Ads API. Check out [Google Ads Query Language](https://developers.google.com/google-ads/api/docs/query/overview) and the [query builder](https://developers.google.com/google-ads/api/docs/query/overview). You can add these as custom queries when configuring the Google Ads source.

Each custom query in the input configuration must work for all the customer account IDs. Otherwise, the customer ID will be skipped for every query that fails the validation test. For example, if your query contains `metrics` fields in the `select` clause, it will not be executed against manager accounts.

Follow Google's guidance on [Selectability between segments and metrics](https://developers.google.com/google-ads/api/docs/reporting/segmentation#selectability_between_segments_and_metrics) when editing custom queries or default stream schemas (which will also be turned into GAQL queries by the connector). Fields like `segments.keyword.info.text`, `segments.keyword.info.match_type`, `segments.keyword.ad_group_criterion` in the `SELECT` clause tell the query to only get the rows of data that have keywords and remove any row that is not associated with a keyword. This is often unobvious and undesired behavior and can lead to missing data records. If you need this field in the stream, add a new stream instead of editing the existing ones.

## Performance considerations

This source is constrained by the [Google Ads API limits](https://developers.google.com/google-ads/api/docs/best-practices/quotas)

## Changelog

| Version  | Date       | Pull Request                                             | Subject                                                                                                                               |
|:---------|:-----------|:---------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------|
| `0.1.44` | 2022-07-27 | [15084](https://github.com/airbytehq/airbyte/pull/15084) | Fix data type `ad_group_criterion.topic.path` in `display_topics_performance_report` and shifted `campaigns` to non-managers streams  |
| `0.1.43` | 2022-07-12 | [14614](https://github.com/airbytehq/airbyte/pull/14614) | Update API version to `v11`, update `google-ads` to 17.0.0                                                                            |
| `0.1.42` | 2022-06-08 | [13624](https://github.com/airbytehq/airbyte/pull/13624) | Update `google-ads` to 15.1.1, pin `protobuf==3.20.0` to work on MacOS M1 machines (AMD)                                              |
| `0.1.41` | 2022-06-08 | [13618](https://github.com/airbytehq/airbyte/pull/13618) | Add missing dependency                                                                                                                |
| `0.1.40` | 2022-06-02 | [13423](https://github.com/airbytehq/airbyte/pull/13423) | Fix the missing data [issue](https://github.com/airbytehq/airbyte/issues/12999)                                                       |
| `0.1.39` | 2022-05-18 | [12914](https://github.com/airbytehq/airbyte/pull/12914) | Fix GAQL query validation and log auth errors instead of failing the sync                                                             |
| `0.1.38` | 2022-05-12 | [12807](https://github.com/airbytehq/airbyte/pull/12807) | Documentation updates                                                                                                                 |
| `0.1.37` | 2022-05-06 | [12651](https://github.com/airbytehq/airbyte/pull/12651) | Improve integration and unit tests                                                                                                    |
| `0.1.36` | 2022-04-19 | [12158](https://github.com/airbytehq/airbyte/pull/12158) | Fix `*_labels` streams data type                                                                                                      |
| `0.1.35` | 2022-04-18 | [9310](https://github.com/airbytehq/airbyte/pull/9310)   | Add new fields to reports                                                                                                             |
| `0.1.34` | 2022-03-29 | [11602](https://github.com/airbytehq/airbyte/pull/11602) | Add budget amount to campaigns stream.                                                                                                |
| `0.1.33` | 2022-03-29 | [11513](https://github.com/airbytehq/airbyte/pull/11513) | When `end_date` is configured in the future, use today's date instead.                                                                |
| `0.1.32` | 2022-03-24 | [11371](https://github.com/airbytehq/airbyte/pull/11371) | Improve how connection check returns error messages                                                                                   |
| `0.1.31` | 2022-03-23 | [11301](https://github.com/airbytehq/airbyte/pull/11301) | Update docs and spec to clarify usage                                                                                                 |
| `0.1.30` | 2022-03-23 | [11221](https://github.com/airbytehq/airbyte/pull/11221) | Add `*_labels` streams to fetch the label text rather than their IDs                                                                  |
| `0.1.29` | 2022-03-22 | [10919](https://github.com/airbytehq/airbyte/pull/10919) | Fix user location report schema and add to acceptance tests                                                                           |
| `0.1.28` | 2022-02-25 | [10372](https://github.com/airbytehq/airbyte/pull/10372) | Add network fields to click view stream                                                                                               |
| `0.1.27` | 2022-02-16 | [10315](https://github.com/airbytehq/airbyte/pull/10315) | Make `ad_group_ads` and other streams support incremental sync.                                                                       |
| `0.1.26` | 2022-02-11 | [10150](https://github.com/airbytehq/airbyte/pull/10150) | Add support for multiple customer IDs.                                                                                                |
| `0.1.25` | 2022-02-04 | [9812](https://github.com/airbytehq/airbyte/pull/9812)   | Handle `EXPIRED_PAGE_TOKEN` exception and retry with updated state.                                                                   |
| `0.1.24` | 2022-02-04 | [9996](https://github.com/airbytehq/airbyte/pull/9996)   | Use Google Ads API version V9.                                                                                                        |
| `0.1.23` | 2022-01-25 | [8669](https://github.com/airbytehq/airbyte/pull/8669)   | Add end date parameter in spec.                                                                                                       |
| `0.1.22` | 2022-01-24 | [9608](https://github.com/airbytehq/airbyte/pull/9608)   | Reduce stream slice date range.                                                                                                       |
| `0.1.21` | 2021-12-28 | [9149](https://github.com/airbytehq/airbyte/pull/9149)   | Update title and description                                                                                                          |
| `0.1.20` | 2021-12-22 | [9071](https://github.com/airbytehq/airbyte/pull/9071)   | Fix: Keyword schema enum                                                                                                              |
| `0.1.19` | 2021-12-14 | [8431](https://github.com/airbytehq/airbyte/pull/8431)   | Add new streams: Geographic and Keyword                                                                                               |
| `0.1.18` | 2021-12-09 | [8225](https://github.com/airbytehq/airbyte/pull/8225)   | Include time_zone to sync. Remove streams for manager account.                                                                        |
| `0.1.16` | 2021-11-22 | [8178](https://github.com/airbytehq/airbyte/pull/8178)   | clarify setup fields                                                                                                                  |
| `0.1.15` | 2021-10-07 | [6684](https://github.com/airbytehq/airbyte/pull/6684)   | Add new stream `click_view`                                                                                                           |
| `0.1.14` | 2021-10-01 | [6565](https://github.com/airbytehq/airbyte/pull/6565)   | Fix OAuth Spec File                                                                                                                   |
| `0.1.13` | 2021-09-27 | [6458](https://github.com/airbytehq/airbyte/pull/6458)   | Update OAuth Spec File                                                                                                                |
| `0.1.11` | 2021-09-22 | [6373](https://github.com/airbytehq/airbyte/pull/6373)   | Fix inconsistent segments.date field type across all streams                                                                          |
| `0.1.10` | 2021-09-13 | [6022](https://github.com/airbytehq/airbyte/pull/6022)   | Annotate Oauth2 flow initialization parameters in connector spec                                                                      |
| `0.1.9`  | 2021-09-07 | [5302](https://github.com/airbytehq/airbyte/pull/5302)   | Add custom query stream support                                                                                                       |
| `0.1.8`  | 2021-08-03 | [5509](https://github.com/airbytehq/airbyte/pull/5509)   | allow additionalProperties in spec.json                                                                                               |
| `0.1.7`  | 2021-08-03 | [5422](https://github.com/airbytehq/airbyte/pull/5422)   | Correct query to not skip dates                                                                                                       |
| `0.1.6`  | 2021-08-03 | [5423](https://github.com/airbytehq/airbyte/pull/5423)   | Added new stream UserLocationReport                                                                                                   |
| `0.1.5`  | 2021-08-03 | [5159](https://github.com/airbytehq/airbyte/pull/5159)   | Add field `login_customer_id` to spec                                                                                                 |
| `0.1.4`  | 2021-07-28 | [4962](https://github.com/airbytehq/airbyte/pull/4962)   | Support new Report streams                                                                                                            |
| `0.1.3`  | 2021-07-23 | [4788](https://github.com/airbytehq/airbyte/pull/4788)   | Support main streams, fix bug with exception `DATE_RANGE_TOO_NARROW` for incremental streams                                          |
| `0.1.2`  | 2021-07-06 | [4539](https://github.com/airbytehq/airbyte/pull/4539)   | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support                                                                                       |
| `0.1.1`  | 2021-06-23 | [4288](https://github.com/airbytehq/airbyte/pull/4288)   | `Bugfix: Correctly declare required parameters`                                                                                       |
