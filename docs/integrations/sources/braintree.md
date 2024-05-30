# Braintree

This page contains the setup guide and reference information for the Braintree source connector.

## Prerequisites

To set up the Braintree source connector, you'll need Braintree's:

1. [Public Key](https://developer.paypal.com/braintree/articles/control-panel/important-gateway-credentials#public-key)
2. [Environment](https://developer.paypal.com/braintree/articles/control-panel/important-gateway-credentials#environment)
3. [Merchant ID](https://developer.paypal.com/braintree/articles/control-panel/important-gateway-credentials#merchant-id)
4. [Private Key](https://developer.paypal.com/braintree/articles/control-panel/important-gateway-credentials#private-key)

We recommend creating a restricted, read-only key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.

## Set up the Braintree connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account or navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Braintree** from the Source type dropdown.
4. Enter the name for the Braintree connector.
5. For **Public Key**, enter your [Braintree Public Key](https://developer.paypal.com/braintree/articles/control-panel/important-gateway-credentials#public-key).
6. For **Start Date**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated.
7. For **Environment**, choose the appropriate option from the dropdown.
8. For **Merchant ID**, enter your [Braintree Merchant ID](https://developer.paypal.com/braintree/articles/control-panel/important-gateway-credentials#merchant-id).
9. For **Private Key**, enter your [Braintree Private Key](https://developer.paypal.com/braintree/articles/control-panel/important-gateway-credentials#private-key).
10. Click **Set up source**.

## Sync overview

This source can sync data for the [Braintree API](https://developers.braintreepayments.com/start/overview). It supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Supported Sync Modes

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | Yes                  |       |
| Namespaces        | No                   |       |

## Supported Streams

The following streams are supported:

- [Customers](https://developer.paypal.com/braintree/docs/reference/request/customer/search)
- [Discounts](https://developer.paypal.com/braintree/docs/reference/response/discount)
- [Disputes](https://developer.paypal.com/braintree/docs/reference/request/dispute/search)
- [Transactions](https://developers.braintreepayments.com/reference/response/transaction/python)
- [Merchant Accounts](https://developer.paypal.com/braintree/docs/reference/response/merchant-account)
- [Plans](https://developer.paypal.com/braintree/docs/reference/response/plan)
- [Subscriptions](https://developer.paypal.com/braintree/docs/reference/response/subscription)

## Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

## Performance considerations

The connector is restricted by normal Braintree [requests limitation](https://developers.braintreepayments.com/reference/general/searching/search-results/python#search-limit) on search transactions.

The Braintree connector should not run into Braintree API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                              |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------- |
| 0.2.1   | 2023-11-08 | [31489](https://github.com/airbytehq/airbyte/pull/31489) | Fix transaction stream custom fields                 |
| 0.2.0   | 2023-07-17 | [29200](https://github.com/airbytehq/airbyte/pull/29200) | Migrate connector to low-code framework              |
| 0.1.5   | 2023-05-24 | [26340](https://github.com/airbytehq/airbyte/pull/26340) | Fix error in `check_connection` in integration tests |
| 0.1.4   | 2023-03-13 | [23548](https://github.com/airbytehq/airbyte/pull/23548) | Update braintree python library version to 4.18.1    |
| 0.1.3   | 2021-12-23 | [8434](https://github.com/airbytehq/airbyte/pull/8434)   | Update fields in source-connectors specifications    |
| 0.1.2   | 2021-12-22 | [9042](https://github.com/airbytehq/airbyte/pull/9042)   | Fix `$ref` in schema and spec                        |
| 0.1.1   | 2021-10-27 | [7432](https://github.com/airbytehq/airbyte/pull/7432)   | Dispute model should accept multiple Evidences       |
| 0.1.0   | 2021-08-17 | [5362](https://github.com/airbytehq/airbyte/pull/5362)   | Initial version                                      |
