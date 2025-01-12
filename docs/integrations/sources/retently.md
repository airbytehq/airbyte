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

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.3.5 | 2025-01-11 | [51346](https://github.com/airbytehq/airbyte/pull/51346) | Update dependencies |
| 0.3.4 | 2024-12-28 | [50672](https://github.com/airbytehq/airbyte/pull/50672) | Update dependencies |
| 0.3.3 | 2024-12-21 | [50250](https://github.com/airbytehq/airbyte/pull/50250) | Update dependencies |
| 0.3.2 | 2024-12-14 | [49684](https://github.com/airbytehq/airbyte/pull/49684) | Update dependencies |
| 0.3.1 | 2024-12-12 | [49045](https://github.com/airbytehq/airbyte/pull/49045) | Update dependencies |
| 0.3.0 | 2024-11-01 | [47291](https://github.com/airbytehq/airbyte/pull/47291) | Migrate to manifest only format |
| 0.2.24 | 2024-10-23 | [47108](https://github.com/airbytehq/airbyte/pull/47108) | Update dependencies |
| 0.2.23 | 2024-10-12 | [46850](https://github.com/airbytehq/airbyte/pull/46850) | Update dependencies |
| 0.2.22 | 2024-10-05 | [46429](https://github.com/airbytehq/airbyte/pull/46429) | Update dependencies |
| 0.2.21 | 2024-09-28 | [46150](https://github.com/airbytehq/airbyte/pull/46150) | Update dependencies |
| 0.2.20 | 2024-09-21 | [45513](https://github.com/airbytehq/airbyte/pull/45513) | Update dependencies |
| 0.2.19 | 2024-09-07 | [45243](https://github.com/airbytehq/airbyte/pull/45243) | Update dependencies |
| 0.2.18 | 2024-08-31 | [44984](https://github.com/airbytehq/airbyte/pull/44984) | Update dependencies |
| 0.2.17 | 2024-08-24 | [44679](https://github.com/airbytehq/airbyte/pull/44679) | Update dependencies |
| 0.2.16 | 2024-08-17 | [44262](https://github.com/airbytehq/airbyte/pull/44262) | Update dependencies |
| 0.2.15 | 2024-08-10 | [43559](https://github.com/airbytehq/airbyte/pull/43559) | Update dependencies |
| 0.2.14 | 2024-08-03 | [43180](https://github.com/airbytehq/airbyte/pull/43180) | Update dependencies |
| 0.2.13 | 2024-07-27 | [42708](https://github.com/airbytehq/airbyte/pull/42708) | Update dependencies |
| 0.2.12 | 2024-07-20 | [42140](https://github.com/airbytehq/airbyte/pull/42140) | Update dependencies |
| 0.2.11 | 2024-07-13 | [41864](https://github.com/airbytehq/airbyte/pull/41864) | Update dependencies |
| 0.2.10 | 2024-07-10 | [41371](https://github.com/airbytehq/airbyte/pull/41371) | Update dependencies |
| 0.2.9 | 2024-07-09 | [41287](https://github.com/airbytehq/airbyte/pull/41287) | Update dependencies |
| 0.2.8 | 2024-07-06 | [40977](https://github.com/airbytehq/airbyte/pull/40977) | Update dependencies |
| 0.2.7 | 2024-06-25 | [40412](https://github.com/airbytehq/airbyte/pull/40412) | Update dependencies |
| 0.2.6 | 2024-06-22 | [40183](https://github.com/airbytehq/airbyte/pull/40183) | Update dependencies |
| 0.2.5 | 2024-06-06 | [39223](https://github.com/airbytehq/airbyte/pull/39223) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.4 | 2024-04-19 | [37248](https://github.com/airbytehq/airbyte/pull/37248) | Updating to 0.80.0 CDK |
| 0.2.3 | 2024-04-18 | [37248](https://github.com/airbytehq/airbyte/pull/37248) | Manage dependencies with Poetry. |
| 0.2.2 | 2024-04-15 | [37248](https://github.com/airbytehq/airbyte/pull/37248) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1 | 2024-04-12 | [37248](https://github.com/airbytehq/airbyte/pull/37248) | schema descriptions |
| 0.2.0 | 2023-08-03 | [29040](https://github.com/airbytehq/airbyte/pull/29040) | Migrate to Low-Code CDK |
| 0.1.6 | 2023-05-10 | [25714](https://github.com/airbytehq/airbyte/pull/25714) | Fix invalid json schema for nps stream |
| 0.1.5 | 2023-05-08 | [25900](https://github.com/airbytehq/airbyte/pull/25900) | Fix integration tests |
| 0.1.4 | 2023-05-08 | [25900](https://github.com/airbytehq/airbyte/pull/25900) | Fix integration tests |
| 0.1.3 | 2022-11-15 | [19456](https://github.com/airbytehq/airbyte/pull/19456) | Add campaign, feedback, outbox and templates streams |
| 0.1.2 | 2021-12-28 | [9045](https://github.com/airbytehq/airbyte/pull/9045) | Update titles and descriptions |
| 0.1.1 | 2021-12-06 | [8043](https://github.com/airbytehq/airbyte/pull/8043) | 🎉 Source Retently: add OAuth 2.0 |
| 0.1.0 | 2021-11-02 | [6966](https://github.com/airbytehq/airbyte/pull/6966) | 🎉 New Source: Retently |

</details>
