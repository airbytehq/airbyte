# Freshservice

## Overview

The Freshservice supports full refresh syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

Several output streams are available from this source:

- [Tickets](https://api.freshservice.com/v2/#view_all_ticket) (Incremental)
- [Problems](https://api.freshservice.com/v2/#problems) (Incremental)
- [Changes](https://api.freshservice.com/v2/#changes) (Incremental)
- [Releases](https://api.freshservice.com/v2/#releases) (Incremental)
- [Requesters](https://api.freshservice.com/v2/#requesters)
- [Agents](https://api.freshservice.com/v2/#agents)
- [Locations](https://api.freshservice.com/v2/#locations)
- [Products](https://api.freshservice.com/v2/#products)
- [Vendors](https://api.freshservice.com/v2/#vendors)
- [Assets](https://api.freshservice.com/v2/#assets)
- [PurchaseOrders](https://api.freshservice.com/v2/#purchase-order)
- [Software](https://api.freshservice.com/v2/#software)
- [Satisfaction Survey Responses](https://api.freshservice.com/#ticket_csat_attributes)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| SSL connection    | No         |
| Namespaces        | No         |

### Performance considerations

The Freshservice connector should not run into Freshservice API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- Freshservice Account
- Freshservice API Key
- Freshservice domain name
- Replciation Start Date

### Setup guide

Please read [How to find your API key](https://api.freshservice.com/#authentication).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                |
| :------ | :--------- | :------------------------------------------------------- |:---------------------------------------------------------------------------------------|
| 1.3.6   | 2024-05-15 | [38195](https://github.com/airbytehq/airbyte/pull/38195) | Make connector compatible with builder                                                 |
| 1.3.5   | 2024-04-19 | [37162](https://github.com/airbytehq/airbyte/pull/37162) | Updating to 0.80.0 CDK                                                                 |
| 1.3.4   | 2024-04-18 | [37162](https://github.com/airbytehq/airbyte/pull/37162) | Manage dependencies with Poetry.                                                       |
| 1.3.3   | 2024-04-15 | [37162](https://github.com/airbytehq/airbyte/pull/37162) | Base image migration: remove Dockerfile and use the python-connector-base image        |
| 1.3.2   | 2024-04-12 | [37162](https://github.com/airbytehq/airbyte/pull/37162) | schema descriptions                                                                    |
| 1.3.1   | 2024-01-29 | [34633](https://github.com/airbytehq/airbyte/pull/34633) | Add backoff policy for `Requested Items` stream                                        |
| 1.3.0   | 2024-01-15 | [29126](https://github.com/airbytehq/airbyte/pull/29126) | Add `Requested Items` stream                                                           |
| 1.2.0   | 2023-08-06 | [29126](https://github.com/airbytehq/airbyte/pull/29126) | Migrated to Low-Code CDK                                                               |
| 1.1.0   | 2023-05-09 | [25929](https://github.com/airbytehq/airbyte/pull/25929) | Add stream for customer satisfaction survey responses endpoint                         |
| 1.0.0   | 2023-05-02 | [25743](https://github.com/airbytehq/airbyte/pull/25743) | Correct data types in tickets, agents and requesters schemas to match Freshservice API |
| 0.1.1   | 2021-12-28 | [9143](https://github.com/airbytehq/airbyte/pull/9143)   | Update titles and descriptions                                                         |
| 0.1.0   | 2021-10-29 | [6967](https://github.com/airbytehq/airbyte/pull/6967)   | 🎉 New Source: Freshservice                                                            |

</details>