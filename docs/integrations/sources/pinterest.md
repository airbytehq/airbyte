# Pinterest

This page contains the setup guide and reference information for the Pinterest source connector.

## Prerequisites

To set up the Pinterest source connector with Airbyte Open Source, you'll need your Pinterest [App ID and secret key](https://developers.pinterest.com/docs/getting-started/set-up-app/) and the [refresh token](https://developers.pinterest.com/docs/getting-started/authentication/#Refreshing%20an%20access%20token).

## Setup guide

<!-- env:cloud -->
**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Pinterest** from the Source type dropdown.
4. Enter the name for the Pinterest connector.
5. For **Start Date**, enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data. As per Pinterest API restriction, the date cannot be more than 90 days in the past.
6. The **OAuth2.0** authorization method is selected by default. Click **Authenticate your Pinterest account**. Log in and authorize your Pinterest account.
7. Click **Set up source**.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Pinterest** from the Source type dropdown.
4. Enter the name for the Pinterest connector.
5. For **Start Date**, enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data. As per Pinterest API restriction, the date cannot be more than 90 days in the past.
6. The **OAuth2.0** authorization method is selected by default. For **Client ID** and **Client Secret**, enter your Pinterest [App ID and secret key](https://developers.pinterest.com/docs/getting-started/set-up-app/). For **Refresh Token**, enter your Pinterest [Refresh Token](https://developers.pinterest.com/docs/getting-started/authentication/#Refreshing%20an%20access%20token).
7. Click **Set up source**.
<!-- /env:oss -->

## Supported sync modes

The Pinterest source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

* [Account analytics](https://developers.pinterest.com/docs/api/v5/#operation/user_account/analytics) \(Incremental\)
* [Boards](https://developers.pinterest.com/docs/api/v5/#operation/boards/list) \(Full table\)
  * [Board sections](https://developers.pinterest.com/docs/api/v5/#operation/board_sections/list) \(Full table\)
    * [Pins on board section](https://developers.pinterest.com/docs/api/v5/#operation/board_sections/list_pins) \(Full table\)
  * [Pins on board](https://developers.pinterest.com/docs/api/v5/#operation/boards/list_pins) \(Full table\)
* [Ad accounts](https://developers.pinterest.com/docs/api/v5/#operation/ad_accounts/list) \(Full table\)
  * [Ad account analytics](https://developers.pinterest.com/docs/api/v5/#operation/ad_account/analytics) \(Incremental\)
  * [Campaigns](https://developers.pinterest.com/docs/api/v5/#operation/campaigns/list) \(Incremental\)
    * [Campaign analytics](https://developers.pinterest.com/docs/api/v5/#operation/campaigns/list) \(Incremental\)
  * [Ad groups](https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/list) \(Incremental\)
    * [Ad group analytics](https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/analytics) \(Incremental\)
  * [Ads](https://developers.pinterest.com/docs/api/v5/#operation/ads/list) \(Incremental\)
    * [Ad analytics](https://developers.pinterest.com/docs/api/v5/#operation/ads/analytics) \(Incremental\)

## Performance considerations

The connector is restricted by the Pinterest [requests limitation](https://developers.pinterest.com/docs/api/v5/#tag/Rate-limits).

#####  Rate Limits

- Analytics streams: 300 calls per day / per user \
- Ad accounts streams (Campaigns, Ad groups, Ads): 1000 calls per min / per user / per app \
- Boards streams: 10 calls per sec / per user / per app

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                 |
|:--------|:-----------|:---------------------------------------------------------|:--------------------------------------------------------------------------------------------------------|
| 0.5.2   | 2023-06-02 | [26949](https://github.com/airbytehq/airbyte/pull/26949) | Update `BoardPins` stream with `note` property                                                         |
| 0.5.1   | 2023-05-11 | [25984](https://github.com/airbytehq/airbyte/pull/25984) | Add pattern for start_date                                                                              |
| 0.5.0   | 2023-05-17 | [26188](https://github.com/airbytehq/airbyte/pull/26188) | Add `product_tags` field to the `BoardPins` stream                                                      |
| 0.4.0   | 2023-05-16 | [26112](https://github.com/airbytehq/airbyte/pull/26112) | Add `is_standard` field to the `BoardPins` stream                                                       |
| 0.3.0   | 2023-05-09 | [25915](https://github.com/airbytehq/airbyte/pull/25915) | Add `creative_type` field to the `BoardPins` stream                                                     |
| 0.2.6   | 2023-04-26 | [25548](https://github.com/airbytehq/airbyte/pull/25548) | Fixed `format` issue for `boards` stream schema for fields with `date-time`                             |
| 0.2.5   | 2023-04-19 | [00000](https://github.com/airbytehq/airbyte/pull/00000) | Update `AMOUNT_OF_DAYS_ALLOWED_FOR_LOOKUP` to 89 days                                                   |
| 0.2.4   | 2023-02-25 | [23457](https://github.com/airbytehq/airbyte/pull/23457) | Adding missing columns for analytics streams for pinterest source                                       |
| 0.2.3   | 2023-03-01 | [23649](https://github.com/airbytehq/airbyte/pull/23649) | Fix for `HTTP - 400 Bad Request` when requesting data >= 90 days                                        |
| 0.2.2   | 2023-01-27 | [22020](https://github.com/airbytehq/airbyte/pull/22020) | Set `AvailabilityStrategy` for streams explicitly to `None`                                             |
| 0.2.1   | 2022-12-15 | [20532](https://github.com/airbytehq/airbyte/pull/20532) | Bump CDK version                                                                                        |
| 0.2.0   | 2022-12-13 | [20242](https://github.com/airbytehq/airbyte/pull/20242) | Added data-type normalization up to the schemas declared                                                |
| 0.1.9   | 2022-09-06 | [15074](https://github.com/airbytehq/airbyte/pull/15074) | Added filter based on statuses                                                                          |
| 0.1.8   | 2022-10-21 | [18285](https://github.com/airbytehq/airbyte/pull/18285) | Fix type of `start_date`                                                                                |
| 0.1.7   | 2022-09-29 | [17387](https://github.com/airbytehq/airbyte/pull/17387) | Set `start_date` dynamically based on API restrictions.                                                 |
| 0.1.6   | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304) | Use CDK 0.1.89                                                                                          |
| 0.1.5   | 2022-09-16 | [16799](https://github.com/airbytehq/airbyte/pull/16799) | Migrate to per-stream state                                                                             |
| 0.1.4   | 2022-09-06 | [16161](https://github.com/airbytehq/airbyte/pull/16161) | Added ability to handle `429 - Too Many Requests` error with respect to `Max Rate Limit Exceeded Error` |
| 0.1.3   | 2022-09-02 | [16271](https://github.com/airbytehq/airbyte/pull/16271) | Added support of `OAuth2.0` authentication method                                                       |
| 0.1.2   | 2021-12-22 | [10223](https://github.com/airbytehq/airbyte/pull/10223) | Fix naming of `AD_ID` and `AD_ACCOUNT_ID` fields                                                        |
| 0.1.1   | 2021-12-22 | [9043](https://github.com/airbytehq/airbyte/pull/9043)   | Update connector fields title/description                                                               |
| 0.1.0   | 2021-10-29 | [7493](https://github.com/airbytehq/airbyte/pull/7493)   | Release Pinterest CDK Connector                                                                         |
