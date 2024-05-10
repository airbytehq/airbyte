# Shortio

## Sync overview

The Shopify source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [Shortio API](https://developers.short.io/reference).

### Output schema

This Source is capable of syncing the following Streams:

- [Clicks](https://developers.short.io/reference#getdomaindomainidlink_clicks)
- [Links](https://developers.short.io/reference#apilinksget)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | Yes                  |       |
| Namespaces                | No                   |       |

## Getting started

1. Sign in at `app.short.io`.
2. Go to settings and click on `Integrations & API`.
3. In the API tab, click `Create API Kay`. Select `Private Key`.
4. Use the created secret key to configure your source!

## Changelog

| Version | Date       | Pull Request                                             | Subject                                           |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------ |
| 0.2.1   | 2024-05-02 | [37597](https://github.com/airbytehq/airbyte/pull/37597) | Change `last_records` to `last_record`            |
| 0.2.0   | 2023-08-02 | [28950](https://github.com/airbytehq/airbyte/pull/28950) | Migrate to Low-Code CDK                           |
| 0.1.3   | 2022-08-01 | [15066](https://github.com/airbytehq/airbyte/pull/15066) | Update primary key to `idString`                  |
| 0.1.2   | 2021-12-28 | [8628](https://github.com/airbytehq/airbyte/pull/8628)   | Update fields in source-connectors specifications |
| 0.1.1   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)   | Remove base-python dependencies                   |
| 0.1.0   | 2021-08-16 | [3787](https://github.com/airbytehq/airbyte/pull/5418)   | Add Native Shortio Source Connector               |
