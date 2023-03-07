# Flexport

## Sync overview

Flexport source uses [Flexport API](https://developers.flexport.com/s/api) to extract data from Flexport.

### Output schema

This Source is capable of syncing the following data as streams:

- [Companies](https://apidocs.flexport.com/reference/company)
- [Locations](https://apidocs.flexport.com/reference/location)
- [Products](https://apidocs.flexport.com/reference/product)
- [Invoices](https://apidocs.flexport.com/reference/invoices)
- [Shipments](https://apidocs.flexport.com/reference/shipment)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `number` | `number` | float number |
| `integer` | `integer` | whole number |
| `date` | `string` | FORMAT YYYY-MM-DD |
| `datetime` | `string` | FORMAT YYYY-MM-DDThh:mm:ss |
| `array` | `array` |  |
| `boolean` | `boolean` | True/False |
| `string` | `string` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Overwrite Sync | Yes |  |
| Full Refresh Append Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Incremental - Append + Deduplication Sync | Yes |  |
| Namespaces | No |  |

## Getting started

### Authentication

Authentication uses a pre-created API token which can be [created in the UI](https://apidocs.flexport.com/reference/authentication).

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.1 | 2022-07-26 | [15033](https://github.com/airbytehq/airbyte/pull/15033) | Source Flexport: Update schemas |
| 0.1.0 | 2021-12-14 | [8777](https://github.com/airbytehq/airbyte/pull/8777) | New Source: Flexport |
