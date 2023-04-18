# Open Exchange Rates

## Overview

The integration pulls data from [Open Exchange Rates](https://openexchangerates.org/)

#### Output schema

It contains one stream: `open_exchange_rates`

Each record in the stream contains many fields:

* The timestamp of the record
* Base currency
* The conversion rates from the base currency to the target currency

#### Data type mapping

Currencies are `number` and the date is a `string`.

#### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Namespaces | No |

### Getting started

### Requirements

* App ID

### Setup guide

In order to get an `app_id` please go to [this](https://docs.openexchangerates.org/reference/authentication) page and follow the steps needed. After registration and login you will see your `app_id`, also you may find it [here](https://openexchangerates.org/account).

If you have `free` subscription plan \(you may check it [here](https://openexchangerates.org/account/usage)\) this means that you will have 2 limitations:

1. 1000 API calls per month.
2. You won't be able to specify the `base` parameter, meaning that you will be dealing only with default base value which is USD.

## CHANGELOG

| Version | Date       | Pull Request                                             | Subject                                                                                              |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------------------------------------------------------- |
| 0.1.0   | 2022-11-15 | [19436](https://github.com/airbytehq/airbyte/issues/19436) | Created CDK native Open Exchange Rates connector  |
