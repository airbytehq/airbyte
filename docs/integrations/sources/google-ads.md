# Google Ads

This page contains the setup guide and reference information for the Google Ads source connector.

## Prerequisites

Google Ads registered account with

- Customer ID
- Login Customer ID (you can find more information about this field in [Google Ads docs](https://developers.google.com/google-ads/api/docs/concepts/call-structure#cid))
- Custom GAQL Queries (if needed)

Also:

- Start Date
- End Date
- Conversion Window

For Airbyte OSS:
Google Ads Account with an approved Developer Token. (note: In order to get API access to Google Ads, you must have a "manager" account; standard accounts cannot generate a Developer Token. This manager account must be created separately from your standard account. You can find more information about this distinction in the [Google Ads docs](https://support.google.com/google-ads/answer/6139186).)
You'll also need to find these values. See the [setup guide](#setup-guide) for instructions.

- Client ID
- Client Secret
- Refresh Token

## Setup guide

### Step 1: Set up Google Ads

This guide will provide information as if starting from scratch. Please skip over any steps you have already completed.

1. Create a Google Ads Account. Here are [Google's instructions](https://support.google.com/google-ads/answer/6366720) on how to create one.
2. Create a Google Ads MANAGER Account. Here are [Google's instructions](https://ads.google.com/home/tools/manager-accounts/) on how to create one.
3. You should now have two Google Ads accounts: a normal account and a manager account. Link the Manager account to the normal account following [Google's documentation](https://support.google.com/google-ads/answer/7459601).
4. Select your `customer_id`. The `customer_id` refers to the id of each of your Google Ads accounts. This is the 10 digit number in the top corner of the page when you are in Google Ads UI. The source will only pull data from the accounts for which you provide an id. If you are having trouble finding it, check out [Google's instructions](https://support.google.com/google-ads/answer/1704344).

### Airbyte Open Source additional setup steps

1. Apply for a developer token (**make sure you follow our** [**instructions**](google-ads.md#how-to-apply-for-the-developer-token) on your Manager account. This token allows you to access your data from the Google Ads API. Here are [Google's instructions](https://developers.google.com/google-ads/api/docs/first-call/dev-token). The docs are a little unclear on this point, but you will _not_ be able to access your data via the Google Ads API until this token is approved. You cannot use a test developer token, it has to be at least a basic developer token. It usually takes Google 24 hours to respond to these applications. This developer token is the value you will use in the `developer_token` field.
2. Fetch your `client_id`, `client_secret`, and `refresh_token`. Google provides [instructions](https://developers.google.com/google-ads/api/docs/first-call/overview) on how to do this.

### How to apply for the developer token

Google is very picky about which software and which use case can get access to a developer token. The Airbyte team has worked with the Google Ads team to whitelist Airbyte and make sure you can get one (see [issue 1981](https://github.com/airbytehq/airbyte/issues/1981) for more information).
When you apply for a token, you need to mention:

- Why you need the token (eg: want to run some internal analytics...)
- That you will be using the Airbyte Open Source project
- That you have full access to the code base (because we're open source)
- That you have full access to the server running the code (because you're self-hosting Airbyte)

## Step 2: Set up the Google Ads connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Google Ads connector and select **Google Ads** from the Source type dropdown.
4. Click `Authenticate your Google Ads account` to sign in with Google and authorize your account.
5. Get the customer ID for your account. Learn how to do that [here](https://support.google.com/google-ads/answer/1704344)
6. If your access to the account is through a manager account, get the customer ID of the manager account.
7. Fill out a start date, and optionally, a conversion window, and custom [GAQL](https://developers.google.com/google-ads/api/docs/query/overview).
8. You're done.

### For Airbyte OSS:

1. Create a new Google Ads source with a suitable name.
2. Get the customer ID for your account. Learn how to do that [here](https://support.google.com/google-ads/answer/1704344)
3. If your access to the account is through a manager account, get the customer ID of the manager account.
4. Fill out a start date, and optionally, end date and a conversion window, and custom [GAQL](https://developers.google.com/google-ads/api/docs/query/overview).
5. Fill out the Client ID, Client Secret, Access Token(if any), Refresh Token and the Developer Token from [Step 1](#step-1-set-up-google-ads))
6. You're done

## Supported sync modes

The Google Ads source connector supports the following[ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh | Overwrite
- Full Refresh | Append
- Incremental Sync | Append
- Incremental Sync | Deduped History

## Supported Streams

This source is capable of syncing the tables described below and can sync custom queries using GAGL.
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
    Due to constraints from the Google Ads API, the `click_view` stream retrieves data one day at a time and can only retrieve data newer than 90 days ago
    :::

    :::note
    Due to constraints from the Google Ads API, [metrics](https://developers.google.com/google-ads/api/fields/v9/metrics) cannot be requested for a manager account. Therefore, report streams are only available when pulling data from a non-manager account.
    :::

    :::note
    For incremental streams data is synced up to the previous day using your Google Ads account time zone. The reason is that Google Ads can filter data only by [date](https://developers.google.com/google-ads/api/fields/v9/ad_group_ad#segments.date) without time. Also, some reports cannot load data in real time due to Google Ads [limitations](https://support.google.com/google-ads/answer/2544985?hl=en).
    :::

## Custom Query: understanding Google Ads Query Language

The Google Ads Query Language can query the Google Ads API. Check out [Google Ads Query Language](https://developers.google.com/google-ads/api/docs/query/overview) and the [query builder](https://developers.google.com/google-ads/api/docs/query/overview). You can add these as custom queries when configuring the Google Ads source.

    :::note
    Each custom query in the input configuration must work for all the customer account IDs. Otherwise, the customer ID will be skipped for every query that fails the validation test. For example, if your query contains `metrics` fields in the `select` clause, it will not be executed against manager accounts.
    :::

    :::warning
    Please take into account Google's note on [Selectability between segments and metrics](https://developers.google.com/google-ads/api/docs/reporting/segmentation#selectability_between_segments_and_metrics) when editing custom queries or default stream schemas (which will also be turned into GAQL queries by the connector). Fields like `segments.keyword.info.text`, `segments.keyword.info.match_type`, `segments.keyword.ad_group_criterion` in the `SELECT` clause tell the query to only get the rows of data that have keywords, and remove any row that is not associated with a keyword. This is often not obvious and undesired behaviour and can lead to missing data records. If you do need this field in the stream, please choose adding a new stream instead of editing existing ones.
    :::

## Performance considerations

This source is constrained by whatever API limits are set for the Google Ads that is used. You can read more about those limits in the [Google Developer docs](https://developers.google.com/google-ads/api/docs/best-practices/quotas).

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
