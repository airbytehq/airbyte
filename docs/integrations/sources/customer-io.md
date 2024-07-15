# Customer.io

## Overview

The Customer.io source is maintained by [Faros
AI](https://github.com/faros-ai/airbyte-connectors/tree/main/sources/customer-io-source).
Please file any support requests on that repo to minimize response time from the
maintainers. The source supports both Full Refresh and Incremental syncs. You
can choose if this source will copy only the new or updated data, or all rows
in the tables and columns you set up for replication, every time a sync is run.

### Output schema

Several output streams are available from this source:

- [Campaigns](https://customer.io/docs/api/#operation/listCampaigns) \(Incremental\)
- [Campaign Actions](https://customer.io/docs/api/#operation/listCampaignActions) \(Incremental\)
- [Newsletters](https://customer.io/docs/api/#operation/listNewsletters) \(Incremental\)

If there are more endpoints you'd like Faros AI to support, please [create an
issue.](https://github.com/faros-ai/airbyte-connectors/issues/new)

### Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| SSL connection    | Yes        |
| Namespaces        | No         |

### Performance considerations

The Customer.io API is divided into three different hosts, each serving a
different component of Customer.io. This source only uses the Beta API host,
which enforces a rate limit of 10 requests per second. Please [create an
issue](https://github.com/faros-ai/airbyte-connectors/issues/new) if you see any
rate limit issues.

## Getting started

### Requirements

- Customer.io App API Key

Please follow the [their documentation for generating an App API Key](https://customer.io/docs/managing-credentials/).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                   | Subject                    |
| :------ | :--------- | :------------------------------------------------------------- | :------------------------- |
| 0.2.2 | 2024-06-04 | [38980](https://github.com/airbytehq/airbyte/pull/38980) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.1 | 2024-05-31 | [38812](https://github.com/airbytehq/airbyte/pull/38812) | [autopull] Migrate to base image and poetry |
| 0.2.0 | 2021-11-09 | [29385](https://github.com/airbytehq/airbyte/pull/29385) | Migrate TS CDK to Low code |
| 0.1.23  | 2021-11-09 | [126](https://github.com/faros-ai/airbyte-connectors/pull/126) | Add Customer.io source     |

</details>