# Amazon Ads

## Sync overview

This source can sync data for the [Amazon Advertising API](https://advertising.amazon.com/API/docs/en-us/what-is/amazon-advertising-api).

### Output schema

This source is capable of syncing the following streams:

* [Profiles](https://advertising.amazon.com/API/docs/en-us/reference/2/profiles#/Profiles)
* [Sponsored Brands Campaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Campaigns)
* [Sponsored Brands Ad groups](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Ad%20groups)
* [Sponsored Brands Keywords](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Keywords)
* [Sponsored Display Campaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Campaigns)
* [Sponsored Display Ad groups](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Ad%20groups)
* [Sponsored Display Product Ads](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Product%20ads)
* [Sponsored Display Targetings](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Targeting)
* [Sponsored Products Campaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Campaigns)
* [Sponsored Products Ad groups](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Ad%20groups)
* [Sponsored Products Keywords](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Keywords)
* [Sponsored Products Negative keywords](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Negative%20keywords)
* [Sponsored Products Ads](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Product%20ads)
* [Sponsored Products Targetings](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Product%20targeting)
* [Brands Reports](https://advertising.amazon.com/API/docs/en-us/reference/sponsored-brands/2/reports)
* [Display Reports](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Reports)
* [Products Reports](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Reports)

All the reports are generated for day before relatively to target profile' timezone

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `int`, `float`, `number` | `number` |  |
| `date` | `date` |  |
| `datetime` | `datetime` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | yes |  |
| Incremental Sync | yes |  |
| Namespaces | No |  |

### Performance considerations

Information about expected report generation waiting time you may find [here](https://advertising.amazon.com/API/docs/en-us/get-started/developer-notes).

## Getting started

### Requirements

* client_id
* client_secret
* refresh_token
* scope
* start_date (optional)

More how to get client_id and client_secret you can find on [AWS docs](https://advertising.amazon.com/API/docs/en-us/setting-up/step-1-create-lwa-app).

Refresh token is generated according to standard [AWS Oauth 2.0 flow](https://developer.amazon.com/docs/login-with-amazon/conceptual-overview.html)

Scope usually has "advertising::campaign_management" value, but customers may need to set scope to "cpc_advertising:campaign_management",

Start date used for generating reports starting from the specified start date. Should be in YYYY-MM-DD format and not more than 60 days in the past. If not specified today date is used. Date for specific profile is calculated according to its timezone, this parameter should be specified in UTC timezone. Since it have no sense of generate report for current day (metrics could be changed) it generates report for day before (e.g. if start_date is 2021-10-11 it would use 20211010 as reportDate parameter for request).


## CHANGELOG

| Version | Date | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| `0.1.0` | 2021-08-13 | [#5023](https://github.com/airbytehq/airbyte/pull/5023) | `Initial version` |
