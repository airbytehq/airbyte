# Paystack

## Overview

The Paystack source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This Source is capable of syncing the following core streams:

[Customers](https://paystack.com/docs/api/#customer-list) \(Incremental\)
[Disputes](https://paystack.com/docs/api/#dispute-list) \(Incremental\)
[Invoices](https://paystack.com/docs/api/#invoice-list) \(Incremental\)
[Refunds](https://paystack.com/docs/api/#refund-list) \(Incremental\)
[Settlements](https://paystack.com/docs/api/#settlement) \(Incremental\)
[Subscriptions](https://paystack.com/docs/api/#subscription-list) \(Incremental\)
[Transactions](https://paystack.com/docs/api/#transaction-list) \(Incremental\)
[Transfers](https://paystack.com/docs/api/#transfer-list) \(Incremental\)

### Note on Incremental Syncs

The Paystack API does not allow querying objects which were updated since the last sync. Therefore, this connector uses the `createdAt` field to query for new data in your Paystack account.

If your data is updated after creation, you can use the Loockback Window option when configuring the connector to always reload data from the past N days. This will allow you to pick up updates to the data.

### Data type mapping

The [Paystack API](https://paystack.com/docs/api) is compatible with the [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Airbyte uses internally \(`string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`\), so no type conversions happen as part of this source.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Incremental - Dedupe Sync | Yes |
| SSL connection | Yes |

### Performance considerations

The Paystack connector should not run into Paystack API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Paystack API Secret Key

### Setup guide

Visit the [Paystack dashboard settings page](https://dashboard.paystack.com/#/settings/developer) with developer level access or more to see the secret key for your account. Secret keys for the live Paystack environment will be prefixed with `sk_live_`.

Unfortunately Paystack does not yet support restricted permission levels on secret keys. This means that you will have to use the same secret key here that you use for charging customers. Use at your own risk. In the future Paystack might support restricted access levels and in that case Airbyte only requires a read-only access level key.

If you would like to test Airbyte using test data on Paystack, `sk_test_` API keys are also supported.


## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.1  | 2021-12-07 | [8582](https://github.com/airbytehq/airbyte/pull/8582) | Update connector fields title/description |
| 0.1.0  | 2021-10-20 | [7214](https://github.com/airbytehq/airbyte/pull/7214) | Add Paystack source connector |