# Google Ads

This page contains the setup guide and reference information for the Google Ads source connector.

## Prerequisites

- A [Google Ads Account](https://support.google.com/google-ads/answer/6366720) [linked](https://support.google.com/google-ads/answer/7459601) to a [Google Ads Manager account](https://ads.google.com/home/tools/manager-accounts/)
<!-- env:oss -->
- (For Airbyte Open Source) [A developer token](#step-1-for-airbyte-oss-apply-for-a-developer-token)
<!-- /env:oss -->

## Setup guide

<!-- env:oss -->

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

<!-- /env:oss -->
<!-- env:cloud -->

**For Airbyte Cloud:**

To set up Google Ads as a source in Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
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
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

To set up Google Ads as a source in Airbyte Open Source:

1. Log into your Airbyte Open Source account.
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

The Google Ads source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental Sync - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

**Important note**:

    Usage of Conversion Window may lead to duplicates in Incremental Sync,
    because connector is forced to read data in the given range (Last Sync - Conversion window)

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
- [shopping_performance_report](https://developers.google.com/google-ads/api/docs/migration/mapping#shopping_performance)
- [user_location_report](https://developers.google.com/google-ads/api/fields/v11/user_location_view)

:::note
Due to Google Ads API constraints, the `click_view` stream retrieves data one day at a time and can only retrieve data newer than 90 days ago. Also, [metrics](https://developers.google.com/google-ads/api/fields/v11/metrics) cannot be requested for a Google Ads Manager account. Report streams are only available when pulling data from a non-manager account.
:::

For incremental streams, data is synced up to the previous day using your Google Ads account time zone since Google Ads can filter data only by [date](https://developers.google.com/google-ads/api/fields/v11/ad_group_ad#segments.date) without time. Also, some reports cannot load data real-time due to Google Ads [limitations](https://support.google.com/google-ads/answer/2544985?hl=en).

<!-- /env:oss -->

## Custom Query: Understanding Google Ads Query Language

Additional streams for Google Ads can be dynamically created using custom queries.

The Google Ads Query Language queries the Google Ads API. Review the [Google Ads Query Language](https://developers.google.com/google-ads/api/docs/query/overview) and the [query builder](https://developers.google.com/google-ads/api/fields/v13/query_validator) to validate your query. You can then add these as custom queries when configuring the Google Ads source.

Example GAQL Custom Query:

```
SELECT
    campaign.name,
    metrics.conversions,
    metrics.conversions_by_conversion_date
FROM ad_group
```

Note the segments.date is automatically added to the output, and does not need to be specified in the custom query. All custom reports will by synced by day.

Each custom query in the input configuration must work for all the customer account IDs. Otherwise, the customer ID will be skipped for every query that fails the validation test. For example, if your query contains metrics fields in the select clause, it will not be executed against manager accounts.

Follow Google's guidance on [Selectability between segments and metrics](https://developers.google.com/google-ads/api/docs/reporting/segmentation#selectability_between_segments_and_metrics) when editing custom queries or default stream schemas (which will also be turned into GAQL queries by the connector). Fields like `segments.keyword.info.text`, `segments.keyword.info.match_type`, `segments.keyword.ad_group_criterion` in the `SELECT` clause tell the query to only get the rows of data that have keywords and remove any row that is not associated with a keyword. This is often unobvious and undesired behavior and can lead to missing data records. If you need this field in the stream, add a new stream instead of editing the existing ones.

:::info
For an existing Google Ads source, when you are updating or removing Custom GAQL Queries, you should also subsequently refresh your source schema to pull in any changes.
:::

<!-- env:oss -->

## Performance considerations

This source is constrained by the [Google Ads API limits](https://developers.google.com/google-ads/api/docs/best-practices/quotas)

Due to a limitation in the Google Ads API which does not allow getting performance data at a granularity level smaller than a day, the Google Ads connector usually pulls data up until the previous day. For example, if the sync runs on Wednesday at 5 PM, then data up until Tuesday midnight is pulled. Data for Wednesday is exported only if a sync runs after Wednesday (for example, 12:01 AM on Thursday) and so on. This avoids syncing partial performance data, only to have to resync it again once the full day's data has been recorded by Google. For example, without this functionality, a sync which runs on Wednesday at 5 PM would get ads performance data for Wednesday between 12:01 AM - 5 PM on Wednesday, then it would need to run again at the end of the day to get all of Wednesday's data.

## Changelog

| Version  | Date       | Pull Request                                             | Subject                                                                                                                               |
|:---------|:-----------|:---------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------|
| `0.4.3`  | 2023-07-05 | [27959](https://github.com/airbytehq/airbyte/pull/27959) | Add `audience` and `user_interest` streams                                                                                            |
| `0.3.3`  | 2023-07-03 | [27913](https://github.com/airbytehq/airbyte/pull/27913) | Improve Google Ads exception handling (wrong customer ID)                                                                             |
| `0.3.2`  | 2023-06-29 | [27835](https://github.com/airbytehq/airbyte/pull/27835) | Fix bug introduced in 0.3.1: update query template                                                                                    |
| `0.3.1`  | 2023-06-26 | [27711](https://github.com/airbytehq/airbyte/pull/27711) | Refactor date slicing; make start date inclusive                                                                                      |
| `0.3.0`  | 2023-06-26 | [27738](https://github.com/airbytehq/airbyte/pull/27738) | License Update: Elv2                                                                                                                  |
| `0.2.24` | 2023-06-06 | [27608](https://github.com/airbytehq/airbyte/pull/27608) | Improve Google Ads exception handling                                                                                                 |
| `0.2.23` | 2023-06-06 | [26905](https://github.com/airbytehq/airbyte/pull/26905) | Replace deprecated `authSpecification` in the connector specification with `advancedAuth`                                             |
| `0.2.22` | 2023-06-02 | [26948](https://github.com/airbytehq/airbyte/pull/26948) | Refactor error messages; add `pattern_descriptor` for fields in spec                                                                  |
| `0.2.21` | 2023-05-30 | [25314](https://github.com/airbytehq/airbyte/pull/25314) | Add full refresh custom table `asset_group_listing_group_filter`                                                                      |
| `0.2.20` | 2023-05-30 | [25624](https://github.com/airbytehq/airbyte/pull/25624) | Add `asset` Resource to full refresh custom tables (GAQL Queries)                                                                     |
| `0.2.19` | 2023-05-15 | [26209](https://github.com/airbytehq/airbyte/pull/26209) | Handle Token Refresh errors as `config_error`                                                                                         |
| `0.2.18` | 2023-05-15 | [25947](https://github.com/airbytehq/airbyte/pull/25947) | Improve GAQL parser error message if multiple resources provided                                                                      |
| `0.2.17` | 2023-05-11 | [25987](https://github.com/airbytehq/airbyte/pull/25987) | Categorized Config Errors Accurately                                                                                                  |
| `0.2.16` | 2023-05-10 | [25965](https://github.com/airbytehq/airbyte/pull/25965) | Fix Airbyte date-time data-types                                                                                                      |
| `0.2.14` | 2023-03-21 | [24945](https://github.com/airbytehq/airbyte/pull/24945) | For custom google query fixed schema type for "data_type: ENUM" and "is_repeated: true" to array of strings                           |
| `0.2.13` | 2023-03-21 | [24338](https://github.com/airbytehq/airbyte/pull/24338) | Migrate to v13                                                                                                                        |
| `0.2.12` | 2023-03-17 | [22985](https://github.com/airbytehq/airbyte/pull/22985) | Specified date formatting in specification                                                                                            |
| `0.2.11` | 2023-03-13 | [23999](https://github.com/airbytehq/airbyte/pull/23999) | Fix incremental sync for Campaigns stream                                                                                             |
| `0.2.10` | 2023-02-11 | [22703](https://github.com/airbytehq/airbyte/pull/22703) | Add support for custom full_refresh streams                                                                                           |
| `0.2.9`  | 2023-01-23 | [21705](https://github.com/airbytehq/airbyte/pull/21705) | Fix multibyte issue; Bump google-ads package to 19.0.0                                                                                |
| `0.2.8`  | 2023-01-18 | [21517](https://github.com/airbytehq/airbyte/pull/21517) | Write fewer logs                                                                                                                      |
| `0.2.7`  | 2023-01-10 | [20755](https://github.com/airbytehq/airbyte/pull/20755) | Add more logs to debug stuck syncs                                                                                                    |
| `0.2.6`  | 2022-12-22 | [20855](https://github.com/airbytehq/airbyte/pull/20855) | Retry 429 and 5xx errors                                                                                                              |
| `0.2.5`  | 2022-11-22 | [19700](https://github.com/airbytehq/airbyte/pull/19700) | Fix schema for `campaigns` stream                                                                                                     |
| `0.2.4`  | 2022-11-09 | [19208](https://github.com/airbytehq/airbyte/pull/19208) | Add TypeTransofrmer to Campaings stream to force proper type casting                                                                  |
| `0.2.3`  | 2022-10-17 | [18069](https://github.com/airbytehq/airbyte/pull/18069) | Add `segments.hour`, `metrics.ctr`, `metrics.conversions` and `metrics.conversions_values` fields to `campaigns` report stream        |
| `0.2.2`  | 2022-10-21 | [17412](https://github.com/airbytehq/airbyte/pull/17412) | Release with CDK >= 0.2.2                                                                                                             |
| `0.2.1`  | 2022-09-29 | [17412](https://github.com/airbytehq/airbyte/pull/17412) | Always use latest CDK version                                                                                                         |
| `0.2.0`  | 2022-08-23 | [15858](https://github.com/airbytehq/airbyte/pull/15858) | Mark the `query` and `table_name` fields in `custom_queries` as required                                                              |
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
| `0.1.16` | 2021-11-22 | [8178](https://github.com/airbytehq/airbyte/pull/8178)   | Clarify setup fields                                                                                                                  |
| `0.1.15` | 2021-10-07 | [6684](https://github.com/airbytehq/airbyte/pull/6684)   | Add new stream `click_view`                                                                                                           |
| `0.1.14` | 2021-10-01 | [6565](https://github.com/airbytehq/airbyte/pull/6565)   | Fix OAuth Spec File                                                                                                                   |
| `0.1.13` | 2021-09-27 | [6458](https://github.com/airbytehq/airbyte/pull/6458)   | Update OAuth Spec File                                                                                                                |
| `0.1.11` | 2021-09-22 | [6373](https://github.com/airbytehq/airbyte/pull/6373)   | Fix inconsistent segments.date field type across all streams                                                                          |
| `0.1.10` | 2021-09-13 | [6022](https://github.com/airbytehq/airbyte/pull/6022)   | Annotate Oauth2 flow initialization parameters in connector spec                                                                      |
| `0.1.9`  | 2021-09-07 | [5302](https://github.com/airbytehq/airbyte/pull/5302)   | Add custom query stream support                                                                                                       |
| `0.1.8`  | 2021-08-03 | [5509](https://github.com/airbytehq/airbyte/pull/5509)   | Allow additionalProperties in spec.json                                                                                               |
| `0.1.7`  | 2021-08-03 | [5422](https://github.com/airbytehq/airbyte/pull/5422)   | Correct query to not skip dates                                                                                                       |
| `0.1.6`  | 2021-08-03 | [5423](https://github.com/airbytehq/airbyte/pull/5423)   | Added new stream UserLocationReport                                                                                                   |
| `0.1.5`  | 2021-08-03 | [5159](https://github.com/airbytehq/airbyte/pull/5159)   | Add field `login_customer_id` to spec                                                                                                 |
| `0.1.4`  | 2021-07-28 | [4962](https://github.com/airbytehq/airbyte/pull/4962)   | Support new Report streams                                                                                                            |
| `0.1.3`  | 2021-07-23 | [4788](https://github.com/airbytehq/airbyte/pull/4788)   | Support main streams, fix bug with exception `DATE_RANGE_TOO_NARROW` for incremental streams                                          |
| `0.1.2`  | 2021-07-06 | [4539](https://github.com/airbytehq/airbyte/pull/4539)   | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support                                                                                       |
| `0.1.1`  | 2021-06-23 | [4288](https://github.com/airbytehq/airbyte/pull/4288)   | Fix `Bugfix: Correctly declare required parameters`                                                                                   |

<!-- /env:oss -->
