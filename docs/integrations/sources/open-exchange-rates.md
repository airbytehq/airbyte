# Open Exchange Rates

## Overview

This connector syncs exchange rates from the Open Exchange Rates API [https://openexchangerates.org](https://openexchangerates.org).

Only [historical exchange rates](https://docs.openexchangerates.org/docs/historical-json) are supported so far.

#### Output schema

It contains one stream: `historical_exchange_rates`

Each record in the stream contains the following fields:

* The `timestamp` of the exchange rate
* The `base` currency
* The rates containing one field for every supported and requested [currency](https://docs.openexchangerates.org/v0.7/docs/supported-currencies) with the exchange rate value on that date.

#### Data type mapping

The timestamp is an `integer`, the base currency is a `string`, and currencies are `number`.

#### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Namespaces | No |

### Getting started

#### Requirements
- A unique App ID to access the open exchange rates API.


#### Setup guide

##### Step 1. Get your unique App ID

If you never registered to the service, go to [this](https://openexchangerates.org/signup) page and enter needed info.
After login you will be able to generate a new `App ID` in the `App IDs` section [here](https://openexchangerates.org/account/app-ids).

##### Step 2. Setup the connector

If you have the `free` subscription plan, you won't be able to specify the `Base currency` parameter (leave it empty), meaning that you will be dealing only with default base value which is USD.


## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2022-02-11 | [xxxx](https://github.com/airbytehq/airbyte/pull/xxxx) | Implement Open Exchange Rates API |
