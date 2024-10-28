# Paystack

This page contains the setup guide and reference information for the Paystack source connector.

## Prerequisites

- Secret Key
- Start Day
- Lookback Window

## Setup guide

### Step 1: Set up Paystack connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.io/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Paystack** from the Source type dropdown.
4. Enter a name for your source.
5. For **Secret Key** enter your secret key. The Paystack API key usually starts with **'sk*live*'**. You can find yours secret key [here](https://dashboard.paystack.com/#/settings/developer).
6. For **Start Date** enter UTC date and time in the format **2017-01-25T00:00:00Z**. Any data before this date will not be replicated.
7. For **Lookback Window (in days)** enter the number of days. When set, the connector will always reload data from the past N days, where N is the value set here. This is useful if your data is updated after creation.

## Supported sync modes

The Paystack source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

## Supported Streams

- [Customers](https://paystack.com/docs/api/customer#list) \(Incremental\)
- [Disputes](https://paystack.com/docs/api/dispute) \(Incremental\)
- [Invoices](https://paystack.com/docs/api/payment-request) \(Incremental\)
- [Refunds](https://paystack.com/docs/api/refund) \(Incremental\)
- [Settlements](https://paystack.com/docs/api/settlement) \(Incremental\)
- [Subscriptions](https://paystack.com/docs/api/subscription) \(Incremental\)
- [Transactions](https://paystack.com/docs/api/transaction) \(Incremental\)
- [Transfers](https://paystack.com/docs/api/transfer) \(Incremental\)

### Note on Incremental Syncs

The Paystack API does not allow querying objects which were updated since the last sync. Therefore, this connector uses the `createdAt` field to query for new data in your Paystack account.

If your data is updated after creation, you can use the Loockback Window option when configuring the connector to always reload data from the past N days. This will allow you to pick up updates to the data.

## Data type map

The [Paystack API](https://paystack.com/docs/api) is compatible with the [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Airbyte uses internally \(`string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`\), so no type conversions happen as part of this source.

### Features

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes        |
| Incremental - Dedupe Sync | Yes        |
| SSL connection            | Yes        |

### Performance considerations

The Paystack connector should not run into Paystack API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                        |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------- |
| 1.1.2 | 2024-10-28 | [47518](https://github.com/airbytehq/airbyte/pull/47518) | Update dependencies |
| 1.1.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 1.1.0 | 2024-08-15 | [44101](https://github.com/airbytehq/airbyte/pull/44101) | Refactor connector to manifest-only format |
| 1.0.11 | 2024-08-12 | [43809](https://github.com/airbytehq/airbyte/pull/43809) | Update dependencies |
| 1.0.10 | 2024-08-10 | [43464](https://github.com/airbytehq/airbyte/pull/43464) | Update dependencies |
| 1.0.9 | 2024-08-03 | [43106](https://github.com/airbytehq/airbyte/pull/43106) | Update dependencies |
| 1.0.8 | 2024-07-31 | [42901](https://github.com/airbytehq/airbyte/pull/42901) | New field added for `transfers` stream |
| 1.0.7 | 2024-07-27 | [42655](https://github.com/airbytehq/airbyte/pull/42655) | Update dependencies |
| 1.0.6 | 2024-07-20 | [42323](https://github.com/airbytehq/airbyte/pull/42323) | Update dependencies |
| 1.0.5 | 2024-07-13 | [41694](https://github.com/airbytehq/airbyte/pull/41694) | Update dependencies |
| 1.0.4 | 2024-07-10 | [41424](https://github.com/airbytehq/airbyte/pull/41424) | Update dependencies |
| 1.0.3 | 2024-07-09 | [41214](https://github.com/airbytehq/airbyte/pull/41214) | Update dependencies |
| 1.0.2 | 2024-07-06 | [40783](https://github.com/airbytehq/airbyte/pull/40783) | Update dependencies |
| 1.0.1 | 2024-06-26 | [40453](https://github.com/airbytehq/airbyte/pull/40453) | Update dependencies |
| 1.0.0 | 2024-06-25 | [39395](https://github.com/airbytehq/airbyte/pull/39395) | Migrate python cdk to low code |
| 0.1.5 | 2024-06-22 | [40081](https://github.com/airbytehq/airbyte/pull/40081) | Update dependencies |
| 0.1.4 | 2024-05-20 | [38430](https://github.com/airbytehq/airbyte/pull/38430) | [autopull] base image + poetry + up_to_date |
| 0.1.3 | 2023-03-21 | [24247](https://github.com/airbytehq/airbyte/pull/24247) | Specified date formatting in specification |
| 0.1.2 | 2023-03-15 | [24085](https://github.com/airbytehq/airbyte/pull/24085) | Set additionalProperties: true, add TypeTransformer to Refunds |
| 0.1.1 | 2021-12-07 | [8582](https://github.com/airbytehq/airbyte/pull/8582) | Update connector fields title/description |
| 0.1.0 | 2021-10-20 | [7214](https://github.com/airbytehq/airbyte/pull/7214) | Add Paystack source connector |

</details>
