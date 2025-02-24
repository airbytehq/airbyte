# Customer.io

## Overview

This source provides access to the Customer.io API data.

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
| 0.3.10 | 2025-02-22 | [54374](https://github.com/airbytehq/airbyte/pull/54374) | Update dependencies |
| 0.3.9 | 2025-02-15 | [51670](https://github.com/airbytehq/airbyte/pull/51670) | Update dependencies |
| 0.3.8 | 2025-01-11 | [51062](https://github.com/airbytehq/airbyte/pull/51062) | Update dependencies |
| 0.3.7 | 2025-01-04 | [50582](https://github.com/airbytehq/airbyte/pull/50582) | Update dependencies |
| 0.3.6 | 2024-12-21 | [49999](https://github.com/airbytehq/airbyte/pull/49999) | Update dependencies |
| 0.3.5 | 2024-12-14 | [49490](https://github.com/airbytehq/airbyte/pull/49490) | Update dependencies |
| 0.3.4 | 2024-12-12 | [48923](https://github.com/airbytehq/airbyte/pull/48923) | Update dependencies |
| 0.3.3 | 2024-11-04 | [48225](https://github.com/airbytehq/airbyte/pull/48225) | Update dependencies |
| 0.3.2 | 2024-10-28 | [47464](https://github.com/airbytehq/airbyte/pull/47464) | Update dependencies |
| 0.3.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.3.0 | 2024-08-15 | [44158](https://github.com/airbytehq/airbyte/pull/44158) | Refactor connector to manifest-only format |
| 0.2.15 | 2024-08-12 | [43889](https://github.com/airbytehq/airbyte/pull/43889) | Update dependencies |
| 0.2.14 | 2024-08-10 | [43513](https://github.com/airbytehq/airbyte/pull/43513) | Update dependencies |
| 0.2.13 | 2024-08-03 | [43185](https://github.com/airbytehq/airbyte/pull/43185) | Update dependencies |
| 0.2.12 | 2024-07-27 | [42631](https://github.com/airbytehq/airbyte/pull/42631) | Update dependencies |
| 0.2.11 | 2024-07-20 | [42219](https://github.com/airbytehq/airbyte/pull/42219) | Update dependencies |
| 0.2.10 | 2024-07-13 | [41808](https://github.com/airbytehq/airbyte/pull/41808) | Update dependencies |
| 0.2.9 | 2024-07-10 | [41389](https://github.com/airbytehq/airbyte/pull/41389) | Update dependencies |
| 0.2.8 | 2024-07-09 | [41225](https://github.com/airbytehq/airbyte/pull/41225) | Update dependencies |
| 0.2.7 | 2024-07-06 | [40883](https://github.com/airbytehq/airbyte/pull/40883) | Update dependencies |
| 0.2.6 | 2024-06-29 | [40624](https://github.com/airbytehq/airbyte/pull/40624) | Update dependencies |
| 0.2.5 | 2024-06-27 | [38318](https://github.com/airbytehq/airbyte/pull/38318) | Make compatability with builder |
| 0.2.4 | 2024-06-25 | [40369](https://github.com/airbytehq/airbyte/pull/40369) | Update dependencies |
| 0.2.3 | 2024-06-22 | [39953](https://github.com/airbytehq/airbyte/pull/39953) | Update dependencies |
| 0.2.2 | 2024-06-04 | [38980](https://github.com/airbytehq/airbyte/pull/38980) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.1 | 2024-05-31 | [38812](https://github.com/airbytehq/airbyte/pull/38812) | [autopull] Migrate to base image and poetry |
| 0.2.0 | 2021-11-09 | [29385](https://github.com/airbytehq/airbyte/pull/29385) | Migrate TS CDK to Low code |
| 0.1.23  | 2021-11-09 | [126](https://github.com/faros-ai/airbyte-connectors/pull/126) | Add Customer.io source     |

</details>
