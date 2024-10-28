# GoCardless

## Overview

The GoCardless source can sync data from the [GoCardless API](https://gocardless.com/)

#### Output schema

This source is capable of syncing the following streams:

- Mandates
- Payments
- Payouts
- Refunds

#### Features

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | No         |
| Namespaces                | No         |

### Requirements / Setup Guide

- Access Token
- GoCardless Environment
- GoCardless Version
- Start Date

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                   |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------- |
| 0.2.1   | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version   |
| 0.2.0 | 2024-08-15 | [44145](https://github.com/airbytehq/airbyte/pull/44145) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-12 | [43840](https://github.com/airbytehq/airbyte/pull/43840) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43706](https://github.com/airbytehq/airbyte/pull/43706) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43230](https://github.com/airbytehq/airbyte/pull/43230) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42810](https://github.com/airbytehq/airbyte/pull/42810) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42223](https://github.com/airbytehq/airbyte/pull/42223) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41826](https://github.com/airbytehq/airbyte/pull/41826) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41559](https://github.com/airbytehq/airbyte/pull/41559) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41291](https://github.com/airbytehq/airbyte/pull/41291) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40846](https://github.com/airbytehq/airbyte/pull/40846) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40370](https://github.com/airbytehq/airbyte/pull/40370) | Update dependencies |
| 0.1.4 | 2024-06-21 | [39946](https://github.com/airbytehq/airbyte/pull/39946) | Update dependencies |
| 0.1.3 | 2024-06-06 | [39207](https://github.com/airbytehq/airbyte/pull/39207) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.2 | 2024-06-05 | [38818](https://github.com/airbytehq/airbyte/pull/38818) | Make compatible with the builder |
| 0.1.1 | 2024-05-20 | [38425](https://github.com/airbytehq/airbyte/pull/38425) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-19 | [17792](https://github.com/airbytehq/airbyte/pull/17792) | Initial release supporting the GoCardless |

</details>
