# Retently

## Overview

The Retently source supports full refresh sync.

### Output schema

Several output streams are available from this source:

* [Customers](https://www.retently.com/api/#api-get-customers-get)
* [Companies](https://www.retently.com/api/#api-get-companies-get)
* [Reports](https://www.retently.com/api/#api-get-reports-get)

If there are more endpoints you'd like Airbyte to support, please [create an issue](https://github.com/airbytehq/airbyte/issues/new/choose).

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| SSL connection | No |
| Namespaces | No |

## Getting started

### Requirements

* Retently Account
* Retently API Token

### Setup guide

Retently supports two types of authentication: by API Token or using Retently oAuth application.

You can get the API Token for Retently [here](https://app.retently.com/settings/api/tokens).
OAuth application is [here](https://app.retently.com/settings/oauth).

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.3 | 2022-11-15 | [19456](https://github.com/airbytehq/airbyte/pull/19456) | Add campaign, feedback, outbox and templates streams |
| 0.1.2 | 2021-12-28 | [9045](https://github.com/airbytehq/airbyte/pull/9045)   | Update titles and descriptions |
| 0.1.1 | 2021-12-06 | [8043](https://github.com/airbytehq/airbyte/pull/8043)   | 🎉 Source Retently: add OAuth 2.0 |
| 0.1.0 | 2021-11-02 | [6966](https://github.com/airbytehq/airbyte/pull/6966)   | 🎉 New Source: Retently |
