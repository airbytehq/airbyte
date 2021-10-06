# Paypal Transaction API

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

* client_id. 
* secret.
* is_sandbox.

### Setup guide

In order to get an `Client ID` and `Secret` please go to [this](https://developer.paypal.com/docs/platforms/get-started/ page and follow the instructions. After registration you may find your `Client ID` and `Secret` [here](https://developer.paypal.com/developer/accounts/).


## Performance considerations

Paypal transaction API has some [limits](https://developer.paypal.com/docs/integration/direct/transaction-search/)
- `start_date_min` = 3 years, API call lists transaction for the previous three years.
- `start_date_max` = 1.5 days, it takes a maximum of three hours for executed transactions to appear in the list transactions call. It is set to 1.5 days by default based on experience, otherwise API throw an error.
- `stream_slice_period` = 1 day, the maximum supported date range is 31 days.
- `records_per_request` = 10000, the maximum number of records in a single request.
- `page_size` = 500, the maximum page size is 500.
- `requests_per_minute` = 30, maximum limit is 50 requests per minute from IP address to all endpoint

Transactions sync is performed with default `stream_slice_period` = 1 day, it means that there will be 1 request for each day between start_date and now (or end_date). if `start_date` is greater then `start_date_max`.
Balances sync is similarly performed with default `stream_slice_period` = 1 day, but it will do additional request for the end_date of the sync (now).

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.1   | 2021-08-03 | [5155](https://github.com/airbytehq/airbyte/pull/5155) | fix start_date_min limit |
| 0.1.0   | 2021-06-10 | [4240](https://github.com/airbytehq/airbyte/pull/4240) | PayPal Transaction Search API |

