# Flexport

## Sync overview

Flexport source uses [Flexport API](https://developers.flexport.com/s/api) to extract data from Flexport.

### Output schema

This Source is capable of syncing the following data as streams:

- [Companies](https://apidocs.flexport.com/v3/tag/Company)
- [Locations](https://apidocs.flexport.com/v3/tag/Location)
- [Products](https://apidocs.flexport.com/v3/tag/Product)
- [Invoices](https://apidocs.flexport.com/v3/tag/Invoices)
- [Shipments](https://apidocs.flexport.com/v3/tag/Shipment)

### Data type mapping

| Integration Type | Airbyte Type | Notes                      |
| :--------------- | :----------- | :------------------------- |
| `number`         | `number`     | float number               |
| `integer`        | `integer`    | whole number               |
| `date`           | `string`     | FORMAT YYYY-MM-DD          |
| `datetime`       | `string`     | FORMAT YYYY-MM-DDThh:mm:ss |
| `array`          | `array`      |                            |
| `boolean`        | `boolean`    | True/False                 |
| `string`         | `string`     |                            |

### Features

| Feature                                   | Supported?\(Yes/No\) | Notes |
| :---------------------------------------- | :------------------- | :---- |
| Full Refresh Overwrite Sync               | Yes                  |       |
| Full Refresh Append Sync                  | Yes                  |       |
| Incremental - Append Sync                 | Yes                  |       |
| Incremental - Append + Deduplication Sync | Yes                  |       |
| Namespaces                                | No                   |       |

## Getting started

### Authentication

Authentication uses a pre-created API token which can be [created in the UI](https://apidocs.flexport.com/v3/tag/Authentication/).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------ |
| 0.2.15 | 2024-08-31 | [45035](https://github.com/airbytehq/airbyte/pull/45035) | Update dependencies |
| 0.2.14 | 2024-08-24 | [44638](https://github.com/airbytehq/airbyte/pull/44638) | Update dependencies |
| 0.2.13 | 2024-08-17 | [44308](https://github.com/airbytehq/airbyte/pull/44308) | Update dependencies |
| 0.2.12 | 2024-08-12 | [43918](https://github.com/airbytehq/airbyte/pull/43918) | Update dependencies |
| 0.2.11 | 2024-08-03 | [43129](https://github.com/airbytehq/airbyte/pull/43129) | Update dependencies |
| 0.2.10 | 2024-07-27 | [42621](https://github.com/airbytehq/airbyte/pull/42621) | Update dependencies |
| 0.2.9 | 2024-07-20 | [42390](https://github.com/airbytehq/airbyte/pull/42390) | Update dependencies |
| 0.2.8 | 2024-07-13 | [41926](https://github.com/airbytehq/airbyte/pull/41926) | Update dependencies |
| 0.2.7 | 2024-07-10 | [41526](https://github.com/airbytehq/airbyte/pull/41526) | Update dependencies |
| 0.2.6 | 2024-07-09 | [41145](https://github.com/airbytehq/airbyte/pull/41145) | Update dependencies |
| 0.2.5 | 2024-07-06 | [40777](https://github.com/airbytehq/airbyte/pull/40777) | Update dependencies |
| 0.2.4 | 2024-06-25 | [40454](https://github.com/airbytehq/airbyte/pull/40454) | Update dependencies |
| 0.2.3 | 2024-06-22 | [40013](https://github.com/airbytehq/airbyte/pull/40013) | Update dependencies |
| 0.2.2 | 2024-06-04 | [38943](https://github.com/airbytehq/airbyte/pull/38943) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.1 | 2024-05-20 | [38427](https://github.com/airbytehq/airbyte/pull/38427) | [autopull] base image + poetry + up_to_date |
| 0.2.0 | 2023-08-23 | [29151](https://github.com/airbytehq/airbyte/pull/29151) | Migrate to low-code |
| 0.1.1 | 2022-07-26 | [15033](https://github.com/airbytehq/airbyte/pull/15033) | Source Flexport: Update schemas |
| 0.1.0 | 2021-12-14 | [8777](https://github.com/airbytehq/airbyte/pull/8777) | New Source: Flexport |

</details>
