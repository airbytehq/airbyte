# Exchange Rates API

## Overview

The exchange rates integration is a toy integration to demonstrate how Airbyte works with a very simple source.

It pulls all its data from [https://exchangeratesapi.io](https://exchangeratesapi.io)

#### Output schema

It contains one stream: `exchange_rates`

Each record in the stream contains many fields:

- The date of the record
- One field for every supported [currency](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html) which contain the value of that currency on that date.

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

- API Access Key

### Setup guide

In order to get an `API Access Key` please go to [this](https://manage.exchangeratesapi.io/signup/free) page and enter needed info. After registration and login you will see your `API Access Key`, also you may find it [here](https://manage.exchangeratesapi.io/dashboard).

If you have `free` subscription plan \(you may check it [here](https://manage.exchangeratesapi.io/plan)\) this means that you will have 2 limitations:

1. 1000 API calls per month.
2. You won't be able to specify the `base` parameter, meaning that you will be dealing only with default base value which is EUR.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                             |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------ |
| 1.2.7   | 2022-10-31 | [18726](https://github.com/airbytehq/airbyte/pull/18726) | Fix handling error during check connection                                                                          |
| 1.2.6   | 2022-08-23 | [15884](https://github.com/airbytehq/airbyte/pull/15884) | Migrated to new API Layer endpoint                                                                                  |
| 0.2.6   | 2022-04-20 | [12230](https://github.com/airbytehq/airbyte/pull/12230) | Update connector to use a `spec.yaml`                                                                               |
| 0.2.5   | 2021-11-12 | [7936](https://github.com/airbytehq/airbyte/pull/7936)   | Add ignore_weekends boolean option                                                                                  |
| 0.2.4   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)   | Remove base-python dependencies                                                                                     |
| 0.2.3   | 2021-06-06 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | Add `AIRBYTE_ENTRYPOINT` for kubernetes support                                                                     |
| 0.2.2   | 2021-05-28 | [3677](https://github.com/airbytehq/airbyte/pull/3677)   | Adding clearer error message when a currency isn't supported. access_key field in spec.json was marked as sensitive |
| 0.2.0   | 2021-05-26 | [3566](https://github.com/airbytehq/airbyte/pull/3566)   | Move from `api.ratesapi.io/` to `api.exchangeratesapi.io/`. Add required field `access_key` to `config.json`.       |
| 0.1.0   | 2021-04-19 | [2942](https://github.com/airbytehq/airbyte/pull/2942)   | Implement Exchange API using the CDK                                                                                |
