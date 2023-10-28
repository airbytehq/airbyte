# Lago API

## Sync overview

This source can sync data from the [Lago API](https://doc.getlago.com/docs/guide/intro/welcome). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

 * billable_metrics
 * plans
 * coupons
 * add_ons
 * invoices
 * customers
 * subscriptions

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |


## Getting started

### Requirements
* Lago API URL
* Lago API KEY

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.3.0   | 2023-10-05 | [#31099](https://github.com/airbytehq/airbyte/pull/31099) | Added customer_usage and wallet stream           |
| 0.2.0   | 2023-09-19 | [#30572](https://github.com/airbytehq/airbyte/pull/30572) | Source GetLago: Support API URL           |
| 0.1.0   | 2022-10-26 | [#18727](https://github.com/airbytehq/airbyte/pull/18727) | 🎉 New Source: getLago API [low-code CDK] |