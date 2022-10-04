# Orb

## Overview

The Orb source supports both Full Refresh and Incremental syncs. For incremental syncs, this source
will only read and output new records based on their `created_at` timestamp.

### Output schema

This Source is capable of syncing the following core resources, each of which has a separate Stream. Note that all of the streams are incremental:

* [Subscriptions](https://docs.withorb.com/docs/orb-docs/api-reference/operations/list-subscriptions)
* [Plans](https://docs.withorb.com/docs/orb-docs/api-reference/operations/list-plans)
* [Customers](https://docs.withorb.com/docs/orb-docs/api-reference/operations/list-customers)
* [Credits Ledger Entries](https://docs.withorb.com/docs/orb-docs/api-reference/operations/get-a-customer-credit-ledger)


As a caveat, the Credits Ledger Entries must read all Customers for an incremental sync, but will only incrementally return new ledger entries for each customers.

### Note on Incremental Syncs

The Orb API does not allow querying objects based on an `updated_at` time. Therefore, this connector uses the `created_at` field to query for new data since the last sync.

In order to capture data that has been updated after creation, please run a periodic Full Refresh.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Incremental - Dedupe Sync | Yes |
| SSL connection | Yes |

### Performance considerations

The Orb connector should not run into Orb API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Orb Account
* Orb API Key

### Setup guide

Please reach out to the Orb team at [team@withorb.com](mailto:team@withorb.com) to request
an Orb Account and API Key.

## Changelog

| Version | Date | Pull Request | Subject |
| --- | --- | --- | --- |
| 0.1.3 | 2022-08-26 | [16017](https://github.com/airbytehq/airbyte/pull/16017) | Add credit block id to ledger entries
| 0.1.2 | 2022-04-20 | [11528](https://github.com/airbytehq/airbyte/pull/11528) | Add cost basis to ledger entries, update expiration date, sync only committed entries
| 0.1.1 | 2022-03-03 | [10839](https://github.com/airbytehq/airbyte/pull/10839) | Support ledger entries with numeric properties + schema fixes
| 0.1.0 | 2022-02-01 | | New Source: Orb
| :--- | :--- | :--- | :--- |

