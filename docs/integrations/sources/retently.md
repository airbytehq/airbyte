# Retently

## Overview

The Retently source supports full refresh sync.

### Output schema

Several output streams are available from this source:

- [Customers](https://www.retently.com/api/#api-get-customers-get)
- [Companies](https://www.retently.com/api/#api-get-companies-get)
- [Reports](https://www.retently.com/api/#api-get-reports-get)
- [Campaigns](https://www.retently.com/api/#api-get-campaigns)
- [Feedback](https://www.retently.com/api/#api-get-feedback-get)
- [NPS](https://www.retently.com/api/#api-get-latest-score)
- [Outbox](https://www.retently.com/api/#api-get-sent-surveys)
- [Templates](https://www.retently.com/api/#api-get-templates-get)

If there are more endpoints you'd like Airbyte to support, please [create an issue](https://github.com/airbytehq/airbyte/issues/new/choose).

### Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| SSL connection    | No         |
| Namespaces        | No         |

## Getting started

### Requirements

- Retently Account
- Retently API Token

### Setup guide

Retently supports two types of authentication: by API Token or using Retently oAuth application.

You can get the API Token for Retently [here](https://app.retently.com/settings/api/tokens).
OAuth application is [here](https://app.retently.com/settings/oauth).

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.2.4   | 2024-04-19 | [37248](https://github.com/airbytehq/airbyte/pull/37248) | Updating to 0.80.0 CDK                                                          |
| 0.2.3   | 2024-04-18 | [37248](https://github.com/airbytehq/airbyte/pull/37248) | Manage dependencies with Poetry.                                                |
| 0.2.2   | 2024-04-15 | [37248](https://github.com/airbytehq/airbyte/pull/37248) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1   | 2024-04-12 | [37248](https://github.com/airbytehq/airbyte/pull/37248) | schema descriptions                                                             |
| 0.2.0   | 2023-08-03 | [29040](https://github.com/airbytehq/airbyte/pull/29040) | Migrate to Low-Code CDK                                                         |
| 0.1.6   | 2023-05-10 | [25714](https://github.com/airbytehq/airbyte/pull/25714) | Fix invalid json schema for nps stream                                          |
| 0.1.5   | 2023-05-08 | [25900](https://github.com/airbytehq/airbyte/pull/25900) | Fix integration tests                                                           |
| 0.1.4   | 2023-05-08 | [25900](https://github.com/airbytehq/airbyte/pull/25900) | Fix integration tests                                                           |
| 0.1.3   | 2022-11-15 | [19456](https://github.com/airbytehq/airbyte/pull/19456) | Add campaign, feedback, outbox and templates streams                            |
| 0.1.2   | 2021-12-28 | [9045](https://github.com/airbytehq/airbyte/pull/9045)   | Update titles and descriptions                                                  |
| 0.1.1   | 2021-12-06 | [8043](https://github.com/airbytehq/airbyte/pull/8043)   | 🎉 Source Retently: add OAuth 2.0                                               |
| 0.1.0   | 2021-11-02 | [6966](https://github.com/airbytehq/airbyte/pull/6966)   | 🎉 New Source: Retently                                                         |
