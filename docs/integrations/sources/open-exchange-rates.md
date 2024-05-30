# Open Exchange Rates

## Overview

The integration pulls data from [Open Exchange Rates](https://openexchangerates.org/)

#### Output schema

It contains one stream: `open_exchange_rates`

Each record in the stream contains many fields:

- The timestamp of the record
- Base currency
- The conversion rates from the base currency to the target currency

#### Data type mapping

Currencies are `number` and the date is a `string`.

#### Features

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes        |
| Namespaces                | No         |

### Getting started

### Requirements

- App ID

### Setup guide

In order to get an `app_id` please go to [this](https://docs.openexchangerates.org/reference/authentication) page and follow the steps needed. After registration and login you will see your `app_id`, also you may find it [here](https://openexchangerates.org/account).

If you have `free` subscription plan \(you may check it [here](https://openexchangerates.org/account/usage)\) this means that you will have 2 limitations:

1. 1000 API calls per month.
2. You won't be able to specify the `base` parameter, meaning that you will be dealing only with default base value which is USD.

## CHANGELOG

| Version | Date       | Pull Request                                               | Subject                                                                         |
| :------ | :--------- | :--------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.2.5   | 2024-05-14 | [38141](https://github.com/airbytehq/airbyte/pull/38141)   | Make connector compatable with builder                                          |
| 0.2.4   | 2024-04-19 | [37208](https://github.com/airbytehq/airbyte/pull/37208)   | Updating to 0.80.0 CDK                                                          |
| 0.2.3   | 2024-04-18 | [37208](https://github.com/airbytehq/airbyte/pull/37208)   | Manage dependencies with Poetry.                                                |
| 0.2.2   | 2024-04-15 | [37208](https://github.com/airbytehq/airbyte/pull/37208)   | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1   | 2024-04-12 | [37208](https://github.com/airbytehq/airbyte/pull/37208)   | schema descriptions                                                             |
| 0.2.0   | 2023-10-03 | [30983](https://github.com/airbytehq/airbyte/pull/30983)   | Migrate to low code                                                             |
| 0.1.0   | 2022-11-15 | [19436](https://github.com/airbytehq/airbyte/issues/19436) | Created CDK native Open Exchange Rates connector                                |
