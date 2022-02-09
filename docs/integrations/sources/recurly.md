# Recurly

## Overview

The Recurly source supports _Full Refresh_ as well as _Incremental_ syncs. 

_Full Refresh_ sync means every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.
_Incremental_ syn means only changed resources are copied from Recurly. For the first run, it will be a Full Refresh sync.

### Output schema

Several output streams are available from this source:

* [Accounts](https://docs.recurly.com/docs/accounts)
* [Account Coupon Redemptions](https://docs.recurly.com/docs/coupons#redemptions)
* [Coupons](https://docs.recurly.com/docs/coupons)
* [Automated Exports](https://docs.recurly.com/docs/export-overview)
* [Invoices](https://docs.recurly.com/docs/invoices)
* [Measured Units](https://developers.recurly.com/api/v2021-02-25/index.html#tag/measured_unit)
* [Plans](https://docs.recurly.com/docs/plans)
* [Subscriptions](https://docs.recurly.com/docs/subscriptions)
* [Transactions](https://docs.recurly.com/docs/transactions)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Replicate Incremental Deletes | Coming soon |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The Recurly connector should not run into Recurly API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Recurly Account
* Recurly API Key

### Setup guide

Generate a API key using the [Recurly documentation](https://docs.recurly.com/docs/api-keys#section-find-or-generate-your-api-key)

We recommend creating a restricted, read-only key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.

## CHANGELOG

| Version | Date       | Pull Request | Subject |
|:--------|:-----------| :--- | :--- |
| 0.3.2   | 2022-01-20 | [8617](https://github.com/airbytehq/airbyte/pull/8617) | Update connector fields title/description |
| 0.3.1   | 2022-01-10 | [9382](https://github.com/airbytehq/airbyte/pull/9382) | Source Recurly: avoid loading all accounts when importing account coupon redemptions |
| 0.3.0   | 2021-12-08 | [8468](https://github.com/airbytehq/airbyte/pull/8468) | Support Incremental Sync Mode |
