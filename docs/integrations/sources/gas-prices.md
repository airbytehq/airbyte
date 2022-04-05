# Gas Prices

## Sync overview

This source can sync data for the [Gas Prices API](https://www.collectapi.com/api/gasPrice/gas-prices-api/). It supports only Full Refresh syncs.

### Output schema

This Source is capable of syncing the following Streams:

* [USA State Prices](https://www.collectapi.com/api/gasPrice/gas-prices-api/stateUsaPrice)

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
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |
| Namespaces | No |  |

### Performance considerations

The connector is restricted by normal Collect API [requests limitation](https://www.collectapi.com/api/gasPrice/gas-prices-api/).

The Gas Prices connector should not run into API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* API Key

### Setup guide

Please create an account [here](https://www.collectapi.com/auth) to obtain an API Key for your account.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2022-03-21 | Pending | New Source: Gas Prices |