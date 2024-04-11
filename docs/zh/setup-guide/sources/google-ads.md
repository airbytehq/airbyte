# Google Ads

This page contains the setup guide and reference information for Google Ads.

## Prerequisites

* A [Google Ads Account](https://support.google.com/google-ads/answer/6366720) linked to a [Google Ads Manager account](https://support.google.com/google-ads/answer/7459601)

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Namespaces | No |

## Setup guide

1. Select **Google Ads** from the Source list.

2. Enter a **Source Name**.

3. Click **Sign in with Google** to authenticate your Google Ads account. In the pop-up, select the appropriate Google account and click Continue to proceed.

4. Enter a comma-separated list of the **Customer ID(s)** for your account. These IDs are 10-digit numbers that uniquely identify your account. To find your Customer ID, please follow [Google's instructions](https://support.google.com/google-ads/answer/1704344).

5. (Optional) Enter a **Start Date** in `YYYY-MM-DD` format. The data added on and after this date will be replicated. Default start date is 2 years ago.

6. (Optional) You can use the **Custom GAQL Queries** field to enter a custom query using Google Ads Query Language. Click Add and enter your query, as well as the desired name of the table for this data in the destination. Multiple queries can be provided. For more information on formulating these queries, refer to our guide below.

7. (Required for Manager accounts) If accessing your account through a Google Ads Manager account, you must enter the [Customer ID](https://developers.google.com/google-ads/api/docs/concepts/call-structure#cid) of the Manager account.

8. (Optional) Enter a **Conversion Window**. This is the number of days after an ad interaction during which a conversion is recorded in Google Ads. For more information on this topic, refer to the [Google Ads Help Center](https://support.google.com/google-ads/answer/3123169?hl=en). This field defaults to 14 days.

9. (Optional) Enter an **End Date** in `YYYY-MM-DD` format. Any data added after this date will not be replicated. Leaving this field blank will replicate all data from the start date onward.

10. Click **Save & Test**.

## Supported streams

This source is capable of syncing the following streams:

### Main Tables

* [customer](https://developers.google.com/google-ads/api/fields/v14/customer)
* [customer_label](https://developers.google.com/google-ads/api/fields/v14/customer_label)
* [campaign_criterion](https://developers.google.com/google-ads/api/fields/v14/campaign_criterion)
* [campaign_bidding_strategy](https://developers.google.com/google-ads/api/fields/v14/campaign)
* [campaign_label](https://developers.google.com/google-ads/api/fields/v14/campaign_label)
* [label](https://developers.google.com/google-ads/api/fields/v14/label)
* [ad_group_ad](https://developers.google.com/google-ads/api/fields/v14/ad_group_ad)
* [ad_group_ad_label](https://developers.google.com/google-ads/api/fields/v14/ad_group_ad_label)
* [ad_group](https://developers.google.com/google-ads/api/fields/v14/ad_group)
* [ad_group_label](https://developers.google.com/google-ads/api/fields/v14/ad_group_label)
* [ad_group_bidding_strategy](https://developers.google.com/google-ads/api/fields/v14/ad_group)
* [ad_group_criterion](https://developers.google.com/google-ads/api/fields/v14/ad_group_criterion)
* [ad_listing_group_criterion](https://developers.google.com/google-ads/api/fields/v14/ad_group_criterion)
* [ad_group_criterion_label](https://developers.google.com/google-ads/api/fields/v14/ad_group_criterion_label)
* [audience](https://developers.google.com/google-ads/api/fields/v14/audience)
* [user_interest](https://developers.google.com/google-ads/api/fields/v14/user_interest)
* [click_view](https://developers.google.com/google-ads/api/reference/rpc/v14/ClickView)

### Report Tables

* [account_performance_report](https://developers.google.com/google-ads/api/docs/migration/mapping#account_performance)
* [campaign](https://developers.google.com/google-ads/api/fields/v14/campaign)
* [campaign_budget](https://developers.google.com/google-ads/api/fields/v13/campaign_budget)
* [geographic_view](https://developers.google.com/google-ads/api/fields/v14/geographic_view)
* [user_location_view](https://developers.google.com/google-ads/api/fields/v14/user_location_view)
* [display_keyword_view](https://developers.google.com/google-ads/api/fields/v14/display_keyword_view)
* [topic_view](https://developers.google.com/google-ads/api/fields/v14/topic_view)
* [shopping_performance_view](https://developers.google.com/google-ads/api/docs/migration/mapping#shopping_performance)
* [keyword_view](https://developers.google.com/google-ads/api/fields/v14/keyword_view)
* [ad_group_ad_legacy](https://developers.google.com/google-ads/api/fields/v14/ad_group_ad)

## Troubleshooting

1. This source is constrained by the [Google Ads API limits](https://developers.google.com/google-ads/api/docs/best-practices/quotas).

  Due to a limitation in the Google Ads API which does not allow getting performance data at a granularity level smaller than a day, the Google Ads connector usually pulls data up until the previous day. For example, if the sync runs on Wednesday at 5 PM, then data up until Tuesday midnight is pulled. Data for Wednesday is exported only if a sync runs after Wednesday (for example, 12:01 AM on Thursday) and so on. This avoids syncing partial performance data, only to have to resync it again once the full day's data has been recorded by Google. For example, without this functionality, a sync which runs on Wednesday at 5 PM would get ads performance data for Wednesday between 12:01 AM - 5 PM on Wednesday, then it would need to run again at the end of the day to get all of Wednesday's data.

2. Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.
