# Facebook Marketing

## Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes | except AdCreatives |

## Supported Tables

This Source is capable of syncing the following tables and their data:

* [AdSets](https://developers.facebook.com/docs/marketing-api/reference/ad-campaign#fields)
* [Ads](https://developers.facebook.com/docs/marketing-api/reference/adgroup#fields)
* [AdCreatives](https://developers.facebook.com/docs/marketing-api/reference/ad-creative#fields)
* [Campaigns](https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group#fields)
* [AdInsights](https://developers.facebook.com/docs/marketing-api/reference/adgroup/insights/)

You can segment the AdInsights table into parts based on the following information. Each part will be synced as a separate table if normalization is enabled:

* Country
* DMA \(Designated Market Area\)
* Gender & Age
* Platform & Device
* Region

For more information, see the [Facebook Insights API documentation. ](https://developers.facebook.com/docs/marketing-api/reference/adgroup/insights/)\

## Getting Started \(Airbyte Cloud\)

1. Click `Authenticate your Facebook Marketing account`.
2. Enter your Account ID. Learn how to find it are [here](https://www.facebook.com/business/help/1492627900875762).
3. Enter a start date and your Insights settings.
4. You're done.

## Getting Started \(Airbyte Open-Source\)

#### Requirements

* A Facebook Ad Account ID
* A Facebook App which has the Marketing API enabled
* A Facebook Marketing API Access Token
* Request a rate limit increase from Facebook

Follow the [Facebook documentation for obtaining your Ad Account ID](https://www.facebook.com/business/help/1492627900875762) and keep that on hand. We'll need this ID to configure Facebook as a source in Airbyte.

#### If you don't have a Facebook App

Visit the [Facebook Developers App hub](https://developers.facebook.com/apps/) and create an App and choose "Manage Business Integrations" as the purpose of the app. Fill out the remaining fields to create your app, then follow along the "Enable the Marketing API for your app" section.

From the App's Dashboard screen \(seen in the screenshot below\) enable the Marketing API for your app if it is not already setup.

![](../../.gitbook/assets/facebook_marketing_api.png)

#### API Access Token

In the App Dashboard screen, click Marketing API --&gt; Tools on the left sidebar. Then highlight all the available token permissions \(`ads_management`, `ads_read`, `read_insights`\) and click "Get token". A long string of characters should appear in front of you; **this is the access token.** Copy this string for use in the Airbyte UI later.

![](../../.gitbook/assets/facebook_access_token.png)

### Request rate limit increase

Facebook [heavily throttles](https://developers.facebook.com/docs/marketing-api/overview/authorization#limits) API tokens generated from Facebook Apps with the "Standard Access" tier \(the default tier for new apps\), making it infeasible to use the token for syncs with Airbyte. You'll need to request an upgrade to Advanced Access for your app on the following permissions:

* Ads Management Standard Access
* ads\_read
* ads\_management

See the Facebook [documentation on Authorization](https://developers.facebook.com/docs/marketing-api/overview/authorization/#access-levels) for information about how to request Advanced Access to the relevant permissions.

With the Ad Account ID and API access token, you should be ready to start pulling data from the Facebook Marketing API. Head to the Airbyte UI to setup your source connector!

## Rate Limiting & Performance Considerations \(Airbyte Open Source\)

Facebook heavily throttles API tokens generated from Facebook Apps by default, making it infeasible to use such a token for syncs with Airbyte. To be able to use this connector without your syncs taking days due to rate limiting follow the instructions in the Setup Guide below to access better rate limits.

See Facebook's [documentation on rate limiting](https://developers.facebook.com/docs/marketing-api/overview/authorization/#access-levels) for more information on requesting a quota upgrade.

## Custom Insights
In order to retrieve specific fields from Facebook Ads Insights combined with other breakdowns, there is a mechanism to allow you to choose which fields and breakdowns to sync.
It is highly recommended to follow the [documenation](https://developers.facebook.com/docs/marketing-api/insights/breakdowns), as there are limitations related to breakdowns. Some fields can not be requested and many others just work combined with specific fields, for example, the breakdown **app_id** is only supported with the **total_postbacks** field.
By now, the only check done when setting up a source is to check if the fields, breakdowns and action breakdowns are within the ones provided by Facebook. This is, if you enter a good input, it's gonna be validated, but after, if the calls to Facebook API with those pareameters fails you will receive an error from the API.
As a summary, custom insights allows to replicate only some fields, resulting in sync speed increase.

#### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.2.32  | 2022-01-07 | [10138](https://github.com/airbytehq/airbyte/pull/10138) | Add `primary_key` for all insights streams. |
| 0.2.31  | 2021-12-29 | [9138](https://github.com/airbytehq/airbyte/pull/9138) | Fixed videos stream format field incorrect type |
| 0.2.30  | 2021-12-20 | [8962](https://github.com/airbytehq/airbyte/pull/8962) | Added `asset_feed_spec` field to `ad creatives` stream |
| 0.2.29  | 2021-12-17 | [8649](https://github.com/airbytehq/airbyte/pull/8649) | Retrive ad_creatives image as data encoded |
| 0.2.28  | 2021-12-13 | [8742](https://github.com/airbytehq/airbyte/pull/8742) | Fix for schema generation related to "breakdown" fields |
| 0.2.27  | 2021-11-29 | [8257](https://github.com/airbytehq/airbyte/pull/8257) | Add fields to Campaign stream |
| 0.2.26  | 2021-11-19 | [7855](https://github.com/airbytehq/airbyte/pull/7855) | Add Video stream |
| 0.2.25  | 2021-11-12 | [7904](https://github.com/airbytehq/airbyte/pull/7904) | Implement retry logic for async jobs |
| 0.2.24  | 2021-11-09 | [7744](https://github.com/airbytehq/airbyte/pull/7744) | Fix fail when async job takes too long |
| 0.2.23  | 2021-11-08 | [7734](https://github.com/airbytehq/airbyte/pull/7734) | Resolve $ref field for discover schema |
| 0.2.22  | 2021-11-05 | [7605](https://github.com/airbytehq/airbyte/pull/7605) | Add job retry logics to AdsInsights stream |
| 0.2.21  | 2021-10-05 | [4864](https://github.com/airbytehq/airbyte/pull/4864) | Update insights streams with custom entries for fields, breakdowns and action_breakdowns |
| 0.2.20 | 2021-10-04 | [6719](https://github.com/airbytehq/airbyte/pull/6719) | Update version of facebook\_bussiness package to 12.0 |
| 0.2.19 | 2021-09-30 | [6438](https://github.com/airbytehq/airbyte/pull/6438) | Annotate Oauth2 flow initialization parameters in connector specification |
| 0.2.18 | 2021-09-28 | [6499](https://github.com/airbytehq/airbyte/pull/6499) | Fix field values converting fail |
| 0.2.17 | 2021-09-14 | [4978](https://github.com/airbytehq/airbyte/pull/4978) | Convert values' types according to schema types |
| 0.2.16 | 2021-09-14 | [6060](https://github.com/airbytehq/airbyte/pull/6060) | Fix schema for `ads_insights` stream |
| 0.2.15 | 2021-09-14 | [5958](https://github.com/airbytehq/airbyte/pull/5958) | Fix url parsing and add report that exposes conversions |
| 0.2.14 | 2021-07-19 | [4820](https://github.com/airbytehq/airbyte/pull/4820) | Improve the rate limit management |
| 0.2.12 | 2021-06-20 | [3743](https://github.com/airbytehq/airbyte/pull/3743) | Refactor connector to use CDK: - Improve error handling. - Improve async job performance \(insights\). - Add new configuration parameter `insights_days_per_job`. - Rename stream `adsets` to `ad_sets`. - Refactor schema logic for insights, allowing to configure any possible insight stream. |
| 0.2.10 | 2021-06-16 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Update version of facebook\_bussiness to 11.0 |
| 0.2.9 | 2021-06-10 | [3996](https://github.com/airbytehq/airbyte/pull/3996) | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support |
| 0.2.8 | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add 80000 as a rate-limiting error code |
| 0.2.7 | 2021-06-03 | [3646](https://github.com/airbytehq/airbyte/pull/3646) | Add missing fields to AdInsights streams |
| 0.2.6 | 2021-05-25 | [3525](https://github.com/airbytehq/airbyte/pull/3525) | Fix handling call rate limit |
| 0.2.5 | 2021-05-20 | [3396](https://github.com/airbytehq/airbyte/pull/3396) | Allow configuring insights lookback window |
| 0.2.4 | 2021-05-13 | [3395](https://github.com/airbytehq/airbyte/pull/3395) | Fix an issue that caused losing Insights data from the past 28 days while incremental sync |
| 0.2.3 | 2021-04-28 | [3116](https://github.com/airbytehq/airbyte/pull/3116) | Wait longer \(5 min\) for async jobs to start |
| 0.2.2 | 2021-04-03 | [2726](https://github.com/airbytehq/airbyte/pull/2726) | Fix base connector versioning |
| 0.2.1 | 2021-03-12 | [2391](https://github.com/airbytehq/airbyte/pull/2391) | Support FB Marketing API v10 |
| 0.2.0 | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238) | Protocol allows future/unknown properties |
| 0.1.4 | 2021-02-24 | [1902](https://github.com/airbytehq/airbyte/pull/1902) | Add `include_deleted` option in params |
| 0.1.3 | 2021-02-15 | [1990](https://github.com/airbytehq/airbyte/pull/1990) | Support Insights stream via async queries |
| 0.1.2 | 2021-01-22 | [1699](https://github.com/airbytehq/airbyte/pull/1699) | Add incremental support |
| 0.1.1 | 2021-01-15 | [1552](https://github.com/airbytehq/airbyte/pull/1552) | Release Native Facebook Marketing Connector |
