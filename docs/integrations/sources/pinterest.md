# Pinterest

This page contains the setup guide and reference information for the Pinterest source connector.

## Prerequisites

Please read [How to get your credentials](https://developers.pinterest.com/docs/api/v5/#tag/Authentication).

## Setup guide
## Step 1: Set up the Pinterest connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Pinterest connector and select **Pinterest** from the Source type dropdown. 
4. Enter the `start_date` you want your sync to start from. `start_date` should be no older than 914 days from today, that's the restriction of the Pinterest API for some of the streams.
5. Choose `OAuth2.0` in `Authorization Method` list
6. Click on `Authenticate your Pinterest account` button
7. Proceed with OAuth authentication of your account in the pop-up window that appears after previous step
8. Click **Set up source**

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard
2. Set the name for your source 
3. Enter your `client_id`
4. Enter your `client_secret`
5. Enter your `refresh_token`
6. Enter the `start_date` you want your sync to start from.`start_date` should be no older than 914 days from today, that's the restriction of the Pinterest API for some of the streams.
5. Choose `OAuth2.0` in `Authorization Method` list

7. Click **Set up source**

## Supported sync modes

The Pinterest source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes        |
| SSL connection            | Yes        |
| Namespaces                | No         |

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

The connector is restricted by normal Pinterest [requests limitation](https://developers.pinterest.com/docs/api/v5/#tag/Rate-limits).

#####  Rate Limits

Analytics streams - 300 calls per day / per user \
Ad accounts streams (Campaigns, Ad groups, Ads) - 1000 calls per min / per user / per app \
Boards streams - 10 calls per sec / per user / per app

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                 |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------ |
| 0.1.8   | 2022-10-21 | [18285](https://github.com/airbytehq/airbyte/pull/18285) | Fix type of `start_date`                                                                                |
| 0.1.7   | 2022-09-29 | [17387](https://github.com/airbytehq/airbyte/pull/17387) | Set `start_date` dynamically based on API restrictions.                                                 |
| 0.1.6   | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304) | Use CDK 0.1.89                                                                                          |
| 0.1.5   | 2022-09-16 | [16799](https://github.com/airbytehq/airbyte/pull/16799) | Migrate to per-stream state                                                                             |
| 0.1.4   | 2022-09-06 | [16161](https://github.com/airbytehq/airbyte/pull/16161) | Added ability to handle `429 - Too Many Requests` error with respect to `Max Rate Limit Exceeded Error` |
| 0.1.3   | 2022-09-02 | [16271](https://github.com/airbytehq/airbyte/pull/16271) | Added support of `OAuth2.0` authentication method                                                       |
| 0.1.2   | 2021-12-22 | [10223](https://github.com/airbytehq/airbyte/pull/10223) | Fix naming of `AD_ID` and `AD_ACCOUNT_ID` fields                                                        |
| 0.1.1   | 2021-12-22 | [9043](https://github.com/airbytehq/airbyte/pull/9043)   | Update connector fields title/description                                                               |
| 0.1.0   | 2021-10-29 | [7493](https://github.com/airbytehq/airbyte/pull/7493)   | Release Pinterest CDK Connector                                                                         |
