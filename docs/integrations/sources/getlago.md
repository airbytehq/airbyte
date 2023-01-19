# getLago API

## Sync overview

This source can sync data from the [getLago API](https://doc.getlago.com/docs/guide/intro/welcome). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

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

* getLago API KEY

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.0   | 2022-10-26 | [#18727](https://github.com/airbytehq/airbyte/pull/18727) | 🎉 New Source: getLago API [low-code CDK] |