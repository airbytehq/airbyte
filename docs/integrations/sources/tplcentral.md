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
| 0.1.5 | 2024-06-06 | [39150](https://github.com/airbytehq/airbyte/pull/39150) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.4 | 2024-06-03 | [38919](https://github.com/airbytehq/airbyte/pull/38919) | Replace AirbyteLogger with logging.Logger |
| 0.1.3 | 2024-06-03 | [38919](https://github.com/airbytehq/airbyte/pull/38919) | Replace AirbyteLogger with logging.Logger |
| 0.1.2 | 2024-05-20 | [38403](https://github.com/airbytehq/airbyte/pull/38403) | [autopull] base image + poetry + up_to_date |
| 0.1.1 | 2022-11-01 | [18763](https://github.com/airbytehq/airbyte/pull/18763) | Check if `url_base` parameter is set to HTTPS URL. |
| 0.1.0 | 2021-08-18 | [7322](https://github.com/airbytehq/airbyte/pull/7322) | New Source: 3PL Central |

</details>
