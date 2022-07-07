# Paypal Transaction

## Overview

The [Paypal Transaction API](https://developer.paypal.com/docs/api/transaction-search/v1/). is used to get the history of transactions for a PayPal account.

#### Output schema

This Source is capable of syncing the following core Streams:

* [Transactions](https://developer.paypal.com/docs/api/transaction-search/v1/#transactions)
* [Balances](https://developer.paypal.com/docs/api/transaction-search/v1/#balances)

#### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |

#### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Namespaces | No |

### Getting started

### Requirements

* client\_id. 
* secret.
* is\_sandbox.

### Setup guide

In order to get an `Client ID` and `Secret` please go to \[this\]\([https://developer.paypal.com/docs/platforms/get-started/](https://developer.paypal.com/docs/platforms/get-started/) page and follow the instructions. After registration you may find your `Client ID` and `Secret` [here](https://developer.paypal.com/developer/accounts/).

## Performance considerations

Paypal transaction API has some [limits](https://developer.paypal.com/docs/integration/direct/transaction-search/)

* `start_date_min` = 3 years, API call lists transaction for the previous three years.
* `start_date_max` = 1.5 days, it takes a maximum of three hours for executed transactions to appear in the list transactions call. It is set to 1.5 days by default based on experience, otherwise API throw an error.
* `stream_slice_period` = 1 day, the maximum supported date range is 31 days.
* `records_per_request` = 10000, the maximum number of records in a single request.
* `page_size` = 500, the maximum page size is 500.
* `requests_per_minute` = 30, maximum limit is 50 requests per minute from IP address to all endpoint

Transactions sync is performed with default `stream_slice_period` = 1 day, it means that there will be 1 request for each day between start\_date and now \(or end\_date\). if `start_date` is greater then `start_date_max`. Balances sync is similarly performed with default `stream_slice_period` = 1 day, but it will do additional request for the end\_date of the sync \(now\).

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                 |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------------|
| 0.1.6   | 2022-06-10 | [13682](https://github.com/airbytehq/airbyte/pull/13682) | Update paypal transaction schema                                        |
| 0.1.5   | 2022-04-27 | [12335](https://github.com/airbytehq/airbyte/pull/12335) | Adding fixtures to mock time.sleep for connectors that explicitly sleep |
| 0.1.4   | 2021-12-22 | [9034](https://github.com/airbytehq/airbyte/pull/9034)   | Update connector fields title/description                               |
| 0.1.3   | 2021-12-16 | [8580](https://github.com/airbytehq/airbyte/pull/8580)   | Added more logs during `check connection` stage                         |
| 0.1.2   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)   | Remove base-python dependencies                                         |
| 0.1.1   | 2021-08-03 | [5155](https://github.com/airbytehq/airbyte/pull/5155)   | fix start\_date\_min limit                                              |
| 0.1.0   | 2021-06-10 | [4240](https://github.com/airbytehq/airbyte/pull/4240)   | PayPal Transaction Search API                                           |

