# TPL/3PL Central

## Overview

The 3PL Central source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

Several output streams are available from this source:

- [StockSummaries](https://api.3plcentral.com/rels/inventory/stocksummaries) \(Full table\)
- [Customers](https://api.3plcentral.com/rels/customers/customers) \(Full table\)
- [Items](https://api.3plcentral.com/rels/customers/items) \(Incremental\)
- [StockDetails](https://api.3plcentral.com/rels/inventory/stockdetails) \(Incremental\)
- [Inventory](https://api.3plcentral.com/rels/inventory/inventory) \(Incremental\)
- [Orders](https://api.3plcentral.com/rels/orders/orders) \(Incremental\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes        |
| SSL connection            | Yes        |
| Namespaces                | No         |

## Getting started

### Requirements

- Client ID
- Client Secret
- User login ID and/or name
- 3PL GUID
- Customer ID
- Facility ID
- Start date

### Setup guide

Please read [How to get your APIs credentials](https://help.3plcentral.com/hc/en-us/articles/360056546352-Getting-Started-with-Credential-Management).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                            |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------- |
| 0.1.34 | 2025-02-01 | [53049](https://github.com/airbytehq/airbyte/pull/53049) | Update dependencies |
| 0.1.33 | 2025-01-25 | [52413](https://github.com/airbytehq/airbyte/pull/52413) | Update dependencies |
| 0.1.32 | 2025-01-18 | [51981](https://github.com/airbytehq/airbyte/pull/51981) | Update dependencies |
| 0.1.31 | 2025-01-11 | [51428](https://github.com/airbytehq/airbyte/pull/51428) | Update dependencies |
| 0.1.30 | 2024-12-28 | [50761](https://github.com/airbytehq/airbyte/pull/50761) | Update dependencies |
| 0.1.29 | 2024-12-21 | [50358](https://github.com/airbytehq/airbyte/pull/50358) | Update dependencies |
| 0.1.28 | 2024-12-14 | [49410](https://github.com/airbytehq/airbyte/pull/49410) | Update dependencies |
| 0.1.27 | 2024-11-25 | [48648](https://github.com/airbytehq/airbyte/pull/48648) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.1.26 | 2024-11-04 | [48200](https://github.com/airbytehq/airbyte/pull/48200) | Update dependencies |
| 0.1.25 | 2024-10-28 | [47030](https://github.com/airbytehq/airbyte/pull/47030) | Update dependencies |
| 0.1.24 | 2024-10-12 | [46809](https://github.com/airbytehq/airbyte/pull/46809) | Update dependencies |
| 0.1.23 | 2024-10-05 | [46508](https://github.com/airbytehq/airbyte/pull/46508) | Update dependencies |
| 0.1.22 | 2024-09-28 | [46188](https://github.com/airbytehq/airbyte/pull/46188) | Update dependencies |
| 0.1.21 | 2024-09-21 | [45761](https://github.com/airbytehq/airbyte/pull/45761) | Update dependencies |
| 0.1.20 | 2024-09-14 | [45559](https://github.com/airbytehq/airbyte/pull/45559) | Update dependencies |
| 0.1.19 | 2024-09-07 | [45299](https://github.com/airbytehq/airbyte/pull/45299) | Update dependencies |
| 0.1.18 | 2024-08-31 | [44951](https://github.com/airbytehq/airbyte/pull/44951) | Update dependencies |
| 0.1.17 | 2024-08-24 | [44691](https://github.com/airbytehq/airbyte/pull/44691) | Update dependencies |
| 0.1.16 | 2024-08-17 | [44229](https://github.com/airbytehq/airbyte/pull/44229) | Update dependencies |
| 0.1.15 | 2024-08-10 | [43476](https://github.com/airbytehq/airbyte/pull/43476) | Update dependencies |
| 0.1.14 | 2024-08-03 | [43095](https://github.com/airbytehq/airbyte/pull/43095) | Update dependencies |
| 0.1.13 | 2024-07-27 | [42725](https://github.com/airbytehq/airbyte/pull/42725) | Update dependencies |
| 0.1.12 | 2024-07-20 | [42138](https://github.com/airbytehq/airbyte/pull/42138) | Update dependencies |
| 0.1.11 | 2024-07-13 | [41894](https://github.com/airbytehq/airbyte/pull/41894) | Update dependencies |
| 0.1.10 | 2024-07-10 | [41418](https://github.com/airbytehq/airbyte/pull/41418) | Update dependencies |
| 0.1.9 | 2024-07-09 | [41087](https://github.com/airbytehq/airbyte/pull/41087) | Update dependencies |
| 0.1.8 | 2024-07-06 | [40909](https://github.com/airbytehq/airbyte/pull/40909) | Update dependencies |
| 0.1.7 | 2024-06-25 | [40322](https://github.com/airbytehq/airbyte/pull/40322) | Update dependencies |
| 0.1.6 | 2024-06-22 | [40069](https://github.com/airbytehq/airbyte/pull/40069) | Update dependencies |
| 0.1.5 | 2024-06-06 | [39150](https://github.com/airbytehq/airbyte/pull/39150) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.4 | 2024-06-03 | [38919](https://github.com/airbytehq/airbyte/pull/38919) | Replace AirbyteLogger with logging.Logger |
| 0.1.3 | 2024-06-03 | [38919](https://github.com/airbytehq/airbyte/pull/38919) | Replace AirbyteLogger with logging.Logger |
| 0.1.2 | 2024-05-20 | [38403](https://github.com/airbytehq/airbyte/pull/38403) | [autopull] base image + poetry + up_to_date |
| 0.1.1 | 2022-11-01 | [18763](https://github.com/airbytehq/airbyte/pull/18763) | Check if `url_base` parameter is set to HTTPS URL. |
| 0.1.0 | 2021-08-18 | [7322](https://github.com/airbytehq/airbyte/pull/7322) | New Source: 3PL Central |

</details>
