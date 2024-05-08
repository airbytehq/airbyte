# Chargify

## Overview

The Chargify source supports Full Refresh syncs for Customers and Subscriptions endpoints.

### Available streams

Several output streams are available from this source:

- [Customers](https://developers.chargify.com/docs/api-docs/b3A6MTQxMDgyNzY-list-or-find-customers)
- [Subscriptions](https://developers.chargify.com/docs/api-docs/b3A6MTQxMDgzODk-list-subscriptions)

If there are more streams you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

### Performance considerations

The Chargify connector should not run into Chargify API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- Chargify API Key
- Chargify domain

### Setup guide

Please follow the [Chargify documentation for generating an API key](https://developers.chargify.com/docs/api-docs/YXBpOjE0MTA4MjYx-chargify-api).

## Changelog

| Version | Date       | Pull Request                                             | Subject                                     |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------ |
| 0.4.0   | 2023-10-16 | [31116](https://github.com/airbytehq/airbyte/pull/31116) | Add Coupons, Transactions, Invoices Streams |
| 0.3.0   | 2023-08-10 | [29130](https://github.com/airbytehq/airbyte/pull/29130) | Migrate Python CDK to Low Code              |
| 0.2.0   | 2023-08-08 | [29218](https://github.com/airbytehq/airbyte/pull/29218) | Fix schema                                  |
| 0.1.0   | 2022-03-16 | [10853](https://github.com/airbytehq/airbyte/pull/10853) | Initial release                             |
