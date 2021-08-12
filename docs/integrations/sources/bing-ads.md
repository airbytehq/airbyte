# Bing Ads

## Overview

This source can sync data from the [Bing Ads](https://docs.microsoft.com/en-us/advertising/guides/?view=bingads-13).
Connector is based on a [Bing Ads Python SDK](https://github.com/BingAds/BingAds-Python-SDK).

### Output schema

This Source is capable of syncing the following core Streams:

* [Accounts](https://docs.microsoft.com/en-us/advertising/customer-management-service/searchaccounts?view=bingads-13)
* [Campaigns](https://docs.microsoft.com/en-us/advertising/campaign-management-service/getcampaignsbyaccountid?view=bingads-13)
* [AdGroups](https://docs.microsoft.com/en-us/advertising/campaign-management-service/getadgroupsbycampaignid?view=bingads-13)
* [Ads](https://docs.microsoft.com/en-us/advertising/campaign-management-service/getadsbyadgroupid?view=bingads-13)


### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |
| Namespaces | No |  |

### Performance considerations

API limits number of requests for all Microsoft Advertising clients. You can find detailied info [here](https://docs.microsoft.com/en-us/advertising/guides/services-protocol?view=bingads-13#throttling)

## Getting started

### Requirements

* accounts: Has 2 options
    - fetch data from all accounts to which you have access
    - you need to provide specific account ids for which you a going to pull data. Use this [guide](https://docs.microsoft.com/en-us/advertising/guides/get-started?view=bingads-13#get-ids) to find your account id
* user_id:  Sign in to the Microsoft Advertising web application. The URL will contain a uid key/value pair in the query string that identifies your User ID
* customer_id: Use this [guide](https://docs.microsoft.com/en-us/advertising/guides/get-started?view=bingads-13#get-ids) to get this id
* developer_token: You can find this token [here](https://docs.microsoft.com/en-us/advertising/guides/get-started?view=bingads-13#get-developer-token)
* refresh_token: Token received during [auth process](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth?view=bingads-13)
* client_secret: Secret generated during application registration
* client_id: Id generated during application registration

### Setup guide

* [Register Application](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-register?view=bingads-13) in Azure portal
* Perform these [steps](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-consent?view=bingads-13l) to get auth code.
* [Get refresh token](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-get-tokens?view=bingads-13) using auth code from previous step

Full authentication process described [here](https://docs.microsoft.com/en-us/advertising/guides/get-started?view=bingads-13#access-token)

Be aware that `refresh token` will expire in 90 days. You need to repeat auth process to get the new one `refresh token`


## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.0   | 2021-07-22 | [4911](https://github.com/airbytehq/airbyte/pull/4911) | Initial release supported core streams (Accounts, Campaigns, Ads, AdGroups) |
