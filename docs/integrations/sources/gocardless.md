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
| 0.1.2 | 2024-06-05 | [38818](https://github.com/airbytehq/airbyte/pull/38818) | Make compatible with the builder            |
| 0.1.1 | 2024-05-20 | [38425](https://github.com/airbytehq/airbyte/pull/38425) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-19 | [17792](https://github.com/airbytehq/airbyte/pull/17792) | Initial release supporting the GoCardless |

</details>