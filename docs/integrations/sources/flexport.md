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
| 0.3.10 | 2025-01-25 | [52301](https://github.com/airbytehq/airbyte/pull/52301) | Update dependencies |
| 0.3.9 | 2025-01-18 | [51655](https://github.com/airbytehq/airbyte/pull/51655) | Update dependencies |
| 0.3.8 | 2025-01-11 | [51084](https://github.com/airbytehq/airbyte/pull/51084) | Update dependencies |
| 0.3.7 | 2024-12-28 | [50565](https://github.com/airbytehq/airbyte/pull/50565) | Update dependencies |
| 0.3.6 | 2024-12-21 | [50031](https://github.com/airbytehq/airbyte/pull/50031) | Update dependencies |
| 0.3.5 | 2024-12-14 | [49508](https://github.com/airbytehq/airbyte/pull/49508) | Update dependencies |
| 0.3.4 | 2024-12-12 | [49210](https://github.com/airbytehq/airbyte/pull/49210) | Update dependencies |
| 0.3.3 | 2024-11-04 | [48291](https://github.com/airbytehq/airbyte/pull/48291) | Update dependencies |
| 0.3.2 | 2024-10-29 | [47898](https://github.com/airbytehq/airbyte/pull/47898) | Update dependencies |
| 0.3.1 | 2024-10-28 | [47580](https://github.com/airbytehq/airbyte/pull/47580) | Update dependencies |
| 0.3.0 | 2024-10-05 | [46416](https://github.com/airbytehq/airbyte/pull/46416) | Migrate to Manifest-only CDK |
| 0.2.20 | 2024-10-05 | [46455](https://github.com/airbytehq/airbyte/pull/46455) | Update dependencies |
| 0.2.19 | 2024-09-28 | [46199](https://github.com/airbytehq/airbyte/pull/46199) | Update dependencies |
| 0.2.18 | 2024-09-21 | [45735](https://github.com/airbytehq/airbyte/pull/45735) | Update dependencies |
| 0.2.17 | 2024-09-14 | [45508](https://github.com/airbytehq/airbyte/pull/45508) | Update dependencies |
| 0.2.16 | 2024-09-07 | [45309](https://github.com/airbytehq/airbyte/pull/45309) | Update dependencies |
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
