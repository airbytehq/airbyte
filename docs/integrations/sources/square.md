# Square

## Overview

The Square Source can sync data from the [Square API](https://developer.squareup.com/reference/square)

Useful links:

* [Square API Explorer](https://developer.squareup.com/explorer/square)
* [Square API Docs](https://developer.squareup.com/reference/square)
* [Square Developer Dashboard](https://developer.squareup.com/apps)

#### Output schema

This Source is capable of syncing the following Streams:

* [Items](https://developer.squareup.com/explorer/square/catalog-api/search-catalog-objects) \(Incremental\)
* [Categories](https://developer.squareup.com/explorer/square/catalog-api/search-catalog-objects) \(Incremental\)
* [Discounts](https://developer.squareup.com/explorer/square/catalog-api/search-catalog-objects) \(Incremental\)
* [Taxes](https://developer.squareup.com/explorer/square/catalog-api/search-catalog-objects) \(Incremental\)
* [ModifierLists](https://developer.squareup.com/explorer/square/catalog-api/search-catalog-objects) \(Incremental\)
* [Payments](https://developer.squareup.com/reference/square_2021-06-16/payments-api/list-payments) \(Incremental\)
* [Refunds](https://developer.squareup.com/reference/square_2021-06-16/refunds-api/list-payment-refunds) \(Incremental\)
* [Locations](https://developer.squareup.com/explorer/square/locations-api/list-locations) 
* [Team Members](https://developer.squareup.com/reference/square_2021-06-16/team-api/search-team-members) \(old V1 Employees API\) 
* [List Team Member Wages](https://developer.squareup.com/explorer/square/labor-api/list-team-member-wages)  \(old V1 Roles API\) 
* [Customers](https://developer.squareup.com/explorer/square/customers-api/list-customers) 
* [Shifts](https://developer.squareup.com/reference/square/labor-api/search-shifts) 
* [Orders](https://developer.squareup.com/reference/square/orders-api/search-orders) 

#### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `integer` | `integer` |  |
| `array` | `array` |  |
| `object` | `object` |  |
| `boolean` | `boolean` |  |

#### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Namespaces | No |

### Requirements

* api\_key - The Square API key token 
* is\_sandbox - the switch between sandbox \(true\) and production \(false\) environments 

### Setup guide

To get the API key for your square application follow [Geting started](https://developer.squareup.com/docs/get-started) and [Access token](https://developer.squareup.com/docs/build-basics/access-tokens) guides

## Performance considerations

No defined API rate limits were found in Square documentation however considering [this information](https://stackoverflow.com/questions/28033966/whats-the-rate-limit-on-the-square-connect-api/28053836#28053836) it has 10 QPS limits. The connector doesn't handle rate limits exceptions, but no errors were raised during testing.

Some Square API endpoints has different page size limitation

* Items - 1000
* Categories - 1000
* Discounts - 1000
* Taxes - 1000
* ModifierLists - 1000
* Payments - 100
* Refunds - 100
* TeamMembers - 100
* ListTeamMemberWages - 200 
* Shifts - 200
* Orders - 500 

## Changelog

| Version | Date       | Pull Request | Subject                                                  |
|:--------|:-----------| :--- |:---------------------------------------------------------|
| 0.1.4   | 2021-12-02 | [6842](https://github.com/airbytehq/airbyte/pull/6842) | Added oauth support                                      |
| 0.1.3   | 2021-12-06 | [8425](https://github.com/airbytehq/airbyte/pull/8425) | Update title, description fields in spec |
| 0.1.2   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499) | Remove base-python dependencies                          |
| 0.1.1   | 2021-07-09 | [4645](https://github.com/airbytehq/airbyte/pull/4645) | Update \_send\_request method due to Airbyte CDK changes |
| 0.1.0   | 2021-06-30 | [4439](https://github.com/airbytehq/airbyte/pull/4439) | Initial release supporting the Square API                |

