# Pinterest

## Overview

The Pinterest source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Source Connector is based on a [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

### Output schema

Several output streams are available from this source:

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


If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The connector is restricted by normal Pinterest [requests limitation](https://developers.pinterest.com/docs/api/v5/#tag/Rate-limits).

#####  Rate Limits

Analytics streams - 300 calls per day / per user \
Ad accounts streams (Campaigns, Ad groups, Ads) - 1000 calls per min / per user / per app \
Boards streams - 10 calls per sec / per user / per app

The Pinterest connector should not run into Pinterest API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Pinterest Client Id
* Pinterest Client Secret
* Pinterest Refresh token

### Setup guide

Please read [How to get your credentials](https://developers.pinterest.com/docs/api/v5/#tag/Authentication).

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2021-10-29 | [7493](https://github.com/airbytehq/airbyte/pull/7493) | Release Pinterest CDK Connector |

