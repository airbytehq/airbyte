# Lago API

## Sync overview

This source can sync data from the [Lago API](https://doc.getlago.com/docs/guide/intro/welcome). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- billable_metrics
- plans
- coupons
- add_ons
- invoices
- customers
- subscriptions
- customer_usage
- customer_usage_past

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

## Getting started

### Requirements

- Lago API URL
- Lago API KEY

## Changelog

| Version | Date       | Pull Request                                              | Subject                                   |
| :------ | :--------- | :-------------------------------------------------------- | :---------------------------------------- |
| 0.7.9 | 2025-01-25 | [52368](https://github.com/airbytehq/airbyte/pull/52368) | Update dependencies |
| 0.7.8 | 2025-01-18 | [51667](https://github.com/airbytehq/airbyte/pull/51667) | Update dependencies |
| 0.7.7 | 2025-01-11 | [51126](https://github.com/airbytehq/airbyte/pull/51126) | Update dependencies |
| 0.7.6 | 2024-12-28 | [50575](https://github.com/airbytehq/airbyte/pull/50575) | Update dependencies |
| 0.7.5 | 2024-12-21 | [50044](https://github.com/airbytehq/airbyte/pull/50044) | Update dependencies |
| 0.7.4 | 2024-12-14 | [49504](https://github.com/airbytehq/airbyte/pull/49504) | Update dependencies |
| 0.7.3 | 2024-12-12 | [48208](https://github.com/airbytehq/airbyte/pull/48208) | Update dependencies |
| 0.7.2 | 2024-10-29 | [47730](https://github.com/airbytehq/airbyte/pull/47730) | Update dependencies |
| 0.7.1 | 2024-10-28 | [47596](https://github.com/airbytehq/airbyte/pull/47596) | Update dependencies |
| 0.7.0 | 2024-09-12 | [45452](https://github.com/airbytehq/airbyte/pull/45452) | Endpoint customer usage: import current from subscription and add new stream customer_usage_past |
| 0.6.0 | 2024-09-06 | [45193](https://github.com/airbytehq/airbyte/pull/45193) | Endpoint customer usage ignore 405 response |
| 0.5.0 | 2024-08-23 | [44613](https://github.com/airbytehq/airbyte/pull/44613) | Refactor connector to manifest-only format |
| 0.4.11 | 2024-08-17 | [44273](https://github.com/airbytehq/airbyte/pull/44273) | Update dependencies |
| 0.4.10 | 2024-08-12 | [43800](https://github.com/airbytehq/airbyte/pull/43800) | Update dependencies |
| 0.4.9 | 2024-08-10 | [43655](https://github.com/airbytehq/airbyte/pull/43655) | Update dependencies |
| 0.4.8 | 2024-08-03 | [43099](https://github.com/airbytehq/airbyte/pull/43099) | Update dependencies |
| 0.4.7 | 2024-07-27 | [42727](https://github.com/airbytehq/airbyte/pull/42727) | Update dependencies |
| 0.4.6 | 2024-07-20 | [41719](https://github.com/airbytehq/airbyte/pull/41719) | Update dependencies |
| 0.4.5 | 2024-07-10 | [41523](https://github.com/airbytehq/airbyte/pull/41523) | Update dependencies |
| 0.4.4 | 2024-07-09 | [41133](https://github.com/airbytehq/airbyte/pull/41133) | Update dependencies |
| 0.4.3 | 2024-07-06 | [40786](https://github.com/airbytehq/airbyte/pull/40786) | Update dependencies |
| 0.4.2 | 2024-06-25 | [40265](https://github.com/airbytehq/airbyte/pull/40265) | Update dependencies |
| 0.4.1 | 2024-06-22 | [39979](https://github.com/airbytehq/airbyte/pull/39979) | Update dependencies |
| 0.4.0 | 2024-06-13 | [35661](https://github.com/airbytehq/airbyte/pull/35661) | Add `fee` stream |
| 0.3.2 | 2024-06-04 | [39094](https://github.com/airbytehq/airbyte/pull/39094) | [autopull] Upgrade base image to v1.2.1 |
| 0.3.1 | 2024-05-21 | [38479](https://github.com/airbytehq/airbyte/pull/38479) | [autopull] base image + poetry + up_to_date |
| 0.3.0   | 2023-10-05 | [#31099](https://github.com/airbytehq/airbyte/pull/31099) | Added customer_usage and wallet stream    |
| 0.2.0   | 2023-09-19 | [#30572](https://github.com/airbytehq/airbyte/pull/30572) | Source GetLago: Support API URL           |
| 0.1.0   | 2022-10-26 | [#18727](https://github.com/airbytehq/airbyte/pull/18727) | 🎉 New Source: getLago API [low-code CDK] |
