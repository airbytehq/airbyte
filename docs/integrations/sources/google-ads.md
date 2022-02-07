# Google Ads

{% hint style="warning" %}
If you don't already have a developer token from Google Ads, make sure you follow the [instructions](google-ads.md#how-to-apply-for-the-developer-token) so your request doesn't get denied.
{% endhint %}

## Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |

## Supported Tables

This source is capable of syncing the following tables and their data:

#### Main Tables

* [accounts](https://developers.google.com/google-ads/api/fields/v8/customer)
* [ad\_group\_ads](https://developers.google.com/google-ads/api/fields/v8/ad_group_ad)
* [ad\_groups](https://developers.google.com/google-ads/api/fields/v8/ad_group)
* [campaigns](https://developers.google.com/google-ads/api/fields/v8/campaign)
* [click\_view](https://developers.google.com/google-ads/api/reference/rpc/v8/ClickView)
* [keyword](https://developers.google.com/google-ads/api/fields/v8/keyword_view)
* [geographic](https://developers.google.com/google-ads/api/fields/v8/geographic_view)


#### Report Tables

* [account\_performance\_report](https://developers.google.com/google-ads/api/docs/migration/mapping#account_performance)
* [ad\_group\_ad\_report](https://developers.google.com/google-ads/api/docs/migration/mapping#ad_performance)
* [display\_keyword\_report](https://developers.google.com/google-ads/api/docs/migration/mapping#display_keyword_performance)
* [display\_topics\_report](https://developers.google.com/google-ads/api/docs/migration/mapping#display_topics_performance)
* [shopping\_performance\_report](https://developers.google.com/google-ads/api/docs/migration/mapping#shopping_performance)

**Note**: Due to constraints from the Google Ads API, the `click_view` stream retrieves data one day at a time and can only retrieve data newer than 90 days ago

**Note**: Due to constraints from the Google Ads API, [metrics](https://developers.google.com/google-ads/api/fields/v8/metrics) cannot be requested for a manager account. Therefore, report streams are only available when pulling data from a non-manager account. 

**Note**: For incremental streams data is synced up to the previous day using your Google Ads account time zone. The reason is that Google Ads can filter data only by [date](https://developers.google.com/google-ads/api/fields/v8/ad_group_ad#segments.date) without time. Also, some report cannot load data in real time due to Google Ads [limitations](https://support.google.com/google-ads/answer/2544985?hl=en).

## Getting Started \(Airbyte-Cloud\)

1. Click `Authenticate your Google Ads account` to sign in with Google and authorize your account.
2. Get the customer ID for your account. Learn how to do that [here](https://support.google.com/google-ads/answer/1704344)
3. If your access to the account is through a manager account, get the customer ID of the manager account.
4. Fill out a start date, and optionally, a conversion window, and custom [GAQL](https://developers.google.com/google-ads/api/docs/query/overview).
5. You're done.

## Getting Started \(Airbyte Open-Source\)

#### Requirements

Google Ads Account with an approved Developer Token \(note: In order to get API access to Google Ads, you must have a "manager" account. This must be created separately from your standard account. You can find more information about this distinction in the [google ads docs](https://ads.google.com/home/tools/manager-accounts/).\)

* developer\_token
* client\_id
* client\_secret
* refresh\_token
* start\_date
* customer\_id
* login\_customer\_id \(you can find more information about this field in [Google Ads docs](https://developers.google.com/google-ads/api/docs/concepts/call-structure#cid)\)

#### Setup guide

This guide will provide information as if starting from scratch. Please skip over any steps you have already completed.

* Create an Google Ads Account. Here are [Google's instruction](https://support.google.com/google-ads/answer/6366720) on how to create one.
* Create an Google Ads MANAGER Account. Here are [Google's instruction](https://ads.google.com/home/tools/manager-accounts/) on how to create one.
* You should now have two Google Ads accounts: a normal account and a manager account. Link the Manager account to the normal account following [Google's documentation](https://support.google.com/google-ads/answer/7459601).
* Apply for a developer token \(**make sure you follow our** [**instructions**](google-ads.md#how-to-apply-for-the-developer-token)\) on your Manager account.  This token allows you to access your data from the Google Ads API. Here are [Google's instructions](https://developers.google.com/google-ads/api/docs/first-call/dev-token). The docs are a little unclear on this point, but you will _not_ be able to access your data via the Google Ads API until this token is approved. You cannot use a test developer token, it has to be at least a basic developer token. It usually takes Google 24 hours to respond to these applications. This developer token is the value you will use in the `developer_token` field.
* Fetch your `client_id`, `client_secret`, and `refresh_token`. Google provides [instructions](https://developers.google.com/google-ads/api/docs/first-call/overview) on how to do this.
* Select your `customer_id`. The `customer_id` refers to the id of each of your Google Ads accounts. This is the 10 digit number in the top corner of the page when you are in Google Ads UI. The source will only pull data from the accounts for which you provide an id. If you are having trouble finding it, check out [Google's instructions](https://support.google.com/google-ads/answer/1704344).

Wow! That was a lot of steps. We are working on making the OAuth flow for all of our connectors simpler \(allowing you to skip needing to get a `developer_token` and a `refresh_token` which are the most painful / time-consuming steps in this walkthrough\).

### How to apply for the developer token

Google is very picky about which software and which use case can get access to a developer token. The Airbyte team has worked with the Google Ads team to whitelist Airbyte and make sure you can get one \(see [issue 1981](https://github.com/airbytehq/airbyte/issues/1981) for more information\).

When you apply for a token, you need to mention:

* Why you need the token \(eg: want to run some internal analytics...\)
* That you will be using the Airbyte Open Source project
* That you have full access to the code base \(because we're open source\)
* That you have full access to the server running the code \(because you're self-hosting Airbyte\)

If for any reason the request gets denied, let us know and we will be able to unblock you.

#### Understanding Google Ads Query Language

The Google Ads Query Language can query the Google Ads API. Check out [Google Ads Query Language](https://developers.google.com/google-ads/api/docs/query/overview)

## Rate Limiting & Performance Considerations \(Airbyte Open Source\)

This source is constrained by whatever API limits are set for the Google Ads that is used. You can read more about those limits in the [Google Developer docs](https://developers.google.com/google-ads/api/docs/best-practices/quotas).

## CHANGELOG

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| `0.1.25` | 2022-02-04 | [9812](https://github.com/airbytehq/airbyte/pull/9812) | Handle `EXPIRED_PAGE_TOKEN` exception and retry with updated state. |
| `0.1.24` | 2022-02-04 | [9996](https://github.com/airbytehq/airbyte/pull/9996) | Use Google Ads API version V9. |
| `0.1.23` | 2022-01-25 | [8669](https://github.com/airbytehq/airbyte/pull/8669) | Add end date parameter in spec. |
| `0.1.22` | 2022-01-24 | [9608](https://github.com/airbytehq/airbyte/pull/9608) | Reduce stream slice date range. |
| `0.1.21` | 2021-12-28 | [9149](https://github.com/airbytehq/airbyte/pull/9149) | Update title and description |
| `0.1.20` | 2021-12-22 | [9071](https://github.com/airbytehq/airbyte/pull/9071) | Fix: Keyword schema enum |
| `0.1.19` | 2021-12-14 | [8431](https://github.com/airbytehq/airbyte/pull/8431) | Add new streams: Geographic and Keyword |
| `0.1.18` | 2021-12-09 | [8225](https://github.com/airbytehq/airbyte/pull/8225) | Include time_zone to sync. Remove streams for manager account. |
| `0.1.16` | 2021-11-22 | [8178](https://github.com/airbytehq/airbyte/pull/8178) | clarify setup fields |
| `0.1.15` | 2021-10-07 | [6684](https://github.com/airbytehq/airbyte/pull/6684) | Add new stream `click_view` |
| `0.1.14` | 2021-10-01 | [6565](https://github.com/airbytehq/airbyte/pull/6565) | Fix OAuth Spec File |
| `0.1.13` | 2021-09-27 | [6458](https://github.com/airbytehq/airbyte/pull/6458) | Update OAuth Spec File |
| `0.1.11` | 2021-09-22 | [\#6373](https://github.com/airbytehq/airbyte/pull/6373) | Fix inconsistent segments.date field type across all streams |
| `0.1.10` | 2021-09-13 | [\#6022](https://github.com/airbytehq/airbyte/pull/6022) | Annotate Oauth2 flow initialization parameters in connector spec |
| `0.1.9` | 2021-09-07 | [\#5302](https://github.com/airbytehq/airbyte/pull/5302) | Add custom query stream support |
| `0.1.8` | 2021-08-03 | [\#5509](https://github.com/airbytehq/airbyte/pull/5509) | allow additionalProperties in spec.json |
| `0.1.7` | 2021-08-03 | [\#5422](https://github.com/airbytehq/airbyte/pull/5422) | Correct query to not skip dates |
| `0.1.6` | 2021-08-03 | [\#5423](https://github.com/airbytehq/airbyte/pull/5423) | Added new stream UserLocationReport |
| `0.1.5` | 2021-08-03 | [\#5159](https://github.com/airbytehq/airbyte/pull/5159) | Add field `login_customer_id` to spec |
| `0.1.4` | 2021-07-28 | [\#4962](https://github.com/airbytehq/airbyte/pull/4962) | Support new Report streams |
| `0.1.3` | 2021-07-23 | [\#4788](https://github.com/airbytehq/airbyte/pull/4788) | Support main streams, fix bug with exception `DATE_RANGE_TOO_NARROW` for incremental streams |
| `0.1.2` | 2021-07-06 | [\#4539](https://github.com/airbytehq/airbyte/pull/4539) | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support |
| `0.1.1` | 2021-06-23 | [\#4288](https://github.com/airbytehq/airbyte/pull/4288) | `Bugfix: Correctly declare required parameters` |

