# Exchange Rates API

## Overview

The exchange rates integration is a toy integration to demonstrate how Airbyte works with a very simple source.

It pulls all its data from [https://exchangeratesapi.io/](https://exchangeratesapi.io/)

#### Output schema

It contains one stream: `exchange_rate`

Each record in the stream contains many fields:

* The date of the record
* One field for every supported [currency](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html) which contain the value of that currency on that date.

#### Data type mapping

Currencies are `number` and the date is a `string`.

#### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |

### Getting started

#### Setup guide

Specify the reference currency and the start date when you want to collect currencies.

