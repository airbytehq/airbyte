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

| Version | Date       | Pull Request                                             | Subject                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------ |
| 0.2.1 | 2024-05-20 | [38427](https://github.com/airbytehq/airbyte/pull/38427) | [autopull] base image + poetry + up_to_date |
| 0.2.0 | 2023-08-23 | [29151](https://github.com/airbytehq/airbyte/pull/29151) | Migrate to low-code |
| 0.1.1 | 2022-07-26 | [15033](https://github.com/airbytehq/airbyte/pull/15033) | Source Flexport: Update schemas |
| 0.1.0 | 2021-12-14 | [8777](https://github.com/airbytehq/airbyte/pull/8777) | New Source: Flexport |
