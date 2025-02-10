# Recurly

## Overview

The Recurly source supports _Full Refresh_ as well as _Incremental_ syncs.

_Full Refresh_ sync means every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.
_Incremental_ syn means only changed resources are copied from Recurly. For the first run, it will be a Full Refresh sync.

### Output schema

Several output streams are available from this source:

- [Accounts](https://docs.recurly.com/docs/accounts)
- [Account Notes](https://docs.recurly.com/docs/accounts#account-notes)
- [Account Coupon Redemptions](https://docs.recurly.com/docs/coupons#redemptions)
- [Add Ons](https://docs.recurly.com/docs/plans#add-ons-1)
- [Billing Infos](https://docs.recurly.com/docs/accounts#billing-info)
- [Coupons](https://docs.recurly.com/docs/coupons)
- [Unique Coupons](https://docs.recurly.com/docs/bulk-unique-coupons)
- [Credit Payments](https://docs.recurly.com/docs/invoices)
- [Automated Exports](https://docs.recurly.com/docs/export-overview)
- [Invoices](https://docs.recurly.com/docs/invoices)
- [Measured Units](https://developers.recurly.com/api/v2021-02-25/index.html#tag/measured_unit)
- [Line Items](https://docs.recurly.com/docs/invoices#line-items)
- [Plans](https://docs.recurly.com/docs/plans)
- [Shipping Addresses](https://docs.recurly.com/docs/shipping-addresses)
- [Shipping Methods](https://docs.recurly.com/docs/shipping#shipping-methods)
- [Subscriptions](https://docs.recurly.com/docs/subscriptions)
- [Subscription Changes](https://docs.recurly.com/docs/change-subscription#subscription-changes)
- [Transactions](https://docs.recurly.com/docs/transactions)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature                       | Supported?  |
| :---------------------------- | :---------- |
| Full Refresh Sync             | Yes         |
| Incremental Sync              | Yes         |
| Replicate Incremental Deletes | Coming soon |
| SSL connection                | Yes         |
| Namespaces                    | No          |

### Performance considerations

The Recurly connector should not run into Recurly API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- Recurly Account
- Recurly API Key

### Setup guide

Generate a API key using the [Recurly documentation](https://docs.recurly.com/docs/api-keys#section-find-or-generate-your-api-key)

We recommend creating a restricted, read-only key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                              |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------------------------------------------------------------- |
| 1.3.10 | 2025-02-08 | [53507](https://github.com/airbytehq/airbyte/pull/53507) | Update dependencies |
| 1.3.9 | 2025-02-01 | [52982](https://github.com/airbytehq/airbyte/pull/52982) | Update dependencies |
| 1.3.8 | 2025-01-25 | [52493](https://github.com/airbytehq/airbyte/pull/52493) | Update dependencies |
| 1.3.7 | 2025-01-18 | [51864](https://github.com/airbytehq/airbyte/pull/51864) | Update dependencies |
| 1.3.6 | 2025-01-11 | [51351](https://github.com/airbytehq/airbyte/pull/51351) | Update dependencies |
| 1.3.5 | 2024-12-28 | [50684](https://github.com/airbytehq/airbyte/pull/50684) | Update dependencies |
| 1.3.4 | 2024-12-21 | [50289](https://github.com/airbytehq/airbyte/pull/50289) | Update dependencies |
| 1.3.3 | 2024-12-14 | [49718](https://github.com/airbytehq/airbyte/pull/49718) | Update dependencies |
| 1.3.2 | 2024-12-12 | [49333](https://github.com/airbytehq/airbyte/pull/49333) | Update dependencies |
| 1.3.1 | 2024-12-11 | [49091](https://github.com/airbytehq/airbyte/pull/49091) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 1.3.0 | 2024-11-13 | [48474](https://github.com/airbytehq/airbyte/pull/48474) | Remove definition and schema redundancy, update to latest CDK and make compatibility with builder |
| 1.2.0 | 2024-11-04 | [47290](https://github.com/airbytehq/airbyte/pull/47290) | Migrate to manifest only format |
| 1.1.13 | 2024-11-04 | [48248](https://github.com/airbytehq/airbyte/pull/48248) | Update dependencies |
| 1.1.12 | 2024-10-28 | [47067](https://github.com/airbytehq/airbyte/pull/47067) | Update dependencies |
| 1.1.11 | 2024-10-12 | [46829](https://github.com/airbytehq/airbyte/pull/46829) | Update dependencies |
| 1.1.10 | 2024-10-05 | [46456](https://github.com/airbytehq/airbyte/pull/46456) | Update dependencies |
| 1.1.9 | 2024-09-28 | [46140](https://github.com/airbytehq/airbyte/pull/46140) | Update dependencies |
| 1.1.8 | 2024-09-21 | [45764](https://github.com/airbytehq/airbyte/pull/45764) | Update dependencies |
| 1.1.7 | 2024-09-14 | [45471](https://github.com/airbytehq/airbyte/pull/45471) | Update dependencies |
| 1.1.6 | 2024-09-07 | [45274](https://github.com/airbytehq/airbyte/pull/45274) | Update dependencies |
| 1.1.5 | 2024-08-31 | [45050](https://github.com/airbytehq/airbyte/pull/45050) | Update dependencies |
| 1.1.4 | 2024-08-24 | [44742](https://github.com/airbytehq/airbyte/pull/44742) | Update dependencies |
| 1.1.3 | 2024-08-17 | [44210](https://github.com/airbytehq/airbyte/pull/44210) | Update dependencies |
| 1.1.2 | 2024-08-10 | [43472](https://github.com/airbytehq/airbyte/pull/43472) | Update dependencies |
| 1.1.1 | 2024-08-03 | [43144](https://github.com/airbytehq/airbyte/pull/43144) | Update dependencies |
| 1.1.0 | 2024-07-24 | [40729](https://github.com/airbytehq/airbyte/pull/40729) | Migrate connector to low code |
| 1.0.12 | 2024-07-20 | [42206](https://github.com/airbytehq/airbyte/pull/42206) | Update dependencies |
| 1.0.11 | 2024-07-13 | [41836](https://github.com/airbytehq/airbyte/pull/41836) | Update dependencies |
| 1.0.10 | 2024-07-10 | [41500](https://github.com/airbytehq/airbyte/pull/41500) | Update dependencies |
| 1.0.9 | 2024-07-09 | [41174](https://github.com/airbytehq/airbyte/pull/41174) | Update dependencies |
| 1.0.8 | 2024-07-06 | [40820](https://github.com/airbytehq/airbyte/pull/40820) | Update dependencies |
| 1.0.7 | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215) | Replaced deprecated AirbyteLogger with logging.Logger |
| 1.0.6 | 2024-06-25 | [40474](https://github.com/airbytehq/airbyte/pull/40474) | Update dependencies |
| 1.0.5 | 2024-06-22 | [40012](https://github.com/airbytehq/airbyte/pull/40012) | Update dependencies |
| 1.0.4 | 2024-06-06 | [39178](https://github.com/airbytehq/airbyte/pull/39178) | [autopull] Upgrade base image to v1.2.2 |
| 1.0.3 | 2024-04-19 | [37246](https://github.com/airbytehq/airbyte/pull/37246) | Updating to 0.80.0 CDK |
| 1.0.2 | 2024-04-12 | [37246](https://github.com/airbytehq/airbyte/pull/37246) | schema descriptions |
| 1.0.1 | 2024-03-05 | [35828](https://github.com/airbytehq/airbyte/pull/35828) | Bump version to unarchive supportLevel in Cloud productionDB |
| 1.0.0 | 2024-03-01 | [35763](https://github.com/airbytehq/airbyte/pull/35763) | Re-introduce updated connector to catalog from archival repo |
| 0.5.0 | 2024-02-22 | [34622](https://github.com/airbytehq/airbyte/pull/34622) | Republish connector using base image/Poetry, update schemas |
| 0.4.1 | 2022-06-10 | [13685](https://github.com/airbytehq/airbyte/pull/13685) | Add state_checkpoint_interval to Recurly stream |
| 0.4.0 | 2022-01-28 | [9866](https://github.com/airbytehq/airbyte/pull/9866) | Revamp Recurly Schema and add more resources |
| 0.3.2 | 2022-01-20 | [8617](https://github.com/airbytehq/airbyte/pull/8617) | Update connector fields title/description |
| 0.3.1 | 2022-01-10 | [9382](https://github.com/airbytehq/airbyte/pull/9382) | Source Recurly: avoid loading all accounts when importing account coupon redemptions |
| 0.3.0 | 2021-12-08 | [8468](https://github.com/airbytehq/airbyte/pull/8468) | Support Incremental Sync Mode |

</details>
