# Recurly

## Overview

The Recurly source supports Full Refresh syncs. That is, every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.

### Output schema

Several output streams are available from this source:

* [Accounts](https://docs.recurly.com/docs/accounts)
* [Coupons](https://docs.recurly.com/docs/coupons)
* Automated Exports
* [Invoices](https://docs.recurly.com/docs/invoices)
* Measured Units
* [Plans](https://docs.recurly.com/docs/plans)
* [Subscriptions](https://docs.recurly.com/docs/subscriptions)
* [Transactions](https://docs.recurly.com/docs/transactions)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Coming soon |
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
| 0.2.6   | 2021-12-06 | [8468](https://github.com/airbytehq/airbyte/pull/8468) | Migrate to the CDK |

