# Outbrain Amplify

## Sync overview

This source can sync data for the [Outbrain Amplify API](https://amplifyv01.docs.apiary.io/#reference/authentications). It supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This Source is capable of syncing the following core Streams:

- marketers stream.
- campaigns by marketers stream.-Incremental
- campaigns geo-location stream.
- promoted links for campaigns stream.
- promoted links sequence for campaigns stream.
- budgets for marketers stream.
- performance report campaigns by marketers stream.
- performance report periodic by marketers stream.
- performance report periodic by marketers campaign stream.
- performance report periodic content by promoted links campaign stream.
- performance report marketers by publisher stream.
- performance report publishers by campaigns stream.
- performance report marketers by platforms stream.
- performance report marketers campaigns by platforms stream.
- performance report marketers by geo performance stream.
- performance report marketers campaigns by geo stream.
- performance report marketers by Interest stream.

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `integer`        | `integer`    |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | Yes                  |       |
| Namespaces        | No                   |       |

### Performance considerations

The Outbrain Amplify connector should not run into Outbrain Amplify API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- Credentials and start-date.

### Setup guide

Specify credentials and a start date.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                            |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------- |
| 0.1.12 | 2024-08-31 | [45024](https://github.com/airbytehq/airbyte/pull/45024) | Update dependencies |
| 0.1.11 | 2024-08-24 | [44737](https://github.com/airbytehq/airbyte/pull/44737) | Update dependencies |
| 0.1.10 | 2024-08-17 | [44351](https://github.com/airbytehq/airbyte/pull/44351) | Update dependencies |
| 0.1.9 | 2024-08-10 | [43605](https://github.com/airbytehq/airbyte/pull/43605) | Update dependencies |
| 0.1.8 | 2024-08-03 | [43068](https://github.com/airbytehq/airbyte/pull/43068) | Update dependencies |
| 0.1.7 | 2024-07-27 | [42754](https://github.com/airbytehq/airbyte/pull/42754) | Update dependencies |
| 0.1.6 | 2024-07-20 | [42334](https://github.com/airbytehq/airbyte/pull/42334) | Update dependencies |
| 0.1.5 | 2024-07-13 | [41869](https://github.com/airbytehq/airbyte/pull/41869) | Update dependencies |
| 0.1.4 | 2024-07-10 | [41574](https://github.com/airbytehq/airbyte/pull/41574) | Update dependencies |
| 0.1.3 | 2024-07-08 | [41035](https://github.com/airbytehq/airbyte/pull/41035) | Migrate to poetry |
| 0.1.2 | 2022-08-25 | [15667](https://github.com/airbytehq/airbyte/pull/15667) | Add message when no data available |
| 0.1.1 | 2022-05-30 | [11732](https://github.com/airbytehq/airbyte/pull/11732) | Fix docs |
| 0.1.0 | 2022-05-30 | [11732](https://github.com/airbytehq/airbyte/pull/11732) | Initial Release |

</details>
