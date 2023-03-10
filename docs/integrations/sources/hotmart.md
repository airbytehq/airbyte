# Hotmart

This page guides you through the process of setting up the Hotmart source connector.

## Prerequisites

* [Hotmart Developer Credentials](https://app-vlc.hotmart.com/tools/credentials)

## Sync overview

This source can sync data for the [Hotmart Developers API](https://developers.hotmart.com/docs/en/).

### Output schema

This Source is capable of syncing the following core Streams:

* [SalesHistory](https://developers.hotmart.com/docs/en/v1/sales/sales-history)
* [SalesCommissions](https://developers.hotmart.com/docs/en/v1/sales/sales-commissions)
* [SalesPriceDetails](https://developers.hotmart.com/docs/en/v1/sales/sales-price-details)
* [SalesUsers](https://developers.hotmart.com/docs/en/v1/sales/sales-users)

### Performance considerations / Rate Limiting

The Hotmart Developers API is rate limited at 100 requests per minute as stated [here](https://developers.hotmart.com/docs/en/start/rate-limit).

Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* [Developer Credentials](https://developers.hotmart.com/docs/en/start/app-auth/)

### Setup guide

The Hotmart Developer Credentials can be obtained following the following steps:

1. [Sign in](https://app-vlc.hotmart.com/login) to your Hotmart Account.
2. Go to **Tools** > [Developer Credentials](https://app-vlc.hotmart.com/tools/credentials).
3. Click the **Create Credential** and give your credential a name.
4. Click **Confirm** and the three pieces of information will be generated.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2023-02-16 | [23157](https://github.com/airbytehq/airbyte/pull/23157) | Initial Release |