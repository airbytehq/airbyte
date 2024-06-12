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
| 0.1.2   | 2022-08-25 | [15667](https://github.com/airbytehq/airbyte/pull/15667) | Add message when no data available |
| 0.1.1   | 2022-05-30 | [11732](https://github.com/airbytehq/airbyte/pull/11732) | Fix docs                           |
| 0.1.0   | 2022-05-30 | [11732](https://github.com/airbytehq/airbyte/pull/11732) | Initial Release                    |

</details>