# Orb

## Overview

The Orb source supports both Full Refresh and Incremental syncs. For incremental syncs, this source
will only read and output new records based on their `created_at` timestamp.

### Output schema

This Source is capable of syncing the following core resources, each of which has a separate Stream. Note that all of the streams are incremental:

- [Subscriptions](https://docs.withorb.com/reference/list-subscriptions)
- [Plans](https://docs.withorb.com/reference/list-plans)
- [Customers](https://docs.withorb.com/reference/list-customers)
- [Credits Ledger Entries](https://docs.withorb.com/reference/fetch-customer-credits-ledger)
- [Subscription Usage](https://docs.withorb.com/reference/fetch-subscription-usage)

As a caveat, the Credits Ledger Entries must read all Customers for an incremental sync, but will only incrementally return new ledger entries for each customers.

Similarily, the Subscription Usage stream must read all Subscriptions for an incremental sync (and all Plans if using the optional `subscription_usage_grouping_key`), but will only incrementally return new usage entries for each subscription.

### Note on Incremental Syncs

The Orb API does not allow querying objects based on an `updated_at` time. Therefore, this connector uses the `created_at` field (or the `timeframe_start` field in the Subscription Usage stream) to query for new data since the last sync.

In order to capture data that has been updated after creation, please run a periodic Full Refresh.

### Features

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes        |
| Incremental - Dedupe Sync | Yes        |
| SSL connection            | Yes        |

### Performance considerations

The Orb connector should not run into Orb API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

:::warning
The `credit_ledger_entries` stream will now include `events` data. This upgrade uses the `created_at` timestamps from the `credits` to establish a 30-day timeframe, with the earliest `created_at` as the starting point. This restriction is set by the Orb API.
:::

:::info
If you are using the `start_date` and `end_date` parameter with the `credit_ledger_entries` stream it will sync all customers created during the that time window. It isn't possible to query data directly to `credit_ledger_entries`. The connector need to retrieve data from customers first to ingest the credit data.
:::

## Getting started

### Requirements

- Orb Account
- Orb API Key

### Setup guide

Please reach out to the Orb team at [team@withorb.com](mailto:team@withorb.com) to request
an Orb Account and API Key.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                               |
|---------|------------| -------------------------------------------------------- |-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2.0.13 | 2024-10-05 | [46395](https://github.com/airbytehq/airbyte/pull/46395) | Update dependencies |
| 2.0.12 | 2024-09-28 | [45785](https://github.com/airbytehq/airbyte/pull/45785) | Update dependencies |
| 2.0.11 | 2024-09-14 | [45472](https://github.com/airbytehq/airbyte/pull/45472) | Update dependencies |
| 2.0.10 | 2024-09-07 | [45212](https://github.com/airbytehq/airbyte/pull/45212) | Update dependencies |
| 2.0.9 | 2024-08-24 | [44626](https://github.com/airbytehq/airbyte/pull/44626) | Update dependencies |
| 2.0.8 | 2024-08-10 | [43601](https://github.com/airbytehq/airbyte/pull/43601) | Update dependencies |
| 2.0.7 | 2024-08-03 | [43163](https://github.com/airbytehq/airbyte/pull/43163) | Update dependencies |
| 2.0.6 | 2024-07-20 | [42198](https://github.com/airbytehq/airbyte/pull/42198) | Update dependencies |
| 2.0.5 | 2024-07-13 | [41720](https://github.com/airbytehq/airbyte/pull/41720) | Update dependencies |
| 2.0.4 | 2024-07-10 | [41386](https://github.com/airbytehq/airbyte/pull/41386) | Update dependencies |
| 2.0.3 | 2024-07-09 | [41090](https://github.com/airbytehq/airbyte/pull/41090) | Update dependencies |
| 2.0.2 | 2024-07-06 | [40826](https://github.com/airbytehq/airbyte/pull/40826) | Update dependencies |
| 2.0.1 | 2024-06-29 | [40541](https://github.com/airbytehq/airbyte/pull/40541) | Update dependencies |
| 2.0.0 | 2024-06-24 | [40227](https://github.com/airbytehq/airbyte/pull/40227) | Migrate connector to Low Code. Update data type of credit_block_per_unit_cost_basis field in credits_ledger_entries stream to match return type from the upstream API |
| 1.2.4 | 2024-06-22 | [40004](https://github.com/airbytehq/airbyte/pull/40004) | Update dependencies |
| 1.2.3 | 2024-06-04 | [39015](https://github.com/airbytehq/airbyte/pull/39015) | [autopull] Upgrade base image to v1.2.1 |
| 1.2.2 | 2024-04-19 | [37211](https://github.com/airbytehq/airbyte/pull/37211) | Updating to 0.80.0 CDK |
| 1.2.1 | 2024-04-12 | [37211](https://github.com/airbytehq/airbyte/pull/37211) | schema descriptions |
| 1.2.0   | 2024-03-19 | [x](https://github.com/airbytehq/airbyte/pull/x)         | Expose `end_date`parameter                                                                                                                                            |
| 1.1.2   | 2024-03-13 | [x](https://github.com/airbytehq/airbyte/pull/x)         | Fix window to 30 days for events query timesframe start and query                                                                                                     |
| 1.1.1   | 2024-02-07 | [35005](https://github.com/airbytehq/airbyte/pull/35005) | Pass timeframe_start, timeframe_end to events query                                                                                                                   |
| 1.1.0   | 2023-03-03 | [24567](https://github.com/airbytehq/airbyte/pull/24567) | Add Invoices incremental stream merged from [#24737](https://github.com/airbytehq/airbyte/pull/24737)                                                                 |
| 1.0.0   | 2023-02-02 | [21951](https://github.com/airbytehq/airbyte/pull/21951) | Add SubscriptionUsage stream, and made `start_date` a required field                                                                                                  |
| 0.1.4   | 2022-10-07 | [17761](https://github.com/airbytehq/airbyte/pull/17761) | Fix bug with enriching ledger entries with multiple credit blocks                                                                                                     |
| 0.1.3   | 2022-08-26 | [16017](https://github.com/airbytehq/airbyte/pull/16017) | Add credit block id to ledger entries                                                                                                                                 |
| 0.1.2   | 2022-04-20 | [11528](https://github.com/airbytehq/airbyte/pull/11528) | Add cost basis to ledger entries, update expiration date, sync only committed entries                                                                                 |
| 0.1.1   | 2022-03-03 | [10839](https://github.com/airbytehq/airbyte/pull/10839) | Support ledger entries with numeric properties + schema fixes                                                                                                         |
| 0.1.0   | 2022-02-01 |                                                          | New Source: Orb                                                                                                                                                       |
| :---    | :---       | :---                                                     | :---                                                                                                                                                                  |

</details>
